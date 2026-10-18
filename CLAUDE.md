# ha-goto

Live: v2.0.2 (2026-10-18) - G.722 wideband call_tts audio via aiogotoconnect 0.3.0 (SDP-negotiated, G.711 fallback; lib live-smoked on a real call). v2 base (app-credentials OAuth, SMS) validated live on Taylor's HA (2026.10.2).

## What This Is
Home Assistant custom integration (domain `goto_sms`) that sends SMS via GoTo Connect and, optionally, places TTS phone calls over SIP. Used by Taylor in production (see Live line) and published via HACS.

## Stack
- Python, Home Assistant custom integration (min HA 2025.1.0, see `hacs.json`); config-entry only.
- Auth: HA Application Credentials + OAuth2 (`GoToBasicAuthImplementation`), scope `messaging.v1.send`.
- SMS and voice via the `aiogotoconnect==0.3.0` PyPI lib (async; `GoToMessaging`, `GoToVoice`); 0.3.0 negotiates G.722 wideband for `call_tts` audio when GoTo accepts it (it does — live-smoked 2026-10-18), else G.711.
- Tests: pytest + pytest-homeassistant-custom-component.

## Local Development
```bash
git clone git@github.com:oneofthegeeks/ha-goto.git && cd ha-goto && git checkout v2
python -m venv .venv && .venv/bin/pip install -r requirements_test.txt
```
No running HA needed; copy `custom_components/goto_sms` into a HA config dir to try it live.

## Testing
`.venv/bin/python -m pytest` (61 tests). CI (`.github/workflows/ci.yml`, push/PR on main + v2): pytest, hassfest, HACS action.

## Deployment
HACS custom repo (default-store submission pending: hacs/default PR #12130). **Main is PR-only** (ruleset: required checks pytest floor/latest + hassfest + hacs, no force-push) — work lands via PRs that Taylor merges. Release = `git tag vX.Y.Z` (admin-only via tag ruleset) + GitHub release on `main`; Taylor is the only releaser. Entity-based notify and the `goto_connect` domain rename are deferred to the core-submission plan.

## Key Files
`custom_components/goto_sms/`:
- `__init__.py` - `async_setup` (registers services, legacy notify config), `async_setup_entry` (OAuth session, `GoToData`)
- `config_flow.py` / `options_flow.py` - OAuth flow (entry VERSION 2) / optional SIP options
- `application_credentials.py` - Basic-auth token implementation
- `migration.py` - v1 -> v2 entry migration
- `services.py` + `services.yaml` - `send_sms`, `call_tts` (schemas, TTS rendering, errors)
- `notify.py` - legacy `notify.goto_sms` shim; `const.py`; `icons.json`; `brand/`
- `tests/`, `docs/notes/ha-facts.md` (HA API research), `docs/superpowers/` (spec + plan)

## Gotchas
- SIP registrar is `reg.jiveip.net` plus a per-account outbound proxy (`<account>.jive.rtcfront.net`); `sip.goto.com` does not exist. Proxy is required in practice.
- GoTo has no working SIP-TLS endpoint for these devices; UDP is correct.
- GoTo's token endpoint needs HTTP Basic auth (`client_id:client_secret`), not body credentials.
- v1 entries nest tokens under `data["tokens"]` (`access_token`, `refresh_token`, `token_expires_at` as naive local ISO string); client creds are top-level.
- A migrated entry with no refresh token must reauth (`ConfigEntryAuthFailed`), not refresh `None`.
- Services are registered in `async_setup`, not per entry; `call_tts` is admin-only (checked manually; response-capable admin helper does not exist in 2025.1).
- `call_tts` templates render strictly (error), `send_sms` falls back to raw text (v1 behavior).
- HA 2025.1 lacks `tts.async_create_stream`; audio comes from the media-source helpers. `tts` is only an after_dependency, imported lazily.
- `answered` is true for voicemail pickup; caller ID is the account default.
- `scope` is added by the implementation's `extra_authorize_data`; do not repeat it in the flow.
- Template variables from `data` are top-level (`{{ zone }}`), not `{{ data.zone }}`.
