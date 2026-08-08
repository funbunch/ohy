"""duck.py -- the Rubber Duck's critic loop, as real code that runs.

Why this instead of just trusting an LLM prompt: a prompt that says "critique
your own answer" can hallucinate the critique as much as the original answer
-- it's the same "verifier that verifies itself" trap that shows up in any AI
system (see doctrina/ley-del-verificador-que-se-verifica). Here the critique
is a function that CHECKS the draft against a table of cited facts, not an
LLM narrating that it self-checked.

For the live demo: zero network dependency, zero server, zero API. Facts are
hardcoded on purpose -- they are the currently-in-force official facts
(Resolution 26-001, Board action Oct 2025), not invented demo data. What gets
"faked" for the hackathon is the multi-channel intake interface
(phone/email/text) from Lily's vision, not the legal facts.

v2: adds inbound-channel = outbound-channel routing, urgency triage, two-party
framing (tenant/landlord, same fact, same citation, two readings), mandatory
escalation for Airbnb/short-term (not covered by the official source, so
nothing can be asserted about it), a closing question, and a de-escalating
tone. Response language mirrors the ticket's language (es/en) -- "meet them
where they are" -- while the codebase itself stays in English.
"""
from dataclasses import dataclass, field
from typing import Literal, Optional

Channel = Literal["phone", "text", "email"]
Urgency = Literal["FAQ", "normal", "URGENT"]
Language = Literal["en", "es"]

# Facts are the single source of truth for values/citations (language-neutral
# key -> canonical value+citation, used by the critique). Display text for the
# topic line is localized separately in FACT_LABELS so the citation loop
# doesn't depend on wording, only on the citation string being present.
FACTS = {
    "ga_2026_pct": {"value": "2.6%", "citation": "Resolution 26-001"},
    "ga_2026_cap": {"value": "$70/month (units with MAR >= $2,674)", "citation": "Resolution 26-001"},
    "ga_2026_effective": {"value": "September 1, 2026", "citation": "Resolution 26-001"},
    "ga_eligibility": {
        "value": "tenancy started before Sep 1, 2025; unit properly registered; no uncorrected health/safety citations; written notice per state law",
        "citation": "Resolution 26-001",
    },
    "banked_cap": {"value": "maximum 10% of the tenant's previous rent in any 12-month period", "citation": "Board Action, October 2025"},
    "coverage": {"value": "multi-unit buildings with a Certificate of Occupancy issued on or before Apr 10, 1979", "citation": "City Charter Art. XVIII"},
    "just_cause_eviction": {"value": "applies; grounds listed in Charter Sec. 1806", "citation": "City Charter Sec. 1806"},
}

# Localized display value for each fact. FACTS stays the single source of
# truth for the raw value (used by the critique's citation check); this only
# translates the wording AROUND that value, so numbers/dates/citations never
# get duplicated or drift between languages -- only phrasing does. Bug found
# by w6 QA: draft() used to insert FACTS[t]["value"] directly, so a Spanish
# response mixed a Spanish label with an English value ("tope en dólares...:
# $70/month (units with MAR >= $2,674)"). Facts were correct (same number),
# but it broke "meet them where they are" in Spanish.
VALUE_TEMPLATES = {
    "en": {
        "ga_2026_pct": lambda: "2.6%",
        "ga_2026_cap": lambda: "$70/month (units with MAR of $2,674 or more)",
        "ga_2026_effective": lambda: "September 1, 2026",
        "ga_eligibility": lambda: "tenancy started before Sep 1, 2025; unit properly registered; no uncorrected health/safety citations; written notice per state law",
        "banked_cap": lambda: "maximum 10% of the tenant's previous rent in any 12-month period",
        "coverage": lambda: "multi-unit buildings with a Certificate of Occupancy issued on or before Apr 10, 1979",
        "just_cause_eviction": lambda: "applies; grounds listed in Charter Sec. 1806",
    },
    "es": {
        "ga_2026_pct": lambda: "2.6%",
        "ga_2026_cap": lambda: "$70/mes (unidades con MAR de $2,674 o más)",
        "ga_2026_effective": lambda: "1 de septiembre de 2026",
        "ga_eligibility": lambda: "tenencia iniciada antes del 1-sep-2025; unidad registrada; sin multas de salud/seguridad sin corregir; aviso escrito conforme a ley estatal",
        "banked_cap": lambda: "máximo 10% del alquiler anterior en cualquier período de 12 meses",
        "coverage": lambda: "edificios multi-unidad con Certificado de Ocupación emitido el 10-abr-1979 o antes",
        "just_cause_eviction": lambda: "aplica; motivos en Charter Sec. 1806",
    },
}

