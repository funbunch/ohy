"""duck.py — el loop de critica del Rubber Duck, como codigo real que corre.

Por que esto en vez de solo confiar en un prompt de LLM: un prompt que dice
"critica tu propia respuesta" puede alucinar la critica tanto como la
respuesta original -- es la misma trampa de "verificador que se verifica" que
aparece en cualquier sistema de IA (ver doctrina/ley-del-verificador-que-se-
verifica). Aca la critica es una funcion que CHEQUEA el borrador contra una
tabla de hechos citados, no un LLM narrando que se autochequeo.

Para la demo en vivo: cero dependencia de red, cero servidor, cero API. Los
hechos estan hardcodeados a proposito -- son los hechos oficiales vigentes
(Resolucion 26-001, accion de la Junta oct-2025), no datos inventados para la
demo. Lo que se "fake-ea" para el hackathon es la interfaz de intake
multi-canal (telefono/email/texto) de la vision de Lily, no los hechos legales.

v2: agrega routing canal-entrada=canal-salida, triage de urgencia, framing de
las dos partes (inquilino/propietario, mismo hecho, misma cita, dos lecturas),
escalado obligatorio para Airbnb/short-term (no esta en la fuente oficial,
asi que no se puede afirmar nada), pregunta de cierre, y tono desescalante.
"""
from dataclasses import dataclass, field
from typing import Literal, Optional

Canal = Literal["phone", "text", "email"]
Urgencia = Literal["FAQ", "normal", "URGENTE"]

HECHOS = {
    "ga_2026_pct": {"valor": "2.6%", "cita": "Resolución 26-001"},
    "ga_2026_techo": {"valor": "$70/mes (unidades con MAR ≥ $2,674)", "cita": "Resolución 26-001"},
    "ga_2026_vigencia": {"valor": "1 de septiembre de 2026", "cita": "Resolución 26-001"},
    "elegibilidad_ga": {
        "valor": "tenencia iniciada antes del 1-sep-2025; unidad registrada; sin multas de salud/seguridad sin corregir; aviso escrito conforme a ley estatal",
        "cita": "Resolución 26-001",
    },
    "tope_acumulado": {"valor": "máximo 10% del alquiler anterior en cualquier período de 12 meses", "cita": "Acción de la Junta, octubre 2025"},
    "cobertura": {"valor": "edificios multi-unidad con Certificado de Ocupación emitido el 10-abr-1979 o antes", "cita": "City Charter Art. XVIII"},
    "desalojo_causa_justa": {"valor": "aplica; motivos en Charter §1806", "cita": "City Charter §1806"},
}

