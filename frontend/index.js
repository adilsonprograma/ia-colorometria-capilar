document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chatWindow');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const retryBtn = document.getElementById('retryBtn');
    const restartBtn = document.getElementById('restartBtn');
    const noticeBox = document.getElementById('noticeBox');
    const statusBadge = document.getElementById('statusBadge');

    const stepper = document.getElementById('stepper');
    const chipsContainer = document.getElementById('chipsContainer');
    const tabChatBtn = document.getElementById('tabChatBtn');
    const tabProtocolBtn = document.getElementById('tabProtocolBtn');
    const chatColumn = document.getElementById('chatColumn');
    const protocolColumn = document.getElementById('protocolColumn');
    const dashboardPlaceholder = document.getElementById('dashboardPlaceholder');
    const dashboardContent = document.getElementById('dashboardContent');

    const valBaseColor = document.getElementById('valBaseColor');
    const valTargetColor = document.getElementById('valTargetColor');
    const valTechnique = document.getElementById('valTechnique');
    const valPorosity = document.getElementById('valPorosity');
    const valNaturalTone = document.getElementById('valNaturalTone');
    const valFantasyTone = document.getElementById('valFantasyTone');
    const valResultTone = document.getElementById('valResultTone');
    const valOxVolume = document.getElementById('valOxVolume');
    const valOxGrams = document.getElementById('valOxGrams');
    const valOxAction = document.getElementById('valOxAction');
    const valOswaldGuidance = document.getElementById('valOswaldGuidance');
    const valNaturalToneRule = document.getElementById('valNaturalToneRule');
    const valMixCm = document.getElementById('valMixCm');
    const valMixCmDesc = document.getElementById('valMixCmDesc');
    const valHydrationFreq = document.getElementById('valHydrationFreq');
    const valNutritionFreq = document.getElementById('valNutritionFreq');
    const valReconstructionFreq = document.getElementById('valReconstructionFreq');
    const barHydration = document.getElementById('barHydration');
    const barNutrition = document.getElementById('barNutrition');
    const barReconstruction = document.getElementById('barReconstruction');
    const valStepsList = document.getElementById('valStepsList');
    const valCaution = document.getElementById('valCaution');

    const defaultServerOrigin = 'http://127.0.0.1:8000';
    const apiOriginParam = new URLSearchParams(window.location.search).get('apiOrigin');
    const apiOriginMeta = document.querySelector('meta[name="coloria-api-origin"]')?.content || '';
    const apiOriginGlobal =
        typeof window.COLORIA_API_ORIGIN === 'string' ? window.COLORIA_API_ORIGIN : '';
    const apiOriginStored = getStoredApiOrigin();
    const fallbackApiOrigin =
        window.location.protocol === 'file:' ? defaultServerOrigin : window.location.origin;
    const configuredApiOrigin =
        apiOriginParam || apiOriginGlobal || apiOriginMeta || apiOriginStored || fallbackApiOrigin;
    const apiOrigin = normalizeApiOrigin(configuredApiOrigin, fallbackApiOrigin);

    if (apiOriginParam) {
        persistApiOrigin(apiOrigin);
    }
    const fallbackPrompt =
        'Ola! Sou a ColorIA. Vamos montar um protocolo tecnico de colorimetria. Primeiro, me diga qual e a cor atual ou base do cabelo.';
    const defaultFormulaPartGrams = 30;
    const formulaReferenceGuidance =
        'A proporcao final deve seguir a indicacao do fabricante (ex.: 1:1 ou 1:1,5).';
    const baseColorToneLevels = {
        preto: '1',
        castanho: '5',
        loiro: '8',
        ruivo: '7',
        grisalho: '10'
    };
    const naturalToneLabels = {
        '1': 'preto',
        '2': 'castanho muito escuro',
        '3': 'castanho escuro',
        '4': 'castanho medio',
        '5': 'castanho claro',
        '6': 'loiro escuro',
        '7': 'loiro medio',
        '8': 'loiro claro',
        '9': 'loiro muito claro',
        '10': 'loiro clarissimo'
    };
    const fantasyToneLabels = {
        '0.11': 'acinzentado intenso',
        '0.1': 'acinzentado',
        '0.2': 'irisado ou perolado',
        '0.3': 'dourado',
        '0.4': 'cobre',
        '0.5': 'acaju ou marsala',
        '0.6': 'vermelho'
    };
    const fantasyToneGuidance = {
        '0.11': 'Reflexo frio intenso, util para segurar amarelo e ajudar no controle do calor residual.',
        '0.1': 'Reflexo acinzentado para esfriar fundos alaranjados e deixar a leitura mais neutra.',
        '0.2': 'Reflexo irisado ou perolado, bom para amarelos mais claros e acabamento mais suave.',
        '0.3': 'Reflexo dourado para aquecer, devolver luminosidade e manter o fundo mais solar.',
        '0.4': 'Reflexo cobre para reforcar calor e construir ruivos ou acobreados.',
        '0.5': 'Reflexo acaju ou marsala, com leitura vermelho-violeta mais profunda.',
        '0.6': 'Reflexo vermelho para intensificar calor, profundidade e saturacao.'
    };

    let initialPrompt = fallbackPrompt;
    let context = createInitialContext();
    let isRequestInFlight = false;
    let isServerOnline = false;
    let interactionMode = 'connecting';

    function createInitialContext() {
        return {
            step: 0,
            baseColor: '',
            targetColor: '',
            technique: '',
            waterTest: ''
        };
    }

    function getStoredApiOrigin() {
        try {
            return window.localStorage.getItem('coloria.apiOrigin') || '';
        } catch (error) {
            return '';
        }
    }

    function persistApiOrigin(value) {
        try {
            window.localStorage.setItem('coloria.apiOrigin', value);
        } catch (error) {
            // Armazenamento local pode estar indisponivel em alguns navegadores.
        }
    }

    function normalizeApiOrigin(value, fallback) {
        const candidate = String(value || '').trim();
        const fallbackValue = String(fallback || '').trim();
        const resolved = candidate || fallbackValue;
        return resolved.replace(/\/+$/, '');
    }

    function buildApiUrl(path) {
        const normalizedPath = path.startsWith('/') ? path : `/${path}`;
        return `${apiOrigin}${normalizedPath}`;
    }

    function normalizeText(text) {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function detectBaseColor(text) {
        const normalized = normalizeText(text);
        const keywords = {
            preto: 'preto',
            negro: 'preto',
            castanho: 'castanho',
            moreno: 'castanho',
            marrom: 'castanho',
            loiro: 'loiro',
            loira: 'loiro',
            ruivo: 'ruivo',
            ruiva: 'ruivo',
            grisalho: 'grisalho',
            canoso: 'grisalho',
            branco: 'grisalho'
        };

        for (const [keyword, canonical] of Object.entries(keywords)) {
            if (normalized.includes(keyword)) {
                return canonical;
            }
        }

        if (/\b(escuro|claro|medio)\b/.test(normalized)) {
            if (['castanho', 'moreno', 'marrom'].some((keyword) => normalized.includes(keyword))) {
                return 'castanho';
            }

            if (normalized.includes('loiro')) {
                return 'loiro';
            }
        }

        return null;
    }

    function detectTechnique(text) {
        const normalized = normalizeText(text);
        const techniques = {
            'descoloracao global': [
                'descoloracao global',
                'global',
                'clareamento total',
                'platinado completo'
            ],
            mechas: ['mechas', 'luzes', 'papel', 'touca'],
            balayage: ['balayage', 'moren iluminada', 'free hand', 'mao livre'],
            'correcao de cor': ['correcao de cor', 'correcao', 'decapagem', 'limpeza de cor'],
            'retoque de raiz': ['retoque de raiz', 'retoque', 'raiz'],
            'coloracao sem descolorir': [
                'sem descolorir',
                'tonalizacao',
                'tonalizar',
                'matizacao',
                'banho de brilho',
                'coloracao'
            ]
        };

        for (const [technique, keywords] of Object.entries(techniques)) {
            if (keywords.some((keyword) => normalized.includes(keyword))) {
                return technique;
            }
        }

        return null;
    }

    function detectWaterTest(text) {
        const normalized = normalizeText(text);
        const waterTests = {
            boia: ['boia', 'flutua', 'fica em cima', 'superficie'],
            meio: ['meio', 'metade', 'centro', 'no meio'],
            afunda: ['afunda', 'fundo', 'desce', 'afundou']
        };

        for (const [waterTest, keywords] of Object.entries(waterTests)) {
            if (keywords.some((keyword) => normalized.includes(keyword))) {
                return waterTest;
            }
        }

        return null;
    }

    function describeWaterTest(waterTest) {
        const descriptions = {
            boia: 'boia (baixa porosidade)',
            meio: 'meio (porosidade equilibrada)',
            afunda: 'afunda (alta porosidade)'
        };

        return descriptions[waterTest] || waterTest;
    }

    function getBaseTone(baseColor) {
        return baseColorToneLevels[baseColor] || '6';
    }

    function describeOxidantAction(oxidantVolume) {
        const actions = {
            10: 'Apenas deposita cor sem grande elevacao de fundo.',
            20: 'Clareia 1 a 2 tons e ajuda na cobertura de brancos.',
            30: 'Clareia 2 a 3 tons.',
            40: 'Clareia ate 4 tons.'
        };

        return actions[oxidantVolume] || 'A volumagem precisa ser confirmada pela marca.';
    }

    function estimateOxidantVolume(baseTone, naturalTone, targetColor) {
        const normalizedTarget = normalizeText(targetColor);

        if (['branco', 'brancos', 'cobrir'].some((keyword) => normalizedTarget.includes(keyword))) {
            return 20;
        }

        const lift = Math.max(Number.parseInt(naturalTone, 10) - Number.parseInt(baseTone, 10), 0);

        if (lift === 0) {
            return 10;
        }

        if (lift <= 2) {
            return 20;
        }

        if (lift <= 3) {
            return 30;
        }

        return 40;
    }

    function combineFormulaResult(naturalTone, fantasyTone) {
        return `${naturalTone}${fantasyTone.slice(1)}`;
    }

    function createFormulaProfile(baseTone, naturalTone, fantasyTone, targetColor) {
        const oxidantVolume = estimateOxidantVolume(baseTone, naturalTone, targetColor);

        return {
            baseTone,
            naturalTone,
            naturalLabel: naturalToneLabels[naturalTone] || `tom ${naturalTone}`,
            fantasyTone,
            fantasyLabel: fantasyToneLabels[fantasyTone] || 'reflexo personalizado',
            approximateResult: combineFormulaResult(naturalTone, fantasyTone),
            oxidantVolume,
            oxidantAction: describeOxidantAction(oxidantVolume),
            mixRule11Amount: Math.max(0, 11 - Number.parseInt(naturalTone, 10))
        };
    }

    function detectRequestedFormulaCode(text) {
        const normalized = normalizeText(text);
        const match = normalized.match(/\b(10|[1-9])[.,](11|1|2|3|4|5|6)\b/);

        if (!match) {
            return null;
        }

        const naturalTone = match[1];
        const fantasySuffix = match[2];
        const fantasyTone = fantasySuffix === '11' ? '0.11' : `0.${fantasySuffix}`;
        return { naturalTone, fantasyTone };
    }

    function buildFormulaProfile(targetColor, baseColor) {
        const baseTone = getBaseTone(baseColor);
        const explicitCode = detectRequestedFormulaCode(targetColor);

        if (explicitCode) {
            return createFormulaProfile(
                baseTone,
                explicitCode.naturalTone,
                explicitCode.fantasyTone,
                targetColor
            );
        }

        const normalizedTarget = normalizeText(targetColor);
        const defaultNaturalTone = baseTone;

        if (['platin', 'acinzent', 'gelo'].some((keyword) => normalizedTarget.includes(keyword))) {
            return createFormulaProfile(baseTone, '10', '0.11', targetColor);
        }

        if (['perol', 'irisad'].some((keyword) => normalizedTarget.includes(keyword))) {
            return createFormulaProfile(baseTone, '10', '0.2', targetColor);
        }

        if (['matiz', 'matizacao', 'tonaliz'].some((keyword) => normalizedTarget.includes(keyword))) {
            const naturalTone = ['loiro', 'grisalho'].includes(baseColor) ? '9' : defaultNaturalTone;
            return createFormulaProfile(baseTone, naturalTone, '0.11', targetColor);
        }

        if (normalizedTarget.includes('dourad')) {
            return createFormulaProfile(baseTone, '9', '0.3', targetColor);
        }

        if (['ruivo', 'cobre', 'acobreado', 'ginger'].some((keyword) => normalizedTarget.includes(keyword))) {
            return createFormulaProfile(baseTone, '7', '0.4', targetColor);
        }

        if (['marsala', 'vinho', 'ameixa', 'acaju'].some((keyword) => normalizedTarget.includes(keyword))) {
            return createFormulaProfile(baseTone, '5', '0.5', targetColor);
        }

        if (normalizedTarget.includes('vermelho')) {
            return createFormulaProfile(baseTone, '6', '0.6', targetColor);
        }

        if (['branco', 'brancos', 'cobrir'].some((keyword) => normalizedTarget.includes(keyword))) {
            return createFormulaProfile(baseTone, defaultNaturalTone, '0.1', targetColor);
        }

        if (['castanho', 'chocolate', 'frio', 'marrom'].some((keyword) => normalizedTarget.includes(keyword))) {
            return createFormulaProfile(baseTone, '5', '0.1', targetColor);
        }

        if (normalizedTarget.includes('loiro')) {
            return createFormulaProfile(baseTone, '10', '0.11', targetColor);
        }

        return createFormulaProfile(baseTone, defaultNaturalTone, '0.3', targetColor);
    }

    function getGoalProfile(targetColor, baseColor) {
        const normalizedTarget = normalizeText(targetColor);

        if (
            ['platin', 'acinzent', 'perol', 'gelo', 'loiro'].some((keyword) =>
                normalizedTarget.includes(keyword)
            )
        ) {
            return {
                label: 'loiro frio ou platinado',
                expectedBackground: 'amarelo claro a amarelo palha',
                oswaldGuidance:
                    'Pela Estrela de Oswald, amarelo neutraliza com violeta e laranja com azul. Se o fundo abrir muito dourado, use violeta. Se abrir amarelo-alaranjado, use azul com violeta.',
                naturalReference: 'base natural no nivel de altura de tom alcancado',
                fantasyReference: 'nuance fria, como acinzentada, irisada ou violeta',
                oxHint:
                    '10 a 20 volumes para tonalizacao. No clareamento, 20 ou 30 volumes conforme resistencia do fio.',
                bleachingTarget: 'amarelo claro uniforme antes da matizacao',
                caution:
                    'Se houver coloracao artificial escura, pode ser necessario corrigir ou decapar antes, porque tinta nao clareia tinta.'
            };
        }

        if (['ruivo', 'cobre', 'acobreado', 'ginger'].some((keyword) => normalizedTarget.includes(keyword))) {
            return {
                label: 'ruivo cobre',
                expectedBackground: 'laranja dourado',
                oswaldGuidance:
                    'Na Estrela de Oswald, azul neutraliza laranja. Para um cobre bonito, nao anule totalmente o laranja; use azul apenas se o fundo abrir quente demais ou manchado.',
                naturalReference: 'base natural no mesmo nivel do ruivo desejado',
                fantasyReference: 'nuance cobre ou cobre dourado',
                oxHint:
                    '20 volumes na maioria dos depositos e 30 volumes quando precisar abrir mais a base.',
                bleachingTarget: 'amarelo alaranjado limpo, sem manchas',
                caution:
                    'Ruivos desbotam rapido. Vale reforcar pigmento no tonalizante final e manter temperatura de agua mais fria na manutencao.'
            };
        }

        if (['marsala', 'vinho', 'ameixa', 'acaju'].some((keyword) => normalizedTarget.includes(keyword))) {
            return {
                label: 'marsala ou acaju profundo',
                expectedBackground: 'vermelho com apoio de cobre ou violeta',
                oswaldGuidance:
                    'Na Estrela de Oswald, verde neutraliza vermelho. Use verde apenas para segurar excesso de vermelho. Para manter marsala, preserve reflexos vermelho-violeta sem neutralizar demais.',
                naturalReference: 'base natural do mesmo nivel para sustentacao do fundo',
                fantasyReference: 'nuance vermelho, violeta ou vermelho-violeta',
                oxHint:
                    '20 volumes para depositar cor e 30 volumes se precisar abrir levemente a base antes.',
                bleachingTarget: 'fundo limpo sem laranja sujo antes da coloracao',
                caution:
                    'Em bases muito escuras, o marsala costuma aparecer melhor depois de uma abertura previa controlada.'
            };
        }

        if (normalizedTarget.includes('vermelho')) {
            return {
                label: 'vermelho intenso',
                expectedBackground: 'vermelho aberto com apoio de cobre',
                oswaldGuidance:
                    'Na Estrela de Oswald, verde neutraliza vermelho. Use verde apenas para segurar excesso de calor quando o objetivo nao for um vermelho muito vivo.',
                naturalReference: 'base natural no mesmo nivel para sustentar intensidade',
                fantasyReference: 'nuance vermelha para reforcar saturacao e profundidade',
                oxHint:
                    '20 volumes para depositar e 30 volumes quando precisar abrir levemente a base.',
                bleachingTarget: 'fundo limpo e uniforme, sem manchas quentes excessivas',
                caution:
                    'Vermelhos intensos costumam desbotar mais rapido e pedem manutencao de pigmento com mais frequencia.'
            };
        }

        if (['branco', 'brancos', 'cobrir'].some((keyword) => normalizedTarget.includes(keyword))) {
            return {
                label: 'cobertura de brancos',
                expectedBackground: 'deposito uniforme sem necessidade de descoloracao',
                oswaldGuidance:
                    'A leitura pela Estrela de Oswald entra mais na neutralizacao final. Em cobertura de brancos, o principal e usar base natural para ancoragem da cor.',
                naturalReference: 'base natural da mesma altura do tom desejado',
                fantasyReference: 'nuance desejada em apoio, sem retirar a base natural da formula',
                oxHint: '20 volumes para cobertura mais consistente de brancos.',
                bleachingTarget: 'nao se aplica, salvo correcao previa',
                caution:
                    'Para alta porcentagem de brancos, mantenha a base natural sempre presente na formula para evitar transparencia.'
            };
        }

        if (
            ['castanho', 'chocolate', 'escurecer', 'frio', 'marrom'].some((keyword) =>
                normalizedTarget.includes(keyword)
            )
        ) {
            return {
                label: 'castanho de profundidade fria ou neutra',
                expectedBackground: 'laranja ou vermelho, dependendo da base',
                oswaldGuidance:
                    'Na Estrela de Oswald, azul neutraliza laranja e verde neutraliza vermelho. Para fechar em castanho frio, controle o calor com reflexos frios sem anular demais a profundidade.',
                naturalReference: 'base natural na altura final desejada',
                fantasyReference: 'nuance fria, como acinzentada ou mate, em apoio ao castanho',
                oxHint: '10 a 20 volumes para deposito e escurecimento seguro.',
                bleachingTarget: 'na maioria dos casos nao precisa abrir; apenas equalizar fundo',
                caution:
                    'Se o cabelo estiver muito claro e poroso, faca pre-pigmentacao antes do escurecimento para evitar manchas.'
            };
        }

        return {
            label: `resultado personalizado saindo de ${baseColor}`,
            expectedBackground: 'fundo de clareamento compativel com o nivel desejado',
            oswaldGuidance:
                'Use a Estrela de Oswald assim: amarelo neutraliza com violeta, laranja com azul e vermelho com verde. Preserve ou neutralize o fundo conforme o efeito final.',
            naturalReference: 'base natural no nivel que vai sustentar a cor final',
            fantasyReference: 'nuance fantasia ou reflexo que represente o efeito desejado',
            oxHint: '10 a 20 volumes para deposito e 20 a 30 volumes quando houver abertura controlada.',
            bleachingTarget: 'clareamento uniforme antes da matizacao ou coloracao final',
            caution: 'Cheque historico quimico e elasticidade antes de elevar muito a altura de tom.'
        };
    }

    function buildTechniqueSteps(technique, profile) {
        if (technique === 'descoloracao global') {
            return [
                'Faca anamnese, teste de mecha e teste de elasticidade antes de iniciar.',
                'Divida o cabelo em quatro quadrantes para manter aplicacao limpa e uniforme.',
                'Aplique o descolorante primeiro em comprimento e pontas se a raiz estiver mais quente ou virgem, deixando a raiz por ultimo quando necessario.',
                `Monitore o fundo de clareamento ate chegar em ${profile.bleachingTarget}.`,
                'Enxague, reequilibre o pH, seque cerca de 80% e so depois aplique a formula de coloracao ou tonalizacao.'
            ];
        }

        if (technique === 'mechas') {
            return [
                'Faca teste de mecha e separe o cabelo em quadrantes organizados.',
                'Selecione mechas finas ou medias conforme o efeito desejado e isole com papel ou manta.',
                'Sature bem o descolorante para evitar manchas e acompanhe a abertura mecha por mecha.',
                `Pare o clareamento quando o fundo atingir ${profile.bleachingTarget}.`,
                'Enxague, trate e tonalize usando a formula final para alinhar reflexo e brilho.'
            ];
        }

        if (technique === 'balayage') {
            return [
                'Faca diagnostico de fundo e porosidade antes das pinceladas.',
                'Divida o cabelo em diagonais e aplique em formato de V ou W para um degrade suave.',
                'Concentre saturacao nas areas que precisam mais luz e esfume a raiz para manter profundidade.',
                `Controle o clareamento ate chegar em ${profile.bleachingTarget}.`,
                'Depois do enxague, faca tonalizacao de raiz e comprimento para acabamento mais profissional.'
            ];
        }

        if (technique === 'correcao de cor') {
            return [
                'Mapeie manchas, fundos diferentes e historico de coloracoes anteriores.',
                'Se houver excesso de pigmento artificial, considere limpeza de cor ou decapagem controlada antes de clarear.',
                'Equalize porosidade antes de aplicar nova quimica para evitar sobrecarga em areas frageis.',
                `Somente depois avance ate ${profile.bleachingTarget} ou para o nivel compativel com o objetivo.`,
                'Finalize com formula corretiva e acompanhe o resultado mecha por mecha.'
            ];
        }

        if (technique === 'retoque de raiz') {
            return [
                'Isole apenas o crescimento novo para nao sobrepor quimica onde ja existe clareamento.',
                'Aplique com precisao na raiz, respeitando a largura do crescimento.',
                'Monitore a abertura ate igualar com comprimento e pontas.',
                'Se precisar, emulsione rapidamente para unificar reflexo sem sensibilizar o restante.',
                'Finalize com tonalizacao ou coloracao de alinhamento.'
            ];
        }

        return [
            'Faca teste de mecha, porosidade e compatibilidade antes da aplicacao.',
            'Equalize a fibra com tratamento rapido para a cor assentar de forma mais uniforme.',
            'Aplique a formula da raiz para o comprimento respeitando o tempo de pausa da marca.',
            'Emulsione nos minutos finais para uniformizar reflexo e brilho.',
            'Enxague, sele cuticulas e finalize com mascara pos-coloracao.'
        ];
    }

    function buildWaterPlan(waterTest) {
        if (waterTest === 'boia') {
            return [
                'Diagnostico: baixa porosidade. O fio resiste a absorver agua e produto.',
                'Hidratacao: 1 vez por semana com mascaras leves e um pouco de calor umido para melhor penetracao.',
                'Nutricao: a cada 15 dias com oleos leves, evitando excesso para nao pesar.',
                'Reconstrucao: a cada 30 dias ou apenas quando houver quimica mais forte.'
            ];
        }

        if (waterTest === 'meio') {
            return [
                'Diagnostico: porosidade equilibrada. O fio costuma responder bem aos processos.',
                'Hidratacao: 1 vez por semana para manter maleabilidade e brilho.',
                'Nutricao: a cada 15 dias para segurar emoliencia e controle de frizz.',
                'Reconstrucao: a cada 20 a 30 dias, especialmente apos descoloracao.'
            ];
        }

        return [
            'Diagnostico: alta porosidade. O fio absorve rapido, mas perde agua e pigmento com facilidade.',
            'Hidratacao: 1 a 2 vezes por semana com ativos umectantes e selagem no enxague.',
            'Nutricao: semanal para repor lipideos e reduzir aspereza.',
            'Reconstrucao: a cada 10 a 15 dias, com cautela para nao enrijecer demais a fibra.'
        ];
    }

    function buildNumberingSection(formulaProfile) {
        return [
            'Numero antes do ponto: altura de tom da cor, na escala natural de 1 a 10.',
            `Altura de tom sugerida: ${formulaProfile.naturalTone} (${formulaProfile.naturalLabel}).`,
            'Numero apos o ponto: reflexo ou nuance secundaria da formula.',
            `Reflexo sugerido: ${formulaProfile.fantasyTone} (${formulaProfile.fantasyLabel}).`,
            `Leitura final do codigo aproximado: ${formulaProfile.approximateResult}.`
        ];
    }

    function buildChemistrySection(profile, formulaProfile) {
        const naturalGrams = defaultFormulaPartGrams;
        const fantasyGrams = defaultFormulaPartGrams;
        const resultGrams = naturalGrams + fantasyGrams;
        const oxidantGrams = resultGrams * 1.5;

        return [
            'Creme colorante alcalino: a amonia ou agente similar abre a cuticula para a entrada dos precursores de cor.',
            `Formula em gramas: ${naturalGrams} g do tom natural ${formulaProfile.naturalTone} + ${fantasyGrams} g da nuance ${formulaProfile.fantasyTone} = ${resultGrams} g de coloracao.`,
            `OX pela leitura da elevacao: ${formulaProfile.oxidantVolume} volumes. ${formulaProfile.oxidantAction}`,
            `Pela regra do projeto, OX = 1,5 vezes o total da coloracao (proporcao 1:1,5): ${resultGrams} x 1.5 = ${oxidantGrams} g de oxidante.`,
            formulaReferenceGuidance,
            `Leitura tecnica complementar: ${profile.oxHint}`
        ];
    }

    function buildColorimetrySection(profile, formulaProfile) {
        return [
            `Formula da cor: ${formulaProfile.naturalTone} + ${formulaProfile.fantasyTone} = ${formulaProfile.approximateResult}.`,
            `Cor desejada aproximada: ${formulaProfile.approximateResult}.`,
            `Fundo esperado: ${profile.expectedBackground}.`,
            `Neutralizacao ou preservacao: ${profile.oswaldGuidance}`,
            `Leitura do reflexo ${formulaProfile.fantasyTone}: ${fantasyToneGuidance[formulaProfile.fantasyTone] || 'Use a nuance para aquecer ou esfriar conforme o fundo.'}`,
            'Mistura de tons: quando dois tons com o mesmo reflexo sao usados, o resultado pode caminhar para um intermediario. Ex.: 7.1 + 9.1 = 8.1.',
            `Regra do 11 para mix ou matizador: 11 - ${formulaProfile.naturalTone} = ${formulaProfile.mixRule11Amount}. Isso indica ate ${formulaProfile.mixRule11Amount} cm de corretor quando houver necessidade tecnica de neutralizacao.`
        ];
    }

    function buildMechanismSection(formulaProfile) {
        return [
            'Abertura: o alcalinizante eleva o pH e abre as cuticulas.',
            `Oxidacao ou clareamento: a OX de ${formulaProfile.oxidantVolume} volumes libera oxigenio e atua no cortex.`,
            'Deposito: os pigmentos artificiais entram no cortex e se oxidam para formar a nova cor.',
            'Selagem: apos enxague e tratamento de pH mais baixo, a fibra tende a reter melhor a cor.'
        ];
    }

    function buildProtocolResponse(currentContext) {
        const profile = getGoalProfile(currentContext.targetColor, currentContext.baseColor);
        const formulaProfile = buildFormulaProfile(
            currentContext.targetColor,
            currentContext.baseColor
        );
        const techniqueSteps = buildTechniqueSteps(currentContext.technique, profile);
        const waterPlan = buildWaterPlan(currentContext.waterTest);
        const numberingLines = buildNumberingSection(formulaProfile);
        const chemistryLines = buildChemistrySection(profile, formulaProfile);
        const colorimetryLines = buildColorimetrySection(profile, formulaProfile);
        const mechanismLines = buildMechanismSection(formulaProfile);
        const lines = [
            'Protocolo tecnico sugerido',
            '',
            'Diagnostico',
            `- Base atual: ${currentContext.baseColor}`,
            `- Objetivo final: ${currentContext.targetColor}`,
            `- Tecnica escolhida: ${currentContext.technique}`,
            `- Teste da agua: ${describeWaterTest(currentContext.waterTest)}`,
            '',
            'Passo a passo profissional'
        ];

        techniqueSteps.forEach((step, index) => {
            lines.push(`${index + 1}. ${step}`);
        });

        lines.push('');
        lines.push('Leitura da numeracao');
        numberingLines.forEach((line) => {
            lines.push(`- ${line}`);
        });
        lines.push('');
        lines.push('Quimica da formula');
        chemistryLines.forEach((line) => {
            lines.push(`- ${line}`);
        });
        lines.push('');
        lines.push('Leitura pela Estrela de Oswald');
        colorimetryLines.forEach((line) => {
            lines.push(`- ${line}`);
        });
        lines.push('');
        lines.push('Mecanismo de acao');
        mechanismLines.forEach((line) => {
            lines.push(`- ${line}`);
        });

        lines.push('');
        lines.push('Hidratacao e cronograma pelo teste da agua');
        waterPlan.forEach((line) => {
            lines.push(`- ${line}`);
        });

        lines.push('');
        lines.push('Observacao profissional');
        lines.push(`- ${profile.caution}`);

        if (
            currentContext.baseColor === 'preto' &&
            ['loiro', 'platin', 'clarear'].some((keyword) =>
                normalizeText(currentContext.targetColor).includes(keyword)
            )
        ) {
            lines.push(
                '- Em base preta, a subida para loiro costuma exigir mais de uma etapa e muito controle de fundo para preservar integridade.'
            );
        }

        lines.push('');
        lines.push(
            'Se quiser montar outro protocolo, clique em Reiniciar ou digite reiniciar.'
        );
        return lines.join('\n');
    }

    function processLocalInput(text, currentContext) {
        const userText = text.trim();
        const normalizedText = normalizeText(userText);

        if (normalizedText.includes('reiniciar')) {
            return {
                response: initialPrompt,
                context: createInitialContext(),
                restart: true
            };
        }

        if (currentContext.step === 0) {
            const baseColor = detectBaseColor(userText);

            if (!baseColor) {
                return {
                    response:
                        'Nao consegui identificar a cor base. Tente responder com algo como preto, castanho, loiro, ruivo ou grisalho.',
                    context: currentContext,
                    restart: false
                };
            }

            return {
                response: `Entendi. Sua base atual e ${baseColor}. Agora me diga o objetivo final. Exemplos: loiro platinado, ruivo cobre, marsala, cobertura de brancos, castanho frio ou matizacao.`,
                context: {
                    step: 1,
                    baseColor,
                    targetColor: '',
                    technique: '',
                    waterTest: ''
                },
                restart: false
            };
        }

        if (currentContext.step === 1) {
            return {
                response:
                    `Objetivo registrado: ${userText}. Agora diga qual tecnica o profissional vai usar. Exemplos: descoloracao global, mechas, balayage, correcao de cor, retoque de raiz ou coloracao sem descolorir.`,
                context: {
                    step: 2,
                    baseColor: currentContext.baseColor,
                    targetColor: userText,
                    technique: '',
                    waterTest: ''
                },
                restart: false
            };
        }

        if (currentContext.step === 2) {
            const technique = detectTechnique(userText);

            if (!technique) {
                return {
                    response:
                        'Nao consegui identificar a tecnica. Responda com uma destas opcoes: descoloracao global, mechas, balayage, correcao de cor, retoque de raiz ou coloracao sem descolorir.',
                    context: currentContext,
                    restart: false
                };
            }

            return {
                response: `Perfeito. Tecnica escolhida: ${technique}. Agora me diga o resultado do teste da agua. Responda com boia, meio ou afunda.`,
                context: {
                    step: 3,
                    baseColor: currentContext.baseColor,
                    targetColor: currentContext.targetColor,
                    technique,
                    waterTest: ''
                },
                restart: false
            };
        }

        if (currentContext.step === 3) {
            const waterTest = detectWaterTest(userText);

            if (!waterTest) {
                return {
                    response:
                        'Nao entendi o resultado do teste da agua. Responda com boia, meio ou afunda.',
                    context: currentContext,
                    restart: false
                };
            }

            const nextContext = {
                step: 4,
                baseColor: currentContext.baseColor,
                targetColor: currentContext.targetColor,
                technique: currentContext.technique,
                waterTest
            };

            return {
                response: buildProtocolResponse(nextContext),
                context: nextContext,
                restart: false
            };
        }

        return {
            response:
                'Ja concluimos esse protocolo. Se quiser montar outro processo, clique em Reiniciar ou digite reiniciar.',
            context: currentContext,
            restart: false
        };
    }

    function getConnectionErrorMessage() {
        return `Nao consegui conectar ao servidor em ${apiOrigin}. Execute "python app.py" nesta pasta e abra http://127.0.0.1:8000.`;
    }

    function addMessage(text, sender) {
        const message = document.createElement('div');
        message.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        message.textContent = text;
        chatWindow.appendChild(message);
        scrollToBottom();
    }

    function clearMessages() {
        chatWindow.innerHTML = '';
    }

    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        chatWindow.appendChild(indicator);
        scrollToBottom();
        return indicator;
    }

    function removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.remove();
        }
    }

    function setNotice(message, variant) {
        if (!message) {
            noticeBox.textContent = '';
            noticeBox.className = 'notice hidden';
            return;
        }

        noticeBox.textContent = message;
        noticeBox.className = `notice notice-${variant}`;
    }

    function setStatus(mode) {
        interactionMode = mode;
        statusBadge.className = `status-badge status-${mode}`;

        if (mode === 'online') {
            statusBadge.textContent = 'Servidor online';
            return;
        }

        if (mode === 'local') {
            statusBadge.textContent = 'Modo local';
            return;
        }

        statusBadge.textContent = 'Conectando';
    }

    function setFormEnabled(enabled) {
        userInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        restartBtn.disabled = !enabled;
    }

    function updateStepper(step) {
        if (!stepper) return;
        const steps = stepper.querySelectorAll('.step');
        steps.forEach((el) => {
            el.classList.remove('active', 'completed');
            const stepNum = Number.parseInt(el.getAttribute('data-step') || '0', 10);
            if (stepNum < step) {
                el.classList.add('completed');
            } else if (stepNum === step) {
                el.classList.add('active');
            }
        });
    }

    function renderChips(step) {
        if (!chipsContainer) return;
        chipsContainer.innerHTML = '';
        let options = [];

        if (step === 0) {
            options = [
                { label: 'Preto', value: 'Preto' },
                { label: 'Castanho', value: 'Castanho' },
                { label: 'Loiro', value: 'Loiro' },
                { label: 'Ruivo', value: 'Ruivo' },
                { label: 'Grisalho', value: 'Grisalho' }
            ];
        } else if (step === 1) {
            options = [
                { label: 'Loiro Platinado', value: 'Loiro platinado' },
                { label: 'Ruivo Cobre', value: 'Ruivo cobre' },
                { label: 'Marsala', value: 'Marsala' },
                { label: 'Castanho Frio', value: 'Castanho frio' },
                { label: 'Cobertura de Brancos', value: 'Cobertura de brancos' }
            ];
        } else if (step === 2) {
            options = [
                { label: 'Descoloração Global', value: 'Descoloração global' },
                { label: 'Mechas', value: 'Mechas' },
                { label: 'Balayage', value: 'Balayage' },
                { label: 'Retoque de Raiz', value: 'Retoque de raiz' },
                { label: 'Coloração sem Descolorir', value: 'Coloração sem descolorir' },
                { label: 'Correção de Cor', value: 'Correção de cor' }
            ];
        } else if (step === 3) {
            options = [
                { label: 'Boia (Baixa Porosidade)', value: 'Boia' },
                { label: 'Meio (Porosidade Equilibrada)', value: 'Meio' },
                { label: 'Afunda (Alta Porosidade)', value: 'Afunda' }
            ];
        }

        if (options.length > 0 && !isRequestInFlight) {
            options.forEach(opt => {
                const chipEl = document.createElement('button');
                chipEl.className = 'chip';
                chipEl.type = 'button';
                chipEl.textContent = opt.label;
                chipEl.addEventListener('click', () => {
                    if (isRequestInFlight) return;
                    addMessage(opt.value, 'user');
                    processInput(opt.value);
                });
                chipsContainer.appendChild(chipEl);
            });
            chipsContainer.classList.remove('hidden');
        } else {
            chipsContainer.classList.add('hidden');
        }
    }

    function updateDashboard() {
        if (!dashboardPlaceholder || !dashboardContent) return;

        if (!context.baseColor) {
            dashboardPlaceholder.classList.remove('hidden');
            dashboardContent.classList.add('hidden');
            return;
        }

        dashboardPlaceholder.classList.add('hidden');
        dashboardContent.classList.remove('hidden');

        // Badges do diagnóstico
        if (valBaseColor) valBaseColor.textContent = context.baseColor || '-';
        if (valTargetColor) valTargetColor.textContent = context.targetColor || '-';
        if (valTechnique) valTechnique.textContent = context.technique || '-';
        if (valPorosity) valPorosity.textContent = context.waterTest ? describeWaterTest(context.waterTest) : '-';

        // Cartões
        const cardFormula = document.querySelector('.card-formula');
        const cardOswald = document.querySelector('.card-oswald');
        const cardSteps = document.querySelector('.card-steps');
        const cardSchedule = document.querySelector('.card-schedule');
        const cardCaution = document.querySelector('.card-caution');

        // Fórmula e Oswald
        if (context.targetColor) {
            if (cardFormula) cardFormula.classList.remove('hidden');
            if (cardOswald) cardOswald.classList.remove('hidden');

            const profile = getGoalProfile(context.targetColor, context.baseColor);
            const formulaProfile = buildFormulaProfile(context.targetColor, context.baseColor);

            if (valNaturalTone) valNaturalTone.textContent = formulaProfile.naturalTone;
            if (valNaturalToneRule) valNaturalToneRule.textContent = formulaProfile.naturalTone;
            if (valFantasyTone) valFantasyTone.textContent = formulaProfile.fantasyTone;
            if (valResultTone) valResultTone.textContent = formulaProfile.approximateResult;
            
            if (valOxVolume) valOxVolume.textContent = formulaProfile.oxidantVolume;
            if (valOxGrams) valOxGrams.textContent = (30 + 30) * 1.5;
            if (valOxAction) valOxAction.textContent = formulaProfile.oxidantAction;

            if (valOswaldGuidance) valOswaldGuidance.textContent = profile.oswaldGuidance;
            if (valMixCm) valMixCm.textContent = formulaProfile.mixRule11Amount;
            if (valMixCmDesc) valMixCmDesc.textContent = formulaProfile.mixRule11Amount;
        } else {
            if (cardFormula) cardFormula.classList.add('hidden');
            if (cardOswald) cardOswald.classList.add('hidden');
        }

        // Passo a Passo da Técnica
        if (context.technique) {
            if (cardSteps) cardSteps.classList.remove('hidden');
            const profile = getGoalProfile(context.targetColor, context.baseColor);
            const steps = buildTechniqueSteps(context.technique, profile);
            
            if (valStepsList) {
                valStepsList.innerHTML = '';
                steps.forEach(stepText => {
                    const li = document.createElement('li');
                    li.textContent = stepText;
                    valStepsList.appendChild(li);
                });
            }
        } else {
            if (cardSteps) cardSteps.classList.add('hidden');
        }

        // Cronograma e Precaução
        if (context.waterTest) {
            if (cardSchedule) cardSchedule.classList.remove('hidden');
            if (cardCaution) cardCaution.classList.remove('hidden');

            let hydrationFreq = '', nutritionFreq = '', reconstructionFreq = '';
            let hydrationFill = '0%', nutritionFill = '0%', reconstructionFill = '0%';

            if (context.waterTest === 'boia') {
                hydrationFreq = '1x / semana';
                hydrationFill = '60%';
                nutritionFreq = 'A cada 15 dias';
                nutritionFill = '40%';
                reconstructionFreq = 'A cada 30 dias';
                reconstructionFill = '20%';
            } else if (context.waterTest === 'meio') {
                hydrationFreq = '1x / semana';
                hydrationFill = '60%';
                nutritionFreq = 'A cada 15 dias';
                nutritionFill = '40%';
                reconstructionFreq = 'A cada 20 a 30 dias';
                reconstructionFill = '30%';
            } else if (context.waterTest === 'afunda') {
                hydrationFreq = '1 a 2x / semana';
                hydrationFill = '90%';
                nutritionFreq = 'Semanal';
                nutritionFill = '80%';
                reconstructionFreq = 'A cada 10 a 15 dias';
                reconstructionFill = '70%';
            }

            if (valHydrationFreq) valHydrationFreq.textContent = hydrationFreq;
            if (barHydration) barHydration.style.width = hydrationFill;

            if (valNutritionFreq) valNutritionFreq.textContent = nutritionFreq;
            if (barNutrition) barNutrition.style.width = nutritionFill;

            if (valReconstructionFreq) valReconstructionFreq.textContent = reconstructionFreq;
            if (barReconstruction) barReconstruction.style.width = reconstructionFill;

            const profile = getGoalProfile(context.targetColor, context.baseColor);
            let cautionText = profile.caution;
            if (context.baseColor === 'preto' && 
                ['loiro', 'platin', 'clarear'].some(kw => normalizeText(context.targetColor).includes(kw))) {
                cautionText += ' Em base preta, a subida para loiro costuma exigir mais de uma etapa e muito controle de fundo para preservar integridade.';
            }
            if (valCaution) valCaution.textContent = cautionText;
        } else {
            if (cardSchedule) cardSchedule.classList.add('hidden');
            if (cardCaution) cardCaution.classList.add('hidden');
        }
    }

    function updateUI() {
        updateStepper(context.step);
        renderChips(context.step);
        updateDashboard();
    }

    function restartConversation() {
        context = createInitialContext();
        clearMessages();
        addMessage(initialPrompt, 'bot');
        userInput.value = '';
        userInput.focus();
        updateUI();
    }

    function buildError(message, isConnectionError) {
        const error = new Error(message);
        error.isConnectionError = Boolean(isConnectionError);
        return error;
    }

    async function fetchJson(path, options = {}) {
        let response;

        try {
            response = await fetch(buildApiUrl(path), options);
        } catch (error) {
            throw buildError(getConnectionErrorMessage(), true);
        }

        const contentType = response.headers.get('Content-Type') || '';
        if (!contentType.includes('application/json')) {
            throw buildError('O servidor respondeu em um formato invalido.', true);
        }

        const payload = await response.json();

        if (!response.ok) {
            throw buildError(payload.error || 'Nao foi possivel concluir a requisicao.', false);
        }

        return payload;
    }

    async function requestHealth() {
        return fetchJson('/api/health');
    }

    async function requestBotResponse(text) {
        return fetchJson('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                context
            })
        });
    }

    async function requestResponse(text) {
        if (!isServerOnline) {
            return processLocalInput(text, context);
        }

        return requestBotResponse(text);
    }

    async function bootstrap(resetConversation) {
        setStatus('connecting');
        setFormEnabled(false);
        retryBtn.disabled = true;

        try {
            const health = await requestHealth();
            isServerOnline = true;
            initialPrompt = typeof health.initialPrompt === 'string' ? health.initialPrompt : fallbackPrompt;

            setStatus('online');
            setNotice('', 'info');
            retryBtn.disabled = false;
            setFormEnabled(true);

            if (resetConversation) {
                restartConversation();
            } else {
                userInput.focus();
                updateUI();
            }
        } catch (error) {
            isServerOnline = false;
            setStatus('local');
            setFormEnabled(true);
            retryBtn.disabled = false;
            setNotice(
                'Conectado no Modo Local (Offline). Você pode usar o assistente normalmente!',
                'info'
            );

            if (resetConversation) {
                restartConversation();
            } else {
                userInput.focus();
                updateUI();
            }
        }
    }

    async function processInput(text) {
        const indicator = showTypingIndicator();
        isRequestInFlight = true;
        setFormEnabled(false);
        retryBtn.disabled = true;

        try {
            const payload = await requestResponse(text);
            context = payload.context || createInitialContext();
            removeTypingIndicator(indicator);
            addMessage(payload.response, 'bot');

            if (payload.restart) {
                context = createInitialContext();
            }

            setNotice('', 'info');
        } catch (error) {
            removeTypingIndicator(indicator);

            if (error.isConnectionError) {
                isServerOnline = false;
                setStatus('local');

                const fallbackPayload = processLocalInput(text, context);
                context = fallbackPayload.context || createInitialContext();
                addMessage(fallbackPayload.response, 'bot');

                if (fallbackPayload.restart) {
                    context = createInitialContext();
                }

                setNotice(
                    'Modo Local ativado automaticamente para garantir o funcionamento.',
                    'info'
                );
            } else {
                addMessage(error.message, 'bot');
                setNotice(error.message, 'error');
            }
        } finally {
            isRequestInFlight = false;
            retryBtn.disabled = false;
            setFormEnabled(true);
            updateUI();

            if (interactionMode !== 'connecting') {
                userInput.focus();
            }
        }
    }

    function handleSend() {
        const text = userInput.value.trim();

        if (!text || isRequestInFlight) {
            return;
        }

        addMessage(text, 'user');
        userInput.value = '';
        processInput(text);
    }

    sendBtn.addEventListener('click', handleSend);
    retryBtn.addEventListener('click', () => {
        bootstrap(true);
    });
    restartBtn.addEventListener('click', () => {
        restartConversation();
        setNotice('', 'info');
    });
    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSend();
        }
    });

    if (tabChatBtn && tabProtocolBtn) {
        tabChatBtn.addEventListener('click', () => {
            tabChatBtn.classList.add('active');
            tabProtocolBtn.classList.remove('active');
            chatColumn.classList.remove('hidden-tab');
            protocolColumn.classList.remove('active-tab');
        });

        tabProtocolBtn.addEventListener('click', () => {
            tabProtocolBtn.classList.add('active');
            tabChatBtn.classList.remove('active');
            chatColumn.classList.add('hidden-tab');
            protocolColumn.classList.add('active-tab');
        });
    }

    bootstrap(true);
});
