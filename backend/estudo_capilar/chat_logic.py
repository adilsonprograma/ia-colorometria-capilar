from __future__ import annotations

import re

from .colorimetria import build_formula_profile
from .estudo import build_protocol_response
from .models import ChatResult, ConversationState
from .text_utils import normalize_text

INITIAL_PROMPT = (
    "Ola! Sou a ColorIA. Vamos montar um protocolo tecnico de colorimetria. "
    "Primeiro, me diga qual e a cor atual ou base do cabelo. Exemplos: preto, "
    "castanho, loiro, ruivo ou grisalho."
)
UNKNOWN_BASE_COLOR_PROMPT = (
    "Nao consegui identificar a cor base. Tente responder com algo como preto, "
    "castanho, loiro, ruivo ou grisalho."
)
GOAL_PROMPT_TEMPLATE = (
    "Entendi. Sua base atual e {base_color}. Agora me diga o objetivo final. "
    "Exemplos: loiro platinado, ruivo cobre, marsala, cobertura de brancos, "
    "castanho frio ou matizacao."
)
TECHNIQUE_PROMPT_TEMPLATE = (
    "Objetivo registrado: {target_color}. Agora diga qual tecnica o profissional "
    "vai usar. Exemplos: descoloracao global, mechas, balayage, correcao de cor, "
    "retoque de raiz ou coloracao sem descolorir."
)
UNKNOWN_TECHNIQUE_PROMPT = (
    "Nao consegui identificar a tecnica. Responda com uma destas opcoes: "
    "descoloracao global, mechas, balayage, correcao de cor, retoque de raiz "
    "ou coloracao sem descolorir."
)
WATER_TEST_PROMPT_TEMPLATE = (
    "Perfeito. Tecnica escolhida: {technique}. Agora me diga o resultado do teste "
    "da agua. Responda com boia, meio ou afunda."
)
UNKNOWN_WATER_TEST_PROMPT = (
    "Nao entendi o resultado do teste da agua. Responda com boia, meio ou afunda."
)

BASE_COLOR_KEYWORDS = {
    "preto": "preto",
    "negro": "preto",
    "castanho": "castanho",
    "moreno": "castanho",
    "marrom": "castanho",
    "loiro": "loiro",
    "loira": "loiro",
    "ruivo": "ruivo",
    "ruiva": "ruivo",
    "grisalho": "grisalho",
    "canoso": "grisalho",
    "branco": "grisalho",
}

TECHNIQUE_KEYWORDS = {
    "descoloracao global": (
        "descoloracao global",
        "global",
        "clareamento total",
        "platinado completo",
    ),
    "mechas": ("mechas", "luzes", "papel", "touca"),
    "balayage": ("balayage", "moren iluminada", "free hand", "mao livre"),
    "correcao de cor": ("correcao de cor", "correcao", "decapagem", "limpeza de cor"),
    "retoque de raiz": ("retoque de raiz", "retoque", "raiz"),
    "coloracao sem descolorir": (
        "sem descolorir",
        "tonalizacao",
        "tonalizar",
        "matizacao",
        "banho de brilho",
        "coloracao",
    ),
}

WATER_TEST_KEYWORDS = {
    "boia": ("boia", "flutua", "fica em cima", "superficie"),
    "meio": ("meio", "metade", "centro", "no meio"),
    "afunda": ("afunda", "fundo", "desce", "afundou"),
}


def detect_base_color(text: str) -> str | None:
    normalized_text = normalize_text(text)

    for keyword, canonical in BASE_COLOR_KEYWORDS.items():
        if keyword in normalized_text:
            return canonical

    if re.search(r"\b(escuro|claro|medio)\b", normalized_text):
        if any(keyword in normalized_text for keyword in ("castanho", "moreno", "marrom")):
            return "castanho"
        if "loiro" in normalized_text:
            return "loiro"

    return None


def detect_technique(text: str) -> str | None:
    normalized_text = normalize_text(text)
    for technique, keywords in TECHNIQUE_KEYWORDS.items():
        if any(keyword in normalized_text for keyword in keywords):
            return technique
    return None


def detect_water_test(text: str) -> str | None:
    normalized_text = normalize_text(text)
    for water_test, keywords in WATER_TEST_KEYWORDS.items():
        if any(keyword in normalized_text for keyword in keywords):
            return water_test
    return None


def process_input(text: str, state: ConversationState) -> ChatResult:
    user_text = text.strip()
    normalized_text = normalize_text(user_text)

    if "reiniciar" in normalized_text:
        return ChatResult(
            response=INITIAL_PROMPT,
            state=ConversationState(),
            restart=True,
        )

    if state.step == 0:
        base_color = detect_base_color(user_text)
        if base_color is None:
            return ChatResult(response=UNKNOWN_BASE_COLOR_PROMPT, state=state)

        next_state = ConversationState(step=1, base_color=base_color)
        return ChatResult(
            response=GOAL_PROMPT_TEMPLATE.format(base_color=base_color),
            state=next_state,
        )

    if state.step == 1:
        target_color = user_text.strip()
        next_state = ConversationState(
            step=2,
            base_color=state.base_color,
            target_color=target_color,
        )
        return ChatResult(
            response=TECHNIQUE_PROMPT_TEMPLATE.format(target_color=target_color),
            state=next_state,
        )

    if state.step == 2:
        technique = detect_technique(user_text)
        if technique is None:
            return ChatResult(response=UNKNOWN_TECHNIQUE_PROMPT, state=state)

        next_state = ConversationState(
            step=3,
            base_color=state.base_color,
            target_color=state.target_color,
            technique=technique,
        )
        return ChatResult(
            response=WATER_TEST_PROMPT_TEMPLATE.format(technique=technique),
            state=next_state,
        )

    if state.step == 3:
        water_test = detect_water_test(user_text)
        if water_test is None:
            return ChatResult(response=UNKNOWN_WATER_TEST_PROMPT, state=state)

        next_state = ConversationState(
            step=4,
            base_color=state.base_color,
            target_color=state.target_color,
            technique=state.technique,
            water_test=water_test,
        )
        return ChatResult(
            response=build_protocol_response(next_state),
            state=next_state,
        )

    return ChatResult(
        response=(
            "Ja concluimos esse protocolo. Se quiser montar outro processo, clique em "
            "Reiniciar ou digite reiniciar."
        ),
        state=state,
    )