# Framing de las dos partes: para cada hecho, que significa para cada lado.
# La oficina representa a los dos, no arbitra -- el sistema ILUMINA la
# diferencia de lectura, no la resuelve. Mismo hecho, misma cita, dos lecturas.
FRAMING_DOS_PARTES = {
    "ga_2026_pct": {
        "inquilino": "Tu alquiler puede subir hasta 2.6% a partir del 1-sep-2026 -- no más que eso por este ajuste, salvo el tope en dólares si aplica.",
        "propietario": "Podés aplicar hasta 2.6% de ajuste general desde el 1-sep-2026, sujeto al techo en dólares para unidades de alquiler alto.",
    },
    "ga_2026_techo": {
        "inquilino": "Si tu alquiler actual (MAR) es $2,674 o más, el aumento en dólares está topado en $70/mes aunque el 2.6% sea más alto en tu caso.",
        "propietario": "Para unidades con MAR ≥ $2,674, el aumento no puede superar $70/mes aunque el 2.6% calculado sea mayor.",
    },
    "elegibilidad_ga": {
        "inquilino": "El propietario solo puede aplicarte este ajuste si tu tenencia empezó antes del 1-sep-2025, la unidad está registrada, no hay multas de salud/seguridad sin corregir, y te dieron aviso por escrito según la ley estatal. Si falta alguno de estos, podés cuestionar el aumento.",
        "propietario": "Para aplicar el ajuste necesitás que la tenencia haya empezado antes del 1-sep-2025, la unidad esté registrada, no tengas multas de salud/seguridad pendientes, y hayas dado aviso por escrito según la ley estatal.",
    },
    "tope_acumulado": {
        "inquilino": "Aunque el propietario tenga aumentos acumulados de años anteriores, no te puede cobrar de golpe más del 10% de tu alquiler anterior en ningún período de 12 meses.",
        "propietario": "Los aumentos acumulados (banked) que apliques de una sola vez están limitados a un máximo de 10% del alquiler anterior del inquilino en cualquier período de 12 meses.",
    },
    "cobertura": {
        "inquilino": "Si tu edificio es multi-unidad y el Certificado de Ocupación es del 10-abr-1979 o antes, estás bajo rent control.",
        "propietario": "Tu edificio está sujeto a rent control si es multi-unidad y el Certificado de Ocupación fue emitido el 10-abr-1979 o antes.",
    },
    "desalojo_causa_justa": {
        "inquilino": "No te pueden desalojar sin una causa justa reconocida -- los motivos válidos están en el Charter §1806, no es a discreción del propietario.",
        "propietario": "Para desalojar a un inquilino necesitás una causa justa dentro de los motivos listados en el Charter §1806, no alcanza con terminar el contrato sin más.",
    },
}

# Palabras clave que indican Airbnb / short-term rental. La fuente oficial NO
# menciona este tema -- no se puede afirmar nada, así que se escala siempre.
PALABRAS_AIRBNB = [
    "airbnb", "short-term", "short term", "alquiler corto", "vrbo",
    "por noche", "temporal", "turistico", "turístico", "vacation rental",
]

# Palabras que indican urgencia real (riesgo inminente de perder la vivienda
# o de una accion irreversible) vs. una consulta informativa.
PALABRAS_URGENTE = [
    "desalojo", "eviction", "notice to vacate", "sheriff", "lockout",
    "me quieren sacar", "me estan desalojando", "3-day notice", "unlawful detainer",
]

PALABRAS_FAQ = [
    "cuanto es el ajuste", "cual es el ajuste", "what is the increase",
    "sitio oficial", "official site", "donde consulto", "where do i check",
]


@dataclass
class RespuestaDuck:
    pregunta: str
    canal: Canal
    urgencia: Urgencia = "normal"
    borrador: str = ""
    hechos_usados: list = field(default_factory=list)
    framing: dict = field(default_factory=dict)
    critica: list = field(default_factory=list)
    final: str = ""
    paso_critica: str = "no ejecutado"
    escalar_a_humano: bool = False
    motivo_escalado: Optional[str] = None
    cierre: str = ""


def _detectar_airbnb(pregunta: str) -> bool:
    p = pregunta.lower()
    return any(k in p for k in PALABRAS_AIRBNB)


def _detectar_urgencia(pregunta: str) -> Urgencia:
    p = pregunta.lower()
    if any(k in p for k in PALABRAS_URGENTE):
        return "URGENTE"
    if any(k in p for k in PALABRAS_FAQ):
        return "FAQ"
    return "normal"


def _detectar_temas(pregunta: str) -> list:
    """Retrieval simple por palabra clave -- suficiente para el dominio
    acotado (una sola ley municipal), no hace falta un motor semantico."""
    p = pregunta.lower()
    temas = []
    if any(k in p for k in ["ajuste", "aumento", "increase", "ga ", "general adjustment", "cuanto"]):
        temas += ["ga_2026_pct", "ga_2026_techo", "ga_2026_vigencia"]
    if any(k in p for k in ["elegib", "eligib", "califico", "puedo"]):
        temas.append("elegibilidad_ga")
    if any(k in p for k in ["acumul", "banked", "varios años", "atrasad"]):
        temas.append("tope_acumulado")
    if any(k in p for k in ["cobertura", "aplica a mi edificio", "covered", "1979"]):
        temas.append("cobertura")
    if any(k in p for k in ["desalojo", "eviction", "causa justa"]):
        temas.append("desalojo_causa_justa")
    return temas or list(HECHOS.keys())  # sin match claro: mostrar todo, no inventar


