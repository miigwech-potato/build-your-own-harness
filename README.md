# Build Your Own Harness

**How to build an AI agent harness from first principles.**

A *harness* is the control layer around a model: the loop, the tools, the state, the stops, and the place where **capability is not mistaken for authority**.

This repo is a learning path, not a product. Rebuild a thin harness yourself. Star counts measure attention; a working loop measures understanding.

Related:

- [hivemind](https://github.com/miigwech-potato/hivemind) — consensus notation, Gate, channel, boundaries
- [recreate-from-scratch](https://github.com/miigwech-potato/recreate-from-scratch) — broader from-scratch index

---

## What a harness is

```text
┌─────────────────────────────────────────┐
│                 HARNESS                 │
│  ┌─────────┐   ┌─────────┐   ┌───────┐ │
│  │  LOOP   │──►│  TOOLS  │──►│ STATE │ │
│  └─────────┘   └─────────┘   └───────┘ │
│        │              │           │     │
│        └──────────────┴───────────┘     │
│                     │                   │
│              ┌──────┴──────┐            │
│              │    GATE     │  authorize │
│              │  or HOLD 𝄐  │  before    │
│              └──────┬──────┘  side effect│
└─────────────────────┼───────────────────┘
                      ▼
                 WORLD / APIs
```

The model proposes. The harness **runs, bounds, records, and stops**.

---

## Learning path (minimal → real)

### Stage 0 — One shot (not a harness yet)

- Call a model once; print text.
- **Done when:** you see raw model output with no tools.

### Stage 1 — The loop

- `while not done: observe → propose → maybe act → observe`
- Cap iterations (`max_steps`).
- **Done when:** a goal can take 3+ steps without you pasting context by hand.

### Stage 2 — Tool boundary

- Allowlist of tools (functions with JSON schemas).
- Parse tool calls; reject unknown names.
- Return tool results as observations (not as silent side effects outside the log).
- **Done when:** the model can only touch what you registered.

### Stage 3 — State

- Transcript / messages list.
- Optional scratchpad separate from user-visible reply.
- Persist run under a `run_id` (file or SQLite is enough).
- **Done when:** you can resume or audit one run after process restart (even roughly).

### Stage 4 — Gate (the important stage)

Before any tool that has **external consequence** (send, buy, delete, write production, post):

1. Canonicalize the action payload.
2. Hash it.
3. Require an explicit approval record bound to that hash — or **HOLD ( آم)**.
4. Log what was seen.

```text
capability ≠ authority
no recorded AUTHORIZED → do not act
```

**Done when:** removing the Gate makes dangerous tools callable, and with the Gate they are not.

### Stage 5 — Multi-role (optional swarm)

- Scout: propose only (cloud / options).
- Worker: refine, weigh.
- Gate: measure + authorize or hold.
- Act: runs only on verified authorization.

See [hivemind](https://github.com/miigwech-potato/hivemind) for notation (`POTENTIAL`, `DECISION`, channel envelopes).

### Stage 6 — Hardening

- Timeouts, budgets (tokens, dollars, wall clock).
- Redaction of secrets in logs.
- Idempotency keys for tools that retry.
- Clear `stop` reasons: success, max_steps, hold, error.

---

## Reference skeleton

See [`harness.py`](harness.py) for a **tiny, dependency-free** skeleton:

- in-process allowlisted tools
- step limit
- gate for `external` tools
- transcript log

It uses a fake model so you can learn the shape without API keys. Replace `propose()` with a real model call when ready.

```bash
python harness.py
```

---

## Design rules (short)

1. **Allowlist tools** — never “run whatever the model named.”
2. **Log the transcript** — proposals and observations.
3. **Gate side effects** — hash-bound approval or hold.
4. **Bound the loop** — max steps, max cost, wall timeout.
5. **Stop is valid** — HOLD is a successful safety outcome.
6. **Don’t invent crypto** — use standard libraries if you sign approvals.

---

## Common failure modes

| Failure | Fix |
|---------|-----|
| Tool use without allowlist | Registry + reject unknown |
| Infinite loop | `max_steps` + idle detection |
| Approval by vibes | Hash-bound token |
| Act on stale approval | Bind hash to exact payload |
| Logs full of secrets | Redact; separate secret store |
| “The model said yes” as authority | Gate owned by harness, not model |

---

## Map to hivemind

| Harness piece | Hivemind |
|---------------|----------|
| Propose only | Scout / POTENTIAL |
| Refine | Worker |
| Approve / hold | Gate / DECISION |
| Execute | Act |
| Message bus | `channel.py` envelopes |
| Hard limits | `flow/BOUNDARIES.flow` |

---

## Contributing

- PRs: clearer stages, better skeletons, real-world postmortems (`I built a harness and …`).
- No guides aimed at unauthorized access or harm.
- Prefer small, readable code over framework lookalikes.

---

## Licence

CC0 for the explanatory text in this repo unless noted.  
Code in `harness.py` is CC0 as well — use it, break it, rebuild it.

---

米 only on a recorded AUTHORIZED.  
Everything else: 𝄐
