# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Site institucional do **Hotel Dominguez Plaza** (Nova Friburgo/RJ), em construção. O projeto é uma cópia do template-modelo de pousada da Komplexa Hotéis (base da Pousada fictícia "Vale das Araucárias") que está sendo adaptado para o cliente real. HTML5, CSS3 e JavaScript vanilla — sem build, sem framework, sem `package.json`, sem testes. Português do Brasil em todo o conteúdo.

**Estado atual:** o código ainda contém a identidade fictícia da Pousada Vale das Araucárias (Campos do Pinhão/RS). A adaptação para o Dominguez Plaza ainda não começou — `hotel-config.json`, os HTMLs e as constantes de `main.js` precisam ser reescritos com os dados reais (ver seção "Contexto do cliente" abaixo). As fotos reais já estão disponíveis em `Fotos/` e vídeos em `Videos/`, mas ainda não foram movidos para `assets/img/` nem referenciados nas páginas.

Os dois briefings na raiz (`# Briefing do Cliente — Hotel Dominguez Plaza.md` e `# Briefing do Sistema — Hotel Dominguez Plaza.md`) são a fonte de verdade para conteúdo. O `README.md` tem o passo a passo genérico de adaptação do template.

## Desenvolvimento

Sem build e sem instalação:

```bash
python -m http.server 8000
# ou
npx serve .
```

Sem testes e sem linting.

## Estrutura de páginas

Cada página é um diretório com `index.html` para URLs limpas:

```
/                            Home (hero + strip + prévias de sobre/acomodações/blog + CTA)
/sobre/                      Sobre, história
/experiencia/                Atividades / experiências
/acomodacoes/                Grid de acomodações (sem filtros)
/galeria/                    Galeria completa com lightbox (array único)
/localizacao/                Mapa + atrações próximas
/contato/                    Formulário + mapa
/blog/                       Índice do blog
/blog/_template/             Template para novos posts (marcadores %%PLACEHOLDER%%)
/blog/{slug}/                Posts individuais
```

Raiz também guarda: `hotel-config.json`, `blog-plan.json`, `sitemap.xml`, `robots.txt`, os dois briefings `.md` do cliente, `README.md` com o passo a passo de replicação, `favicon.svg`, e as pastas `Fotos/` e `Videos/` com o acervo real do Dominguez.

## Arquitetura essencial

### CSS único — `assets/css/style.css`

Todo o estilo em um só arquivo, guiado por custom properties (`--accent: #5b7a3d` verde floresta, `--cta: #f6b230` dourado, `--font-display: 'Pinyon Script'`, `--font-body: 'Raleway'`). Responsivo em 768/640/480px. Espaçamentos via `clamp()`. Classes curtas quase-BEM: `.rc` room card, `.gi` gallery item, `.exp-card`, `.rp-c`, `.aud-card`, `.fg`, `.btn-gold`/`.btn-green`/`.btn-outline`/`.btn-outline-w`.

Os tokens de cor herdados do template são verdes/dourados de pousada serrana — **reavaliar para o Dominguez** (hotel urbano histórico em Nova Friburgo, mais de 110 anos): paleta de marca, tipografia display e fotos hero provavelmente precisam mudar.

### JS único — `assets/js/main.js`

Toda a interatividade vive aqui. Primitivas principais:

- `sendToWebhook(payload)` — POST JSON para `WEBHOOK_URL` com `{hotel, origem_pagina, url, timestamp, ...payload}`. Usado por todos os forms.
- `pushLead(tipo)` — empurra um evento `gerar_lead` no dataLayer do GTM, com `lead_tipo`.
- `submitContact` — trata o form de `/contato/`.
- Menu mobile (`openMob`/`closeMob`), header sticky (hero-mode ↔ solid no scroll), lightbox (`openLB`/`closeLB`/`navLB`, lê de `LB_SRCS`), banner de cookies, lazy-load observer, swap do título da aba quando a aba fica oculta.

### Constantes no topo de `main.js` (editar aqui, não em valores espalhados)

