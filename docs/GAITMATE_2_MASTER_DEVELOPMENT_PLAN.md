# GAITMATE 2.0 — MASTER DEVELOPMENT PLAN

**Version:** 1.0 — Locked Scope / Implementation Blueprint  
**Project:** GaitMate — Ankle Biomechanics & Rehabilitation Platform  
**Release target:** Portfolio-quality, deployed, end-to-end demonstrable application  
**Primary personas:** Patient and Physician / Rehabilitation Clinician  
**Demo model:** Exactly two linked fictional accounts (one patient, one physician)  
**Status:** Ready for implementation  

---

## PRODUCT MISSION

Build a two-sided rehabilitation platform connecting ankle biomechanics monitoring, clinician-directed rehabilitation, patient feedback, and explainable threshold notifications. The first release is a **research/demo application**, not a medical device, clinical decision support product, or emergency response service.

**The defining demo story:** A physician assigns a rehabilitation plan; the patient completes exercises and reports discomfort; a replayed ankle sensor recording generates a flagged monitoring event; the physician reviews the evidence, communicates with the patient, and revises the plan; both accounts see consistent, persistent updates.

### Locked decisions

- **Two roles:** Patient and Physician. Separate navigation and permissions, shared backend and underlying records.
- **Two linked demo accounts:** One fictional patient and one fictional physician, pre-associated; role switching is a demo convenience, not an authorization bypass.
- **Ankle-first:** ATFL, CFL, and PTFL are the first monitoring targets. No generalized PT platform scope creep.
- **CSV:** Retain the original CSV as an internal fixture for demo replay and testing. **No public CSV import/upload feature.**
- **No actual hardware in v1:** Clearly label all replayed/synthetic data. Provide a future-compatible provider boundary.
- **Risk:** Explainable, configurable, versioned heuristic monitoring thresholds; no validated injury probabilities, medical diagnoses, or emergency guarantees.
- **Rehabilitation:** Clinician-created and clinician-edited plans only; no AI-generated treatment suggestions.
- **Messaging:** In-app secure messaging, not personal email integration. No promise of emergency communication.
- **Future only:** Advanced analytics reports, real wearable sensor integration, appointments/scheduling.
- **Explicitly cut:** AI-assisted rehabilitation suggestions and external EHR integrations.

### Roadmap classification

- **FOUNDATION:** Required technical infrastructure and security controls.
- **MUST SHIP:** Required for release and the filmed demo.
- **SHIP LATER:** Design extension points now, do not implement product functionality in v1.
- **CUT:** Out of scope, including adjacent features that undermine focus.

### Definition of done for *every* phase

1. Implementation is merged through a reviewed PR with a clear description.
2. API contracts, schemas, and migrations are updated as needed.
3. Happy-path, error-path, and relevant authorization tests pass.
4. UI is responsive, keyboard-operable, and includes loading, empty, and failure states where applicable.
5. No secrets, real patient information, fabricated clinical claims, or unlabelled demo measurements are introduced.
6. Acceptance criteria are demonstrated with reproducible steps and captured in the phase PR.

---

# PART I — PRODUCT CONTRACT AND TECHNICAL FOUNDATION

## FEATURE 0 — Product contract, legacy audit, and implementation guardrails

### PHASE 0: Audit the prototype and freeze the scope — FOUNDATION

1. Inventory the existing Flask routes, services, CSV loader, risk calculations, HTML pages, JavaScript behaviors, assets, and sample recordings.
2. Identify reusable domain concepts (ATFL/CFL/PTFL, strain-related metrics, exercise catalog, threshold events) separately from legacy implementations.
3. Document the original CSV schema: columns, timestamps, units, sample rate (if known), missing values, and provenance; **do not assume measurements are clinically valid ligament strain**.
4. Establish the primary user journeys for patient and physician, including plan assignment, exercise feedback, messaging, alert review, and plan revision.
5. Write the explicit v1 feature matrix, ship-later list, and exclusions from the locked decisions above.
6. Create low-fidelity route maps and screen inventories for both roles; define navigation, shared design language, and accessibility expectations.
7. Specify the canonical domain vocabulary: user, relationship, profile, recording session, reading, metric, baseline, threshold policy, event, plan, plan version, exercise, completion, conversation, notification, and audit event.
8. Record product assumptions, unknown sensor semantics, medical-safety disclaimers, and unresolved decisions in an ADR/decision log.
9. Define the featured demo patient's fictional history and the exact end-to-end storyline; avoid designing for an unnecessary multi-patient demo population.
10. Produce a traceability matrix mapping every must-ship feature to a phase, endpoint, screen, and acceptance test.

**Acceptance gate:** Every locked feature has an owner in the roadmap; the sample recording has a documented schema and limitations; the two-role workflow can be narrated from beginning to end without imaginary functionality.