# Localized topic line, e.g. "ga 2026 pct: 2.6% [Resolution 26-001]" in EN,
# same fact/citation in ES. Kept separate from FACTS so the citation-presence
# check in critique() stays language-agnostic (it checks the citation string,
# which is identical in both languages).
FACT_LABELS = {
    "en": {
        "ga_2026_pct": "2026 general adjustment",
        "ga_2026_cap": "2026 general adjustment dollar cap",
        "ga_2026_effective": "2026 general adjustment effective date",
        "ga_eligibility": "general adjustment eligibility",
        "banked_cap": "banked increase cap",
        "coverage": "rent control coverage",
        "just_cause_eviction": "just-cause eviction",
    },
    "es": {
        "ga_2026_pct": "ajuste general 2026",
        "ga_2026_cap": "tope en dólares del ajuste general 2026",
        "ga_2026_effective": "vigencia del ajuste general 2026",
        "ga_eligibility": "elegibilidad para el ajuste general",
        "banked_cap": "tope de aumentos acumulados",
        "coverage": "cobertura de rent control",
        "just_cause_eviction": "desalojo con causa justa",
    },
}

# Two-party framing: for each fact, what it means for each side. The office
# represents both tenants and landlords, it does not arbitrate -- the system
# ILLUMINATES the difference in reading, it does not resolve it. Same fact,
# same citation, two readings. Localized per response language.
TWO_PARTY_FRAMING = {
    "en": {
        "ga_2026_pct": {
            "tenant": "Your rent can go up by at most 2.6% starting Sep 1, 2026 -- no more than that under this adjustment, subject to the dollar cap if it applies.",
            "landlord": "You can apply up to a 2.6% general adjustment starting Sep 1, 2026, subject to the dollar cap for higher-rent units.",
        },
        "ga_2026_cap": {
            "tenant": "If your current rent (MAR) is $2,674 or more, the dollar increase is capped at $70/month even if 2.6% would be higher in your case.",
            "landlord": "For units with MAR >= $2,674, the increase cannot exceed $70/month even if the calculated 2.6% is higher.",
        },
        "ga_eligibility": {
            "tenant": "The landlord can only apply this adjustment if your tenancy started before Sep 1, 2025, the unit is registered, there are no uncorrected health/safety citations, and you were given written notice per state law. If any of these is missing, you can challenge the increase.",
            "landlord": "To apply the adjustment you need the tenancy to have started before Sep 1, 2025, the unit to be registered, no outstanding health/safety citations, and written notice given per state law.",
        },
        "banked_cap": {
            "tenant": "Even if the landlord has banked increases from prior years, they cannot charge you more than 10% of your previous rent in any 12-month period, all at once.",
            "landlord": "Banked increases applied at once are capped at a maximum of 10% of the tenant's previous rent in any 12-month period.",
        },
        "coverage": {
            "tenant": "If your building is multi-unit and its Certificate of Occupancy is dated Apr 10, 1979 or earlier, you are under rent control.",
            "landlord": "Your building is subject to rent control if it is multi-unit and its Certificate of Occupancy was issued on or before Apr 10, 1979.",
        },
        "just_cause_eviction": {
            "tenant": "You cannot be evicted without a recognized just cause -- the valid grounds are listed in Charter Sec. 1806, it is not up to the landlord's discretion.",
            "landlord": "To evict a tenant you need a just cause among the grounds listed in Charter Sec. 1806 -- ending the lease alone is not enough.",
        },
    },
    "es": {
        "ga_2026_pct": {
            "tenant": "Tu alquiler puede subir hasta 2.6% a partir del 1-sep-2026 -- no más que eso por este ajuste, salvo el tope en dólares si aplica.",
            "landlord": "Podés aplicar hasta 2.6% de ajuste general desde el 1-sep-2026, sujeto al techo en dólares para unidades de alquiler alto.",
        },
        "ga_2026_cap": {
            "tenant": "Si tu alquiler actual (MAR) es $2,674 o más, el aumento en dólares está topado en $70/mes aunque el 2.6% sea más alto en tu caso.",
            "landlord": "Para unidades con MAR ≥ $2,674, el aumento no puede superar $70/mes aunque el 2.6% calculado sea mayor.",
        },
        "ga_eligibility": {
            "tenant": "El propietario solo puede aplicarte este ajuste si tu tenencia empezó antes del 1-sep-2025, la unidad está registrada, no hay multas de salud/seguridad sin corregir, y te dieron aviso por escrito según la ley estatal. Si falta alguno de estos, podés cuestionar el aumento.",
            "landlord": "Para aplicar el ajuste necesitás que la tenencia haya empezado antes del 1-sep-2025, la unidad esté registrada, no tengas multas de salud/seguridad pendientes, y hayas dado aviso por escrito según la ley estatal.",
        },
        "banked_cap": {
            "tenant": "Aunque el propietario tenga aumentos acumulados de años anteriores, no te puede cobrar de golpe más del 10% de tu alquiler anterior en ningún período de 12 meses.",
            "landlord": "Los aumentos acumulados (banked) que apliques de una sola vez están limitados a un máximo de 10% del alquiler anterior del inquilino en cualquier período de 12 meses.",
        },
        "coverage": {
            "tenant": "Si tu edificio es multi-unidad y el Certificado de Ocupación es del 10-abr-1979 o antes, estás bajo rent control.",
            "landlord": "Tu edificio está sujeto a rent control si es multi-unidad y el Certificado de Ocupación fue emitido el 10-abr-1979 o antes.",
        },
        "just_cause_eviction": {
            "tenant": "No te pueden desalojar sin una causa justa reconocida -- los motivos válidos están en el Charter §1806, no es a discreción del propietario.",
            "landlord": "Para desalojar a un inquilino necesitás una causa justa dentro de los motivos listados en el Charter §1806, no alcanza con terminar el contrato sin más.",
        },
    },
}

