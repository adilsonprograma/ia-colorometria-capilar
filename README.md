# ColorIA

ColorIA e um assistente local para apoio em colorimetria capilar. O projeto roda com backend em Python e interface web simples, e monta um protocolo tecnico com:

- leitura da base atual do cabelo
- objetivo final da cor
- tecnica escolhida pelo profissional
- orientacao pela Estrela de Oswald
- sugestao de descoloracao ou deposito de cor
- calculo de formula com base natural, cor fantasia e oxidante conforme a regra do projeto
- orientacao de hidratacao com base no teste da agua

## Objetivo do projeto

O app foi pensado para servir como apoio rapido durante simulacoes tecnicas de colorimetria. Ele nao substitui avaliacao profissional presencial, teste de mecha, anamnese ou leitura real da fibra, mas ajuda a organizar um protocolo coerente para estudo, demonstracao e consulta inicial.

## Principais recursos

- servidor HTTP local sem dependencias externas
- interface web com chat guiado
- API simples em JSON
- modo local no frontend caso o servidor nao esteja acessivel
- fluxo em etapas para gerar um protocolo final completo
- testes automatizados para backend e logica de conversa

## Requisitos

- Python 3.10 ou superior
- navegador web moderno

Nao e necessario instalar frameworks web, porque o projeto usa apenas bibliotecas padrao do Python.

## Inicio rapido

Na pasta do projeto, execute:

```bash
python app.py
```

Depois abra:

```text

http://127.0.0.1:8000
```

No Windows, voce tambem pode usar:

```text
start_coloria.bat
```

Esse atalho inicia o servidor e tenta abrir o navegador automaticamente.

## Como usar o assistente

O fluxo principal do app acontece em 4 etapas:

1. informar a cor base ou altura atual do cabelo
2. informar o resultado desejado
3. informar a tecnica escolhida pelo profissional
4. informar o resultado do teste da agua: `boia`, `meio` ou `afunda`

Depois disso, o sistema entrega um protocolo com:

- diagnostico resumido
- passo a passo tecnico da tecnica escolhida
- leitura pela Estrela de Oswald
- fundo esperado de clareamento
- calculo da formula
- recomendacao de oxidante
- cronograma de hidratacao, nutricao e reconstrucao
- observacao tecnica de seguranca

## Exemplo de conversa

Exemplo de sequencia:

1. `preto`
2. `loiro platinado`
3. `descoloracao global`
4. `afunda`

Resultado esperado:

- protocolo de descoloracao global
- observacao de subida de fundo para loiro
- neutralizacao por violeta ou azul/violeta segundo a Estrela de Oswald
- formula com tom natural, nuance fantasia e resultado aproximado da cor
- cronograma para alta porosidade

## Formula usada no protocolo

O app segue a regra solicitada no projeto:

O app combina:

- tom natural de `1` a `10`
- cor fantasia de `0.11` a `0.6`
- oxidante em metade do total da coloracao
- leitura de numeracao, quimica da formula, colorimetria e mecanismo de acao

```text
tom natural + cor fantasia = cor desejada aproximada
OX = metade do total da coloracao
```

Exemplo pratico:

```text
10 + 0.11 = 10.11
30 g do tom natural 10 + 30 g da nuance 0.11 = 60 g de coloracao
60 / 2 = 30 g de oxidante
```

Importante:

- esse calculo e uma regra de referencia usada no projeto
- a proporcao final sempre deve ser validada com a marca e a linha profissional utilizada
- cada fabricante pode exigir proporcao, volumagem e pausa diferentes

O protocolo final agora explica:

- numero antes do ponto como altura de tom
- numero apos o ponto como reflexo ou nuance
- escolha da OX por elevacao aproximada de tons
- neutralizacao pela Estrela de Oswald
- regra do 11 para mix ou matizador
- abertura, oxidacao, deposito e selagem da cor

## Tecnicas reconhecidas

Hoje o assistente reconhece principalmente estas tecnicas:

- `descoloracao global`
- `mechas`
- `balayage`
- `correcao de cor`
- `retoque de raiz`
- `coloracao sem descolorir`

Palavras relacionadas, como `luzes`, `papel`, `decapagem`, `tonalizacao` e `matizacao`, tambem sao aceitas em varios casos.

## Resultados do teste da agua

O sistema entende tres resultados:

- `boia`: baixa porosidade
- `meio`: porosidade equilibrada
- `afunda`: alta porosidade

Com base nisso, ele sugere frequencia de:

- hidratacao
- nutricao
- reconstrucao

## Modos de funcionamento

O projeto pode operar de duas formas:

### 1. Modo com servidor

Quando `python app.py` esta rodando e a pagina e aberta em `http://127.0.0.1:8000`, a interface usa a API HTTP normalmente.

### 2. Modo local do frontend

Se o navegador nao conseguir falar com o backend, a interface entra em `Modo local`. Nesse caso:

- o app continua funcionando
- a conversa e processada no JavaScript
- o usuario nao fica travado por erro de conexao

Mesmo assim, o modo recomendado continua sendo o servidor local, porque ele centraliza a logica e deixa a manutencao mais confiavel.

## Estrutura do projeto