### PHASE 1: Repository, local development, and quality gates — FOUNDATION

1. Create a clean monorepo layout: `apps/web`, `apps/api`, `packages/contracts` (only if useful), `infra`, `scripts`, `tests`, `docs`, and `fixtures`.
2. Archive the old prototype in a clearly labeled legacy location or branch; remove tracked virtual environments, caches, binary clutter, and unnecessary generated files from the new working tree.
3. Initialize React + TypeScript + Vite for the frontend and FastAPI + Pydantic for the backend; preserve Python as the analytics implementation language.
4. Configure Tailwind CSS, shadcn/ui or equivalent accessible component primitives, React Router, TanStack Query, and a charting library.
5. Configure Python dependency management, Ruff, type checking where practical, pytest, frontend linting, formatting, TypeScript strict mode, and Vitest.
6. Add `.env.example`, secret-handling guidance, local database configuration, and a single documented developer bootstrap command or script.
7. Add GitHub Actions for lint, type checks, backend tests, frontend tests, and production builds on pull requests.
8. Define consistent API response/error formats, logging conventions, UTC timestamp policy, and API versioning (`/api/v1`).
9. Set up Docker Compose for local PostgreSQL (and optional API) without requiring containers for every frontend edit.
10. Create a project README with architecture diagram, setup instructions, scripts, and explicit demo/nonclinical status.

**Acceptance gate:** A fresh clone boots frontend, backend, and database using documented commands; CI passes; no legacy dependency or local machine path is required.

## FEATURE 1 — Data persistence and identity

### PHASE 2: Relational schema, migrations, and seed infrastructure — FOUNDATION

1. Configure PostgreSQL, SQLAlchemy, Alembic, and transaction-scoped database sessions.
2. Model `users`, `patient_profiles`, `clinician_profiles`, and `care_relationships` with explicit active/inactive relationship states.
3. Model `sensor_sources`, `recording_sessions`, `sensor_readings`, and `derived_metrics` with timestamps, units, provenance, quality status, and analysis version.
4. Model `rehab_plans`, immutable `rehab_plan_versions`, `plan_exercises`, `exercise_library_items`, `exercise_assignments`, and `exercise_logs`.
5. Model `conversations`, `messages`, `threshold_policies`, `monitoring_events`, `notifications`, and `audit_events`.
6. Establish foreign keys, unique constraints, sensible indexes, cascade/restrict rules, and clear ownership semantics; avoid deleting medical-like histories by accident.
7. Define server-managed timestamps, optimistic concurrency/version fields for mutable plans, and event state transitions.
8. Create initial and rollback-capable Alembic migrations; verify upgrade from an empty database.
9. Implement idempotent seed scripts for exactly two fictional linked accounts, an ankle profile, an initial plan, exercise catalog, and representative history.
10. Add schema tests for integrity, duplicate prevention, relationship constraints, and seed repeatability.

**Acceptance gate:** A fresh database can migrate and seed reproducibly; every core domain entity has a persistent representation and clear ownership.

### PHASE 3: Authentication, authorization, and account lifecycle — MUST SHIP

1. Implement account registration/invitation policy appropriate to the demo; provide pre-seeded demo sign-in paths without embedding privileged credentials in frontend source.
2. Implement secure password hashing, login/logout, session expiry, and server-managed refresh or reauthentication behavior.
3. Define patient and physician role claims and reusable FastAPI authorization dependencies.
4. Enforce patient ownership and active physician–patient relationship checks **at the data access/service layer**, not only in frontend routes.
5. Implement a patient–physician association workflow: invite/request, accept, revoke, and relationship status; seed one accepted relationship.
6. Implement `/me`, role-aware profile retrieval/update, basic account settings, and password-reset flow (using a safe development mail sink if email delivery is not configured).
7. Add rate limiting, input validation, CSRF protection where cookie-based authentication requires it, and safe session cookie/CORS configuration.
8. Build login, unauthorized, expired-session, and role-aware redirect screens.
9. Audit important identity and relationship changes without logging credentials or sensitive message bodies.
10. Write adversarial authorization tests: cross-patient IDs, inactive relationships, patient attempting physician writes, and unauthenticated API calls.

**Acceptance gate:** Both demo users can sign in and see their proper role; changing URLs or API IDs never grants unauthorized access; session expiration and logout work.

---

# PART II — SENSOR DATA AND BIOMECHANICS INTELLIGENCE

## FEATURE 2 — Sensor domain and recorded-session engine

### PHASE 4: Canonical sensor data pipeline — MUST SHIP

