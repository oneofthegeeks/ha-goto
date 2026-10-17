# gotoconnect PyPI Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A pure-asyncio PyPI library `gotoconnect` that sends SMS via GoTo's Messaging v2 API and places outbound SIP calls that stream audio (TTS WAV) to a phone — the foundation for the Home Assistant integration.

**Architecture:** Three independent layers in one package: an OAuth token layer (pluggable, so HA can supply tokens), an aiohttp Messaging v2 client, and a minimal SIP user agent (REGISTER → INVITE with digest auth → RTP audio → BYE) over UDP or TLS, with RTP packetization and WAV→G.711 conversion in-process. Tested against an asyncio fake GoTo SIP server; no binaries.

**Tech Stack:** Python ≥ 3.12, `aiohttp`, `audioop-lts` (py≥3.13 marker), hashlib digest auth, pytest + pytest-asyncio. New repo `oneofthegeeks/gotoconnect` at `~/dev/gotoconnect`, src layout.

**Spec:** `/home/taylor/dev/ha-goto/docs/superpowers/specs/2026-10-17-goto-connect-voice-and-core-design.md` (read it first). Protocol reference: `/home/taylor/dev/goto_demo_scripts/sipp/scenarios.py` (exact proven SIP message flow) and `/home/taylor/dev/goto_demo_scripts/CLAUDE.md` ("SIP (GoTo Connect)" + "SMS" sections).

## Global Constraints

- Pure Python, no binaries, no `requests` — everything asyncio (`aiohttp` for HTTP).
- SIP facts (proven against GoTo prod, do not "improve"): expect **407 Proxy Authentication Required** (handle 401 too); `From` header user = SIP username, never local IP; REGISTER before INVITE with a distinct Call-ID; digest on both REGISTER and INVITE; SDP offers `m=audio <port> RTP/AVP 8 101`, `a=rtpmap:8 PCMA/8000`, `a=rtpmap:101 telephone-event/8000`; default ring timeout 25 s.
- SMS facts: `POST https://api.goto.com/messaging/v1/messages`, JSON `{"ownerPhoneNumber", "contactPhoneNumbers", "body"}`; owner must differ from contact.
- Defaults: SIP server `sip.goto.com`, UDP port 5060, TLS port 5061, outbound proxy optional (when set, it is the connection target; the server stays in URIs).
- Secrets never logged: no passwords, tokens, or digest responses at any log level.
- License MIT, repo private initially, Conventional Commits.
- This library repo may be tagged/released freely — it cannot affect the production `ha-goto` v1.3.10 install (that constraint binds the integration repo only).

## Review Focus

Failure modes the spec implies that must not break a real user — each pinned to a test in the owning task:

1. Callee hangs up mid-playback (the demo hit this: BYE arrives during audio) → call ends cleanly, reported answered, no exception. (Task 8)
2. No answer within ring timeout → CANCEL sent, result `answered=False, reason="no-answer"`, no hang. (Task 8)
3. Busy / rejected (486/603) → clean result `reason="busy"`, ACK sent for the error response. (Task 8)
4. Wrong SIP password (407 loops) → raises `GoToAuthError` after the second challenge, never infinite retry. (Task 8)
5. Arbitrary WAV input (stereo, 44.1 kHz, 24-bit) → converted to 8 kHz mono 16-bit before encoding, no corruption-by-assumption. (Task 5)

---

### Task 1: Repo scaffold + exceptions + token layer

**Files:**
- Create: `~/dev/gotoconnect/pyproject.toml`, `README.md`, `LICENSE` (MIT), `.gitignore`, `.github/workflows/ci.yml`
- Create: `src/gotoconnect/__init__.py`, `src/gotoconnect/exceptions.py`, `src/gotoconnect/auth.py`
- Test: `tests/test_auth.py`

