# GoTo SMS for Home Assistant

[![CI](https://github.com/oneofthegeeks/ha-goto/actions/workflows/ci.yml/badge.svg)](https://github.com/oneofthegeeks/ha-goto/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/setup/prerequisites)

Send SMS from Home Assistant through your GoTo Connect account, and (optionally) place phone
calls that read a message aloud with Home Assistant text-to-speech.

- `goto_sms.send_sms` - SMS with Home Assistant templates
- `notify.goto_sms` - legacy notify service, still supported
- `goto_sms.call_tts` - phone call that speaks a TTS message (optional, needs SIP details)

Requires Home Assistant 2025.1.0 or newer.

## Installation

HACS custom repository (the integration is not yet in the HACS default store):

1. In HACS, open the menu > **Custom repositories**.
2. Add `https://github.com/oneofthegeeks/ha-goto` with category **Integration**.
3. Download **GoTo SMS** and restart Home Assistant.

Manual: copy `custom_components/goto_sms` into your `config/custom_components/` directory and restart.

## Upgrading from v1

Existing installs upgrade in place - your automations keep working. On first start the integration
moves your saved OAuth client ID/secret into Home Assistant's Application Credentials and keeps
your tokens, so you do not have to sign in again. `goto_sms.send_sms` and `notify.goto_sms` keep
the same fields.

If a v1 entry had no refresh token, Home Assistant shows a **Reauthenticate** prompt instead;
follow it once.

**Failed sends now raise.** v1 swallowed send errors (the automation carried on silently); v2
raises them, so failures show up in traces and logs and later steps in the automation stop. If you
want the old "keep going" behavior, set `continue_on_error: true` on the action:

```yaml
- action: goto_sms.send_sms
  continue_on_error: true
```

**Rollback:** back up your Home Assistant config before upgrading. A version-2 config entry cannot
load under v1.3.10; to downgrade you must delete the integration and add it again.

## Setup

### 1. Create a GoTo OAuth client

In the [GoTo Developer Portal](https://developer.goto.com/) create an OAuth client with:

- **Redirect URI:** `https://my.home-assistant.io/redirect/oauth`
- **Scope:** `messaging.v1.send`

Note the client ID and client secret. (If your Home Assistant does not load the `my` integration -
it is part of `default_config` - register `<your HA base URL>/auth/external/callback` instead.)

### 2. Add the integration

1. **Settings > Devices & Services > Add Integration > GoTo SMS**.
2. Home Assistant asks for the application credentials: enter the client ID and secret.
3. Sign in to GoTo and approve access.

## Sending SMS

```yaml
action: goto_sms.send_sms
data:
  message: "Garage door is open ({{ states('sensor.garage_temp') }}°F)"
  target: "+15551234567"
  sender_id: "+15557654321"   # a GoTo number on your account, E.164
```

| Field | Required | Description |
|-------|----------|-------------|
| `message` | yes | Text; Home Assistant templates are rendered |
| `target` | yes | Recipient number with country code |
| `sender_id` | yes | Your GoTo number to send from; must differ from `target` |
| `data` | no | Extra template variables, available by name (see below) |

Keys in `data` become template variables:

```yaml
action: goto_sms.send_sms
data:
  message: "{{ event }} detected in {{ zone }}"
  target: "+15551234567"
  sender_id: "+15557654321"
  data:
    event: "Door opening"
    zone: "front entrance"
```

If a template fails to render, the raw text is sent and an error is logged. The action can
return GoTo's response (`response_variable:`).

### Legacy notify

```yaml
action: notify.goto_sms
data:
  message: "Hello"
  target: ["+15551234567"]
  data:
    sender_id: "+15557654321"
```

The sender goes in `data.sender_id`; other `data` keys are template variables. New automations
should prefer `goto_sms.send_sms`.

## Voice calls (optional)

`goto_sms.call_tts` renders your message with a Home Assistant text-to-speech engine and calls the
number over SIP using the [`gotoconnect`](https://pypi.org/project/gotoconnect/) library. GoTo has no
REST call API, so this needs a SIP device on your account. SMS-only users can skip this section.

### SIP setup

1. In **GoTo Admin > Devices > Add Device > SIP Device**, create a device and note its username,
   password, server and outbound proxy.
2. In Home Assistant: **Settings > Devices & Services > GoTo SMS > Configure**.

| Option | Notes |
|--------|-------|
| SIP username / password | From the device page; enter both or neither. The password is never shown again: leave the field blank to keep the current one |
| SIP server | Defaults to `reg.jiveip.net` |
| Outbound proxy | Account specific, like `youraccount.jive.rtcfront.net` (on the device page). Required in practice - calls fail without it |

Clear the username and password to turn voice off. A text-to-speech integration (Home Assistant
Cloud, Piper, Google Translate, ...) must be set up in Home Assistant.

### Using it

```yaml
action: goto_sms.call_tts
data:
  target: "+15551234567"
  message: "The front door has been open for {{ states('sensor.door_open_minutes') }} minutes"
  tts_engine: tts.home_assistant_cloud   # optional; default engine if omitted
  language: en-US                        # optional
  repeat: 2                              # optional, 1-3, default 1
  ring_timeout: 30                       # optional, 5-60 seconds, default 25
response_variable: call
```

The response has `answered` (bool), `duration` (seconds), `reason` (why the call ended) and
`bye_confirmed` (the far end acknowledged the hang-up). For example, fall back to SMS:

```yaml
- if: "{{ not call.answered }}"
  then:
    - action: goto_sms.send_sms
      data:
        message: "Door alert: nobody picked up"
        target: "+15551234567"
        sender_id: "+15557654321"
```

Notes:

- **Admin only.** `call_tts` dials real phones, so a call made by a non-admin Home Assistant user is
  rejected. Automations and scripts started without a user are fine.
- A message with a template must render cleanly; unlike SMS, a failure is an error rather than
  reading template syntax aloud.
- The caller ID is your GoTo account's default for the SIP device; it cannot be set per call.

## Troubleshooting

- **Reauthenticate prompt / authentication errors:** GoTo rejected the tokens or the OAuth client.
  Follow the prompt on **Devices & Services**, and check the client ID/secret under
  **Settings > Devices & Services > Application Credentials**.
- **SMS not delivered:** use E.164 numbers (`+` and country code) and a `sender_id` that is a GoTo
  number on your account with SMS enabled. Sender and target must differ.
- **Voicemail counts as answered.** If the callee declines or is unavailable and the call rolls to
  voicemail, GoTo picks up, so `answered` is `true`. Read it as "the call connected", not "a person
  heard it".
- **Caller ID** is the GoTo default for the SIP device; change it in GoTo Admin.
- **"Voice calls are not configured":** add SIP details under the integration's **Configure**.
- **"GoTo rejected the SIP credentials":** re-check the username and password.
- **Voice calls fail:** make sure the outbound proxy for your account is set.
- **Debug logs:**

  ```yaml
  logger:
    default: info
    logs:
      custom_components.goto_sms: debug
      gotoconnect: debug
  ```

## Development

```bash
python -m venv .venv && .venv/bin/pip install -r requirements_test.txt
.venv/bin/python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).