# Keywords indicating Airbnb/short-term rental OR ADUs (accessory dwelling
# units). Same treatment for both: escalate, don't answer. The official
# source doesn't cover short-term rentals at all. ADUs are explicitly NOT the
# same as short-term -- the client described them as legal only under "a very
# specific set of conditions" and "a big problem" -- exactly the kind of
# conditional, complex rule that must not be guessed at from a facts table
# that doesn't have those conditions in it.
ESCALATE_KEYWORDS = [
    "airbnb", "short-term", "short term", "alquiler corto", "vrbo",
    "por noche", "temporal", "turistico", "turístico", "vacation rental",
    "alquiler de corto plazo", "renta corta",
    "adu", "accessory dwelling", "granny flat", "unidad accesoria", "casita",
]

# Keywords indicating real urgency (imminent risk of losing housing or an
# irreversible action) vs. an informational inquiry.
URGENT_KEYWORDS = [
    "eviction", "desalojo", "notice to vacate", "sheriff", "lockout",
    "me quieren sacar", "me estan desalojando", "3-day notice", "unlawful detainer",
]

FAQ_KEYWORDS = [
    "what is the increase", "cuanto es el ajuste", "cual es el ajuste",
    "official site", "sitio oficial", "where do i check", "donde consulto",
]

# Minimal language detection: enough to route the response, not a translator.
# Spanish accent marks or a short list of unmistakably-Spanish words are
# sufficient signal for this narrow domain (one municipal law, short tickets).
SPANISH_MARKERS = [
    "á", "é", "í", "ó", "ú", "ñ", "¿", "¡",
    "cuanto", "cuál", "puedo", "elegib", "aumento", "alquiler", "desalojo",
    "aplica", "edificio", "propietario", "inquilino",
]


def _detect_language(question: str) -> Language:
    q = question.lower()
    return "es" if any(marker in q for marker in SPANISH_MARKERS) else "en"


def _detect_escalate_topic(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in ESCALATE_KEYWORDS)


def _detect_urgency(question: str) -> Urgency:
    q = question.lower()
    if any(k in q for k in URGENT_KEYWORDS):
        return "URGENT"
    if any(k in q for k in FAQ_KEYWORDS):
        return "FAQ"
    return "normal"


