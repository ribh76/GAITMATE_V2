from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from gaitmate_api.db.base import Base, IdMixin, UpdatedAtMixin


class User(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('patient', 'clinician')", name="role_allowed"),
        CheckConstraint("status IN ('active', 'inactive')", name="status_allowed"),
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        UniqueConstraint("email"),
        UniqueConstraint("id", "role"),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)


class PatientProfile(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "patient_profiles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "user_role"], ["users.id", "users.role"], ondelete="RESTRICT"
        ),
        CheckConstraint("user_role = 'patient'", name="role_patient"),
    )

    user_id: Mapped[UUID] = mapped_column(unique=True, nullable=False)
    user_role: Mapped[str] = mapped_column(String(16), default="patient", nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)


class ClinicianProfile(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "clinician_profiles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "user_role"], ["users.id", "users.role"], ondelete="RESTRICT"
        ),
        CheckConstraint("user_role = 'clinician'", name="role_clinician"),
    )

    user_id: Mapped[UUID] = mapped_column(unique=True, nullable=False)
    user_role: Mapped[str] = mapped_column(String(16), default="clinician", nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(160))


class CareRelationship(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "care_relationships"
    __table_args__ = (
        UniqueConstraint("patient_id", "clinician_id"),
        UniqueConstraint("id", "patient_id", "clinician_id"),
        CheckConstraint("status IN ('active', 'inactive')", name="status_allowed"),
        CheckConstraint(
            "(status = 'active' AND ended_at IS NULL) OR "
            "(status = 'inactive' AND ended_at IS NOT NULL)",
            name="status_end_consistent",
        ),
        Index("ix_care_relationships_clinician_status", "clinician_id", "status"),
    )

    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    clinician_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinician_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
