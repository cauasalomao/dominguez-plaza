# Template Modelo — Site de Pousada

Site estático em HTML/CSS/JS puro, sem build, sem framework, sem `package.json`. Preenchido com uma identidade fictícia (**Pousada Vale das Araucárias**, em Campos do Pinhão/RS) para servir como **modelo de referência** ao duplicar o projeto para novos clientes.

## Como usar este template para um novo cliente

1. **Duplicar o diretório** para um novo projeto do cliente.
2. **Substituir a identidade fictícia** pelos dados reais do cliente — a lista de busca/substituição está abaixo.
3. **Trocar as imagens de placeholder** por fotos reais do cliente.
4. **Trocar o logo e o favicon** (arquivos `assets/img/logo-placeholder.svg` e `favicon.svg`).
5. **Preencher as integrações** (webhook, GTM, motor de reservas) em `hotel-config.json` e nas constantes do topo de `assets/js/main.js`.
6. **Rodar a verificação:** `grep -r "araucária\|araucarias\|campos do pinhão" --include="*.html" .` deve retornar nada depois da substituição.

### Busca e substituição principais

Execute como par (ex.: `grep -rn "X" .` → trocar por `Y`):

| Encontrar | Trocar por |
|---|---|
| `Pousada Vale das Araucárias` | Nome completo do novo cliente |
| `Vale das Araucárias` | Nome curto do novo cliente |
| `pousadavaledasaraucarias.com.br` | Domínio do novo cliente |
| `contato@pousadavaledasaraucarias.com.br` | E-mail do novo cliente |
| `(51) 99999-8888` | Telefone formatado do novo cliente |
| `5551999998888` | WhatsApp no formato `55 + DDD + número` (sem pontuação) |
| `@pousadavaledasaraucarias` / `instagram.com/pousadavaledasaraucarias` | Handle de Instagram do novo cliente |
| `Campos do Pinhão` | Cidade do novo cliente |
| `Vale dos Pinhões` | Bairro/distrito do novo cliente |
| `Serra Geral` | Região turística do novo cliente |
| `RS 453 Km 58` | Endereço do novo cliente |
| `95270-000` | CEP do novo cliente |
| `RS` (como UF) | UF do novo cliente |
| `Chalé Mirante`, `Chalé Araucária`, `Chalé Rancho`, `Casarão Pinhão` | Nomes das 4 acomodações do novo cliente |
| `Cachoeira do Vale`, `Morro do Alvorecer`, `Serra do Vale Azul`, `Pedra Alta`, `Cascata Congelante`, `Morro dos Pinhais` | Atrações próximas do novo cliente |
| `Galpão da Serra GastroPub`, `Pizzaria Nona`, `Vinícola Alto Pinhão`, `Restaurante Montês` | Restaurantes locais do novo cliente |

Todos os locais onde esses termos aparecem:
- `hotel-config.json` (fonte de verdade — comece por aqui)
- `assets/js/main.js` (apenas as constantes do topo)
- Cada `<page>/index.html`
- `sitemap.xml` e `robots.txt`
- `blog-plan.json`
- Briefings `.md` na raiz
- `blog/cachoeiras-serra-geral/index.html`

### Imagens e favicon

- **`assets/img/placeholder.svg`** — usado em **toda** tag `<img>` e `background-image` do site. Substitua por fotos reais do cliente; pode manter nomes descritivos ou reorganizar em subpastas (`hero/`, `quartos/`, `atividades/`, etc.) e atualizar os paths em cada HTML.
- **`assets/img/logo-placeholder.svg`** — logo do cabeçalho e rodapé. Troque pelo logo do cliente (SVG ou PNG; se PNG, atualize a extensão em cada `<img>` e na constante do modal de reservas no `main.js`).
- **`favicon.svg`** — favicon único. Adicione PNG/ICO extras se precisar de melhor suporte em navegadores antigos.

### Galeria

`galeria/index.html` tem uma única array JS `GALLERY` no rodapé do arquivo. Cada item é `['caminho-relativo', 'alt text']`. Edite a array para adicionar/remover fotos; a grade e o lightbox se regeneram automaticamente.

### Blog

- Novos posts vão em `blog/{slug}/index.html` copiando `blog/_template/index.html` (use os marcadores `%%PLACEHOLDER%%`).
- Cada post criado deve ser adicionado ao `blog-plan.json` (mover de `upcoming` para `published`), ao `sitemap.xml` e receber um card em `blog/index.html`.

### Configuração das integrações

Depois da troca textual, preencha em `hotel-config.json`:

- `integrations.webhook_url` — URL do webhook (n8n, Zapier, etc.) que recebe os leads. Essa URL também precisa ser colada na constante `WEBHOOK_URL` no topo de `assets/js/main.js`.
- `integrations.gtm_id` — ID do GTM; injetar os scripts nos placeholders `<!-- GTM HEAD -->` / `<!-- GTM BODY -->` de cada HTML.
- `integrations.booking_engine_url` — URL base do motor de reservas. Também atualizar as constantes `BOOKING_URL` e `MOTOR_BASE` no `main.js`. Formato esperado: `{MOTOR_BASE}/search/{YYYY-MM-DD}/{YYYY-MM-DD}/{adults}-{age1}-{age2}`.

## Rodando localmente

Sem build. Abra qualquer `index.html` no navegador ou suba um servidor:

```bash
python -m http.server 8000
# ou
npx serve .
```

## Deploy

Push para o repositório do cliente. O projeto fica em sincronia com a branch `main`.

## Estrutura

Leia `CLAUDE.md` para a arquitetura detalhada (como os dois modais globais são injetados, como o cabeçalho troca entre `hero-mode` e `solid`, gotchas do CSS `zoom: 0.8`, etc.).