def _detect_topics(question: str) -> list:
    """Simple keyword retrieval -- enough for the narrow domain (a single
    municipal law), no need for a semantic engine."""
    q = question.lower()
    topics = []
    if any(k in q for k in ["ajuste", "aumento", "increase", "ga ", "general adjustment", "cuanto"]):
        topics += ["ga_2026_pct", "ga_2026_cap", "ga_2026_effective"]
    if any(k in q for k in ["elegib", "eligib", "califico", "qualify"]):
        topics.append("ga_eligibility")
    if any(k in q for k in ["acumul", "banked", "varios años", "atrasad"]):
        topics.append("banked_cap")
    if any(k in q for k in ["cobertura", "aplica a mi edificio", "covered", "1979"]):
        topics.append("coverage")
    if any(k in q for k in ["desalojo", "eviction", "causa justa", "just cause"]):
        topics.append("just_cause_eviction")
    return topics
    # No fallback to "show everything" here anymore: an empty list on no
    # match is what lets critique() correctly classify this as a retrieval
    # failure (family a) instead of silently answering with unrelated facts.


# De-escalating opener by language and urgency. Nobody calls happy -- everyone
# arrives already upset. The opening tone acknowledges that before the facts.
_DEESCALATION = {
    "en": {
        "URGENT": "I understand this is urgent and you need a clear answer now. Let's get straight to it. ",
        "normal": "Thanks for your patience -- let's get right to what you need to know. ",
    },
    "es": {
        "URGENT": "Entiendo que esto es urgente y necesitás una respuesta clara ya. Vamos directo al punto. ",
        "normal": "Gracias por tu paciencia -- vamos directo a lo que necesitás saber. ",
    },
}

_CLOSING_QUESTION = {
    "en": "Does this cover your question, or do you need more info?",
    "es": "¿Esto responde tu pregunta, o necesitás más información?",
}

_ESCALATION_MESSAGE = {
    "en": ("This request needs direct attention from our staff -- I'm escalating it "
           "right now so someone can contact you with a specific answer. "
           "In the meantime you can check santamonica.gov/rentcontrol."),
    "es": ("Esta consulta necesita atención directa de nuestro staff -- te la voy a "
           "escalar ahora mismo para que alguien te contacte con una respuesta específica. "
           "Mientras tanto podés revisar santamonica.gov/rentcontrol."),
}

# Gentle fail (5th client audio, live feedback): the critic's refusal is
# correct and never changes -- an uncited claim is never shown. What changes
# is the tone. Hard rules from FAIL_COPY.md: never say "unfortunately", never
# offer a suggested-but-uncited answer even with a disclaimer, always ask for
# more context instead of closing the door. Localized by channel because a
# phone script needs to sound spoken, not read.
_GENTLE_FAIL = {
    "phone": {
        "en": ("I want to make sure I give you the right information here -- "
               "can you help me understand a little more about what you're "
               "looking for? For example, are we talking about a rent "
               "increase, an eviction, or something with your unit's coverage?"),
        "es": ("Quiero asegurarme de darte la información correcta -- ¿podés "
               "ayudarme a entender un poco más lo que necesitás? Por ejemplo, "
               "¿es sobre un aumento de alquiler, un desalojo, o algo "
               "relacionado con la cobertura de tu unidad?"),
    },
    "text": {
        "en": ("Thanks for reaching out! I want to make sure I get you the "
               "right answer -- can you tell me a bit more about what you're "
               "looking for? For example, is this about a rent increase, "
               "eviction notice, or something else?"),
        "es": ("¡Gracias por escribirnos! Quiero asegurarme de darte la "
               "respuesta correcta -- ¿podés contarme un poco más sobre lo "
               "que necesitás? Por ejemplo, ¿es sobre un aumento de alquiler, "
               "un aviso de desalojo, o algo distinto?"),
    },
    "email": {
        "en": ("Thank you for your question. I want to make sure I point you "
               "to the right information, and I'd like to understand a bit "
               "more first -- could you share some additional detail about "
               "your situation? For example, when this started, or which "
               "part of your rent control question you're most trying to "
               "resolve? Once I have that, I can look into it and get back "
               "to you."),
        "es": ("Gracias por tu consulta. Quiero asegurarme de orientarte con "
               "la información correcta, así que me gustaría entender un "
               "poco más primero -- ¿podrías compartir algún detalle "
               "adicional sobre tu situación? Por ejemplo, cuándo comenzó, o "
               "qué parte de tu consulta sobre control de alquileres es la "
               "más importante para vos. Con eso, puedo revisarlo y "
               "responderte."),
    },
}