1. Define a typed canonical reading contract including source ID, session ID, timestamp, ligament/metric identity, value, unit, and quality flags.
2. Implement a `SensorDataProvider` interface with a replay/fixture implementation and a documented future hardware adapter boundary.
3. Build a **private/internal fixture loader** for the original CSV; reject malformed records and normalize only measurements whose units and meaning are documented.
4. Preserve raw source fields and provenance when normalization or derived calculations occur; never silently invent missing sensor metadata.
5. Create recording session lifecycle states (`created`, `ready`, `playing`, `paused`, `completed`, `failed`) separate from physical device connection state.
6. Persist timestamped readings and expose authorized session metadata, paginated/time-window reading queries, and quality summaries.
7. Implement baseline selection and reference-window storage with explicit comparison semantics and missing-baseline handling.
8. Create deterministic test fixtures for normal, missing, noisy, and threshold-crossing scenarios; label synthetic data as synthetic.
9. Add efficient indexes/query patterns and reasonable batch insertion for time-series reads; do not introduce a time-series database prematurely.
10. Test ingestion idempotency, timestamp ordering, duplicate detection, unit handling, and malformed fixtures.

**Acceptance gate:** The fixture can be loaded reproducibly into persisted sessions; frontend consumers never need to know CSV exists; no replay is mislabeled as a connected sensor.

### PHASE 5: Analytics engine and baseline comparisons — MUST SHIP

1. Audit the legacy risk algorithm and document which assumptions are unsupported; preserve only explainable calculations with known inputs.
2. Implement a pure analytics service for peaks, averages, ranges, standard deviation/variability, and rates of change, using explicit units.
3. Compute ATFL/CFL/PTFL metric series separately; distinguish directly observed values from derived estimates.
4. Implement per-session summaries, selected-window aggregations, and consistent timezone-aware date filtering.
5. Implement baseline-to-current comparison using comparable metric definitions and windows; return `insufficient_data` when comparison is invalid.
6. Implement session-to-session comparisons and derived metric version tags for reproducibility.
7. Define handling for outliers, gaps, invalid quality flags, and short windows without disguising missing evidence as normal results.
8. Expose typed analytics endpoints with calculation metadata, data-source labels, and explanatory fields.
9. Add unit tests for edge cases, zero variance, empty sessions, out-of-order data, missing baselines, and fixture-based regression results.
10. Write a concise analytics methodology document explaining every calculation, limitation, and nonclinical interpretation.

**Acceptance gate:** The same stored inputs produce identical results; the UI can display ligament trends, peaks, variability, and baseline differences without unsupported injury probability claims.

### PHASE 6: Deterministic session replay and live updates — MUST SHIP

1. Define replay controls: start, pause, resume, reset, seek, speed, and completion behavior.
2. Implement server-authoritative replay state or a deterministic coordinated replay model; document the source of truth for time and event emission.
3. Add a WebSocket or server-sent event channel for replay ticks, new readings, and monitoring events; keep REST endpoints for durable history.
4. Ensure replay can be run from the demo UI without uploading a file or exposing a CSV management page.
5. Bind replay readings to the featured fictional patient's recording context, with visible `DEMO REPLAY` labels on both role interfaces.
6. Implement reconnect/resume behavior and graceful fallback when the live connection drops.
7. Ensure repeated playback or seeking does not create duplicate monitoring events or corrupt persisted history.
8. Add playback progress, speed controls, and an explicit `No physical device connected` status.
9. Test pause/seek consistency, event order, reconnects, duplicate suppression, and deterministic end-of-recording state.
10. Provide a scripted one-command demo reset that restores the replay to a known starting state.

**Acceptance gate:** A reviewer can launch the recording, see synchronized time-series updates, pause/seek safely, and rerun the demo without duplicate alerts.

---

# PART III — PATIENT EXPERIENCE

## FEATURE 3 — Patient workspace and ankle monitoring

### PHASE 7: Shared design system and patient application shell — MUST SHIP

1. Define visual tokens, typography, spacing, colors, accessibility states, and chart conventions for the whole application.
2. Build shared components: app shell, sidebar, header, cards, status labels, data tables, dialogs, forms, toasts, skeletons, and error boundaries.
3. Implement role-aware routing and patient navigation: Dashboard, My Ankle, Rehab Plan, Progress, Messages, and Settings.
4. Build the patient dashboard layout with latest available recording status, current plan, upcoming exercises, recent feedback, and unread messages.
5. Make data-source status prominent: historical recording, demo replay, unavailable, or future live device; never infer connectivity from API health.
6. Integrate TanStack Query caching, invalidation, typed API clients, loading/error states, and optimistic updates only where safe.
7. Add responsive layouts for desktop and mobile, with accessible focus management and keyboard navigation.
8. Add empty states for no assigned plan, no baseline, no measurements, and no physician relationship.
9. Add component and route tests for role gating, loading, errors, and responsive critical workflows.

**Acceptance gate:** Patient login opens a cohesive, responsive dashboard with real seeded backend data and honest data-source status; no dashboard KPI is hardcoded in production UI.

