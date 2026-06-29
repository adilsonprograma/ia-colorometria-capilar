from __future__ import annotations

from dataclasses import dataclass

from .colorimetria import (
    ColorimetryCalculation,
    FormulaProfile,
    build_formula_profile,
    build_numbering_section,
    calculate_colorimetry,
)
from .models import ConversationState
from .text_utils import normalize_text

FORMULA_REFERENCE_PART_GRAMS = 30
RESTART_HINT = "Se quiser montar outro protocolo, clique em Reiniciar ou digite reiniciar."


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


@dataclass(slots=True)
class CapillaryStudy:
    profile: GoalProfile
    formula_profile: FormulaProfile
    colorimetry_calculation: ColorimetryCalculation
    technique_steps: list[str]
    water_plan: list[str]
    numbering_lines: list[str]
    chemistry_lines: list[str]
    colorimetry_lines: list[str]
    mechanism_lines: list[str]


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
            natural_reference="base natural no nivel de altura de tom alcancado",
            fantasy_reference="nuance fria, como acinzentada, irisada ou violeta",
            ox_hint=(
                "10 a 20 volumes para tonalizacao. No clareamento, 20 ou 30 volumes "
                "conforme resistencia do fio."
            ),
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
            ox_hint=(
                "20 volumes na maioria dos depositos e 30 volumes quando precisar abrir "
                "mais a base."
            ),
            bleaching_target="amarelo alaranjado limpo, sem manchas",
            caution=(
                "Ruivos desbotam rapido. Vale reforcar pigmento no tonalizante final e "
                "manter temperatura de agua mais fria na manutencao."
            ),
        )

    if any(keyword in normalized_target for keyword in ("marsala", "vinho", "ameixa", "acaju")):
        return GoalProfile(
            label="marsala ou acaju profundo",
            expected_background="vermelho com apoio de cobre ou violeta",
            oswald_guidance=(
                "Na Estrela de Oswald, verde neutraliza vermelho. Use verde apenas para "
                "segurar excesso de vermelho. Para manter marsala, preserve reflexos "
                "vermelho-violeta sem neutralizar demais."
            ),
            natural_reference="base natural do mesmo nivel para sustentacao do fundo",
            fantasy_reference="nuance vermelho, violeta ou vermelho-violeta",
            ox_hint=(
                "20 volumes para depositar cor e 30 volumes se precisar abrir levemente "
                "a base antes."
            ),
            bleaching_target="fundo limpo sem laranja sujo antes da coloracao",
            caution=(
                "Em bases muito escuras, o marsala costuma aparecer melhor depois de uma "
                "abertura previa controlada."
            ),
        )

    if "vermelho" in normalized_target:
        return GoalProfile(
            label="vermelho intenso",
            expected_background="vermelho aberto com apoio de cobre",
            oswald_guidance=(
                "Na Estrela de Oswald, verde neutraliza vermelho. Use verde apenas para "
                "segurar excesso de calor quando o objetivo nao for um vermelho muito vivo."
            ),
            natural_reference="base natural no mesmo nivel para sustentar intensidade",
            fantasy_reference="nuance vermelha para reforcar saturacao e profundidade",
            ox_hint=(
                "20 volumes para depositar e 30 volumes quando precisar abrir levemente "
                "a base."
            ),
            bleaching_target="fundo limpo e uniforme, sem manchas quentes excessivas",
            caution=(
                "Vermelhos intensos costumam desbotar mais rapido e pedem manutencao de "
                "pigmento com mais frequencia."
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
        caution="Cheque historico quimico e elasticidade antes de elevar muito a altura de tom.",
    )


def build_technique_steps(technique: str, profile: GoalProfile) -> list[str]:
    if technique == "descoloracao global":
        return [
            "Faca anamnese, teste de mecha e teste de elasticidade antes de iniciar.",
            "Divida o cabelo em quatro quadrantes para manter aplicacao limpa e uniforme.",
            "Aplique o descolorante primeiro em comprimento e pontas se a raiz estiver mais quente ou virgem, deixando a raiz por ultimo quando necessario.",
            f"Monitore o fundo de clareamento ate chegar em {profile.bleaching_target}.",
            "Enxague, reequilibre o pH, seque cerca de 80% e so depois aplique a formula de coloracao ou tonalizacao.",
        ]

    if technique == "mechas":
        return [
            "Faca teste de mecha e separe o cabelo em quadrantes organizados.",
            "Selecione mechas finas ou medias conforme o efeito desejado e isole com papel ou manta.",
            "Sature bem o descolorante para evitar manchas e acompanhe a abertura mecha por mecha.",
            f"Pare o clareamento quando o fundo atingir {profile.bleaching_target}.",
            "Enxague, trate e tonalize usando a formula final para alinhar reflexo e brilho.",
        ]

    if technique == "balayage":
        return [
            "Faca diagnostico de fundo e porosidade antes das pinceladas.",
            "Divida o cabelo em diagonais e aplique em formato de V ou W para um degrade suave.",
            "Concentre saturacao nas areas que precisam mais luz e esfume a raiz para manter profundidade.",
            f"Controle o clareamento ate chegar em {profile.bleaching_target}.",
            "Depois do enxague, faca tonalizacao de raiz e comprimento para acabamento mais profissional.",
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
            "Finalize com tonalizacao ou coloracao de alinhamento.",
        ]

    return [
        "Faca teste de mecha, porosidade e compatibilidade antes da aplicacao.",
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


def build_chemistry_section(profile: GoalProfile, formula_profile: FormulaProfile) -> list[str]:
    natural_grams = FORMULA_REFERENCE_PART_GRAMS
    fantasy_grams = FORMULA_REFERENCE_PART_GRAMS
    result_grams = natural_grams + fantasy_grams
    oxidant_grams = int(result_grams * 1.5)

    return [
        "Creme colorante alcalino: a amonia ou agente similar abre a cuticula para a entrada dos precursores de cor.",
        (
            f"Formula em gramas: {natural_grams} g do tom natural {formula_profile.natural_tone} + "
            f"{fantasy_grams} g da nuance {formula_profile.fantasy_tone} = {result_grams} g de coloracao."
        ),
        (
            f"OX pela leitura da elevacao: {formula_profile.oxidant_volume} volumes. "
            f"{formula_profile.oxidant_action}"
        ),
        f"Pela regra do projeto, OX = 1,5 vezes o total da coloracao (proporcao 1:1,5): {result_grams} x 1.5 = {oxidant_grams} g de oxidante.",
        f"Leitura tecnica complementar: {profile.ox_hint}",
    ]


def build_colorimetry_section(
    profile: GoalProfile,
    formula_profile: FormulaProfile,
    colorimetry_calculation: ColorimetryCalculation,
) -> list[str]:
    return [
        f"Formula da cor: {colorimetry_calculation.formula_expression}.",
        f"Cor desejada aproximada: {colorimetry_calculation.approximate_result}.",
        f"Fundo esperado: {profile.expected_background}.",
        f"Neutralizacao ou preservacao: {profile.oswald_guidance}",
        colorimetry_calculation.reflection_reading,
        (
            "Mistura de tons: quando dois tons com o mesmo reflexo sao usados, o resultado "
            "pode caminhar para um intermediario. Ex.: 7.1 + 9.1 = 8.1."
        ),
        colorimetry_calculation.mix_rule_11_reading,
    ]


def build_mechanism_section(formula_profile: FormulaProfile) -> list[str]:
    return [
        "Abertura: o alcalinizante eleva o pH e abre as cuticulas.",
        (
            "Oxidacao ou clareamento: "
            f"a OX de {formula_profile.oxidant_volume} volumes libera oxigenio e atua no cortex."
        ),
        "Deposito: os pigmentos artificiais entram no cortex e se oxidam para formar a nova cor.",
        "Selagem: apos enxague e tratamento de pH mais baixo, a fibra tende a reter melhor a cor.",
    ]


def build_capillary_study(state: ConversationState) -> CapillaryStudy:
    profile = get_goal_profile(state.target_color, state.base_color)
    formula_profile = build_formula_profile(state.target_color, state.base_color)
    colorimetry_calculation = calculate_colorimetry(formula_profile)
    technique_steps = build_technique_steps(state.technique, profile)
    water_plan = build_water_plan(state.water_test)
    numbering_lines = build_numbering_section(formula_profile)
    chemistry_lines = build_chemistry_section(profile, formula_profile)
    colorimetry_lines = build_colorimetry_section(profile, formula_profile, colorimetry_calculation)
    mechanism_lines = build_mechanism_section(formula_profile)
    return CapillaryStudy(
        profile=profile,
        formula_profile=formula_profile,
        colorimetry_calculation=colorimetry_calculation,
        technique_steps=technique_steps,
        water_plan=water_plan,
        numbering_lines=numbering_lines,
        chemistry_lines=chemistry_lines,
        colorimetry_lines=colorimetry_lines,
        mechanism_lines=mechanism_lines,
    )


def describe_water_test(water_test: str) -> str:
    descriptions = {
        "boia": "boia (baixa porosidade)",
        "meio": "meio (porosidade equilibrada)",
        "afunda": "afunda (alta porosidade)",
    }
    return descriptions.get(water_test, water_test)


def build_protocol_response(state: ConversationState) -> str:
    study = build_capillary_study(state)

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

    for index, step in enumerate(study.technique_steps, start=1):
        lines.append(f"{index}. {step}")

    lines.extend(["", "Leitura da numeracao"])
    for line in study.numbering_lines:
        lines.append(f"- {line}")

    lines.extend(["", "Quimica da formula"])
    for line in study.chemistry_lines:
        lines.append(f"- {line}")

    lines.extend(["", "Leitura pela Estrela de Oswald"])
    for line in study.colorimetry_lines:
        lines.append(f"- {line}")

    lines.extend(["", "Mecanismo de acao"])
    for line in study.mechanism_lines:
        lines.append(f"- {line}")

    lines.extend(["", "Hidratacao e cronograma pelo teste da agua"])
    for line in study.water_plan:
        lines.append(f"- {line}")

    lines.extend(["", "Observacao profissional", f"- {study.profile.caution}"])

    if state.base_color == "preto" and any(
        keyword in normalize_text(state.target_color) for keyword in ("loiro", "platin", "clarear")
    ):
        lines.append(
            "- Em base preta, a subida para loiro costuma exigir mais de uma etapa e muito controle de fundo para preservar integridade."
        )

    lines.append("")
    lines.append(RESTART_HINT)
    return "\n".join(lines)

