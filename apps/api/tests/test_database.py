from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, event, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from gaitmate_api.db.base import Base
from gaitmate_api.db.models import (
    CareRelationship,
    ClinicianProfile,
    ExerciseLibraryItem,
    PatientProfile,
    PlanExercise,
    RecordingSession,
    RehabPlan,
    RehabPlanVersion,
    SensorSource,
    User,
)
from gaitmate_api.db.session import transaction

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


@pytest.fixture
def database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[Engine, Config]]:
    url = f"sqlite:///{tmp_path / 'schema.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config(str(ALEMBIC_INI))
    command.upgrade(config, "head")
    engine = create_engine(url)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection: object, _connection_record: object) -> None:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")  # type: ignore[attr-defined]

    yield engine, config
    engine.dispose()


def _factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def _identity_pair(session: Session) -> tuple[User, User]:
    patient = User(email="patient@example.test", password_hash="test-hash", role="patient")
    clinician = User(email="clinician@example.test", password_hash="test-hash", role="clinician")
    session.add_all([patient, clinician])
    session.flush()
    session.add_all(
        [
            PatientProfile(user_id=patient.id, display_name="Demo Patient"),
            ClinicianProfile(user_id=clinician.id, display_name="Demo Clinician"),
        ]
    )
    session.flush()
    return patient, clinician


def test_migration_roundtrip(database: tuple[Engine, Config]) -> None:
    engine, config = database
    assert len(inspect(engine).get_table_names()) == 21  # 20 domain tables + alembic_version
    assert all(
        foreign_key.ondelete == "RESTRICT"
        for table in Base.metadata.tables.values()
        for foreign_key in table.foreign_keys
    )
    command.check(config)
    command.downgrade(config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]


def test_transaction_commits_and_rolls_back(database: tuple[Engine, Config]) -> None:
    engine, _ = database
    factory = _factory(engine)
    with transaction(factory) as session:
        session.add(User(email="kept@example.test", password_hash="test-hash", role="patient"))

    with pytest.raises(RuntimeError), transaction(factory) as session:
        session.add(User(email="lost@example.test", password_hash="test-hash", role="patient"))
        session.flush()
        raise RuntimeError("abort")

    with factory() as session:
        assert [user.email for user in session.scalars(select(User).order_by(User.email))] == [
            "kept@example.test"
        ]


def test_roles_relationships_and_restrict_delete(database: tuple[Engine, Config]) -> None:
    engine, _ = database
    factory = _factory(engine)
    with transaction(factory) as session:
        patient, clinician = _identity_pair(session)
        patient_id, clinician_id = patient.id, clinician.id
        session.add(CareRelationship(patient_id=patient_id, clinician_id=clinician_id))

    with pytest.raises(IntegrityError), transaction(factory) as session:
        session.add(ClinicianProfile(user_id=patient_id, display_name="Wrong role"))
        session.flush()

    with pytest.raises(IntegrityError), transaction(factory) as session:
        session.add(CareRelationship(patient_id=patient_id, clinician_id=clinician_id))
        session.flush()

    with pytest.raises(IntegrityError), transaction(factory) as session:
        session.delete(session.get(User, patient_id))
        session.flush()

    with pytest.raises(IntegrityError), transaction(factory) as session:
        relationship = session.scalar(select(CareRelationship))
        assert relationship is not None
        relationship.status = "inactive"
        session.flush()  # ended_at is required for inactive relationships


def test_recording_cannot_claim_another_patients_source(database: tuple[Engine, Config]) -> None:
    engine, _ = database
    factory = _factory(engine)
    with transaction(factory) as session:
        patient, _ = _identity_pair(session)
        other = User(email="other@example.test", password_hash="test-hash", role="patient")
        session.add(other)
        session.flush()
        session.add(PatientProfile(user_id=other.id, display_name="Other Patient"))
        source = SensorSource(
            patient_id=patient.id, name="Demo CSV", kind="replay", provenance="fixture"
        )
        session.add(source)
        session.flush()
        source_id, other_id = source.id, other.id

    with pytest.raises(IntegrityError), transaction(factory) as session:
        session.add(
            RecordingSession(
                source_id=source_id,
                patient_id=other_id,
                started_at=datetime.now(UTC),
                provenance="fixture",
            )
        )
        session.flush()


def test_published_plan_and_exercises_are_immutable(database: tuple[Engine, Config]) -> None:
    engine, _ = database
    factory = _factory(engine)
    with transaction(factory) as session:
        patient, clinician = _identity_pair(session)
        relationship = CareRelationship(patient_id=patient.id, clinician_id=clinician.id)
        library_item = ExerciseLibraryItem(
            created_by_clinician_id=clinician.id,
            slug="ankle-mobility",
            name="Ankle mobility",
            instructions="Demo only",
        )
        session.add_all([relationship, library_item])
        session.flush()
        plan = RehabPlan(
            relationship_id=relationship.id,
            patient_id=patient.id,
            clinician_id=clinician.id,
            title="Demo plan",
        )
        session.add(plan)
        session.flush()
        version = RehabPlanVersion(
            plan_id=plan.id,
            version_number=1,
            authored_by_clinician_id=clinician.id,
            summary="Initial",
        )
        session.add(version)
        session.flush()
        exercise = PlanExercise(version_id=version.id, library_item_id=library_item.id, position=0)
        session.add(exercise)
        session.flush()
        plan_id, version_id, library_id, exercise_id = (
            plan.id,
            version.id,
            library_item.id,
            exercise.id,
        )

    with transaction(factory) as session:
        other_clinician = User(
            email="other-clinician@example.test", password_hash="test-hash", role="clinician"
        )
        session.add(other_clinician)
        session.flush()
        session.add(ClinicianProfile(user_id=other_clinician.id, display_name="Other Clinician"))
        other_clinician_id = other_clinician.id

    with pytest.raises(IntegrityError), transaction(factory) as session:
        session.add(
            RehabPlanVersion(
                plan_id=plan_id,
                version_number=2,
                authored_by_clinician_id=other_clinician_id,
                summary="Wrong author",
            )
        )
        session.flush()

    with transaction(factory) as session:
        version = session.get(RehabPlanVersion, version_id)
        assert version is not None
        version.published_at = datetime.now(UTC)

    with pytest.raises(IntegrityError), transaction(factory) as session:
        version = session.get(RehabPlanVersion, version_id)
        assert version is not None
        version.summary = "Changed"
        session.flush()

    with pytest.raises(IntegrityError), transaction(factory) as session:
        session.add(PlanExercise(version_id=version_id, library_item_id=library_id, position=1))
        session.flush()

    with pytest.raises(IntegrityError), transaction(factory) as session:
        exercise = session.get(PlanExercise, exercise_id)
        assert exercise is not None
        exercise.position = 2
        session.flush()
