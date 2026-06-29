from __future__ import annotations

from dataclasses import dataclass
import re

from .text_utils import normalize_text

BASE_COLOR_TONE_LEVELS = {
    "preto": "1",
    "castanho": "5",
    "loiro": "8",
    "ruivo": "7",
    "grisalho": "10",
}

NATURAL_TONE_LABELS = {
    "1": "preto",
    "2": "castanho muito escuro",
    "3": "castanho escuro",
    "4": "castanho medio",
    "5": "castanho claro",
    "6": "loiro escuro",
    "7": "loiro medio",
    "8": "loiro claro",
    "9": "loiro muito claro",
    "10": "loiro clarissimo",
}

FANTASY_TONE_LABELS = {
    "0.11": "acinzentado intenso",
    "0.1": "acinzentado",
    "0.2": "irisado ou perolado",
    "0.3": "dourado",
    "0.4": "cobre",
    "0.5": "acaju ou marsala",
    "0.6": "vermelho",
}

FANTASY_TONE_GUIDANCE = {
    "0.11": "Reflexo frio intenso, util para segurar amarelo e ajudar no controle do calor residual.",
    "0.1": "Reflexo acinzentado para esfriar fundos alaranjados e deixar a leitura mais neutra.",
    "0.2": "Reflexo irisado ou perolado, bom para amarelos mais claros e acabamento mais suave.",
    "0.3": "Reflexo dourado para aquecer, devolver luminosidade e manter o fundo mais solar.",
    "0.4": "Reflexo cobre para reforcar calor e construir ruivos ou acobreados.",
    "0.5": "Reflexo acaju ou marsala, com leitura vermelho-violeta mais profunda.",
    "0.6": "Reflexo vermelho para intensificar calor, profundidade e saturacao.",
}


@dataclass(slots=True)
class FormulaProfile:
    base_tone: str
    natural_tone: str
    natural_label: str
    fantasy_tone: str
    fantasy_label: str
    approximate_result: str
    oxidant_volume: int
    oxidant_action: str
    mix_rule_11_amount: int


@dataclass(slots=True)
class ColorimetryCalculation:
    formula_expression: str
    approximate_result: str
    reflection_reading: str
    mix_rule_11_reading: str


def get_base_tone(base_color: str) -> str:
    return BASE_COLOR_TONE_LEVELS.get(base_color, "6")


def describe_oxidant_action(oxidant_volume: int) -> str:
    actions = {
        10: "Apenas deposita cor sem grande elevacao de fundo.",
        20: "Clareia 1 a 2 tons e ajuda na cobertura de brancos.",
        30: "Clareia 2 a 3 tons.",
        40: "Clareia ate 4 tons.",
    }
    return actions.get(oxidant_volume, "A volumagem precisa ser confirmada pela marca.")


def estimate_oxidant_volume(base_tone: str, natural_tone: str, target_color: str) -> int:
    normalized_target = normalize_text(target_color)

    if any(keyword in normalized_target for keyword in ("branco", "brancos", "cobrir")):
        return 20

    lift = max(int(natural_tone) - int(base_tone), 0)
    if lift == 0:
        return 10
    if lift <= 2:
        return 20
    if lift <= 3:
        return 30
    return 40


def combine_formula_result(natural_tone: str, fantasy_tone: str) -> str:
    return f"{natural_tone}{fantasy_tone[1:]}"


def create_formula_profile(
    base_tone: str,
    natural_tone: str,
    fantasy_tone: str,
    target_color: str,
) -> FormulaProfile:
    oxidant_volume = estimate_oxidant_volume(base_tone, natural_tone, target_color)
    return FormulaProfile(
        base_tone=base_tone,
        natural_tone=natural_tone,
        natural_label=NATURAL_TONE_LABELS.get(natural_tone, f"tom {natural_tone}"),
        fantasy_tone=fantasy_tone,
        fantasy_label=FANTASY_TONE_LABELS.get(fantasy_tone, "reflexo personalizado"),
        approximate_result=combine_formula_result(natural_tone, fantasy_tone),
        oxidant_volume=oxidant_volume,
        oxidant_action=describe_oxidant_action(oxidant_volume),
        mix_rule_11_amount=max(0, 11 - int(natural_tone)),
    )