```text
app.py               servidor HTTP e rotas da API
chat_logic.py        logica da conversa e montagem do protocolo
index.html           estrutura da interface
style.css            estilos da interface
index.js             fluxo do chat no frontend e modo local
test_app.py          testes do servidor e da API
test_chat_logic.py   testes da logica de colorimetria
start_coloria.bat    atalho para iniciar no Windows
README.md            documentacao do projeto
```

## Arquitetura resumida

### Backend

O backend fica em `app.py` e faz tres coisas principais:

- serve os arquivos estaticos do frontend
- responde o health check em `/api/health`
- recebe mensagens em `/api/chat`

### Motor de conversa

O motor fica em `chat_logic.py` e controla:

- estado da conversa
- reconhecimento de cor base
- reconhecimento da tecnica
- reconhecimento do teste da agua
- perfil do objetivo final
- montagem do protocolo tecnico

### Frontend

O frontend fica em `index.html`, `style.css` e `index.js` e cuida de:

- renderizar a conversa
- enviar requisicoes para a API
- mostrar status do servidor
- ativar modo local se o backend falhar

## API HTTP

### `GET /api/health`

Usado para validar se o servidor esta online.

Exemplo de resposta:

```json
{
  "status": "ok",
  "appName": "ColorIA",
  "initialPrompt": "Ola! Sou a ColorIA..."
}
```

### `POST /api/chat`

Recebe a mensagem atual do usuario e o contexto da conversa.

Exemplo de requisicao:

```json
{
  "message": "descoloracao global",
  "context": {
    "step": 2,
    "baseColor": "preto",
    "targetColor": "loiro platinado",
    "technique": "",
    "waterTest": ""
  }
}
```

Exemplo de resposta:

```json
{
  "response": "Perfeito. Tecnica escolhida: descoloracao global...",
  "context": {
    "step": 3,
    "baseColor": "preto",
    "targetColor": "loiro platinado",
    "technique": "descoloracao global",
    "waterTest": ""
  },
  "restart": false
}
```

## Estado da conversa

O campo `context` usa esta estrutura:

```json
{
  "step": 0,
  "baseColor": "",
  "targetColor": "",
  "technique": "",
  "waterTest": ""
}
```

Significado:

- `step`: etapa atual do fluxo
- `baseColor`: cor base reconhecida
- `targetColor`: objetivo informado pelo usuario
- `technique`: tecnica escolhida
- `waterTest`: resultado do teste da agua

## Testes

Para rodar a suite de testes:

```bash
python -m unittest -v
```

Os testes atuais cobrem:

- carregamento da pagina principal
- health check da API
- chamada de chat em JSON
- deteccao de cor base
- deteccao de tecnica
- deteccao do teste da agua
- geracao do protocolo final

## Solucao de problemas

### O navegador mostra "Servidor offline" ou "Modo local"

Verifique:

- se `python app.py` esta rodando na pasta correta
- se voce abriu `http://127.0.0.1:8000`
- se a porta `8000` nao esta ocupada por outro processo

Se o servidor nao estiver disponivel, a interface continua funcionando em modo local.

### A porta 8000 esta ocupada

Voce pode iniciar em outra porta:

```bash
python app.py --port 8010
```

Se fizer isso, abra a mesma porta no navegador:

```text
http://127.0.0.1:8010
```

### O backend responde, mas o fluxo nao ficou como esperado

Verifique:

- se a base foi escrita com termos reconhecidos, como `preto`, `castanho`, `loiro`, `ruivo` ou `grisalho`
- se a tecnica foi escrita com termos aceitos, como `mechas`, `balayage` ou `descoloracao global`
- se o teste da agua foi informado como `boia`, `meio` ou `afunda`

### O calculo nao bate com a marca que eu uso

Isso pode acontecer. O app segue a regra definida no projeto, mas a formula real deve respeitar:

- a proporcao da marca
- a linha profissional utilizada
- a volumagem recomendada pelo fabricante
- a avaliacao real da fibra

## Limites e cuidados

- o projeto tem foco educacional e consultivo
- ele nao substitui teste de mecha
- ele nao substitui diagnostico presencial
- ele nao mede elasticidade, historico quimico ou resistencia real da fibra
- qualquer procedimento quimico deve ser ajustado pelo profissional responsavel

## Como evoluir o projeto

Alguns pontos naturais de evolucao:

- adicionar mais perfis de objetivo em `chat_logic.py`
- expandir tecnicas reconhecidas
- ajustar formulas por marca profissional
- salvar historico de atendimentos
- exportar o protocolo final em PDF
- criar painel com campos estruturados alem do chat

## Manutencao rapida

Se voce quiser alterar a inteligencia do protocolo, os pontos mais importantes sao:

- `get_goal_profile()` em `chat_logic.py`
- `build_technique_steps()` em `chat_logic.py`
- `build_water_plan()` em `chat_logic.py`
- `build_protocol_response()` em `chat_logic.py`

Se quiser alterar comportamento da interface:

- `index.js` para fluxo e estados
- `index.html` para estrutura
- `style.css` para visual

## Licenca e uso

Se este projeto for usado em ambiente profissional, o ideal e manter um aviso claro de que as respostas sao sugestoes tecnicas e devem ser conferidas por um colorista antes da aplicacao real.
# ia-colorometria-capilar
# ia-colorometria-capilar