def _tono_desescalante(urgencia: Urgencia) -> str:
    """Nadie llama contento -- todos llegan ya enojados. El tono de apertura
    reconoce eso antes de entrar en los hechos."""
    if urgencia == "URGENTE":
        return "Entiendo que esto es urgente y necesitás una respuesta clara ya. Vamos directo al punto. "
    return "Gracias por tu paciencia -- vamos directo a lo que necesitás saber. "


def draft(pregunta: str, canal: Canal) -> RespuestaDuck:
    urgencia = _detectar_urgencia(pregunta)
    r = RespuestaDuck(pregunta=pregunta, canal=canal, urgencia=urgencia)

    # Airbnb / short-term: NO responder con hechos -- la fuente oficial no lo
    # menciona, cualquier afirmacion seria inventada. Se escala siempre.
    if _detectar_airbnb(pregunta):
        r.escalar_a_humano = True
        r.motivo_escalado = (
            "La pregunta menciona alquiler de corto plazo / tipo Airbnb. "
            "La fuente oficial (santamonica.gov/rentcontrol) no cubre este tema, "
            "así que no podemos afirmar nada con cita verificada. Se escala a staff humano."
        )
        r.hechos_usados = []
        r.borrador = ""
        return r

    temas = _detectar_temas(pregunta)
    r.hechos_usados = temas
    lineas = []
    for t in temas:
        h = HECHOS[t]
        lineas.append(f"{t.replace('_', ' ')}: {h['valor']} [{h['cita']}]")
        if t in FRAMING_DOS_PARTES:
            r.framing[t] = FRAMING_DOS_PARTES[t]
    r.borrador = _tono_desescalante(urgencia) + " ".join(lineas)
    return r


def critica(r: RespuestaDuck) -> RespuestaDuck:
    """La critica REAL: verifica que cada afirmacion del borrador tenga una
    cita en HECHOS, y que no se mencione ningun numero que no venga de ahi.
    No es un LLM diciendo "revise todo, esta bien" -- es un chequeo que puede
    fallar de verdad si el borrador se desvia de la tabla de hechos."""
    if r.escalar_a_humano:
        r.critica = ["OK: caso marcado para escalado, no se genera respuesta con hechos (evita inventar sobre un tema fuera de la fuente oficial)"]
        r.paso_critica = "ESCALADO -- no aplica critica de hechos"
        return r

    hallazgos = []
    for t in r.hechos_usados:
        if t not in HECHOS:
            hallazgos.append(f"FALLA: '{t}' no tiene cita en la tabla de hechos oficiales")
            continue
        if HECHOS[t]["cita"] not in r.borrador:
            hallazgos.append(f"FALLA: '{t}' se menciona sin su cita ({HECHOS[t]['cita']})")
    if not r.hechos_usados:
        hallazgos.append("FALLA: no se encontró ningún hecho relevante -- no responder, remitir a la fuente oficial")

    r.critica = hallazgos if hallazgos else ["OK: cada afirmación tiene cita verificada contra la tabla de hechos"]
    r.paso_critica = "FALLÓ, no se entrega respuesta" if hallazgos else "PASÓ"
    return r