def detect_requested_formula_code(text: str) -> tuple[str, str] | None:
    normalized_text = normalize_text(text)
    match = re.search(r"\b(10|[1-9])[.,](11|1|2|3|4|5|6)\b", normalized_text)

    if match is None:
        return None

    natural_tone = match.group(1)
    fantasy_suffix = match.group(2)
    fantasy_tone = "0.11" if fantasy_suffix == "11" else f"0.{fantasy_suffix}"
    return natural_tone, fantasy_tone


def build_formula_profile(target_color: str, base_color: str) -> FormulaProfile:
    base_tone = get_base_tone(base_color)
    explicit_code = detect_requested_formula_code(target_color)
    if explicit_code is not None:
        natural_tone, fantasy_tone = explicit_code
        return create_formula_profile(base_tone, natural_tone, fantasy_tone, target_color)

    normalized_target = normalize_text(target_color)
    default_natural_tone = base_tone

    if any(keyword in normalized_target for keyword in ("platin", "acinzent", "gelo")):
        return create_formula_profile(base_tone, "10", "0.11", target_color)

    if any(keyword in normalized_target for keyword in ("perol", "irisad")):
        return create_formula_profile(base_tone, "10", "0.2", target_color)

    if any(keyword in normalized_target for keyword in ("matiz", "matizacao", "tonaliz")):
        natural_tone = "9" if base_color in {"loiro", "grisalho"} else default_natural_tone
        return create_formula_profile(base_tone, natural_tone, "0.11", target_color)

    if "dourad" in normalized_target:
        return create_formula_profile(base_tone, "9", "0.3", target_color)

    if any(keyword in normalized_target for keyword in ("ruivo", "cobre", "acobreado", "ginger")):
        return create_formula_profile(base_tone, "7", "0.4", target_color)

    if any(keyword in normalized_target for keyword in ("marsala", "vinho", "ameixa", "acaju")):
        return create_formula_profile(base_tone, "5", "0.5", target_color)

    if "vermelho" in normalized_target:
        return create_formula_profile(base_tone, "6", "0.6", target_color)

    if any(keyword in normalized_target for keyword in ("branco", "brancos", "cobrir")):
        return create_formula_profile(base_tone, default_natural_tone, "0.1", target_color)

    if any(keyword in normalized_target for keyword in ("castanho", "chocolate", "frio", "marrom")):
        return create_formula_profile(base_tone, "5", "0.1", target_color)

    if "loiro" in normalized_target:
        return create_formula_profile(base_tone, "10", "0.11", target_color)

    return create_formula_profile(base_tone, default_natural_tone, "0.3", target_color)


def calculate_colorimetry(formula_profile: FormulaProfile) -> ColorimetryCalculation:
    formula_expression = (
        f"{formula_profile.natural_tone} + {formula_profile.fantasy_tone} = "
        f"{formula_profile.approximate_result}"
    )
    reflection_reading = (
        f"Leitura do reflexo {formula_profile.fantasy_tone}: "
        f"{FANTASY_TONE_GUIDANCE.get(formula_profile.fantasy_tone, 'Use a nuance para aquecer ou esfriar conforme o fundo.')}"
    )
    mix_rule_11_reading = (
        "Regra do 11 para mix ou matizador: "
        f"11 - {formula_profile.natural_tone} = {formula_profile.mix_rule_11_amount}. "
        f"Isso indica ate {formula_profile.mix_rule_11_amount} cm de corretor quando houver necessidade tecnica de neutralizacao."
    )
    return ColorimetryCalculation(
        formula_expression=formula_expression,
        approximate_result=formula_profile.approximate_result,
        reflection_reading=reflection_reading,
        mix_rule_11_reading=mix_rule_11_reading,
    )


def build_numbering_section(formula_profile: FormulaProfile) -> list[str]:
    return [
        "Numero antes do ponto: altura de tom da cor, na escala natural de 1 a 10.",
        f"Altura de tom sugerida: {formula_profile.natural_tone} ({formula_profile.natural_label}).",
        "Numero apos o ponto: reflexo ou nuance secundaria da formula.",
        f"Reflexo sugerido: {formula_profile.fantasy_tone} ({formula_profile.fantasy_label}).",
        f"Leitura final do codigo aproximado: {formula_profile.approximate_result}.",
    ]