### PHASE 8: Patient ligament explorer and history — MUST SHIP

1. Build an ankle anatomy view with selectable ATFL, CFL, and PTFL regions and accessible text alternatives.
2. Connect selected ligament to its measurements, latest available value, quality status, and historical time-series chart.
3. Add time-window selection, per-session filtering, and clear recording timestamps.
4. Display peak, mean, variability, and change-from-baseline values where valid.
5. Add annotations for monitoring events on relevant charts without labeling them as confirmed injuries.
6. Integrate replay playback and a moving cursor synchronized to the session timeline.
7. Provide comparative views for the three ligaments with consistent axes/units and explicit missing-data handling.
8. Add clear explanatory copy for metrics and the experimental nature of thresholds.
9. Test chart accuracy against API fixtures, selection state, empty history, and accessibility of nonvisual summaries.

**Acceptance gate:** The patient can select each ligament, inspect history, compare baseline metrics, and watch a recorded session update the visualization accurately.

## FEATURE 4 — Patient rehabilitation and progress

### PHASE 9: Assigned exercises, completion, and feedback — MUST SHIP

1. Implement read-only patient access to the active physician-approved plan and its prescribed exercise schedule.
2. Show exercise instructions, sets, reps, frequency, cautions, and optional media only when content is verified and appropriate.
3. Generate due exercises from the active plan version without double-assigning tasks after edits.
4. Implement exercise completion, skipped, and unable-to-complete outcomes with timestamps.
5. Capture discomfort (0–10), perceived difficulty, optional symptoms, and free-text notes after each attempt.
6. Persist feedback and prevent duplicate submissions using idempotency or unique completion constraints.
7. Show a personal exercise history and allow correction through a clearly auditable mechanism.
8. Surface newly revised plan versions and require the patient UI to refresh assigned tasks accordingly.
9. Write backend authorization tests and frontend submission/retry/error tests.

**Acceptance gate:** A completed exercise and its feedback remain visible after refresh and on the physician account; patients cannot alter prescription parameters.

### PHASE 10: Patient recovery progress dashboard — MUST SHIP

1. Define progress as separate measures, **not** an invented overall healing percentage.
2. Implement adherence as completed scheduled exercises divided by eligible scheduled exercises, with clear rules for skipped/canceled tasks.
3. Visualize self-reported discomfort trends and exercise difficulty over time.
4. Display physician-defined rehabilitation milestones and their recorded completion status.
5. Show ligament measurement trends and monitoring-event history alongside—but not causally attributed to—exercise activity.
6. Add plan-phase timeline and dates of physician revisions.
7. Provide weekly and selected-period summaries with explanations for insufficient history.
8. Add a compact progress summary on the patient dashboard linking to detailed views.
9. Test adherence calculations, revised schedules, empty periods, and date-boundary cases.

**Acceptance gate:** Progress reflects persisted exercise logs, milestone states, and measured data; no UI claims that a ligament has medically healed.

---

# PART IV — PHYSICIAN EXPERIENCE AND REHABILITATION CONTROL

## FEATURE 5 — Physician patient workspace

### PHASE 11: Physician shell, roster, and patient profile — MUST SHIP

1. Build physician navigation: Overview, Patients, Plans, Exercise Library, Alerts, Messages, and Settings.
2. Create the physician overview with assigned-patient count, unread messages, active plan status, and open monitoring events.
3. Implement a searchable patient roster with assignment state and last activity; the seeded demo contains exactly one linked patient.
4. Build a patient detail workspace with tabs for Overview, Monitoring, Rehabilitation, Feedback, Messages, and History.
5. Display the patient ankle profile, relevant limitations, rehabilitation start date, and physician-defined goals.
6. Provide secure editing of clinician-owned profile fields and audit meaningful changes.
7. Integrate the same analytics APIs used by the patient view with more detailed filters and annotations.
8. Show exercise adherence, discomfort reports, and open events together for efficient review.
9. Test roster scoping, direct-link authorization, and state updates across the two accounts.

**Acceptance gate:** The physician can find the linked patient, open a unified record, review measurements and feedback, and cannot view an unassigned patient by ID.

## FEATURE 6 — Exercise library and plan authoring

### PHASE 12: Exercise library and assignment primitives — MUST SHIP

1. Define exercise metadata: title, description, category, instructions, laterality, sets, reps, frequency, and contraindication/caution notes where available.
2. Seed a small, reviewed demonstration library of ankle rehabilitation exercises; do not present content as individualized medical advice.
3. Implement physician-only CRUD for custom exercise entries, with validation and safe archival rather than destructive deletion of referenced exercises.
4. Build search, filter, and exercise-detail screens for the clinician.
5. Support adding exercises to draft plans with plan-specific overrides for sets, reps, frequency, and instructions.
6. Preserve a snapshot or version reference to exercise content when a plan version is activated.
7. Implement ordering, duplication prevention, and schedule validation for assigned exercises.
8. Write tests for physician-only modifications, referenced exercise updates, and schedule consistency.