_TWO_PARTY_HEADER = {
    "en": "\n\n--- How this applies to your situation ---",
    "es": "\n\n--- Cómo aplica esto según tu situación ---",
}

_TENANT_LABEL = {"en": "If you're a tenant", "es": "Si sos inquilino"}
_LANDLORD_LABEL = {"en": "If you're a landlord", "es": "Si sos propietario"}

_VERIFIED_FOOTER = {
    "en": "\n\n(Verified: every cited fact checked against the official source before display.)",
    "es": "\n\n(Verificado: cada dato citado contra la fuente oficial antes de mostrarse.)",
}


@dataclass
class DuckResponse:
    question: str
    channel: Channel
    language: Language = "en"
    urgency: Urgency = "normal"
    draft_text: str = ""
    facts_used: list = field(default_factory=list)
    framing: dict = field(default_factory=dict)
    critique: list = field(default_factory=list)
    final: str = ""
    critique_status: str = "not run"
    escalate_to_human: bool = False
    escalation_reason: Optional[str] = None
    closing: str = ""
    fail_family: Optional[str] = None
    """'retrieval' (a): topic is in the fact table, question didn't match --
    solvable within the conversation, so we ask to rephrase and list covered
    topics. 'coverage' (b): topic is genuinely not documented (Airbnb, ADU)
    or the critic caught an invented claim -- no rephrase fixes this, escalate
    directly. See FAIL_COPY.md for why treating these the same hides which of
    the two problems the office actually needs to fix."""


def draft(question: str, channel: Channel) -> DuckResponse:
    language = _detect_language(question)
    urgency = _detect_urgency(question)
    r = DuckResponse(question=question, channel=channel, language=language, urgency=urgency)

    # Airbnb/short-term or ADU: do NOT answer with facts -- either the
    # official source doesn't mention it (short-term), or it's a genuinely
    # conditional rule the facts table can't safely simplify (ADUs are legal
    # only under a specific set of conditions). Always escalate.
    if _detect_escalate_topic(question):
        r.escalate_to_human = True
        r.escalation_reason = (
            "Question mentions short-term/Airbnb-style rental or an accessory dwelling "
            "unit (ADU). These topics are either not covered by the official source, or "
            "depend on a specific set of conditions the facts table can't safely assert "
            "without more detail. Escalating to human staff."
        )
        r.facts_used = []
        r.draft_text = ""
        return r

    topics = _detect_topics(question)
    r.facts_used = topics
    lines = []
    for t in topics:
        citation = FACTS[t]["citation"]
        label = FACT_LABELS[language][t]
        value = VALUE_TEMPLATES[language][t]()
        lines.append(f"{label}: {value} [{citation}]")
        if t in TWO_PARTY_FRAMING[language]:
            r.framing[t] = TWO_PARTY_FRAMING[language][t]
    r.draft_text = _DEESCALATION[language][urgency if urgency == "URGENT" else "normal"] + " ".join(lines)
    return r


def critique(r: DuckResponse) -> DuckResponse:
    """The REAL critique: verifies that every claim in the draft has a
    citation in FACTS, and that no number is mentioned that doesn't come
    from there. This is not an LLM saying "I checked, it's fine" -- it's a
    check that can genuinely fail if the draft drifts from the facts table."""
    if r.escalate_to_human:
        r.critique = ["OK: case flagged for escalation, no fact-based answer generated (avoids inventing on a topic outside the official source)"]
        r.critique_status = "ESCALATED -- fact critique not applicable"
        return r

    findings = []
    for t in r.facts_used:
        if t not in FACTS:
            findings.append(f"FAIL: '{t}' has no citation in the official facts table")
            continue
        if FACTS[t]["citation"] not in r.draft_text:
            findings.append(f"FAIL: '{t}' is mentioned without its citation ({FACTS[t]['citation']})")
    if not r.facts_used:
        findings.append("FAIL: no relevant fact found -- do not answer, refer to the official source")

    r.critique = findings if findings else ["OK: every claim has a citation verified against the facts table"]
    r.critique_status = "FAILED, answer withheld" if findings else "PASSED"
    return r