**Interfaces:**
- Produces:
  - `exceptions.py`: `GoToError(Exception)`, `GoToAuthError(GoToError)`, `GoToApiError(GoToError)` (has `.status: int`), `GoToSipError(GoToError)`, `GoToCallError(GoToSipError)`.
  - `auth.py`: `TokenProvider = Callable[[], Awaitable[str]]` (type alias — any async callable returning a bearer token; HA passes its own).
  - `class GoToOAuth` — standalone provider: `__init__(self, client_id: str, client_secret: str, refresh_token: str, token_url: str = "https://authentication.logmeininc.com/oauth/token", session: aiohttp.ClientSession | None = None)`; `async def async_get_access_token(self) -> str` (refreshes via `grant_type=refresh_token` with Basic auth `base64(client_id:client_secret)` when missing or within 60 s of expiry, caches otherwise); `refresh_token` attribute updated when the response rotates it.

- [ ] **Step 1: Scaffold repo**

`git init` at `~/dev/gotoconnect`, src layout, `pyproject.toml` with name `gotoconnect`, version `0.1.0`, `requires-python = ">=3.12"`, deps `aiohttp>=3.9`, `audioop-lts>=0.2; python_version >= '3.13'`; dev deps `pytest`, `pytest-asyncio`, `pytest-aiohttp`. CI workflow: on push/PR, run `pytest` on Python 3.12 and 3.13.

- [ ] **Step 2: Write failing tests**

In `tests/test_auth.py` (use `aiohttp.test_utils` or a local `aiohttp.web` app as the token endpoint):
```python
async def test_refreshes_token_with_basic_auth():
    # fake endpoint asserts Authorization == Basic base64(id:secret) and
    # body grant_type=refresh_token, returns {"access_token": "AT1",
    # "refresh_token": "RT2", "expires_in": 3600}
    oauth = GoToOAuth("id", "secret", "RT1", token_url=fake_url)
    assert await oauth.async_get_access_token() == "AT1"
    assert oauth.refresh_token == "RT2"

async def test_caches_until_near_expiry():
    # endpoint counts calls; two gets within expiry window -> 1 call

async def test_http_error_raises_gotoautherror():
    # endpoint returns 401 -> GoToAuthError
```

- [ ] **Step 3: Run tests, verify they fail** (`pytest tests/test_auth.py -v` → import errors/FAIL)
- [ ] **Step 4: Implement `exceptions.py` and `auth.py`**
- [ ] **Step 5: Run tests, verify pass; commit** (`feat: scaffold gotoconnect lib with OAuth token layer`)

### Task 2: Messaging v2 SMS client

**Files:**
- Create: `src/gotoconnect/messaging.py`
- Test: `tests/test_messaging.py`

**Interfaces:**
- Consumes: `TokenProvider`, `GoToApiError`, `GoToAuthError` (Task 1).
- Produces: `class GoToMessaging`: `__init__(self, token_provider: TokenProvider, session: aiohttp.ClientSession | None = None, base_url: str = "https://api.goto.com")`; `async def async_send_sms(self, owner_phone: str, contacts: list[str], body: str) -> dict` (returns parsed response JSON).

- [ ] **Step 1: Write failing tests** — fake `aiohttp.web` endpoint asserting `Authorization: Bearer <token>`, exact JSON body shape `{"ownerPhoneNumber", "contactPhoneNumbers", "body"}`; cases: success 200 returns JSON; 401 → `GoToAuthError`; 4xx/5xx → `GoToApiError` with `.status`; `owner == contact` raises `ValueError` client-side (GoTo rejects it confusingly — fail fast locally).
- [ ] **Step 2: Run tests, verify fail**
- [ ] **Step 3: Implement `messaging.py`**
- [ ] **Step 4: Run tests, verify pass; commit** (`feat: messaging v2 SMS client`)

### Task 3: SIP message build/parse + digest auth

**Files:**
- Create: `src/gotoconnect/sip/__init__.py`, `src/gotoconnect/sip/messages.py`
- Test: `tests/sip/test_messages.py`

