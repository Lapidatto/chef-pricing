<p align="center">
  <img src="./docs/assets/logo-lapidatto.png" alt="Lapidatto" width="240" />
</p>

<h1 align="center">Lapidatto</h1>

<p align="center">
  <strong>Tecnologia simples para pequenos negócios.</strong><br />
  Sistemas modulares, bem acabados e fáceis de usar — para o empreendedor focar no que realmente importa: vender, crescer e ganhar tempo.
</p>

<p align="center">
  <a href="#visão-do-projeto">Visão</a> •
  <a href="#funcionalidades">Funcionalidades</a> •
  <a href="#como-rodar-o-projeto">Como rodar</a> •
  <a href="#qualidade-e-dna-de-qa">Qualidade</a> •
  <a href="#roadmap">Roadmap</a>
</p>

<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/status-em%20desenvolvimento-1482CB?style=for-the-badge" />
  <img alt="SaaS" src="https://img.shields.io/badge/SaaS-modular-073A87?style=for-the-badge" />
  <img alt="QA" src="https://img.shields.io/badge/DNA-QA-DD5502?style=for-the-badge" />
  <img alt="Self-service" src="https://img.shields.io/badge/onboarding-self--service-FCA24C?style=for-the-badge" />
</p>

---

## Visão do projeto

A **Lapidatto** nasce para democratizar o acesso à tecnologia para micro e pequenas empresas.

Nosso primeiro passo é resolver uma dor bem real: **controle de estoque sem complicação**.

A ideia é simples: entregar um sistema que ajude pequenos negócios a sair do caderno, da planilha bagunçada ou do “eu acho que ainda tem no estoque” para uma rotina mais organizada, clara e segura.

> **Estoque em ordem. Cabeça em paz.**

Este projeto faz parte do ecossistema Lapidatto: uma plataforma SaaS modular, pensada para crescer aos poucos, com qualidade, simplicidade e autonomia para quem usa.

---

## O problema que resolvemos

Pequenos negócios normalmente não têm tempo, equipe ou orçamento para lidar com sistemas complexos.

Na prática, isso vira:

- perda de tempo procurando produto;
- venda de item que já acabou;
- estoque parado sem visibilidade;
- retrabalho com planilhas;
- dificuldade para entender o que entra, sai e precisa ser reposto.

A Lapidatto existe para reduzir esse esforço operacional com uma experiência mais simples, didática e confiável.

---

## Nossa solução

Um sistema de gestão modular começando pelo **módulo de estoque/inventário**, com foco em:

- cadastro simples de produtos;
- controle de entrada e saída;
- visão clara do estoque atual;
- organização por categorias;
- fluxo pensado para iniciantes;
- onboarding self-service;
- documentação clara;
- evolução contínua com base em feedback real.

Aqui, a regra é: **se o sistema é difícil de usar, ele não resolveu o problema — só virou mais trabalho.**

---

## Funcionalidades

> Ajuste esta lista conforme o estágio real do projeto.

### Já disponível

- [ ] Cadastro de produtos
- [ ] Edição e remoção de produtos
- [ ] Controle de quantidade em estoque
- [ ] Registro de entrada de itens
- [ ] Registro de saída de itens
- [ ] Busca e filtros
- [ ] Autenticação de usuários
- [ ] Painel inicial com resumo do estoque

### Em desenvolvimento

- [ ] Categorias personalizadas
- [ ] Alertas de estoque baixo
- [ ] Histórico de movimentações
- [ ] Importação via planilha
- [ ] Exportação de dados
- [ ] Relatórios simples
- [ ] Base de conhecimento integrada

### Futuro do ecossistema

- [ ] Módulo financeiro
- [ ] Módulo de vendas
- [ ] Integrações com canais de venda
- [ ] Dashboard com indicadores do negócio
- [ ] Add-ons por necessidade do cliente

---

## Como funciona

A experiência foi pensada para ser direta:

1. **Crie sua conta**  
   Entre no sistema sem burocracia.

2. **Cadastre seus primeiros produtos**  
   Comece pequeno: 10 itens já são suficientes para entender o fluxo.

3. **Controle entrada e saída**  
   Chegou produto? Registra entrada. Vendeu? Registra saída.

4. **Acompanhe seu estoque com clareza**  
   Menos achismo, menos erro e mais controle para decidir melhor.

---

## Tecnologias utilizadas

> Atualize esta seção conforme a stack real do projeto.

| Camada | Tecnologia |
|---|---|
| Frontend | `Ex: React / Next.js / Vue / Angular` |
| Backend | `Ex: Node.js / NestJS / Ruby on Rails / Python` |
| Banco de dados | `Ex: PostgreSQL / MySQL / MongoDB / Supabase` |
| Autenticação | `Ex: JWT / OAuth / Auth.js / Firebase Auth` |
| Testes | `Ex: Jest / Vitest / Cypress / Playwright / RSpec / Pytest` |
| Deploy | `Ex: Vercel / Render / Railway / AWS / Docker` |

---

## Como rodar o projeto

> Os comandos abaixo são um modelo base. Ajuste conforme a tecnologia usada no repositório.

### 1. Clone o repositório

