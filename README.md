# Santa Monica Rent Control Rubber Duck — v2 + Queue

Citation-first AI agent with a mandatory critic loop, now wrapped in a minimal
constituent-support queue so a team (not just one person) can use it.

Built for Ericka Lesley and the residents of Santa Monica.

**New here? Read [ELI5.md](ELI5.md)** — plain-English explanation, no jargon.

## What's here

- `ELI5.md` — what this is and why it matters, in plain English
- `SYSTEM_PROMPT.md` — the agent's full instructions (draft → critique → final answer)
- `index.html` — original one-page prompt-sharing tool (Jennifer, v2)
- `demo.html` — **the hackathon demo**: one question, in, through the critic loop, out — with a queue panel showing the team-support vision
- `duck.py` — the critic-loop logic as real, runnable code (not just a prompt), so the demo's one path is real, not simulated
- `PITCH.md` — the pitch: problem, approach, and what it changes for the office
- `QA-HARD.md` — the hardest questions judges will ask, answered honestly, including what is not built
- `TELEMETRY.md` — what is instrumented and why, including what has not been measured yet
- `FAIL_COPY.md` — the failure-message rationale and channel/language variants
- `city-skin.css` — optional civic look-and-feel overlay, not applied by default

## The one path that has to work

1. A resident's question comes in. (In the demo you pick one of the prepared questions — there is no free-text box.)
2. The agent drafts an answer.
3. The agent critiques its own draft against the official facts (catches invented numbers, missing conditions, overconfidence).
4. The final, cited answer is shown — with the critique visible, so you can see it catch itself.

Everything else (multiple staff, phone/email intake, auto-requeue, analytics) is
the real next-step architecture, shown here as a working queue skeleton — not
faked as done, shown honestly as scaffolding for after today.
