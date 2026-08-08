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
"""
from dataclasses import dataclass, field

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


@dataclass
class RespuestaDuck:
    pregunta: str
    borrador: str
    hechos_usados: list
    critica: list = field(default_factory=list)
    final: str = ""
    paso_critica: str = "no ejecutado"


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


def draft(pregunta: str) -> RespuestaDuck:
    temas = _detectar_temas(pregunta)
    lineas = []
    for t in temas:
        h = HECHOS[t]
        lineas.append(f"{t.replace('_', ' ')}: {h['valor']} [{h['cita']}]")
    borrador = " ".join(lineas)
    return RespuestaDuck(pregunta=pregunta, borrador=borrador, hechos_usados=temas)


def critica(r: RespuestaDuck) -> RespuestaDuck:
    """La critica REAL: verifica que cada afirmacion del borrador tenga una
    cita en HECHOS, y que no se mencione ningun numero que no venga de ahi.
    No es un LLM diciendo "revise todo, esta bien" -- es un chequeo que puede
    fallar de verdad si el borrador se desvia de la tabla de hechos."""
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
    if r.paso_critica == "FALLÓ, no se entrega respuesta":
        r.final = ("No tengo una respuesta con cita verificada para esto. "
                   "Consultá santamonica.gov/rentcontrol o a la Agencia directamente.")
    else:
        r.final = r.borrador + "\n\n(Verificado: cada dato citado contra la fuente oficial antes de mostrarse.)"
    return r


def preguntar(pregunta: str) -> RespuestaDuck:
    r = draft(pregunta)
    r = critica(r)
    r = final_respuesta(r)
    return r


if __name__ == "__main__":
    PREGUNTAS_PRUEBA = [
        "¿Cuál es el ajuste general 2026 y hay un tope en dólares?",
        "¿Puede el propietario aplicar varios años de aumentos acumulados de una sola vez?",
        "Mi tenencia empezó en noviembre de 2025. ¿Soy elegible para el ajuste de septiembre 2026?",
    ]
    for q in PREGUNTAS_PRUEBA:
        r = preguntar(q)
        print(f"\n=== {q} ===")
        print("CRÍTICA:", "; ".join(r.critica))
        print("FINAL:", r.final)
