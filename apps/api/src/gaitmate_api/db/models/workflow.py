from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    JSON,
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


class Conversation(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("relationship_id"),)

    relationship_id: Mapped[UUID] = mapped_column(
        ForeignKey("care_relationships.id", ondelete="RESTRICT"), nullable=False
    )


class Message(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_conversation_sent", "conversation_id", "sent_at"),)

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="RESTRICT"), nullable=False
    )
    sender_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ThresholdPolicy(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "threshold_policies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["relationship_id", "patient_id", "clinician_id"],
            [
                "care_relationships.id",
                "care_relationships.patient_id",
                "care_relationships.clinician_id",
            ],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("relationship_id", "ligament", "metric_name", "version"),
        UniqueConstraint("id", "patient_id"),
        CheckConstraint("version >= 1", name="version_positive"),
        CheckConstraint("ligament IN ('ATFL', 'CFL', 'PTFL')", name="ligament_allowed"),
        CheckConstraint("comparator IN ('gt', 'gte', 'lt', 'lte')", name="comparator_allowed"),
        CheckConstraint("status IN ('active', 'inactive')", name="status_allowed"),
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="time_order"),
        Index("ix_threshold_policies_patient_status", "patient_id", "status"),
    )

    relationship_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    clinician_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinician_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    ligament: Mapped[str] = mapped_column(String(8), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(80), nullable=False)
    comparator: Mapped[str] = mapped_column(String(4), nullable=False)
    threshold_value: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MonitoringEvent(IdMixin, UpdatedAtMixin, Base):
    __tablename__ = "monitoring_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["policy_id", "patient_id"],
            ["threshold_policies.id", "threshold_policies.patient_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["session_id", "patient_id"],
            ["recording_sessions.id", "recording_sessions.patient_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["metric_id", "session_id"],
            ["derived_metrics.id", "derived_metrics.session_id"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("status IN ('open', 'acknowledged', 'resolved')", name="status_allowed"),
        Index(
            "ix_monitoring_events_patient_status_observed", "patient_id", "status", "observed_at"
        ),
    )

    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    policy_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    session_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    metric_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    observed_value: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)


class Notification(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("status IN ('unread', 'read', 'dismissed')", name="status_allowed"),
        Index("ix_notifications_recipient_status_created", "recipient_id", "status", "created_at"),
    )

    recipient_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("monitoring_events.id", ondelete="RESTRICT")
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="unread", nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditEvent(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_subject_created", "subject_type", "subject_id", "created_at"),
        Index("ix_audit_events_actor_created", "actor_id", "created_at"),
    )

    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    details: Mapped[dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