**Interfaces:**
- Produces (all in `messages.py`):
  - `@dataclass SipResponse`: `status: int`, `reason: str`, `headers: dict[str, str]` (case-insensitive get), `body: str`; `classmethod parse(raw: bytes) -> SipResponse`.
  - `@dataclass SipDialog` — generates/holds `call_id: str`, `from_tag: str`, `branch()` (new `z9hG4bK…` per transaction), `cseq: int`.
  - Builders returning `bytes`, each taking explicit kwargs (no hidden state): `build_register(username, domain, local_ip, local_port, dialog, expires=60, auth_header: str | None = None)`; `build_invite(username, domain, to_number, local_ip, local_port, media_port, dialog, auth_header=None)` — SDP body exactly per Global Constraints, `From: <sip:{username}@{domain}>;tag=…`; `build_ack(...)`, `build_bye(...)`, `build_cancel(...)` mirroring the demo scenarios' headers (use `/home/taylor/dev/goto_demo_scripts/sipp/scenarios.py` as the field-level reference).
  - `def digest_response(challenge: str, method: str, uri: str, username: str, password: str) -> str` — parses `WWW-Authenticate`/`Proxy-Authenticate` (MD5, with and without `qop=auth`), returns the full `Authorization:`/`Proxy-Authorization:` header value.

- [ ] **Step 1: Write failing tests** — parse a captured 407 response (lift a real one from the demo's log format in `CLAUDE.md`/scenarios); round-trip: built INVITE contains required headers, SDP lines, Content-Length correct; digest: RFC 2617 example vector (the RFC's `GET /dir/index.html` example) plus a `qop=auth` case computed independently.
- [ ] **Step 2: Run tests, verify fail**
- [ ] **Step 3: Implement** (hashlib only; no external SIP lib)
- [ ] **Step 4: Run tests, verify pass; commit** (`feat: SIP message building, parsing, digest auth`)

### Task 4: Transports (UDP + TLS)

**Files:**
- Create: `src/gotoconnect/sip/transport.py`
- Test: `tests/sip/test_transport.py`

**Interfaces:**
- Produces: `class SipTransport(Protocol)`: `async def connect(self) -> None`, `async def send(self, data: bytes) -> None`, `async def receive(self, timeout: float) -> bytes` (one SIP message per call), `async def close(self) -> None`, `local_addr: tuple[str, int]` property.
  - `class UdpTransport(SipTransport)`: `__init__(self, host: str, port: int = 5060)` — asyncio DatagramProtocol; one datagram = one message.
  - `class TlsTransport(SipTransport)`: `__init__(self, host: str, port: int = 5061, ssl_context: ssl.SSLContext | None = None)` — `asyncio.open_connection` with TLS; frames stream into messages by `Content-Length` (read headers to blank line, then body).
  - `def make_transport(host: str, mode: str, port: int | None = None) -> SipTransport` (`mode` ∈ `"udp" | "tls"`).

- [ ] **Step 1: Write failing tests** — UDP echo server: send/receive round-trip, receive timeout raises `asyncio.TimeoutError`; TLS: self-signed cert asyncio server, verify two back-to-back SIP messages in one stream are split correctly by Content-Length framing.
- [ ] **Step 2: Run, verify fail**
- [ ] **Step 3: Implement `transport.py`**
- [ ] **Step 4: Run, verify pass; commit** (`feat: UDP and TLS SIP transports`)

### Task 5: Audio pipeline (WAV → 8 kHz mono G.711)

**Files:**
- Create: `src/gotoconnect/sip/audio.py`
- Test: `tests/sip/test_audio.py`

**Interfaces:**
- Produces: `def wav_to_g711(wav_bytes: bytes, codec: str = "pcma") -> bytes` — accepts any PCM WAV (any rate/channels/width), returns raw a-law (`"pcma"`) or µ-law (`"pcmu"`) bytes at 8 kHz mono. Uses stdlib `wave` + `audioop` (via `audioop-lts` on 3.13+): width→16-bit (`lin2lin`), stereo→mono (`tomono`), resample (`ratecv`), encode (`lin2alaw`/`lin2ulaw`).