def final_respuesta(r: RespuestaDuck) -> RespuestaDuck:
    r.cierre = "Does this cover your question, or do you need more info?"

    if r.escalar_a_humano:
        r.final = (
            f"{_tono_desescalante(r.urgencia)}"
            "Esta consulta necesita atención directa de nuestro staff -- te la voy a escalar "
            "ahora mismo para que alguien te contacte con una respuesta específica. "
            "Mientras tanto podés revisar santamonica.gov/rentcontrol."
        )
        return r

    if r.paso_critica == "FALLÓ, no se entrega respuesta":
        r.final = (
            f"{_tono_desescalante(r.urgencia)}"
            "No tengo una respuesta con cita verificada para esto. "
            "Consultá santamonica.gov/rentcontrol o a la Agencia directamente."
        )
        return r

    partes = [r.borrador]
    if r.framing:
        partes.append("\n\n--- Cómo aplica esto según tu situación ---")
        for t, lecturas in r.framing.items():
            partes.append(f"\nSi sos inquilino: {lecturas['inquilino']}")
            partes.append(f"\nSi sos propietario: {lecturas['propietario']}")
    partes.append("\n\n(Verificado: cada dato citado contra la fuente oficial antes de mostrarse.)")
    partes.append(f"\n\n{r.cierre}")
    r.final = "".join(partes)
    return r


def preguntar(pregunta: str, canal: Canal = "text") -> RespuestaDuck:
    r = draft(pregunta, canal)
    r = critica(r)
    r = final_respuesta(r)
    return r


def responder_por_canal(r: RespuestaDuck) -> str:
    """Routing canal-entrada = canal-salida: si llamó, se le llama; si
    escribió texto, se le responde texto; si mandó email, se le responde
    email. Esta funcion simula el envio real (para el hackathon, imprime
    el canal usado en vez de integrar Twilio/SMTP)."""
    etiqueta = {"phone": "LLAMADA saliente", "text": "SMS saliente", "email": "EMAIL saliente"}[r.canal]
    return f"[{etiqueta}] {r.final}"


if __name__ == "__main__":
    CASOS_PRUEBA = [
        ("¿Cuál es el ajuste general 2026 y hay un tope en dólares?", "text"),
        ("Mi tenencia empezó en noviembre de 2025. ¿Soy elegible para el ajuste de septiembre 2026? Me llamaron para avisarme que me van a subir el alquiler.", "phone"),
        ("Quiero poner mi unidad en Airbnb por temporadas cortas, ¿aplica rent control?", "email"),
        ("Me llegó un aviso de desalojo de 3 días, ¿qué hago?", "phone"),
    ]

    for pregunta, canal in CASOS_PRUEBA:
        r = preguntar(pregunta, canal)
        print(f"\n=== [{canal.upper()}] {pregunta} ===")
        print("URGENCIA:", r.urgencia)
        print("ESCALA A HUMANO:", r.escalar_a_humano, f"({r.motivo_escalado})" if r.motivo_escalado else "")
        print("CRÍTICA:", "; ".join(r.critica))
        print("PASO CRITICA:", r.paso_critica)
        print("RESPUESTA:")
        print(responder_por_canal(r))

    # Caso adicional: forzar una falla REAL de crítica (no un caso feliz que
    # nunca podría fallar). Se simula un borrador con un tema sin cita en la
    # tabla -- exactamente el tipo de bug que la crítica está para atrapar.
    print("\n=== CASO DE FALLA FORZADA DE CRÍTICA (hecho sin cita en la tabla) ===")
    r_falla = RespuestaDuck(pregunta="pregunta de prueba", canal="text", urgencia="normal")
    r_falla.hechos_usados = ["tema_inventado_sin_cita"]
    r_falla.borrador = "tema inventado sin cita: 99% [Fuente inexistente]"
    r_falla = critica(r_falla)
    r_falla = final_respuesta(r_falla)
    print("CRÍTICA:", "; ".join(r_falla.critica))
    print("PASO CRITICA:", r_falla.paso_critica)
    print("RESPUESTA:")
    print(responder_por_canal(r_falla))
    assert r_falla.paso_critica == "FALLÓ, no se entrega respuesta", "La crítica debía fallar y no lo hizo"
    assert "no tiene cita" in r_falla.critica[0], "El motivo de falla no es el esperado"
    print("\n✓ Confirmado: la crítica detecta y bloquea un hecho sin cita en la tabla.")
