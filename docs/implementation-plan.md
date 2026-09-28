# Wagtail + Zabbix Prototype Implementation Plan

## 1. Current state

The repository now contains a Wagtail 7.2/Django 5.2 project scaffold with split settings, SQLite development configuration, a home page, search, and test coverage. Phase 1 content/authentication and the Phase 2 subscription slice are implemented; notification events, delivery, and Zabbix integration remain.

## 2. Prototype objective

Build a small Wagtail application that demonstrates a complete notification loop:

1. A visitor/user receives a welcome message.
2. An authenticated user subscribes to pages of interest.
3. Wagtail detects relevant page events, such as publication.
4. Subscribers receive a notification.
5. The event and delivery health are visible to Zabbix, and Zabbix can optionally send an alert back to Wagtail.

### Recommended integration boundary

- **Wagtail/Django** owns pages, users, subscriptions, notification content, recipients, and delivery history.
- **Zabbix** owns monitoring, alerting, escalation, and operational visibility.
- A small adapter connects the systems rather than coupling page models directly to Zabbix.

For the prototype, use Zabbix trapper items (via the sender protocol or `zabbix_sender`) for Wagtail-to-Zabbix telemetry. If inbound monitoring alerts are required, configure a Zabbix webhook media type that posts to a protected Wagtail webhook endpoint.

## 3. Scope

### In scope

- Wagtail LTS project with a demonstrable home page.
- Welcome message for a newly registered or first-time authenticated user.
- Subscribe/unsubscribe controls on eligible pages.
- Subscriber notifications for page publication; optionally include update and unpublish events.
- In-app notification inbox, with email as the first optional delivery channel.
- Notification and delivery status tracking.
- Zabbix integration health and event telemetry.
- A reproducible local demo using Docker Compose or documented local services.

### Out of scope for the first prototype

- Full multi-tenant notification preferences.
- High-volume fan-out or guaranteed exactly-once delivery.
- Replacing Zabbix's native media types and escalation engine.
- A production-grade task queue, unless the chosen demo environment already requires one.
- Complex editorial workflows beyond the page lifecycle needed for the demo.

## 4. Suggested domain model

Create a dedicated Django app, for example `notifications`:

- **PageSubscription**: user, page, active flag, subscribed timestamp, optional channel preferences.
- **NotificationEvent**: event type, page/reference, payload, created timestamp, correlation ID.
- **NotificationDelivery**: event, recipient, channel, status, attempt count, last error, delivered timestamp.
- **ZabbixIntegration**: preferably environment/configuration driven for the prototype; store only non-secret display metadata in the database if an admin view is needed.

Use stable event types such as:

- `welcome`
- `page_published`
- `page_updated`
- `page_unpublished`
- `subscription_created`
- `subscription_removed`
- `delivery_failed`
- `zabbix_alert_received`

## 5. Notification flows

### Welcome message

- On first login or registration, create a welcome notification.
- Display it in the Wagtail notification inbox.
- Provide a simple welcome page explaining subscriptions and notification preferences.
- Make the operation idempotent so refreshing or logging in again does not create duplicates.

### Page subscription

- Show a subscribe/unsubscribe control on pages that opt in, likely through a page model flag such as `allow_subscriptions`.
- Require authentication and protect mutations with CSRF and normal permission checks.
- On subscription, create or reactivate `PageSubscription` and create a confirmation notification.
- On unsubscribe, deactivate the subscription rather than deleting history.

### Page lifecycle notification

- Use the Wagtail page lifecycle hook appropriate to the selected LTS release.
- After a page is published, find active subscribers and create one notification event.
- Generate delivery records for each recipient and channel.
- Do not perform a slow external call inside the publish request. For the first version, use an outbox-style record and a management command; move to Celery/RQ later if needed.

### Common notifications

Implement these in priority order:

1. Welcome message.
2. Subscription confirmation and removal confirmation.
3. Page published.
4. Page updated or unpublished.
5. Delivery failure/integration failure.
6. Zabbix problem and recovery notifications received through the inbound webhook.

## 6. Wagtail application structure

Proposed apps/modules:

- `home`: site settings and welcome/home page.
- `content`: demo page types and subscription eligibility.
- `notifications`: models, event creation, templates, inbox, delivery service, and Wagtail hooks.
- `integrations.zabbix`: sender client, payload mapping, webhook authentication, and health checks.

Add a small admin-facing view or Wagtail panel showing:

- active subscriptions,
- recent notification events,
- failed deliveries,
- last successful Zabbix transmission,
- integration configuration status.

## 7. Zabbix interaction design