- [ ] **Step 1: Write failing tests** — generate WAVs in-test with `wave` (440 Hz tone): 44.1 kHz stereo 16-bit, 8 kHz mono 16-bit, 22.05 kHz mono 8-bit; assert output length ≈ duration × 8000 (±1%), pcma and pcmu differ, non-WAV bytes raise `ValueError`. *(Covers Review Focus #5.)*
- [ ] **Step 2: Run, verify fail**
- [ ] **Step 3: Implement `audio.py`**
- [ ] **Step 4: Run, verify pass; commit** (`feat: WAV to G.711 audio pipeline`)

### Task 6: RTP sender

**Files:**
- Create: `src/gotoconnect/sip/rtp.py`
- Test: `tests/sip/test_rtp.py`

**Interfaces:**
- Consumes: G.711 payload bytes (Task 5).
- Produces: `class RtpSender`: `__init__(self, local_port: int = 0)`; `local_port` property (bound port, for SDP `media_port`); `async def stream(self, payload: bytes, dest: tuple[str, int], payload_type: int = 8, stop: asyncio.Event | None = None) -> None` — sends 160-byte frames every 20 ms (RTP header: version 2, random SSRC/initial seq/timestamp, seq+1 and timestamp+160 per packet), returns when payload exhausted or `stop` is set; `async def close(self)`.

- [ ] **Step 1: Write failing tests** — UDP listener collects packets from a 1 s payload: ~50 packets, header fields correct (version bits, PT, monotonic seq, timestamp stride 160), total duration between 0.9–1.5 s (pacing is real but CI-tolerant); setting `stop` mid-stream halts within 100 ms.
- [ ] **Step 2: Run, verify fail**
- [ ] **Step 3: Implement `rtp.py`** (pack headers with `struct`; pace with a drift-free loop: target_time = start + n·0.02, sleep until target)
- [ ] **Step 4: Run, verify pass; commit** (`feat: paced RTP G.711 sender`)

### Task 7: Fake GoTo SIP server (test infra)

**Files:**
- Create: `tests/sip/fake_goto.py`
- Test: `tests/sip/test_fake_goto.py` (self-check)

**Interfaces:**
- Consumes: nothing from the lib (independent reimplementation — it must catch our bugs, not share them). May use the lib's `digest_response` test vectors, not its code.
- Produces: `class FakeGoToServer`: `__init__(self, username: str, password: str, behavior: str = "answer")` with `behavior` ∈ `"answer" | "busy" | "no_answer" | "hangup_during_audio" | "reject_auth"`; `async def start(self) -> tuple[str, int]` (UDP addr); attributes after a run: `registered: bool`, `invite_authenticated: bool`, `rtp_packets: list[bytes]`, `got_ack: bool`, `got_bye: bool`, `got_cancel: bool`; `async def stop(self)`. Protocol behavior: challenge REGISTER and INVITE each with 407 (verify digest with its own MD5 computation), then REGISTER→200; INVITE→100,180 then per `behavior`: 200+SDP (answer; opens an RTP sink), 486 (busy), silence until CANCEL→487 (no_answer), 200 then BYE after 10 RTP packets (hangup_during_audio), always-407 (reject_auth).

- [ ] **Step 1: Write self-check tests** — raw-socket client (test-local helper) registers with correct creds → `registered=True`; wrong digest → stays 407.
- [ ] **Step 2: Run, verify fail; Step 3: Implement; Step 4: Run, verify pass; commit** (`test: fake GoTo SIP server`)

### Task 8: Call state machine — `GoToVoice.call_and_play`

**Files:**
- Create: `src/gotoconnect/sip/call.py`, update `src/gotoconnect/__init__.py` exports (`GoToOAuth`, `GoToMessaging`, `GoToVoice`, `CallResult`, exceptions)
- Test: `tests/sip/test_call.py`

**Interfaces:**
- Consumes: Tasks 3–7 (`SipDialog`, builders, `digest_response`, `make_transport`, `wav_to_g711`, `RtpSender`, `FakeGoToServer`).
- Produces:
  - `@dataclass CallResult`: `answered: bool`, `duration: float`, `reason: str` (`"completed" | "remote-hangup" | "no-answer" | "busy" | "rejected"`).
  - `class GoToVoice`: `__init__(self, username: str, password: str, server: str = "sip.goto.com", proxy: str | None = None, transport: str = "udp", port: int | None = None)`; `async def call_and_play(self, number: str, wav_bytes: bytes, *, ring_timeout: float = 25.0, repeat: int = 1, codec: str = "pcma") -> CallResult`.
  - Flow per call (matches scenarios.py): connect transport (proxy or server) → REGISTER (handle 401/407, re-send with auth, expect 200) → INVITE (handle 407, auth re-INVITE) → await 180/183 then 200 within `ring_timeout` (timeout → CANCEL, await 487, ACK, return no-answer) → parse answer SDP for remote RTP addr/port → ACK → stream audio `repeat` times with 0.5 s gaps, listening for remote BYE (reply 200, return remote-hangup) → BYE → 200 → `CallResult`. Per-call REGISTER, no persistent registration. `# ponytail: per-call REGISTER; persistent registration if call setup latency ever matters`.

- [ ] **Step 1: Write failing tests** against `FakeGoToServer` (one per behavior):
```python
async def test_happy_path():       # answered, rtp_packets flowed, got_ack, got_bye, reason "completed"
async def test_busy():             # answered False, reason "busy"
async def test_no_answer():        # ring_timeout 1.0 -> got_cancel True, reason "no-answer"
async def test_remote_hangup():    # hangup_during_audio -> answered True, reason "remote-hangup", no exception
async def test_bad_password():     # reject_auth -> raises GoToAuthError (no infinite loop)
```
*(Covers Review Focus #1–#4.)*
- [ ] **Step 2: Run, verify fail; Step 3: Implement `call.py`; Step 4: Run full suite `pytest -v`, verify all pass; commit** (`feat: SIP call state machine with TTS audio playback`)

### Task 9: TLS end-to-end, docs, packaging, live smoke

**Files:**
- Modify: `tests/sip/fake_goto.py` (optional TLS listener), `README.md`
- Create: `CLAUDE.md` (Taylor's project template; Tests: pytest), `.github/workflows/publish.yml`, `examples/make_call.py`

**Interfaces:** none new.

- [ ] **Step 1: TLS e2e test** — `FakeGoToServer` gains TLS mode (self-signed cert generated in-test); `test_happy_path_tls()` runs Task 8's happy path with `transport="tls"`; verify pass.
- [ ] **Step 2: `examples/make_call.py`** — argparse script: env vars `GOTO_SIP_USERNAME`/`GOTO_SIP_PASSWORD`, args `--to`, `--wav`, optional `--server/--proxy/--transport`; prints `CallResult`. This is the live-smoke entry point.
- [ ] **Step 3: Docs + packaging** — README (install, SMS example, voice example, how to create the SIP device in GoTo admin — lift from goto_demo_scripts README); CLAUDE.md per template; `publish.yml`: on `v*` tag, build + publish to PyPI via trusted publishing.
- [ ] **Step 4: Full suite green on 3.12 and 3.13 locally; commit** (`docs: README, CLAUDE.md, examples; ci: PyPI publish workflow`)
- [ ] **Step 5: Create private GitHub repo `oneofthegeeks/gotoconnect`, push, verify CI green.**
- [ ] **Step 6: LIVE SMOKE (requires Taylor):** run `examples/make_call.py` with his real SIP creds against his phone; confirm audio heard, both UDP and TLS. Only after this: tag `v0.1.0` → PyPI.

---

## Self-review notes

- Spec coverage: OAuth/token layer ✓ (T1), SMS ✓ (T2), SIP facts ✓ (T3/T8 constraints), UDP+TLS from the start ✓ (T4/T9), PCMA primary + PCMU ✓ (T5/T6), no binaries ✓, lib-not-integration boundary ✓ (TokenProvider pluggable for HA). HA-side work (config flow, notify entities, migration, `call_tts` service, HACS/core submissions) is deliberately **Plan 2**, written after this library exists.
- Types cross-checked: `TokenProvider` consumed by T2; `digest_response`/builders consumed by T7(test-vectors only)/T8; `RtpSender.local_port` feeds `build_invite(media_port=…)`.
- Proportion: 9 tasks, each independently testable; bodies only where tests/signatures don't determine them.
