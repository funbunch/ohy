# Explain It Like I'm Five

## The problem

Rent control rules are complicated. Real people need real answers: *Can my
landlord raise my rent by that much? Am I even covered? Is this eviction
notice legal?*

If you ask a regular AI chatbot, it will answer confidently — and sometimes
it will just **make the numbers up**. It might tell you the increase cap is 8%
when it's actually 2.6%. It sounds just as sure either way.

For a rent control office, that's not a small mistake. Someone could overpay
for a year. Someone could not fight an eviction they had grounds to fight.

## What we built

A rubber duck that talks back — and then double-checks itself before speaking.

Three steps, every single time:

**1. It writes a draft answer.**
Just like any AI would.

**2. It checks its own draft against a list of official facts.**
Every number, every date, every percentage has to match a real source — a City
Charter section, a Board Regulation, a Board Resolution. If something in the
draft isn't on that list, it gets flagged.

**3. Only then does it show you the answer.**
And if step 2 found a problem it can't fix, it doesn't guess. It says "I don't
have a verified answer for this" and points you to the city's official page.

## The part that makes this different

Lots of AI tools *say* they double-check themselves. Usually that means someone
wrote "please review your answer carefully" in the instructions.

The catch: **an AI can make up the review, too.** It'll happily tell you "I
verified this, looks good" about an answer it invented. Asking a system to
grade its own homework doesn't work any better for AI than it does for people.

So we didn't do that. In this project the checking step is **actual code** that
compares the draft against a fixed table of official facts. It is not another
AI opinion. It can genuinely fail — and when it fails, nothing gets shown to
the resident.

You can watch it happen. Open `demo.html`, pick the question marked ⚠️, and
you'll see the system catch a fake number and refuse to answer.

## Try it in 30 seconds

- **`demo.html`** — open it in any browser. No install, no internet needed.
  Pick a question, click Ask, watch all four steps.
- **`index.html`** — copy the agent's instructions to paste into Claude,
  ChatGPT, or Grok and use it yourself right now.

## What's real today vs. what's next

**Real and working today:** the duck, the citation checking, the refusal to
guess.

**Sketched, not built:** the team side. A rent control office doesn't have one
person answering — it has a small team fielding phone calls, texts, and emails,
handing questions back and forth, making sure nothing sits unanswered. You'll
see that as a panel in the demo, clearly labeled as a mockup. It's the honest
next step, not something we're pretending is finished.

---

Built at Claude Impact Lab, Los Angeles — August 8, 2026
For Ericka Lesley and the residents of Santa Monica
