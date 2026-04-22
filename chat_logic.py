from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Any

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
RESTART_HINT = (
    "\n\nSe quiser montar outro protocolo, clique em Reiniciar ou digite reiniciar."
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


@dataclass(slots=True)
class ConversationState:
    step: int = 0
    base_color: str = ""
    target_color: str = ""
    technique: str = ""
    water_test: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "ConversationState":
        data = payload or {}
        step = data.get("step", 0)

        try:
            normalized_step = max(int(step), 0)
        except (TypeError, ValueError):
            normalized_step = 0

        return cls(
            step=normalized_step,
            base_color=str(data.get("baseColor", "") or ""),
            target_color=str(data.get("targetColor", "") or ""),
            technique=str(data.get("technique", "") or ""),
            water_test=str(data.get("waterTest", "") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "baseColor": self.base_color,
            "targetColor": self.target_color,
            "technique": self.technique,
            "waterTest": self.water_test,
        }


@dataclass(slots=True)
class ChatResult:
    response: str
    state: ConversationState
    restart: bool = False


@dataclass(slots=True)
class GoalProfile:
    label: str
    expected_background: str
    oswald_guidance: str
    natural_reference: str
    fantasy_reference: str
    ox_hint: str
    bleaching_target: str
    caution: str


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(
        character for character in normalized if unicodedata.category(character) != "Mn"
    )
    return without_accents.strip()


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


def describe_water_test(water_test: str) -> str:
    descriptions = {
        "boia": "boia (baixa porosidade)",
        "meio": "meio (porosidade equilibrada)",
        "afunda": "afunda (alta porosidade)",
    }
    return descriptions.get(water_test, water_test)


def get_goal_profile(target_color: str, base_color: str) -> GoalProfile:
    normalized_target = normalize_text(target_color)

    if any(
        keyword in normalized_target
        for keyword in ("platin", "acinzent", "perol", "gelo", "loiro")
    ):
        return GoalProfile(
            label="loiro frio ou platinado",
            expected_background="amarelo claro a amarelo palha",
            oswald_guidance=(
                "Pela Estrela de Oswald, amarelo neutraliza com violeta e laranja com "
                "azul. Se o fundo abrir muito dourado, use violeta. Se abrir "
                "amarelo-alaranjado, use azul com violeta."
            ),
            natural_reference="base natural no nivel de altura de tom alcançado",
            fantasy_reference="nuance fria, como acinzentada, irisada ou violeta",
            ox_hint="10 a 20 volumes para tonalizacao. No clareamento, 20 ou 30 volumes conforme resistencia do fio.",
            bleaching_target="amarelo claro uniforme antes da matizacao",
            caution=(
                "Se houver coloracao artificial escura, pode ser necessario corrigir ou "
                "decapar antes, porque tinta nao clareia tinta."
            ),
        )

    if any(keyword in normalized_target for keyword in ("ruivo", "cobre", "acobreado", "ginger")):
        return GoalProfile(
            label="ruivo cobre",
            expected_background="laranja dourado",
            oswald_guidance=(
                "Na Estrela de Oswald, azul neutraliza laranja. Para um cobre bonito, "
                "nao anule totalmente o laranja; use azul apenas se o fundo abrir quente "
                "demais ou manchado."
            ),
            natural_reference="base natural no mesmo nivel do ruivo desejado",
            fantasy_reference="nuance cobre ou cobre dourado",
            ox_hint="20 volumes na maioria dos depositos e 30 volumes quando precisar abrir mais a base.",
            bleaching_target="amarelo alaranjado limpo, sem manchas",
            caution=(
                "Ruivos desbotam rapido. Vale reforcar pigmento no tonalizante final e "
                "manter temperatura de agua mais fria na manutencao."
            ),
        )

    if any(keyword in normalized_target for keyword in ("marsala", "vinho", "ameixa", "vermelho")):
        return GoalProfile(
            label="vermelho profundo ou marsala",
            expected_background="vermelho com apoio de cobre ou violeta",
            oswald_guidance=(
                "Na Estrela de Oswald, verde neutraliza vermelho. Use verde apenas para "
                "segurar excesso de vermelho. Para manter marsala, preserve reflexos "
                "vermelho-violeta sem neutralizar demais."
            ),
            natural_reference="base natural do mesmo nivel para sustentacao do fundo",
            fantasy_reference="nuance vermelho, violeta ou vermelho-violeta",
            ox_hint="20 volumes para depositar cor e 30 volumes se precisar abrir levemente a base antes.",
            bleaching_target="fundo limpo sem laranja sujo antes da coloracao",
            caution=(
                "Em bases muito escuras, o marsala costuma aparecer melhor depois de uma "
                "abertura previa controlada."
            ),
        )

    if any(keyword in normalized_target for keyword in ("branco", "brancos", "cobrir")):
        return GoalProfile(
            label="cobertura de brancos",
            expected_background="deposito uniforme sem necessidade de descoloracao",
            oswald_guidance=(
                "A leitura pela Estrela de Oswald entra mais na neutralizacao final. Em "
                "cobertura de brancos, o principal e usar base natural para ancoragem da cor."
            ),
            natural_reference="base natural da mesma altura do tom desejado",
            fantasy_reference="nuance desejada em apoio, sem retirar a base natural da formula",
            ox_hint="20 volumes para cobertura mais consistente de brancos.",
            bleaching_target="nao se aplica, salvo correcao previa",
            caution=(
                "Para alta porcentagem de brancos, mantenha a base natural sempre presente "
                "na formula para evitar transparencia."
            ),
        )

    if any(keyword in normalized_target for keyword in ("castanho", "chocolate", "escurecer", "frio", "marrom")):
        return GoalProfile(
            label="castanho de profundidade fria ou neutra",
            expected_background="laranja ou vermelho, dependendo da base",
            oswald_guidance=(
                "Na Estrela de Oswald, azul neutraliza laranja e verde neutraliza vermelho. "
                "Para fechar em castanho frio, controle o calor com reflexos frios sem "
                "anular demais a profundidade."
            ),
            natural_reference="base natural na altura final desejada",
            fantasy_reference="nuance fria, como acinzentada ou mate, em apoio ao castanho",
            ox_hint="10 a 20 volumes para deposito e escurecimento seguro.",
            bleaching_target="na maioria dos casos nao precisa abrir; apenas equalizar fundo",
            caution=(
                "Se o cabelo estiver muito claro e poroso, faca pre-pigmentacao antes do "
                "escurecimento para evitar manchas."
            ),
        )

    return GoalProfile(
        label=f"resultado personalizado saindo de {base_color}",
        expected_background="fundo de clareamento compativel com o nivel desejado",
        oswald_guidance=(
            "Use a Estrela de Oswald assim: amarelo neutraliza com violeta, laranja com "
            "azul e vermelho com verde. Preserve ou neutralize o fundo conforme o efeito final."
        ),
        natural_reference="base natural no nivel que vai sustentar a cor final",
        fantasy_reference="nuance fantasia ou reflexo que represente o efeito desejado",
        ox_hint="10 a 20 volumes para deposito e 20 a 30 volumes quando houver abertura controlada.",
        bleaching_target="clareamento uniforme antes da matizacao ou coloracao final",
        caution=(
            "Cheque historico quimico e elasticidade antes de elevar muito a altura de tom."
        ),
    )


def build_technique_steps(technique: str, profile: GoalProfile) -> list[str]:
    if technique == "descoloracao global":
        return [
            "Faça anamnese, teste de mecha e teste de elasticidade antes de iniciar.",
            "Divida o cabelo em quatro quadrantes para manter aplicacao limpa e uniforme.",
            "Aplique o descolorante primeiro em comprimento e pontas se a raiz estiver mais quente ou virgem, deixando a raiz por ultimo quando necessario.",
            f"Monitore o fundo de clareamento ate chegar em {profile.bleaching_target}.",
            "Enxague, reequilibre o pH, seque cerca de 80% e so depois aplique a formula de coloracao ou tonalizacao.",
        ]

    if technique == "mechas":
        return [
            "Faça teste de mecha e separe o cabelo em quadrantes organizados.",
            "Selecione mechas finas ou medias conforme o efeito desejado e isole com papel ou manta.",
            "Sature bem o descolorante para evitar manchas e acompanhe a abertura mecha por mecha.",
            f"Pare o clareamento quando o fundo atingir {profile.bleaching_target}.",
            "Enxague, trate e tonalize usando a formula final para alinhar reflexo e brilho.",
        ]

    if technique == "balayage":
        return [
            "Faça diagnostico de fundo e porosidade antes das pinceladas.",
            "Divida o cabelo em diagonais e aplique em formato de V ou W para um degradê suave.",
            "Concentre saturacao nas areas que precisam mais luz e esfume a raiz para manter profundidade.",
            f"Controle o clareamento ate chegar em {profile.bleaching_target}.",
            "Depois do enxague, faça tonalizacao de raiz e comprimento para acabamento mais profissional.",
        ]

    if technique == "correcao de cor":
        return [
            "Mapeie manchas, fundos diferentes e historico de coloracoes anteriores.",
            "Se houver excesso de pigmento artificial, considere limpeza de cor ou decapagem controlada antes de clarear.",
            "Equalize porosidade antes de aplicar nova quimica para evitar sobrecarga em areas frageis.",
            f"Somente depois avance ate {profile.bleaching_target} ou para o nivel compativel com o objetivo.",
            "Finalize com formula corretiva e acompanhe o resultado mecha por mecha.",
        ]

    if technique == "retoque de raiz":
        return [
            "Isole apenas o crescimento novo para nao sobrepor quimica onde ja existe clareamento.",
            "Aplique com precisao na raiz, respeitando a largura do crescimento.",
            "Monitore a abertura ate igualar com comprimento e pontas.",
            "Se precisar, emulsione rapidamente para unificar reflexo sem sensibilizar o restante.",
            "Finalize com tonalizacao ou coloracao de alinhamento."
        ]

    return [
        "Faça teste de mecha, porosidade e compatibilidade antes da aplicacao.",
        "Equalize a fibra com tratamento rapido para a cor assentar de forma mais uniforme.",
        "Aplique a formula da raiz para o comprimento respeitando o tempo de pausa da marca.",
        "Emulsione nos minutos finais para uniformizar reflexo e brilho.",
        "Enxague, sele cuticulas e finalize com mascara pos-coloracao.",
    ]


def build_water_plan(water_test: str) -> list[str]:
    if water_test == "boia":
        return [
            "Diagnostico: baixa porosidade. O fio resiste a absorver agua e produto.",
            "Hidratacao: 1 vez por semana com mascaras leves e um pouco de calor umido para melhor penetracao.",
            "Nutricao: a cada 15 dias com oleos leves, evitando excesso para nao pesar.",
            "Reconstrucao: a cada 30 dias ou apenas quando houver quimica mais forte.",
        ]

    if water_test == "meio":
        return [
            "Diagnostico: porosidade equilibrada. O fio costuma responder bem aos processos.",
            "Hidratacao: 1 vez por semana para manter maleabilidade e brilho.",
            "Nutricao: a cada 15 dias para segurar emoliencia e controle de frizz.",
            "Reconstrucao: a cada 20 a 30 dias, especialmente apos descoloracao.",
        ]

    return [
        "Diagnostico: alta porosidade. O fio absorve rapido, mas perde agua e pigmento com facilidade.",
        "Hidratacao: 1 a 2 vezes por semana com ativos umectantes e selagem no enxague.",
        "Nutricao: semanal para repor lipideos e reduzir aspereza.",
        "Reconstrucao: a cada 10 a 15 dias, com cautela para nao enrijecer demais a fibra.",
    ]


def build_formula_section(profile: GoalProfile) -> list[str]:
    return [
        f"Base natural: {profile.natural_reference}.",
        f"Cor fantasia ou reflexo: {profile.fantasy_reference}.",
        "Calculo pela regra solicitada: 30 g de cor natural + 30 g de cor fantasia = 60 g de coloracao.",
        "OX = metade do total da coloracao. Entao: 60 / 2 = 30 g de oxidante.",
        f"Oxidante sugerido: {profile.ox_hint}",
    ]


def build_protocol_response(state: ConversationState) -> str:
    profile = get_goal_profile(state.target_color, state.base_color)
    technique_steps = build_technique_steps(state.technique, profile)
    water_plan = build_water_plan(state.water_test)
    formula_lines = build_formula_section(profile)

    lines = [
        "Protocolo tecnico sugerido",
        "",
        "Diagnostico",
        f"- Base atual: {state.base_color}",
        f"- Objetivo final: {state.target_color}",
        f"- Tecnica escolhida: {state.technique}",
        f"- Teste da agua: {describe_water_test(state.water_test)}",
        "",
        "Passo a passo profissional",
    ]

    for index, step in enumerate(technique_steps, start=1):
        lines.append(f"{index}. {step}")

    lines.extend(
        [
            "",
            "Leitura pela Estrela de Oswald",
            f"- Fundo esperado: {profile.expected_background}",
            f"- Neutralizacao ou preservacao: {profile.oswald_guidance}",
            "",
            "Calculo da formula",
        ]
    )

    for line in formula_lines:
        lines.append(f"- {line}")

    lines.extend(["", "Hidratacao e cronograma pelo teste da agua"])
    for line in water_plan:
        lines.append(f"- {line}")

    lines.extend(
        [
            "",
            "Observacao profissional",
            f"- {profile.caution}",
        ]
    )

    if state.base_color == "preto" and any(
        keyword in normalize_text(state.target_color) for keyword in ("loiro", "platin", "clarear")
    ):
        lines.append(
            "- Em base preta, a subida para loiro costuma exigir mais de uma etapa e muito controle de fundo para preservar integridade."
        )

    lines.append(RESTART_HINT.strip())
    return "\n".join(lines)


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
            f"Reiniciar ou digite reiniciar.{RESTART_HINT}"
        ),
        state=state,
    )
