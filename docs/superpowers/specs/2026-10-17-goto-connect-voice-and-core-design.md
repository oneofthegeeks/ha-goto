# GoTo Connect for Home Assistant — Voice Calls + Path to Core

**Date:** 2026-10-17
**Author:** Taylor Brinton (design conversation with Claude)
**Status:** Draft — pending approval

## Intent

`ha-goto` today is a HACS *custom-repository* integration (`goto_sms`, v1.3.10):
OAuth2 config flow, token refresh, and an SMS notify service against the GoTo
Connect Messaging v2 API. ~1,200 lines of Python, synchronous `requests`.

Taylor wants three things, in rising ambition:

1. **Voice alerts** — Home Assistant places a real phone call to a number and
   reads a TTS message aloud ("water leak detected"). Outbound, one-way,
   hang up when done.
2. **Easy installation** — inclusion in the HACS *default* store so users find
   it by searching, no custom-repository step.
3. **Official status** — acceptance into `home-assistant/core` as a built-in
   integration.

## Why voice goes over SIP, not the GoTo REST API

GoTo Connect has **no "place a call and speak this text" REST endpoint**
(unlike Twilio/Vonage). Its Devices & Calls API is WebRTC-based: the caller
must be a live media endpoint (SDP/ICE/RTP via browser-style WebRTC). Running
a WebRTC stack inside an HA integration was rejected.

Instead, the integration acts as a minimal **SIP user agent**: REGISTER
against GoTo's SIP infrastructure with device credentials, INVITE the target
number, stream TTS audio over RTP (PCMU/8000), hang up. Taylor has already
proven this exact flow against GoTo production using SIPp in
`oneofthegeeks/goto_demo_scripts` (wake-up-call demo). That repo is the
reference implementation and holds the hard-won protocol facts (see
Constraints).

Home Assistant core precedent: the official `voip` integration speaks SIP+RTP
in pure asyncio Python via the `voip-utils` PyPI library, including PCMU/8000
streaming. So a SIP media path is an accepted pattern in core.

## Goals

- `goto_connect.call_tts`-style service: call a phone number, speak a
  templated message rendered by any TTS engine the user has configured in HA,
  optionally repeat it, hang up. Report success/failure.
- Keep the existing SMS notify service working throughout.
- Fully async integration backed by a published PyPI client library
  (hard core requirement: API/protocol logic lives in the lib, not the
  integration).
- HACS default store inclusion.
- Core submission as domain `goto_connect`.

## Non-goals