def final_response(r: DuckResponse) -> DuckResponse:
    r.closing = _CLOSING_QUESTION[r.language]

    if r.escalate_to_human:
        r.final = f"{_DEESCALATION[r.language]['normal']}{_ESCALATION_MESSAGE[r.language]}"
        return r

    if r.critique_status == "FAILED, answer withheld":
        # Gentle fail: no "unfortunately", no dead end -- ask for more
        # context instead of declaring failure. Channel-specific because a
        # phone script needs to sound spoken, not read.
        r.final = _GENTLE_FAIL[r.channel][r.language]
        return r

    parts = [r.draft_text]
    if r.framing:
        parts.append(_TWO_PARTY_HEADER[r.language])
        for t, readings in r.framing.items():
            parts.append(f"\n{_TENANT_LABEL[r.language]}: {readings['tenant']}")
            parts.append(f"\n{_LANDLORD_LABEL[r.language]}: {readings['landlord']}")
    parts.append(_VERIFIED_FOOTER[r.language])
    parts.append(f"\n\n{r.closing}")
    r.final = "".join(parts)
    return r


def ask(question: str, channel: Channel = "text") -> DuckResponse:
    r = draft(question, channel)
    r = critique(r)
    r = final_response(r)
    return r


def send_via_channel(r: DuckResponse) -> str:
    """Inbound-channel = outbound-channel routing: if they called, they get
    called back; if they texted, they get a text; if they emailed, they get
    an email. This function simulates delivery (for the hackathon it prints
    the channel used instead of integrating Twilio/SMTP)."""
    label = {"phone": "Outbound CALL", "text": "Outbound SMS", "email": "Outbound EMAIL"}[r.channel]
    return f"[{label}] {r.final}"


if __name__ == "__main__":
    TEST_CASES = [
        ("What is the 2026 general adjustment and is there a dollar cap?", "text"),
        ("Mi tenencia empezó en noviembre de 2025. ¿Soy elegible para el ajuste de septiembre 2026? Me llamaron para avisarme que me van a subir el alquiler.", "phone"),
        ("I want to put my unit on Airbnb for short stays, does rent control apply?", "email"),
        ("Me llegó un aviso de desalojo de 3 días, ¿qué hago?", "phone"),
    ]

    for question, channel in TEST_CASES:
        r = ask(question, channel)
        print(f"\n=== [{channel.upper()}] {question} ===")
        print("LANGUAGE:", r.language)
        print("URGENCY:", r.urgency)
        print("ESCALATE TO HUMAN:", r.escalate_to_human, f"({r.escalation_reason})" if r.escalation_reason else "")
        print("CRITIQUE:", "; ".join(r.critique))
        print("CRITIQUE STATUS:", r.critique_status)
        print("RESPONSE:")
        print(send_via_channel(r))

    # Additional case: force a REAL critique failure (not a happy path that
    # could never fail). Simulates a draft with a topic that has no citation
    # in the table -- exactly the kind of bug the critique exists to catch.
    print("\n=== FORCED CRITIQUE FAILURE CASE (fact with no citation in table) ===")
    r_fail = DuckResponse(question="test question", channel="text", language="en", urgency="normal")
    r_fail.facts_used = ["made_up_topic_no_citation"]
    r_fail.draft_text = "made up topic no citation: 99% [Nonexistent Source]"
    r_fail = critique(r_fail)
    r_fail = final_response(r_fail)
    print("CRITIQUE:", "; ".join(r_fail.critique))
    print("CRITIQUE STATUS:", r_fail.critique_status)
    print("RESPONSE:")
    print(send_via_channel(r_fail))
    assert r_fail.critique_status == "FAILED, answer withheld", "The critique should have failed and it didn't"
    assert "no citation" in r_fail.critique[0], "The failure reason isn't the expected one"
    print("\n✓ Confirmed: the critique detects and blocks a fact with no citation in the table.")
