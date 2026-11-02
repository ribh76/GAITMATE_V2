from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from gaitmate_api.db.base import Base, CreatedAtMixin, IdMixin, UpdatedAtMixin


class SensorSource(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "sensor_sources"
    __table_args__ = (
        UniqueConstraint("patient_id", "name"),
        UniqueConstraint("id", "patient_id"),
        CheckConstraint("kind IN ('replay', 'synthetic', 'hardware')", name="kind_allowed"),
    )

    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)


class RecordingSession(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "recording_sessions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["source_id", "patient_id"],
            ["sensor_sources.id", "sensor_sources.patient_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "patient_id"),
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="time_order"),
        CheckConstraint(
            "quality_status IN ('good', 'suspect', 'rejected')", name="quality_allowed"
        ),
        Index("ix_recording_sessions_patient_started", "patient_id", "started_at"),
    )

    source_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    quality_status: Mapped[str] = mapped_column(String(16), default="good", nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)
    sample_rate_hz: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))


class SensorReading(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (
        UniqueConstraint("session_id", "sequence", "channel"),
        UniqueConstraint("id", "session_id"),
        CheckConstraint("sequence >= 0", name="sequence_nonnegative"),
        CheckConstraint(
            "quality_status IN ('good', 'suspect', 'rejected')", name="quality_allowed"
        ),
        Index("ix_sensor_readings_session_captured", "session_id", "captured_at"),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("recording_sessions.id", ondelete="RESTRICT"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(80), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    quality_status: Mapped[str] = mapped_column(String(16), default="good", nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)


class DerivedMetric(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "derived_metrics"
    __table_args__ = (
        UniqueConstraint("id", "session_id"),
        ForeignKeyConstraint(
            ["reading_id", "session_id"],
            ["sensor_readings.id", "sensor_readings.session_id"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("ligament IN ('ATFL', 'CFL', 'PTFL')", name="ligament_allowed"),
        CheckConstraint(
            "quality_status IN ('good', 'suspect', 'rejected')", name="quality_allowed"
        ),
        Index("ix_derived_metrics_session_ligament_name", "session_id", "ligament", "name"),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("recording_sessions.id", ondelete="RESTRICT"), nullable=False
    )
    reading_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ligament: Mapped[str] = mapped_column(String(8), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    quality_status: Mapped[str] = mapped_column(String(16), default="good", nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(64), nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)