- Two-way conversations, IVR, DTMF menus, or wiring calls into Assist
  (possible later; the SIP plumbing doesn't preclude it).
- Inbound call handling.
- GoTo Contact Center / call-events / reporting features.
- Answering-machine detection. If voicemail picks up, the message lands in
  voicemail — acceptable for v1.

## Anti-goals

- **Shipping binaries** (SIPp, ffmpeg assumptions beyond what HA provides).
  Disqualifies core and breaks non-x86 installs.
- **Breaking existing HACS users.** The `goto_sms` → `goto_connect` rename
  ships with a config-entry migration and release notes; no user re-auths
  from scratch without warning.
- Blocking the HA event loop. Everything async.

## Constraints and known facts

**Core acceptance requirements** (from HA developer docs; builder re-verifies
current rules at build time):

- API client as a standalone published PyPI package, typed, tested, with its
  own repo or clearly maintained source.
- Integration fully async (`aiohttp` / asyncio — no `requests`).
- OAuth through HA's **Application Credentials** framework, not a hand-rolled
  flow.
- Config flow, translations, quality-scale checklist, full test coverage of
  the config flow at minimum.
- Logo/brand PR to `home-assistant/brands` (also required by HACS default).
- New core integrations land in stages: first PR is minimal (config flow +
  one platform). SMS/notify first, voice service in a follow-up PR.
- The current manifest's `"quality_scale": "platinum"` self-claim is invalid
  and must be removed/replaced by the real checklist process.

**GoTo protocol facts, proven in `goto_demo_scripts` (`CLAUDE.md` there):**

- OAuth: `authentication.logmeininc.com/oauth/{authorize,token}`, Basic auth
  with base64(client_id:secret); scopes include `messaging.v1.send`.
- SMS: `POST https://api.goto.com/messaging/v1/messages` with
  `ownerPhoneNumber`, `contactPhoneNumbers`, `body`. Owner ≠ contact.
  No read scope available publicly.
- SIP: GoTo challenges with **407 Proxy Authentication Required** (handle 401
  too); separate **outbound proxy** (connection target) vs **SIP domain**
  (URI headers); `From` header must use the SIP username, not the local IP;
  REGISTER before INVITE with separate Call-ID; digest auth on both.
- Audio: PCMU/8000 — PCM 16-bit 8 kHz mono WAV source.

**SIP credentials:** there is **no public GoTo API** that provisions a SIP
device or returns SIP credentials (confirmed via GoTo dev docs + third-party
endpoint guides). But it's self-service in the portal: **GoTo Connect Admin →
Devices → Add Device → SIP Device** yields a SIP username + password
(documented in goto_demo_scripts' README). Baseline config flow: ask for
username + password only; SIP server defaults to `sip.goto.com` and the
outbound proxy is an optional advanced field. Docs walk the user through the
Add Device step. **Future enhancement, not v1:** API auto-provisioning if
Taylor confirms an internal/partner endpoint exists.

## Decided — by Taylor

- Voice = outbound call, TTS read aloud, one-way. HA generates the TTS audio.
- SIP is the transport.
- Prefer auto-provisioned SIP credentials, accept manual entry since
  auto-provisioning isn't publicly possible (see above).
- End goal is official core integration; HACS improvements land along the way.
- Reference implementation: `oneofthegeeks/goto_demo_scripts`.

## Decided — design calls (Claude's, flag if wrong)

- **New PyPI library**, pure asyncio, owning: OAuth token lifecycle,
  Messaging v2 client, and the SIP/RTP caller. Name candidate `gotoconnect`
  or `aiogotoconnect` — builder checks PyPI availability. Lives in its own
  repo (`oneofthegeeks/<libname>`) with CI publishing to PyPI on tags.
- **SIP implementation:** first evaluate reusing/extending `voip-utils`
  (core's own SIP lib) — it lacks digest auth and REGISTER today. If a clean
  PR or dependency isn't practical, implement a minimal SIP UA in our lib
  (REGISTER, INVITE, digest 401/407, ACK/BYE, single-codec PCMU RTP sender).
  The SIPp scenario XMLs in goto_demo_scripts are the message-level spec.
- **Domain rename** `goto_sms` → `goto_connect`, with automatic config-entry
  migration, during the HACS phase (before core submission).
- **Services:** SMS stays on the notify platform. Voice is
  `goto_connect.call_tts(target, message, tts_engine?, voice?, repeat=2)`.
  Message supports HA templates. Call outcome surfaced via service response /
  events.
- **TTS path:** follow the core `voip` integration's precedent — render via
  HA's TTS machinery, resample to 8 kHz mono PCM in-process (no ffmpeg
  dependency if voip-utils' conversion approach suffices).
- **Rollout order:**
  1. PyPI library (SMS + SIP caller) with its own tests.
  2. Rework `ha-goto` on the lib: async, application-credentials OAuth,
     domain rename + migration, add `call_tts`. Ship via HACS (v2.0.0) —
     Taylor dogfoods voice immediately.
  3. `home-assistant/brands` PR + HACS **default store** submission.
  4. Core PRs, staged: notify/SMS first, voice service second.
- **Testing:** lib gets pytest with a fake SIP server (asyncio) exercising
  the REGISTER/INVITE/auth flow; integration gets HA-standard config-flow
  tests. Live smoke = Taylor's real GoTo account + his phone.
- This is not a Poppy-deployed app: CI is GitHub Actions → PyPI (lib) and
  GitHub releases (integration). No Docker, no Infisical runtime rendering;
  test credentials stay in GitHub secrets / local `.env` only if ever needed.

## Left to the builder

- Exact SIP state machine details, RTP packet timing/jitter handling,
  teardown edge cases (busy, no-answer timeout, 486/487 handling).
- Resampling implementation choice.
- Config flow UX details (one entry with optional SIP section vs. two steps;
  voice should be optional — SMS-only users skip SIP entirely).
- How call progress/outcome maps to HA events and service responses.
- Current HA core submission checklist specifics (rules change; re-read
  developer.home-assistant.io at build time).