```bash
git clone https://github.com/lapidatto/nome-do-repositorio.git
cd nome-do-repositorio
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Depois, preencha o arquivo `.env` com as informações necessárias:

```env
APP_URL=http://localhost:3000
DATABASE_URL=
AUTH_SECRET=
```

### 3. Instale as dependências

```bash
npm install
```

ou, se o projeto usar `pnpm`:

```bash
pnpm install
```

### 4. Rode o projeto localmente

```bash
npm run dev
```

ou:

```bash
pnpm dev
```

Acesse no navegador:

```bash
http://localhost:3000
```

---

## Scripts úteis

> Atualize os scripts conforme o `package.json`, `Makefile` ou ferramenta equivalente do projeto.

```bash
npm run dev       # inicia o ambiente de desenvolvimento
npm run build     # gera a versão de produção
npm run test      # executa os testes
npm run lint      # verifica padrões de código
npm run format    # formata o código
```

---

## Estrutura sugerida do projeto

> Ajuste conforme a estrutura real do repositório.

```bash
.
├── docs/                 # Documentação do projeto
│   └── assets/           # Logo, imagens e materiais visuais
├── src/                  # Código-fonte principal
│   ├── components/       # Componentes de interface
│   ├── pages/            # Páginas ou rotas
│   ├── services/         # Comunicação com APIs e regras externas
│   ├── modules/          # Domínios do sistema
│   └── tests/            # Testes automatizados
├── .env.example          # Exemplo de variáveis de ambiente
├── README.md             # Documentação principal
└── package.json          # Dependências e scripts
```

---

## Qualidade e DNA de QA

A Lapidatto tem uma visão simples sobre qualidade:

> **É melhor entregar menos, mas bem feito, do que lançar correndo e quebrar a rotina de quem usa.**

Por isso, este projeto deve priorizar:

- testes automatizados nos fluxos críticos;
- interface simples e previsível;
- mensagens de erro claras;
- documentação objetiva;
- revisão antes de release;
- feedback real de usuários;
- evolução gradual, sem prometer o que ainda não está pronto.

Qualidade aqui não é detalhe técnico. É respeito com o pequeno empreendedor que depende do sistema para trabalhar melhor.

---

## Princípios de experiência

Tudo na Lapidatto precisa responder a três perguntas:

1. **Está claro?**  
   A pessoa entende sem precisar ser técnica?

2. **Está simples?**  
   O fluxo reduz esforço ou cria mais uma tarefa?

3. **Está útil?**  
   Resolve uma dor real do negócio?

Quando houver dúvida, a decisão deve favorecer clareza, estabilidade e autonomia.

---

## Documentação

A documentação deve funcionar como um “manual amigo”: direto, prático e com exemplos.

Sugestão de conteúdos:

- como cadastrar um produto;
- como registrar entrada de estoque;
- como registrar saída de estoque;
- como organizar categorias;
- como importar dados de uma planilha;
- erros comuns e como resolver;
- perguntas frequentes para iniciantes.

---

## Roadmap

### Fase 1 — Base do estoque

- Cadastro de produtos
- Entrada e saída de itens
- Listagem e busca
- Ajustes de usabilidade
- Primeiros testes com usuários reais

### Fase 2 — Organização e produtividade

- Categorias
- Estoque mínimo
- Histórico de movimentações
- Importação/exportação
- Melhorias no onboarding

### Fase 3 — Inteligência e crescimento

- Relatórios simples
- Indicadores de estoque
- Sugestões de reposição
- Integrações
- Novos módulos do ecossistema Lapidatto

---

## Como contribuir

Contribuições são bem-vindas, principalmente quando ajudam a deixar o sistema mais simples, estável e útil para pequenos negócios.

### Fluxo recomendado

1. Abra uma issue explicando o problema ou sugestão.
2. Crie uma branch com nome claro.
3. Faça a alteração com foco em simplicidade e qualidade.
4. Adicione ou atualize testes quando necessário.
5. Abra um pull request explicando o que foi feito e por quê.

### Padrão de branch

```bash
feature/nome-da-funcionalidade
fix/nome-do-ajuste
docs/nome-da-documentacao
```

### Padrão de commit

```bash
feat: adiciona cadastro de produtos
fix: corrige validação de quantidade em estoque
docs: atualiza instruções de instalação
```

---

## Identidade visual

Para manter consistência com a marca:

- use o logo oficial em `docs/assets/logo-lapidatto.png`;
- mantenha boa área de respiro ao redor do logo;
- evite distorcer, rotacionar ou aplicar sombra no logo;
- priorize tons da família azul e laranja da Lapidatto;
- use fundos claros ou escuros com bom contraste;
- escreva com clareza, sem jargão desnecessário.

Cores de referência:

| Cor | HEX |
|---|---|
| Azul principal | `#073A87` |
| Azul claro | `#1482CB` |
| Azul profundo | `#051E4F` |
| Roxo tecnológico | `#343065` |
| Laranja principal | `#DD5502` |
| Laranja claro | `#FCA24C` |
| Creme | `#F7F1E7` |

---

## Links úteis

- Site: `https://lapidattoconsulting.com`
- Instagram: `https://instagram.com/lapidatto`
- Documentação: `em breve`
- Base de conhecimento: `em breve`
- Changelog: `em breve`

---

## Licença

Este projeto é mantido pela **Lapidatto**.

Defina aqui a licença do projeto:

```text
MIT, Apache-2.0, Proprietária ou outra licença escolhida.
```

---

<p align="center">
  <strong>Lapidatto</strong><br />
  Well-built technology. Made simple.
</p>