```js
const WEBHOOK_URL   // URL do webhook n8n/Zapier — todos os forms postam aqui
const HOTEL_NAME    // usado em todos os payloads de webhook
const WA_NUMBER     // formato '55 + DDD + número' sem pontuação
const WA_MESSAGE    // texto pré-preenchido em wa.me?text=
const BOOKING_URL   // domínio do site
const MOTOR_BASE    // base do motor de reservas
```

## Dois modais globais injetados via JS

Ambos são inseridos no `<body>` em tempo de execução por IIFEs dentro de `main.js`. **Não adicionar HTML por página para eles.** O HTML dos modais está dentro das IIFEs; o CSS está em `style.css`.

### Modal de captura WhatsApp (classes `.wl-*`)

Intercepta **todo** clique em `a[href*="wa.me/"]` do site (botão flutuante, CTAs do hero, redes sociais no footer etc.). Mostra um card de 340px ancorado bottom-right (desktop) / bottom-center (mobile). Campos obrigatórios: nome/email/telefone. No submit: `pushLead('whatsapp_modal')` → webhook → `form.reset()` → fecha → `window.open('wa.me/{WA_NUMBER}?text=...')`. O botão secundário "📅 Reservar Agora Online" fecha este modal e chama `openBooking()` — não repurpose esse botão para outro destino. Fecha com × / backdrop / Esc.

### Modal de reservas (classes `.bk-*`) — motor de reservas

Disparado somente por `onclick="openBooking();return false"` explícito nos CTAs "Reservar". **Não intercepta links globalmente** — o trigger é opt-in por botão. Todos os "Reservar"/"Reservar Agora"/"Reservar Estadia"/"Fazer Reserva" seguem esse padrão, incluindo a versão do mobnav que encadeia `closeMob();openBooking();return false`.

Form: check-in / check-out / adultos (1–5) / crianças (0–3). Mudar o select de crianças renderiza N selects de idade (0–12). Submit monta a URL e faz `window.open(url, '_blank', 'noopener')`, depois fecha. O footer do modal tem um fallback por WhatsApp. Fecha com × / backdrop / Esc.

**Pegadinha importante para o Dominguez:** o template atual monta a URL no formato do motor Foco Multimídia: `{MOTOR_BASE}/search/{YYYY-MM-DD}/{YYYY-MM-DD}/{adults}-{age1}-{age2}` (segmentos de path). **O Dominguez usa Desbravador** em subdomínio — o formato é totalmente diferente, baseado em query string. Exemplo real:

```
https://reservas.desbravador.com.br/hotel-app/hotel-dominguez-plaza/reservation?checkin=2026-04-24&checkout=2026-04-27&adults=1&child1=1&child2=2&child3=0&voucher=&resident=0
```

Parâmetros:
- `checkin`, `checkout` — ISO `YYYY-MM-DD`.
- `adults` — inteiro.
- `child1`, `child2`, `child3` — idade de cada criança (um parâmetro por criança, **não** uma lista). Ao gerar a URL, emitir `child1..N` conforme a quantidade selecionada no select de crianças.
- `voucher` — string (pode ficar vazio).
- `resident` — `0` por padrão.

A função em `main.js` que monta a URL precisa ser reescrita de path-based (Foco) para query-string (Desbravador). Não basta trocar `MOTOR_BASE` — a concatenação de segmentos `{adults}-{age1}-{age2}` deixa de existir.

Ao adicionar um novo CTA "Reservar" em qualquer lugar, use:

```html
<a href="#" onclick="openBooking();return false" class="btn-gold">Reservar Agora</a>
```

## Renderização da galeria

`/galeria/index.html` tem um `<div class="gal-g" id="galGrid"></div>` vazio e uma única array inline `GALLERY` (path + alt) no final da página. Um único pass do script monta o grid e popula `LB_SRCS`. Para adicionar/remover fotos, edite só a array — os índices (`openLB(i)`) são calculados.

Hoje a array contém 12 entradas apontando para `placeholder.svg`. Para o Dominguez, substituir por uma seleção curada das fotos em `Fotos/` (ver seção "Acervo de mídia").

