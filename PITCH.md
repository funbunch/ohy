# PITCH.md — 2-minute spoken script

Read this out loud, not as a document. Cut anything that doesn't sound
natural coming out of your mouth. Target: ~2 minutes at a normal speaking pace.

---

**[1. THE PAIN, IN ONE LINE]**

Nobody calls rent control happy. They're calling with an eviction notice they
don't understand, or a rent increase that feels illegal. Today, a real answer
takes three to five weeks — that's the office's own reported number, not
ours.

**[2. THE RISK NOBODY TALKS ABOUT]**

Point any generic AI chatbot at this and it will answer with total
confidence — and sometimes it just makes the number up. Tell someone the cap
is 8% when it's actually 2.6%, and that's not a UX bug. That's a year of a
tenant overpaying rent, or a landlord losing an eviction case they had
grounds to win.

**[3. WHAT WE DID DIFFERENTLY]**

Every AI tool claims it double-checks itself. Usually that's a prompt saying
"please review your answer." The catch: an AI can hallucinate the review just
as easily as the answer. So the checking step here isn't another AI opinion —
it's actual code that checks the draft against a fixed table of cited facts.
It can genuinely fail. And when it fails, nothing gets shown to the
constituent — it says "I don't have a verified answer" and points to the
official page.

**[4. THE DEMO MOMENT]**

*(Live demo cue: ask the trap question.)* Watch it try to answer, catch
itself against the fact table, and refuse rather than guess. That refusal is
the feature, not a bug.

**[5. THE OWNER STORY — SHOWS THIS ISN'T ONE-SIDED]**

Here's a real question from our conversation with the office: *"I saved my
whole life, bought a beautiful house near the beach. I'm barely there — I
visit in summer. I came back once and found people living inside for almost a
year. At this point I can't just remove them. What are my legal options in
Santa Monica?"* That's a property owner in crisis, not a tenant. The office
represents both sides — tenants and landlords — and has to stay neutral for
both. So for every fact, the system gives the same citation, read two ways:
what it means if you're the tenant, what it means if you're the owner. It
doesn't referee the disagreement. It illuminates it. And it replies on
whatever channel the person reached out on — phone, text, or email — in
their own language.

**[6. WHAT THIS MEANS FOR OVERSIGHT]**

Every ticket generates telemetry: channel, urgency, time to resolution,
whether it needed a human, which topics come up most. That last one matters —
Santa Monica's tenant protections are strong but not widely known, so
consultation volume tells the office exactly where public communication is
falling short. This is the evidence Ericka can bring to oversight and to the
city council — not a vague "it helps," but per-ticket data.

**[7. WHY THIS SCALES — THE DEPLOYABILITY ANGLE]**

Santa Monica isn't the only city with this exact problem. This is built as a
multi-tenant, cloud-native app on purpose — not something installed
one-office-at-a-time. Fix a bug once, every city gets the fix. No
per-customer customization to maintain. That's what makes this a platform,
not a one-off tool for one office.

**[CLOSE]**

Built for Ericka Lesley and the residents of Santa Monica. Every fact you
just saw came from an official source, cited and checked in real time — not
promised, shown.

---

## Notes for whoever presents

- **Zero invented numbers.** The 3–5 week baseline is quoted as *reported by
  the office* — say "reported," don't imply we measured it.
- Don't promise a specific percentage or multiplier of improvement. None has
  been measured yet.
- If asked about Airbnb / short-term rentals in Q&A: the official source
  doesn't address it, so the system escalates to a human rather than
  answering — say that directly if it comes up, don't guess an answer live.
- The owner story (section 5) is the strongest moment in the room — it flips
  the audience's assumption that this tool is only for tenants. Don't rush it.