**Acceptance gate:** A physician can browse/create exercises and configure assignments; a historical plan is not silently altered when library content changes.

### PHASE 13: Rehabilitation plan builder and lifecycle — MUST SHIP

1. Implement a draft plan editor with name, goals, phases, exercises, milestones, and schedule.
2. Add server-side validation for missing exercises, invalid repetitions, conflicting dates, and incomplete activation requirements.
3. Implement plan states: Draft, Active, Paused, Completed, Archived, with explicitly permitted transitions.
4. Ensure only authorized physicians can activate, pause, resume, complete, or archive a patient's plan.
5. Implement immutable plan-version snapshots on every activation or published revision.
6. Build an edit-and-publish workflow that keeps the existing active plan stable until the new version is committed.
7. Prevent simultaneous conflicting edits using version checks and useful conflict messages.
8. Propagate activated revisions to patient exercise assignments and notifications without erasing prior completion logs.
9. Build plan comparison/history screens showing what changed, when, and by whom.
10. Test draft/active transitions, version immutability, revised scheduling, and concurrent update conflicts.

**Acceptance gate:** A physician can publish a plan, revise it, and compare versions; the patient sees only the current published prescription while historical logs remain intact.

### PHASE 14: Physician monitoring review and progress decisions — MUST SHIP

1. Build detailed clinician charts for each ligament with session filters, time windows, and baseline overlays.
2. Display signal quality, source provenance, units, and algorithm/threshold versions alongside interpreted metrics.
3. Add a synchronized view of monitoring events, exercise activity, and patient-reported discomfort on a timeline.
4. Implement clinician annotations linked to a recording/session or event with author and timestamp.
5. Provide a patient progress summary combining adherence, milestones, discomfort, and measurement trends without claiming causality.
6. Add navigation from an event to the exact supporting time window and measurement evidence.
7. Connect the monitoring workspace to the plan revision workflow without automatic clinical recommendations.
8. Test cross-view consistency and preservation of clinician annotations and review history.

**Acceptance gate:** The physician can investigate a flagged reading, inspect surrounding measurements, see patient feedback, and decide whether to edit the plan.

---

# PART V — COMMUNICATION AND MONITORING EVENTS

## FEATURE 7 — Secure patient–physician communication

### PHASE 15: Messaging, unread states, and conversation history — MUST SHIP

1. Model one conversation scoped to the active care relationship (or a clearly defined conversation lifecycle).
2. Implement authorized message send/list/read endpoints with pagination and timestamp ordering.
3. Build a shared message thread component with role-specific entry points from both dashboards.
4. Support unread counts, read receipts or last-read cursors, and reliable updates after refresh.
5. Implement safe text handling, length limits, and protection against HTML/script injection; omit file attachments from v1.
6. Add message notification events without exposing message content in public logs or notification subject lines.
7. Display a clear notice that messaging is not monitored for emergencies.
8. Define messaging behavior when the care relationship is revoked or inactive (history retained, new sends blocked).
9. Test sender identity, access isolation, message ordering, unread state, and failed-send retry behavior.

**Acceptance gate:** Patient and physician exchange persistent messages in both directions, receive unread indicators, and cannot read unrelated conversations.

## FEATURE 8 — Explainable monitoring thresholds and alerts

### PHASE 16: Threshold policy and event detection engine — MUST SHIP

1. Define an experimental threshold policy model scoped to patient, ligament/metric, unit, severity, effective date, and version.
2. Implement physician-only threshold configuration with validation and a clear warning that demo defaults are not clinical injury thresholds.
3. Evaluate magnitude, sustained duration, and rate of change only where sample timing and signal quality support those calculations.
4. Implement deterministic event states (`open`, `acknowledged`, `resolved`) and severity levels (`elevated`, `critical_threshold`).
5. Add hysteresis/cooldown or event-window deduplication to prevent alert storms from repeated measurements.
6. Persist the triggering measurements, recording source, time window, policy version, and calculation explanation.
7. Reject or mark indeterminate events when source quality is inadequate; never equate missing readings with normal health.
8. Make replay-triggered events clearly identifiable as **demo monitoring events** rather than real patient emergencies.
9. Test threshold boundaries, sustained events, cooldown behavior, missing data, policy revisions, and replay idempotency.
10. Document the difference between a configured threshold event, an injury diagnosis, and an emergency response.

**Acceptance gate:** A seeded replay crosses a known experimental threshold, creates one explainable event, and does not flood the database or imply medical certainty.

