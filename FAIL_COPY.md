# FAIL_COPY.md — gentle fail copy for uncited questions

Live client feedback (5th audio, watching the demo): the trap-question block
worked correctly — it caught the invented 8% and refused to answer — but the
failure message felt like a dead end. **This is not one failure mode, it's
two** — the client named both causes without realizing they call for
different responses.

**The system still never answers without a citation, in either case.** Only
the words around that refusal — and whether we ask to reformulate versus
escalate — change.

## The two families, and how to tell them apart

**(a) Retrieval failure** — the topic genuinely *is* in the fact table, but
the question is phrased in a way that didn't match. This is a language
problem, not a coverage problem.
→ **Correct response: help them rephrase, and show which topics we CAN
answer.** This is solvable within the conversation itself — turning the
failure into orientation instead of a dead end.

**(b) Coverage limit** — the topic genuinely is not documented (Airbnb,
ADUs). No rephrasing fixes this — asking them to reformulate wastes their
time chasing something that doesn't exist in the source material.
→ **Correct response: escalate to a human directly.** Don't ask them to try
again first.

**How to distinguish, observably:** if the question's words have *any*
overlap with topics in the fact table (rent increase, eligibility, banked
increases, eviction, coverage, registration) → probably (a), retrieval.
Zero overlap, or it matches a known-excluded topic (Airbnb, ADU) → (b),
coverage limit.

Treating these the same makes the system look equally unhelpful in both
cases, and it hides from the office which of the two it actually needs to
fix: (a) is a UX/matching problem to iterate on; (b) is a documentation gap
that needs a human decision about the underlying rule.

## Hard rules for every variant below (unchanged from v1)

- **The word "unfortunately" is banned.** The client said this twice,
  explicitly.
- **Never assert a legal rule without a citation.** A gentler tone is not
  permission to guess.
- **Never offer a suggested-but-uncited answer**, even hedged with a
  disclaimer like "this is just a suggestion." The client floated this idea
  live and then talked themselves out of it correctly — a municipal office
  giving unsourced legal advice is exactly the exposure this system exists to
  prevent. (Their own proposed alternative — office-pre-approved paragraph
  modules — is documented as a future path at the bottom, not built today.)
- Tone: warm, patient, genuinely curious — like a person who wants to help,
  not a system reporting an error.

## (a) Retrieval failure — copy by channel

Ends by naming the topics we can help with, so the failure becomes a menu,
not a wall.

### Text / SMS

**EN:**
> Thanks for reaching out! I want to make sure I get you the right answer —
> can you tell me a bit more about what you're looking for? I can help with
> things like rent increases, eviction notices, eligibility, or unit
> coverage — which of those is closest to your question?

**ES:**
> ¡Gracias por escribirnos! Quiero asegurarme de darte la respuesta correcta
> — ¿podés contarme un poco más sobre lo que necesitás? Puedo ayudarte con
> temas como aumentos de alquiler, avisos de desalojo, elegibilidad, o
> cobertura de tu unidad — ¿cuál de esos se acerca más a tu consulta?

### Email

**EN:**
> Thank you for your question. I want to make sure I point you to the right
> information, and your question didn't quite match what I have on file —
> could you share a bit more detail? For reference, I can help with rent
> increases, eviction notices, eligibility for protections, banked-increase
> limits, or unit coverage. Let me know which of these is closest, or add
> more detail about your situation, and I'll get back to you.

**ES:**
> Gracias por tu consulta. Quiero asegurarme de orientarte con la
> información correcta, y tu pregunta no coincidió exactamente con lo que
> tengo disponible — ¿podrías darme un poco más de detalle? Como referencia,
> puedo ayudarte con aumentos de alquiler, avisos de desalojo, elegibilidad
> para protecciones, límites de aumentos acumulados, o cobertura de tu
> unidad. Contame cuál se acerca más, o agregá más detalle sobre tu
> situación, y te respondo.

### Phone (spoken script for staff / voice agent)

**EN:**
> I want to make sure I give you the right information here — can you help
> me understand a little more about what you're looking for? I can help
> with things like a rent increase, an eviction notice, eligibility, or
> coverage for your unit — does one of those sound like what you're asking
> about?

**ES:**
> Quiero asegurarme de darte la información correcta — ¿podés ayudarme a
> entender un poco más lo que necesitás? Puedo ayudarte con un aumento de
> alquiler, un aviso de desalojo, elegibilidad, o cobertura de tu unidad —
> ¿alguno de esos se parece a lo que estás preguntando?

## (b) Coverage limit — copy by channel

Does not ask them to try again. Goes straight to a warm handoff.

### Text / SMS

**EN:**
> Thanks for reaching out! This is a topic I don't have verified information
> on yet, so I want to make sure you get an accurate answer instead of a
> guess — I'm connecting you with a member of our team who can help
> directly.

**ES:**
> ¡Gracias por escribirnos! Este es un tema sobre el que todavía no tengo
> información verificada, así que quiero asegurarme de que recibas una
> respuesta precisa en vez de una suposición — te voy a conectar con
> alguien de nuestro equipo que puede ayudarte directamente.

### Email

**EN:**
> Thank you for your question. This touches on an area where we don't yet
> have verified guidance, and I'd rather connect you with someone who can
> give you an accurate answer than guess. A member of our team will follow
> up with you directly on this.