## Padrão de dobras alternadas (página Experiência)

O `<style>` inline em `experiencia/index.html` define modificadores reutilizáveis:

- `.sec-green` / `.sec-green-dark` — seção verde sólida com sobreposições de texto branco para `.feat-block`, `.txt-block`, `.txt-item`. A variante `-dark` usa `--accent-hover` (#1a4922).
- `.sec-photo` — seção com imagem de fundo fixa. **Não use `background-attachment: fixed`** — ele está quebrado globalmente por `html { zoom: 0.8 }`. A solução: a seção tem `clip-path: inset(0)` + `isolation: isolate`; `::before` é `position: fixed; inset: 0` com `background-image: var(--bg-photo)`; `::after` é a sobreposição escura, também fixed. O estilo inline define `--bg-photo: url(...)`. Isso dá um parallax real clipado aos limites da seção.
- `.aud-grid` / `.aud-card` — grid de 3 colunas com cards de imagem, overlay em gradiente e label em fonte display no terço inferior.
- `.quad-split` — imagem à esquerda, texto+cards à direita. Combinado com `.quad-cols` (grid 2×2 de itens).

## Placeholders de imagem e logo

Hoje **todas** as tags `<img>` e `background-image` do projeto apontam para um de três placeholders:

- `assets/img/placeholder.svg` — SVG genérico ("FOTO") usado em 100% dos conteúdos.
- `assets/img/logo-placeholder.svg` — usado no header, footer, e no logo dentro do modal de reservas injetado por JS.
- `favicon.svg` — único favicon referenciado.

Os `alt` descritivos das `<img>` servem como documentação do que entra em cada slot.

## Acervo de mídia — `Fotos/` e `Videos/`

Fotos reais do Dominguez Plaza organizadas por tema:

| Pasta | Nº | Uso sugerido |
|---|---|---|
| `Fotos/suites/` | 100 | Página `/acomodacoes/`, galeria, hero de categorias |
| `Fotos/banheiros/` | 50 | Cards de acomodações, galeria |
| `Fotos/areas-comuns/` | 84 | Home, sobre, galeria |
| `Fotos/areas-externas/` | 160 | Hero da home, localização, galeria |
| `Fotos/piscina/` | 131 | Home, experiência, galeria |
| `Fotos/cafe-da-manha/` | 130 | Home (diferencial), experiência, galeria |
| `Fotos/restaurante/` | 1 | — |
| `Fotos/eventos/` | 188 | **Página nova** (eventos ainda não existe no template) |
| `Fotos/detalhes/` | 73 | Texturas / acentos |
| `Fotos/equipe/` | 15 | Página sobre |
| `Fotos/hospedes-ugc/` | 78 | Depoimentos / home |
| `Fotos/modelos/` | 140 | Fotos produzidas (provavelmente hero e peças-chave) |
| `Fotos/outros/` | 16 | — |

`Videos/` contém MOVs e subpastas por período (2021, 2022 por mês, 2025, Carnaval, Modelos). Utilizar se uma seção pedir background em vídeo.

**Ao popular o site:** copiar/referenciar a partir de `assets/img/` (pode reorganizar em subpastas temáticas) e rodar find/replace trocando `placeholder.svg` pelos paths reais. Substituir `logo-placeholder.svg` e `favicon.svg` pelos ativos do Dominguez.

## Google Maps embed

Os iframes em `/contato/` e `/localizacao/` consultam **pelo nome do negócio**, não pelo endereço. Consultar por endereço faz o Google renderizar uma rota de direção em vez de um pin. Para o Dominguez, usar: `maps.google.com/maps?q=Hotel+Dominguez+Plaza,+Nova+Friburgo+-+RJ&output=embed` (preservando o padrão "nome + cidade + UF", sem rua).

## SEO e structured data

Cada página inclui JSON-LD Schema.org (LodgingBusiness/Hotel na home, WebPage + BreadcrumbList no resto, BlogPosting nos posts), meta tags Open Graph, Twitter cards, URL canônica. `sitemap.xml` e `robots.txt` na raiz — atualizar `sitemap.xml` sempre que um post ou página for adicionado. Para o Dominguez o schema apropriado é `Hotel` (não `LodgingBusiness` genérico).

## Arquivos de configuração

- **`hotel-config.json`** — fonte de verdade para dados do hotel: contato, endereço + coordenadas, acomodações, atividades, pacotes, atrações próximas, integrações (`webhook_url`, `booking_engine_url`), design tokens, configurações de blog. **Ainda contém os dados fictícios da Pousada Vale das Araucárias — começar a adaptação por aqui.** Manter em sincronia com as constantes do `main.js` quando valores mudarem.
- **`blog-plan.json`** — estratégia editorial, regras de SEO, spec do template de post, lista `published` e fila `upcoming`. Pilares ainda são os da pousada (Destino, Experiência, Família, Dicas) — reavaliar para o posicionamento do Dominguez (casais, escapadas, tradição/legado, eventos corporativos/sociais).

## Fluxo de criação de post no blog

1. Pegar próximo item em `blog-plan.json` → `upcoming`.
2. Copiar `blog/_template/index.html` → `blog/{slug}/index.html`.
3. Trocar cada marcador `%%PLACEHOLDER%%` (título, meta desc, slug, data, seções de conteúdo, palavra-chave).
4. Escrever 800–1200 palavras: intro com keyword, 3–5 `<h2>`, 2+ links internos, `.blog-cta-box` no fim.
5. Adicionar card em `blog/index.html` dentro de `#blogGrid`.
6. Adicionar `<url>` em `sitemap.xml`.
7. Mover item de `upcoming` para `published` em `blog-plan.json`.
8. Commitar localmente (push só com ordem explícita — ver "Política de Git").

### Checklist de SEO por post

`<title>` único com keyword (formato `{Título} | Blog Hotel Dominguez Plaza`), meta description ≤155 caracteres, URL canônica, Open Graph, `article:published_time`, JSON-LD `BlogPosting` + `BreadcrumbList`, `<h1>` único, `<h2>` por seção, ≥2 links internos, `.blog-cta-box` no fim.

## Contexto do cliente — Hotel Dominguez Plaza

Fonte: os dois briefings `.md` na raiz. **Este bloco é a referência para qualquer decisão de conteúdo ou copy.**

### Identidade

- **Nome:** Hotel Dominguez Plaza.
- **Responsável:** Marisa Dominguez (sócia, administradora — cresceu dentro da operação, formada em Administração em Nova Friburgo).
- **Prédio:** construído há **mais de 110 anos** no coração de Nova Friburgo. Antes de ser hotel foi sede de fazenda, mansão de veraneio, residência de família e escola; virou hotel com o nome "Schumacher" antes do nome atual.
- **Tradição:** mais de **50 anos** como hotel sob a família Dominguez (completou 50 em 2021; campanha prevista para os **55 anos**). Fundadores: Sr. Julio Dominguez (chegou ao Brasil aos 15, começou no Hotel São Paulo e depois como garçom no Rio) e Dona Glória (chegou ao Brasil em 1950). Casaram em 1961 na Catedral São João Batista. Começaram com o Bar Tingly antes do hotel.
- **Números de marca:** mais de **800 mil clientes atendidos**, **três gerações** de famílias hospedadas.

### Localização e contato

- **Endereço:** Praça do Suspiro, 114 — Centro, **Nova Friburgo/RJ**, CEP 28625-490.
- **Telefone:** +55 22 2523-9787.
- **WhatsApp:** +55 22 99293-8225 (também há +55 22 99844-5510 aparecendo no material de pacotes).
- **Site atual:** hoteldominguez.com.br.
- **Posição:** Praça do Suspiro, centro histórico/turístico/comercial; acesso rápido a todas as entradas/saídas da região serrana (a "Suíça Brasileira").

### Acomodações (4 categorias — diferentes do template)

O template traz 4 chalés rurais. O Dominguez tem **4 categorias de apartamento** em prédio histórico:

1. **Apartamento no Chalé**
2. **Apartamento Colonial** — categoria mais básica. Estrutura mais antiga, estilo clássico, ventilador (nem sempre ar-condicionado), frigobar, TV, banheiro privativo.
3. **Apartamento Colonial — 5º Andar**
4. **Apartamento Especial** — com ar-condicionado frio/quente.

**Suítes** (não são uma 5ª categoria separada na listagem do site, mas aparecem no briefing): hidromassagem e ar-condicionado frio/quente. A maioria dos apartamentos e suítes tem **varanda privativa** com vista para as montanhas — diferencial de copy.

Comodidades gerais: Wi-Fi, frigobar em todos, **estacionamento privativo próprio** (destaque no copy), apartamentos adaptados para necessidades especiais, voltagem 220V em toda a cidade.

### Diferenciais competitivos

- Café da manhã com itens frescos, **produtos da própria horta/casa** (reforçar como peça central — provável que as 130 fotos de `Fotos/cafe-da-manha/` sejam para isso).
- Mais de 50 anos de tradição familiar; 110 anos de prédio histórico.
- **Acessibilidade** (apartamentos para necessidades especiais) — tratar como valor, não só comodidade.
- Localização estratégica na Praça do Suspiro, perto do centro histórico, turístico e comercial.
- **Estacionamento privativo** — relevante para o hóspede de carro vindo do Rio / Região dos Lagos.
- Flexibilidade comercial e negociações diferenciadas (útil para copy de grupos/eventos).

### Eventos — página nova (ainda não existe no template)

O Dominguez tem **4 espaços para eventos intercambiáveis**, capacidade 30–200 pessoas, com equipamentos de informática/áudio/vídeo locáveis. Usado para conferências, convenções, festas, seminários, casamentos, reuniões de trabalho. Há opção de festa tropical na área da piscina com música ao vivo. Serviços: Making Off, arrumação especial no apartamento. 188 fotos disponíveis em `Fotos/eventos/`. **Considerar criar `/eventos/index.html`** (ou anexar a `/experiencia/`) — o template não tem essa página.

### Pacotes

- **Pacote Noite Romântica** (único ativo mencionado no site atual — 1 pessoa, 2 diárias, "consulte").
- Promoções especiais: não há ativas no momento (briefing do cliente).

### Público e mercado

- **Regiões emissoras:** Rio de Janeiro, Niterói, Região dos Lagos, Região Serrana — **não** RS/SC/PR como o template.
- **Perfis:**
  - **Casais em viagem romântica** — charme, varandas, vista para as montanhas.
  - **Famílias** — quartos familiares, piscina, café da manhã incluso.
  - **Turistas de fim de semana** — descanso rápido, escapada curta.
- Ocupação atual: **46%** (objetivo: 100%). Diária média: **R$ 482,00**. Reservas diretas: **90%**.

### Motor de reservas

- **Desbravador** em subdomínio: `https://reservas.desbravador.com.br/hotel-app/hotel-dominguez-plaza/reservation`.
- Formato de URL usa query string (`?checkin=...&checkout=...&adults=...&child1=...&child2=...&child3=...&voucher=&resident=0`) — ver exemplo completo na seção "Modal de reservas" acima.
- **Omnibees** aparece no briefing do cliente como "ação de marketing com resultado" — é o canal de distribuição (channel manager / OTAs), **não** o motor do site. O motor embutido no site é o Desbravador.

### Tom e estilo de escrita

- O site atual do Dominguez usa linguagem formal: "requinte, bom gosto e elegância", "atendimento exclusivo", "Suíça Brasileira". **Manter esse registro elegante** — é o oposto do tom "familiar, sem formalidade" da pousada do template.
- Equilibrar: elegância do prédio histórico + calor do legado familiar de 55 anos. Tradição como ativo de marca, **não** como "antigo/cansado" — modernização digital sem perder a tradição (objetivo explícito no briefing).

### Objetivos do projeto (do cliente)

- Elevar ocupação de 46% para próximo de 100%.
- Fortalecer vendas diretas (já em 90%).
- Explorar legado histórico como ativo de marca.
- Posicionar experiência familiar / atendimento como diferencial premium.
- Criar campanhas para casais e escapadas de fim de semana.

## Checklist de adaptação (ordem recomendada)

Nada disso está feito ainda. Sugestão de sequência:

1. Reescrever `hotel-config.json` com os dados reais do Dominguez (ver "Contexto do cliente" acima). Ajustar `_template_note`.
2. Atualizar constantes no topo de `assets/js/main.js` (`WEBHOOK_URL`, `HOTEL_NAME="Hotel Dominguez Plaza"`, `WA_NUMBER="5522992938225"` sem pontuação, `WA_MESSAGE`, `BOOKING_URL`, `MOTOR_BASE="https://reservas.desbravador.com.br/hotel-app/hotel-dominguez-plaza/reservation"`) e **reescrever a função que monta a URL do motor** de path-based (Foco Multimídia) para query-string (Desbravador, com `child1..N` por criança).
3. Find/replace textual em todos os HTMLs (nome, cidade, UF, contatos, handles sociais — usar a tabela do `README.md` adaptada).
4. Substituir conteúdo de `/acomodacoes/` para as 4 categorias de apartamento (não chalés).
5. Substituir conteúdo de `/sobre/` com a história da família Dominguez (110 anos do prédio + 55 da gestão).
6. Reavaliar `/experiencia/` — o template traz cavalgadas/pescaria; o Dominguez é hotel urbano. Atrações são o centro histórico, piscina, café da manhã da horta, passeios por Nova Friburgo.
7. Criar `/eventos/` (ou embutir em `/experiencia/`) — espaços para 30–200 pessoas.
8. Copiar/otimizar fotos de `Fotos/` → `assets/img/` (por tema) e substituir `placeholder.svg` em todos os HTMLs.
9. Substituir `logo-placeholder.svg` e `favicon.svg` pelos ativos do Dominguez.
10. Atualizar o embed do Google Maps (`q=Hotel+Dominguez+Plaza,+Nova+Friburgo+-+RJ`).
11. Reescrever `blog-plan.json` com pilares apropriados (Tradição/Legado, Nova Friburgo/destino, Casais/romance, Eventos, Dicas para hóspedes).
12. Revisar `sitemap.xml` e meta tags / JSON-LD (`Hotel` schema em vez de `LodgingBusiness` da pousada).

## Convenções

- Dispatcher de webhook trata o roteamento de leads; todo form passa por `sendToWebhook` + `pushLead`.
- Modais usam o toggle da classe `.open`. `document.body.style.overflow = 'hidden'` enquanto aberto, restaurado no fechamento.
- Forms `preventDefault` → webhook → evento GTM → ação de UI (redirect / WhatsApp / estado de sucesso).
- `<style>` inline em subpáginas (sobre, experiencia) guardam regras específicas da página; o global fica em `assets/css/style.css`.
- O path do logo no markup injetado por JS usa `/assets/img/logo-placeholder.svg` absoluto para resolver corretamente a partir de qualquer profundidade — ao trocar pelo logo do Dominguez manter o nome ou atualizar a constante no JS.
- Não edite a CSS legada `.wa-modal` — é herança do template base sem uso; o modal de WhatsApp vivo usa classes `.wl-*`.

## Preferência do usuário — política de Git

Commits locais automáticos na branch `main` são ok e esperados após cada alteração de código, sem precisar pedir.

**Push para o GitHub, porém, NÃO é automático.** Um push anterior do template base sobrescreveu o repositório de um cliente real em produção. Para evitar reincidência:

- **Nunca** rodar `git push`, `gh pr create`, `gh repo create`, ou qualquer comando que envie conteúdo deste diretório para o GitHub por iniciativa própria.
- Publicar só quando o usuário **explicitamente** fornecer, na mesma instrução, **(a)** a URL do repositório remoto correto **e (b)** a ordem clara de dar push/publicar. Ambos os itens precisam estar presentes — um sem o outro não basta.
- Antes de executar o push autorizado, rodar `git remote -v` e confirmar que o remote aponta para a URL fornecida (adicionar/ajustar `origin` se necessário).
