# QA-HARD.md — the hardest questions the judges will ask

Honest answers, not comfortable ones. If the honest answer is "we don't know
yet," that's what's written here — a judge punishes an inflated answer harder
than an honest gap.

---

**Q1. How does the fact table get updated when the Board changes a rule?**

Today, manually. That's a deliberate choice, not a shortcut we ran out of
time for: an automatic update with no human review is exactly the risk this
system exists to prevent. A wrong number entering the fact table
automatically would be just as dangerous as an AI inventing one — the
citation-check only protects against drift *from* the table, not errors *in*
the table. Someone with authority over the actual rule has to be the one who
changes it.

**Q2. What happens if someone asks something the fact table doesn't cover?**

It escalates to a human instead of guessing. We show this live with two real
cases: Airbnb/short-term rentals and ADUs (accessory dwelling units) — both
are things the client explicitly told us are common questions, and both are
areas where the official source is silent or the rules are conditional and
complex. Rather than approximate an answer, the system flags it and hands it
to staff.

**Q3. Isn't this just a chatbot with extra steps?**

No — the distinction is where the checking happens. A prompt that says
"please review your answer" is still an AI opinion about an AI's own draft,
and an AI can hallucinate the review as easily as the answer. Here the
critique step is actual code that compares the draft against a fixed table
of cited facts — it isn't asking a model to grade its own homework. We show
this live: ask the trap question, and the system catches itself and refuses
to answer rather than guess.

**Q4. How much faster is this, really?**

We don't have that number measured yet, and we're not going to pretend we
do. What we have: the office's own reported baseline (3–5 weeks), and the
telemetry instrumentation to measure `time_to_resolution` per ticket once
this runs on real cases. The honest state today is "we built the ruler, we
haven't measured anything with it yet."

**Q5. How do you avoid bias toward tenants or landlords?**

Every fact gets the same citation read two ways: what it means if you're the
tenant, what it means if you're the landlord. The system doesn't referee
disagreements between the two — it illuminates what the rule says for each
side and stops there. The clearest proof of this in the demo is the landlord
case: someone who saved their whole life for one property, came back to find
unauthorized long-term occupants, and needs to understand their legal
options. That's not a "tenant tool with a landlord feature bolted on" — the
same fact-citation mechanism serves both, symmetrically.

**Q6. Who is responsible if the system gives a wrong answer?**

This is a legitimate governance question and it deserves a real answer, not
a dodge. The system is designed to minimize this risk — it escalates rather
than guesses, and every claim is cited against an official source — but "the
code checks itself" is not the same as "nothing can go wrong." Any
constituent-facing deployment needs a human owner at the office who is
accountable for the fact table's accuracy and for reviewing escalated cases.
We built the tool to make that person's job auditable — every response is
traceable to a cited fact — but the tool does not remove the need for that
person.

**Q7. Does this work in another city?**

The architecture does — it's built multi-tenant and cloud-native on purpose,
so a fix or an improvement ships to every deployed city at once instead of
being applied one installation at a time. But the *rules* are local: the
fact table is what changes per city, not the underlying engine (draft →
critique → cited answer). Santa Monica's rent control ordinance is not
Los Angeles's or Oakland's. Porting this to another city means someone builds
and verifies that city's own fact table — the same manual, deliberate process
described in Q1 — not a one-click deploy of Santa Monica's rules onto a
different jurisdiction.

**Q8. This is a hackathon prototype — what's actually production-ready versus
demo-ware?**

Real and working today: the draft → critique → cited-answer loop as runnable
code, the fact table for Santa Monica's 2026 rules, the escalation logic
(Airbnb, ADU), bilingual response templates (en/es). Sketched, not built: the
multi-channel intake (phone/text/email) is designed for but not wired to real
telephony/SMS/email systems; the supervisor dashboard and case-drill-down are
shown as a labeled mockup with mock data, not live case data; the observer
agent that auto-writes case-study narratives is a stated idea from the
client, not implemented. We labeled every mockup as a mockup in the demo
itself — nothing here is presented as more finished than it is.

**Q9. Why should a government office trust an AI system with legal
information at all, given how often AI gets facts wrong?**

That skepticism is the correct starting point, and it's the reason this
system doesn't rely on the AI to know the law — it relies on code that checks
the AI's draft against a table a human populated and can audit. The AI's job
is drafting language and picking which facts are relevant; it is explicitly
not trusted to know what's true. If that split sounds like it removes some of
the "magic" of a chatbot, that's correct — the magic was never the trustworthy
part.

**Q10. What's the actual cost or effort to deploy this for a real office?**

We don't have a cost estimate today, and giving one on stage would be
guessing. What we can say concretely: the fact table for Santa Monica took
building and verifying roughly a dozen specific facts from a handful of
official sources (City Charter, Board Resolutions, Board actions) — that's
the recurring cost per city, not a one-time engineering cost. The engine
itself doesn't change per deployment.

---

## Notes for whoever fields Q&A

- If a question isn't on this list and you don't know the honest answer live,
  say "we haven't verified that, we'd want to check before answering" — that
  is the same discipline the system itself demonstrates. Practicing that
  sentence out loud once removes the temptation to improvise legal or
  technical claims under pressure.
- Q4 and Q10 are the two most likely to tempt an inflated answer. Rehearse
  saying "we don't have that number" without hedging it into sounding like a
  weakness.