### PHASE 17: Notifications, alert center, and acknowledgment — MUST SHIP

1. Implement a persistent notification inbox for both roles with recipient, type, linked resource, delivery state, and read state.
2. Create notification triggers for new messages, published plan revisions, and monitoring events.
3. Implement a physician alert center with open/acknowledged/resolved filters, severity, patient context, and event time.
4. Support acknowledgment and resolution with actor, timestamp, and optional follow-up note.
5. Provide event-to-chart deep links showing the precise readings and policy that caused the alert.
6. Implement idempotent event-to-notification creation and a retryable delivery/outbox pattern as needed.
7. Add visible demo notifications in real time or via reliable polling, with refresh persistence.
8. Define optional email as a future delivery channel unless a privacy-safe, fully configured provider is available; do not imply email is already sent.
9. Add a prominent statement that alerts are not a guaranteed emergency monitoring or response service.
10. Test notification fan-out, deduplication, recipient authorization, read state, acknowledgment, and network retries.

**Acceptance gate:** The demo replay produces a physician notification; the physician opens evidence, acknowledges the event, and both event state and notification history persist.

---

# PART VI — INTEGRATION, SECURITY, AND RELEASE HARDENING

## FEATURE 9 — Cross-role workflows and integrity

### PHASE 18: Full workflow integration and audit trail — MUST SHIP

1. Wire every patient and physician view to the same persistent domain records; remove mock production values and disconnected local-only state.
2. Implement structured audit events for relationship changes, plan publication/revision, threshold policy edits, event acknowledgment, and other sensitive actions.
3. Ensure plan publication, task generation, notifications, and audit entries use consistent transaction boundaries or explicit eventual-consistency behavior.
4. Implement frontend cache invalidation and background refresh so updates appear correctly when switching between accounts.
5. Test the canonical story: plan assignment → patient completion/feedback → replay threshold event → clinician review/message → plan revision → patient update.
6. Verify historical integrity: previous plan versions, messages, completed exercises, and event evidence survive later changes.
7. Add clear, user-friendly failure handling for expired sessions, unavailable services, stale edits, and partial network outages.
8. Produce an end-to-end automated test for the canonical workflow using Playwright or equivalent.
9. Run a manual role-permission audit against every endpoint and every sensitive screen.
10. Reconcile the original feature traceability matrix and identify any must-ship gaps before deployment.

**Acceptance gate:** The full story works from two independent browser sessions, survives refreshes, and has a consistent audit trail with no cross-role data leaks.

### PHASE 19: Security, privacy, accessibility, and reliability — FOUNDATION / MUST SHIP

1. Perform threat modeling for authentication, authorization, patient relationships, replay events, messaging, and exposed demo credentials.
2. Enforce least privilege on every endpoint and verify object-level access with adversarial integration tests.
3. Review secrets, environment configuration, secure cookies, CORS, CSRF where applicable, password hashing, and login throttling.
4. Sanitize user-generated text, validate all inputs, constrain payload sizes, and prevent SQL injection via parameterized ORM access.
5. Remove real patient information and unapproved recordings; publish only fictional or appropriately authorized data.
6. Add audit log redaction and structured application logs that exclude sensitive message contents and authentication secrets.
7. Verify database backups/restoration approach and document data reset and retention expectations for the demo environment.
8. Audit keyboard accessibility, labels, focus states, contrast, chart text alternatives, and mobile layouts.
9. Run basic load/reliability tests on reading queries, replay connections, notification creation, and plan updates.
10. Fix high-severity findings, then rerun unit, integration, end-to-end, and authorization suites.

**Acceptance gate:** No known critical authorization/security defects; the app remains usable under ordinary network failures; the public demo contains no real patient data.

## FEATURE 10 — Deployment and operational readiness

### PHASE 20: Production-style deployment and documentation — MUST SHIP

1. Choose hosting: Vercel for the frontend and a managed API host plus managed PostgreSQL, or a comparably maintainable deployment.
2. Provision separate development and deployed environments with secret management and environment-specific CORS/origin settings.
3. Configure database migrations as an explicit release step with safe failure behavior.
4. Add health/readiness endpoints that distinguish API health, database availability, and actual sensor-source status.
5. Configure HTTPS, production build optimization, request logging, error monitoring, and basic uptime visibility.
6. Seed the two fictional demo accounts and their linked relationship through a secure, repeatable deployment-only process.
7. Implement a protected or operator-run demo reset that restores plans, logs, notifications, and replay position without publicly exposing privileged mutation endpoints.
8. Verify that the deployed app supports two simultaneous logged-in browser sessions and replay updates.
9. Write deployment, rollback, environment configuration, migration, and troubleshooting documentation.
10. Perform a clean deployment rehearsal and smoke test every major patient/physician workflow using the public URL.