### Wagtail to Zabbix

Create a Zabbix host/template for the prototype with trapper items for values such as:

- `wagtail.notification.events`
- `wagtail.notification.deliveries.failed`
- `wagtail.integration.last_success_epoch`
- `wagtail.integration.queue_depth`

Send compact, non-sensitive values or event counters. Do not send page content, email addresses, tokens, or other personal data unless explicitly required.

Add simple Zabbix triggers, for example:

- delivery failures exceed a threshold,
- no successful Wagtail heartbeat within a time window,
- inbound/outbound integration errors persist.

### Zabbix to Wagtail

Only add this direction if the demo needs to show inbound alerts:

- Configure a Zabbix webhook media type/action to POST a signed or secret-bearing payload to Wagtail.
- Expose a CSRF-exempt but authentication-protected endpoint dedicated to Zabbix.
- Validate the shared secret/signature, timestamp/replay constraints, and event schema.
- Store the received alert as a notification event and show it in the inbox.
- Make processing idempotent using the Zabbix event ID.

Keep the sender and receiver behind interfaces so tests do not require a running Zabbix server.

## 8. Implementation phases

### Phase 0 — Confirm decisions and scaffold

- Choose the exact Wagtail LTS and supported Python/Django versions.
- Choose SQLite for the simplest demo or PostgreSQL if the deployment target requires it.
- Decide whether email is real SMTP, console email, or mocked locally.
- Create the Django/Wagtail project, settings split, environment configuration, and basic CI.

### Phase 1 — Content and authentication

- [x] Create the home page and a small demo page hierarchy.
- [x] Configure users, login/logout, and a minimal profile/onboarding path.
- [x] Add page metadata controlling whether subscriptions are allowed.

### Phase 2 — Subscriptions

- [x] Add `PageSubscription` and migrations.
- [x] Implement subscribe/unsubscribe actions and page UI.
- [x] Add permissions, CSRF protection, duplicate prevention, and tests.

### Phase 3 — Notification service

- Add event, delivery, and status models.
- Implement welcome, subscription, and page lifecycle event creation.
- Add inbox views, unread/read state, templates, and basic email rendering.
- Add an outbox/management command for delivery retries.

### Phase 4 — Zabbix adapter

- Implement a typed payload mapper and sender interface.
- Add configuration through environment variables/secrets.
- Send counters/heartbeat and notification delivery metrics.
- Add optional inbound webhook support and idempotency checks.
- Add a sample Zabbix template, trigger definitions, and setup instructions.

### Phase 5 — Hardening and demonstration

- Add retry/backoff, timeouts, structured logging, and correlation IDs.
- Redact secrets and personal data from logs and Zabbix payloads.
- Add health/readiness checks and an integration status screen.
- Run the complete demo from a clean environment and document the expected screenshots/logs.

## 9. Testing strategy

- **Model tests:** subscription uniqueness, deactivation, event idempotency, delivery state transitions.
- **View tests:** authentication, permissions, CSRF, subscribe/unsubscribe, inbox behavior.
- **Wagtail integration tests:** page publish/update/unpublish hooks create the expected events.
- **Adapter tests:** payload mapping, timeouts, retries, malformed responses, and secret handling using mocked HTTP/process calls.
- **Webhook tests:** authentication, replay/idempotency, invalid payloads, and Zabbix problem/recovery mapping.
- **End-to-end smoke test:** create user → receive welcome → subscribe → publish page → see notification → observe Zabbix metric/alert.

## 10. Acceptance criteria

The prototype is complete when:

- A clean install starts Wagtail and displays the welcome experience.
- A user can authenticate, subscribe to an eligible page, and unsubscribe.
- Publishing an eligible page creates exactly one event and a visible notification for each active subscriber.
- Failed delivery is recorded and can be retried without duplicating successful deliveries.
- Wagtail sends a heartbeat and notification/delivery metrics to a configured Zabbix instance, or clearly reports why it is unavailable.
- The optional inbound path accepts a valid Zabbix alert and rejects unauthenticated or duplicate requests.
- The README explains setup, environment variables, demo steps, and the Zabbix template/action configuration.

## 11. Decisions to confirm before implementation

1. Should Zabbix only monitor Wagtail, or should it also be the outbound notification engine?
2. Is the first delivery channel in-app only, console email, real email, or multiple channels?
3. Which Wagtail LTS/Python/Django versions must be supported?
4. Is inbound Zabbix-to-Wagtail alert handling required for the first demo?
5. Should the demo use SQLite or PostgreSQL, and Docker Compose or native local services?
