from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from gaitmate_api.db.base import Base, CreatedAtMixin, IdMixin, UpdatedAtMixin


class RehabPlan(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "rehab_plans"
    __table_args__ = (
        UniqueConstraint("id", "clinician_id"),
        ForeignKeyConstraint(
            ["relationship_id", "patient_id", "clinician_id"],
            [
                "care_relationships.id",
                "care_relationships.patient_id",
                "care_relationships.clinician_id",
            ],
            ondelete="RESTRICT",
        ),
        CheckConstraint("status IN ('draft', 'active', 'archived')", name="status_allowed"),
        Index("ix_rehab_plans_patient_status", "patient_id", "status"),
    )

    relationship_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    clinician_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinician_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="draft", nullable=False)


class RehabPlanVersion(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "rehab_plan_versions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["plan_id", "authored_by_clinician_id"],
            ["rehab_plans.id", "rehab_plans.clinician_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("plan_id", "version_number"),
        CheckConstraint("version_number >= 1", name="version_positive"),
        Index("ix_rehab_plan_versions_plan_published", "plan_id", "published_at"),
    )

    plan_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    version_number: Mapped[int] = mapped_column(nullable=False)
    authored_by_clinician_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinician_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ExerciseLibraryItem(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "exercise_library_items"
    __table_args__ = (UniqueConstraint("slug"),)

    created_by_clinician_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinician_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class PlanExercise(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "plan_exercises"
    __table_args__ = (
        UniqueConstraint("version_id", "position"),
        CheckConstraint("position >= 0", name="position_nonnegative"),
        CheckConstraint("sets IS NULL OR sets > 0", name="sets_positive"),
        CheckConstraint("repetitions IS NULL OR repetitions > 0", name="repetitions_positive"),
        CheckConstraint("hold_seconds IS NULL OR hold_seconds > 0", name="hold_positive"),
    )

    version_id: Mapped[UUID] = mapped_column(
        ForeignKey("rehab_plan_versions.id", ondelete="RESTRICT"), nullable=False
    )
    library_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("exercise_library_items.id", ondelete="RESTRICT"), nullable=False
    )
    position: Mapped[int] = mapped_column(nullable=False)
    sets: Mapped[int | None]
    repetitions: Mapped[int | None]
    hold_seconds: Mapped[int | None]
    clinician_notes: Mapped[str | None] = mapped_column(Text)


class ExerciseAssignment(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "exercise_assignments"
    __table_args__ = (
        UniqueConstraint("plan_exercise_id", "scheduled_for"),
        CheckConstraint("status IN ('assigned', 'completed', 'cancelled')", name="status_allowed"),
        Index("ix_exercise_assignments_scheduled_status", "scheduled_for", "status"),
    )

    plan_exercise_id: Mapped[UUID] = mapped_column(
        ForeignKey("plan_exercises.id", ondelete="RESTRICT"), nullable=False
    )
    scheduled_for: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="assigned", nullable=False)


class ExerciseLog(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "exercise_logs"
    __table_args__ = (
        UniqueConstraint("assignment_id"),
        CheckConstraint(
            "discomfort_score IS NULL OR (discomfort_score >= 0 AND discomfort_score <= 10)",
            name="discomfort_range",
        ),
        Index("ix_exercise_logs_completed_at", "completed_at"),
    )

    assignment_id: Mapped[UUID] = mapped_column(
        ForeignKey("exercise_assignments.id", ondelete="RESTRICT"), nullable=False
    )
    recorded_by_patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    discomfort_score: Mapped[int | None]
    note: Mapped[str | None] = mapped_column(Text)