**ES:**
> Gracias por tu consulta. Esto toca un área sobre la que todavía no
> tenemos información verificada, y prefiero conectarte con alguien que
> pueda darte una respuesta precisa antes que arriesgarme a una suposición.
> Alguien de nuestro equipo te va a contactar directamente sobre esto.

### Phone (spoken script for staff / voice agent)

**EN:**
> That's a great question, and it's actually an area where the rules are
> still being worked out or aren't fully documented yet — rather than guess,
> I want to connect you with someone on our team who can look into the
> specifics for you.

**ES:**
> Es una muy buena pregunta, y en realidad es un área donde las reglas
> todavía se están definiendo o no están completamente documentadas —
> en vez de suponer, quiero conectarte con alguien de nuestro equipo que
> pueda revisar los detalles por vos.

## After a retrieval-failure follow-up: two outcomes

Only applies to family (a). Family (b) always escalates immediately — there
is no "try rephrasing first" step for a genuine coverage gap.

- **If the added context now matches a fact-table topic:** proceed normally
  — draft, critique, cited answer.
- **If it still doesn't match anything verified after one rephrase:**
  escalate to staff. Do not repeat the "tell me more" loop a second time —
  two rounds without a real answer starts to feel like stalling.

  **EN:** "This is a great question, and I want to make sure you get an
  accurate answer — let me connect you with a member of our team who can
  look into the specifics."

  **ES:** "Es una muy buena pregunta, y quiero asegurarme de que recibas una
  respuesta precisa — te voy a conectar con alguien de nuestro equipo que
  puede revisar los detalles."

## (c) Staff draft — for staff, never sent directly to the resident

Jose's resolution to the "uncited advice" tension: when no citation is
possible, instead of offering the resident nothing, the system can draft a
**`[DRAFT]`-marked response with explicit placeholders** — but it goes to
staff, never straight to the constituent.

**Why this distinction is the one that matters, not "cited vs. uncited":**
the real axis is **who stays accountable for the claim**. An office employee
saying something on the phone without citing a specific resolution number is
fine — they're a person with judgment, trainable, accountable. A machine
saying the same thing is accountable to no one, or worse, gets attributed to
the institution itself. A staff-reviewed draft keeps a human accountable in
the loop; an auto-sent uncited answer does not.

**Routing, using the channels we already have:**
- **Phone** → safe as-is. Staff already reads the response aloud, so human
  review already happens by design. The draft serves as their script.
- **Text / email** → the draft is **never auto-sent**. It goes to a staff
  queue marked "pending review." What *does* go to the constituent
  automatically is the (a)/(b) context request above — not the draft.

**The placeholders are the useful part** — they turn uncertainty into a
concrete checklist for the staff member, not a vague "needs review" flag.

**Still prohibited:** a draft asserting a legal rule as fact. Placeholders
mark what needs verifying; they don't fill the gap with a guess.

### Example 1 — unit registration status unclear (EN)

    [DRAFT — requires staff review before sending]
    Thanks for your question about your rent increase notice. Based on what
    you've described, this may depend on your unit's registration status
    with the Rent Control Board.
    [STAFF: verify unit registration status before confirming eligibility]
    [STAFF: confirm tenancy start date — affects which rules apply]

### Ejemplo 2 — fecha de tenencia sin confirmar (ES)

    [BORRADOR — requiere revision de staff antes de enviar]
    Gracias por tu consulta sobre el ajuste de alquiler. Segun lo que
    describis, esto puede depender de cuando comenzo tu tenencia en la
    unidad.
    [STAFF: confirmar fecha de inicio de tenencia -- determina que reglas aplican]
    [STAFF: verificar si la unidad tiene multas de salud/seguridad sin corregir]

### Example 3 — phone script for staff (EN, meant to sound spoken)

> "Okay, based on what you're telling me, here's a draft I'd want to double
> check before I confirm anything — [STAFF: verify MAR amount for this
> unit], [STAFF: confirm no outstanding registration fees]. Let me pull that
> up before I give you a final answer."

## Implementation note for w7

Distinguishing (a) from (b) needs a check at the point where the critic
fails: does the question's topic match anything in the fact table's topic
list (rent increase, eligibility, banked increases, eviction, coverage,
registration), even loosely, or does it hit zero overlap / a known-excluded
topic (Airbnb, ADU)? Airbnb/ADU already have their own escalation keywords
— route those straight to family (b). Anything else that fails the critic
without matching a keyword is family (a) by default.

Family (c) is a separate, optional capability (staff-facing draft with
placeholders) — not a replacement for (a)/(b). If time allows, wire it as an
internal-only output alongside the constituent-facing (a)/(b) message; if not,
it's documented here as a designed-but-not-built feature, same honesty
standard as the pre-approved-modules future path below.

## Future path (documented, not built today)

The client's own proposed alternative to an uncited AI answer: a library of
**office-pre-approved paragraph modules** for common edge cases that don't
map cleanly to a single fact-table entry. Staff (not the AI) would author and
approve these in advance. This solves the same problem the client was trying
to solve with a "suggested, uncited" AI answer, without the legal exposure —
but it requires office staff to write and maintain the modules, so it's a
real next-step feature, not something to fake for today's demo.