**Acceptance gate:** The public app loads securely, both demo accounts function, the canonical workflow completes, and the demo can be reset predictably.

---

# PART VII — DEMONSTRATION, PRESENTATION, AND FINAL SUBMISSION

## FEATURE 11 — Demo experience and project packaging

### PHASE 21: Demo data, scripted narrative, and UI polish — MUST SHIP

1. Finalize one fictional patient profile and one fictional physician profile with a plausible but explicitly simulated rehabilitation scenario.
2. Create deterministic initial conditions: active plan, a few completed exercise logs, baseline recording, and a replay session containing a known threshold event.
3. Make demo account entry straightforward while keeping real authentication/authorization intact.
4. Prepare two browser profiles or windows so patient and physician interactions are visibly independent.
5. Add polished empty/loading/error states, consistent timestamps, helpful terminology, and concise metric explanations.
6. Ensure the replay visibly states that it uses recorded/synthetic data and does not connect to an actual sensor.
7. Script the physician's plan creation/revision and patient's exercise completion/feedback with predictable results.
8. Script the replay alert, physician acknowledgment, in-app message exchange, and revised plan notification.
9. Rehearse a full demo reset and replay multiple times, checking for flaky state, duplicate alerts, or timing dependencies.
10. Capture clean screenshots of the patient dashboard, ligament explorer, physician workspace, plan builder, and alert evidence.

**Acceptance gate:** A single operator can reproduce the entire two-sided narrative without manually editing the database or relying on chance.

### PHASE 22: Final QA, demo video, README, and submission — MUST SHIP

1. Freeze features and create a release candidate tag; only fix bugs or presentation blockers afterward.
2. Run the complete test suite, build checks, migration checks, accessibility smoke test, and production smoke tests.
3. Verify the feature traceability matrix: every must-ship item has a working route, API behavior, and passing acceptance evidence.
4. Write a portfolio-grade README with product pitch, architecture, stack, local setup, demo credentials/instructions, screenshots, and nonclinical limitations.
5. Document analytics formulas, experimental thresholds, sensor provenance, and the future hardware integration seam.
6. Produce a short architecture diagram and a data-flow diagram showing patient/physician workflows and monitoring events.
7. Record the demo video: sign in as physician → show plan → switch to patient → complete exercise and send feedback → run sensor replay → physician receives alert → review evidence → message/revise plan → patient sees update.
8. Edit the video for clarity: readable screen scale, visible role transitions, no false live-device claims, and concise narration of engineering choices.
9. Prepare a final project description, feature list, screenshots, technical challenges, lessons learned, and links to repository, deployed app, and demo video.
10. Perform a final clean-reset walkthrough using only public documentation, then submit/publish the project and tag the release.

**Acceptance gate:** Repository, deployed app, README, screenshots, and demo video all work and tell the same truthful product story; no must-ship feature is merely decorative.

---

# PART VIII — RELEASE CHECKLISTS AND ENGINEERING CONTRACTS

## Canonical end-to-end acceptance scenario

| Step | Acting role | Action | Persisted/verifiable result |
|---|---|---|---|
| 1 | Physician | Sign in and open linked patient | Authorized relationship; correct patient record |
| 2 | Physician | Publish rehab plan v1 | Immutable version; assigned exercises |
| 3 | Patient | Sign in and inspect plan | Same active plan v1 |
| 4 | Patient | Complete exercise, report discomfort | Exercise log and feedback visible to physician |
| 5 | Patient/demo operator | Start labeled session replay | Time-series updates from internal fixture |
| 6 | System | Detect experimental threshold crossing | One versioned event with measurement evidence |
| 7 | Physician | Open and acknowledge alert | Acknowledgment and audit record |
| 8 | Patient | Send an in-app message | Physician unread count increases |
| 9 | Physician | Reply and publish plan v2 | Message persists; plan v1 remains historical |
| 10 | Patient | View revised plan and message | Current plan v2; previous logs preserved |
| 11 | Demo operator | Reset demo | Deterministic initial state restored |

## Suggested API resource groups (contracts finalized during implementation)

- `/api/v1/auth/*`, `/api/v1/me`, `/api/v1/relationships/*`
- `/api/v1/patients/*`, `/api/v1/clinicians/*`
- `/api/v1/sessions/*`, `/api/v1/readings/*`, `/api/v1/analytics/*`, `/api/v1/baselines/*`
- `/api/v1/exercises/*`, `/api/v1/plans/*`, `/api/v1/exercise-logs/*`, `/api/v1/milestones/*`
- `/api/v1/conversations/*`, `/api/v1/messages/*`
- `/api/v1/threshold-policies/*`, `/api/v1/monitoring-events/*`, `/api/v1/notifications/*`
- `/api/v1/replay/*` (restricted to authorized demo contexts)
- `/api/v1/health`, `/api/v1/ready`

