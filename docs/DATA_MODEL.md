# Data model and ownership

The initial Alembic revision creates 20 domain tables. PostgreSQL is the local and
target database; SQLAlchemy models use UUID keys and timestamp columns with time
zone. The API has no patient-facing persistence endpoints yet. The schema is a
foundation for those services, not a claim that workflows are implemented.

| Area | Tables | Owner and important links |
| --- | --- | --- |
| Identity | `users`, `patient_profiles`, `clinician_profiles`, `care_relationships` | A user has one role and at most one matching profile. A relationship identifies one patient and one clinician; its state is `active` or `inactive`. |
| Sensing | `sensor_sources`, `recording_sessions`, `sensor_readings`, `derived_metrics` | Sources belong to patients. A session's patient must match its source; readings and metrics belong to a session. Metrics carry unit, provenance, quality status, and analysis version. |
| Rehabilitation | `rehab_plans`, `rehab_plan_versions`, `exercise_library_items`, `plan_exercises`, `exercise_assignments`, `exercise_logs` | A plan belongs to a care relationship and its patient/clinician pair. Versions belong to one plan and must be authored by its clinician. Assignments and logs inherit patient ownership through their plan exercise. |
| Workflow | `conversations`, `messages`, `threshold_policies`, `monitoring_events`, `notifications`, `audit_events` | Conversations belong to a relationship; policies belong to its patient/clinician pair. An event's patient must match its policy and recording. Notifications belong to a recipient. Audit events retain actor and subject identifiers. |

Every historical foreign key uses `ON DELETE RESTRICT`; ORM relationships have no
delete cascades. Keep users and historical rows, and change status fields instead
of deleting them. A relationship row is unique per patient/clinician pair; its
state can change, with `ended_at` required when inactive. Changes of state should
produce audit events when the service layer is built.

Published plan versions are immutable. Build a draft version and its exercise
rows, then set `published_at`; database triggers reject later updates or deletes
to the version and inserts, updates, or deletes to its exercises. Create a new
version to revise a plan. Version numbers are unique within a plan. PostgreSQL
and SQLite migrations install equivalent guards so local schema tests exercise
this invariant.

Composite foreign keys prevent cross-patient source/session, event/policy, and
event/session links. They also bind plan authors to the plan clinician. Future
service-layer authorization must additionally check that message senders belong
to the conversation's relationship, exercise log authors are the assigned
patient, notification recipients may see their referenced event, and a care
relationship is active at the time of an operation. These checks span several
tables and cannot be inferred from a single foreign key. `audit_events.subject_id`
is deliberately polymorphic so the audit trail can name any entity; its subject
type and ID are recorded, without sensitive contents in `details`.

All instants use UTC. Recording values preserve the unit and provenance supplied
by their source, plus a quality status (`good`, `suspect`, or `rejected`). The
original CSV has unverified units and clinical validity; replay services must
label it as demo data.

## Database commands

After starting PostgreSQL with `docker compose -f infra/compose.yaml up -d --wait db`
and installing API dependencies, run:

```sh
.venv/bin/alembic -c apps/api/alembic.ini upgrade head
.venv/bin/alembic -c apps/api/alembic.ini current
.venv/bin/alembic -c apps/api/alembic.ini check
```

`./scripts/bootstrap.sh` runs the upgrade automatically. The optional API
container also upgrades before serving. Alembic reads `DATABASE_URL` from `.env`
or the environment. Revision files are in
`apps/api/src/gaitmate_api/migrations/versions` and are included in the API wheel.
Downgrading the initial revision drops every domain table and its data; use that
only against a disposable local database.

Use `transaction()` for standalone operations and `get_session()` as the FastAPI
dependency. Both commit when the block completes and roll back when an exception
escapes. Services should keep a single session per request and avoid committing
inside helper functions.

