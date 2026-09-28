# wagtail_zabbix

Prototype Wagtail + Zabbix integration application.

- [Implementation plan](docs/implementation-plan.md)

## Current scaffold

The project is pinned to the Wagtail 7.2 LTS line and Django 5.2. It currently provides:

- A Wagtail home page with an editable welcome message.
- Development settings using console email.
- SQLite for local development.
- Wagtail admin at `/admin/`.
- Search at `/search/`.

## Local setup

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

On Windows, use `.venv\\Scripts\\python.exe` instead of `.venv/bin/python`.

Copy the values from `.env.example` into your shell or deployment secret manager before starting the application. The project does not load `.env` files automatically. The development settings use safe local defaults; do not use them for production.

Open <http://localhost:8000/> for the site and <http://localhost:8000/admin/> for the Wagtail admin.

## Email configuration

Email settings are read from environment variables in `wagtail_zabbix/settings/base.py`.

### Development behavior

Development uses Django's console backend by default:

```text
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails are printed to the terminal running `manage.py runserver`; they are not sent. To exercise a real SMTP server locally, set `EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend` in the environment before starting the server. Never put a real password in source control.

### SMTP settings

| Variable | Purpose | Default |
| --- | --- | --- |
| `EMAIL_BACKEND` | Django email backend class | SMTP in base settings; console in development |
| `EMAIL_HOST` | SMTP server hostname | `localhost` |
| `EMAIL_PORT` | SMTP server port | `25` |
| `EMAIL_HOST_USER` | SMTP username, if required | empty |
| `EMAIL_HOST_PASSWORD` | SMTP password or provider token | empty |
| `EMAIL_USE_TLS` | Enable STARTTLS, normally with port `587` | `false` |
| `EMAIL_USE_SSL` | Enable implicit TLS/SSL, normally with port `465` | `false` |
| `EMAIL_TIMEOUT` | Connection timeout in seconds | `10` |
| `DEFAULT_FROM_EMAIL` | Default sender for application email | `webmaster@localhost` |
| `SERVER_EMAIL` | Sender for error emails | `DEFAULT_FROM_EMAIL` |
| `EMAIL_SUBJECT_PREFIX` | Prefix for automatically generated subjects | `[Wagtail Zabbix] ` |

Example submission for a typical authenticated SMTP provider:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=notifications@example.com
EMAIL_HOST_PASSWORD=provider-generated-password
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_TIMEOUT=10
DEFAULT_FROM_EMAIL=notifications@example.com
SERVER_EMAIL=server@example.com
EMAIL_SUBJECT_PREFIX="[Wagtail Zabbix] "
```

Use **either** `EMAIL_USE_TLS=true` or `EMAIL_USE_SSL=true`, not both. Port `587` generally uses STARTTLS; port `465` generally uses implicit SSL. Provider-specific requirements take precedence. For Gmail, Microsoft 365, and similar services, use an app password or provider-issued SMTP credential rather than a personal account password, and verify that the sender address is permitted.

### Test email delivery

With the development console backend, run:

```bash
.venv/bin/python manage.py shell -c "from django.core.mail import send_mail; send_mail('Wagtail Zabbix test', 'Email configuration works.', None, ['recipient@example.com'])"
```

For SMTP testing, set the SMTP variables in the same shell first. A successful command returns `1`; connection, authentication, TLS, and sender-policy errors are reported in the terminal. Do not log or paste `EMAIL_HOST_PASSWORD` into issue reports.

### Production checklist

- Store SMTP credentials in a secret manager or protected environment variables.
- Use TLS or SSL and a finite `EMAIL_TIMEOUT`.
- Set `DEFAULT_FROM_EMAIL` to a verified sender on the configured domain.
- Configure SPF, DKIM, and DMARC for the sending domain where applicable.
- Keep development on the console backend to prevent accidental external mail.
- Monitor delivery failures and avoid putting personal data or credentials in logs or Zabbix payloads.