## Frontend route map (illustrative)

**Shared:** `/login`, `/settings`, `/unauthorized`  
**Patient:** `/patient`, `/patient/ankle`, `/patient/rehab`, `/patient/progress`, `/patient/messages`  
**Physician:** `/physician`, `/physician/patients`, `/physician/patients/:id`, `/physician/plans`, `/physician/exercises`, `/physician/alerts`, `/physician/messages`

## Data model invariants

1. Every protected patient resource belongs to a patient and is visible only to that patient or an authorized clinician with an active relationship.
2. Plan versions are immutable after publication; edits create new versions.
3. Exercise completion logs reference the applicable assigned plan version.
4. Every monitoring event references the evidence, source, and threshold policy version that produced it.
5. Demo replay is never represented as real-time hardware telemetry.
6. Derived metrics record calculation version and cannot masquerade as directly observed readings.
7. Messages preserve sender identity; notification content never grants access to unauthorized linked resources.
8. Historical records are not silently erased by plan revisions, threshold changes, or relationship revocation.
9. Demo reset is privileged and unavailable to ordinary users in a real clinical deployment.

## Suggested testing pyramid

- **Unit:** Pure analytics, thresholds, adherence, plan transitions, validation.
- **Integration:** Database constraints, API authorization, migrations, notifications, replay idempotency.
- **Frontend:** Forms, charts, role routes, loading/error states, accessibility checks.
- **End-to-end:** Two-account canonical scenario in separate browser contexts.
- **Security:** Cross-user ID tampering, revoked relationships, role escalation, replay abuse.
- **Deployment:** Public-URL smoke tests and reproducible demo reset.

## Phase dependency / critical path

`0 → 1 → 2 → 3 → 4 → 5 → 6` establishes the secure data and replay backbone.  
`3 + 5 → 7 → 8` enables the patient monitoring experience.  
`2 + 3 → 12 → 13 → 9 → 10` enables prescribed rehabilitation and progress.  
`3 + 7 → 11 → 14` enables clinician review.  
`3 → 15` enables secure communication.  
`5 + 6 → 16 → 17` enables evidence-backed alerts.  
`All product modules → 18 → 19 → 20 → 21 → 22` completes integration, release, and submission.

Phases are numbered in a practical build order; some can run in parallel once their dependencies are satisfied. Do not begin UI-only work that assumes an API contract that has not been agreed upon.

## Milestones and stop/go gates

| Milestone | Phases | Exit evidence |
|---|---|---|
| M0 — Scoped and bootable | 0–1 | Clean repo, ADRs, CI, dev environment |
| M1 — Secure persistent core | 2–3 | Seeded database, two working roles, access tests |
| M2 — Biomechanics engine | 4–6 | Normalized recordings, analytics, deterministic replay |
| M3 — Patient product | 7–10 | Dashboard, ankle view, exercises, progress |
| M4 — Clinician product | 11–14 | Roster, plan authoring/versioning, review workspace |
| M5 — Connected care workflow | 15–17 | Messaging, monitoring events, notifications |
| M6 — Release-ready system | 18–20 | End-to-end passing, hardened, deployed |
| M7 — Final deliverable | 21–22 | Resettable demo, video, documentation, release tag |

## Scope control: not in v1

- Public CSV upload/import UI.
- Actual sensor/Bluetooth integration.
- AI/ML injury prediction, AI-generated rehab prescriptions, or clinical risk probability claims.
- External EHR, insurance, billing, scheduling, video visits, or email inbox integrations.
- A generalized multi-clinic administrative platform.
- Guaranteed emergency monitoring, dispatch, or real-time clinical intervention.
- Advanced downloadable clinical reports (reserved for a later release).

## Future extension points (do not implement prematurely)

1. **Hardware:** Add a physical `SensorDataProvider` implementation with device pairing, verified calibration, and explicit connectivity semantics.
2. **Reporting:** Generate longitudinal clinician-review PDFs from versioned analytics and patient histories.
3. **Scheduling:** Introduce appointments only when patient/clinician calendar workflows are a validated product need.
4. **Clinical validation:** Work with qualified domain experts to validate measurement mapping, thresholds, reliability, and safety before making medical claims.

---

# FINAL DEFINITION OF RELEASE SUCCESS

GaitMate 2.0 is complete when a new reviewer can open the deployed app, use **one fictional patient account and one fictional physician account**, observe persistent shared records, inspect meaningful ATFL/CFL/PTFL analytics, follow a clinician-managed rehabilitation plan, submit exercise feedback, exchange messages, watch a clearly labeled simulated session trigger an explainable monitoring alert, acknowledge that alert, revise the plan with immutable history, and reproduce the entire scenario after a demo reset.

**Ship a complete vertical workflow, not a collection of attractive but disconnected screens.**
