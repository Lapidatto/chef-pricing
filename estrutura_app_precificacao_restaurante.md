# Estrutura técnica — Aplicativo Python para precificação de pratos de restaurante

## 1. Objetivo do sistema

Criar um aplicativo desktop para Windows, feito em Python, para ajudar um chef/cozinha a:

- cadastrar ingredientes comprados;
- cadastrar produções internas da cozinha;
- montar pratos finais;
- calcular custo técnico de cada prato;
- calcular preço sugerido de venda;
- salvar os dados localmente em arquivos CSV;
- permitir que o usuário abra esses CSVs no Excel;
- validar os CSVs quando forem editados manualmente fora do sistema.

O sistema deve ser um projeto único, em formato de monorepo, com separação clara entre:

- front-end desktop;
- camada de aplicação;
- domínio/regra de negócio;
- infraestrutura de persistência em CSV;
- testes;
- empacotamento para Windows.

---

## 2. Decisão de stack recomendada

### 2.1 Linguagem

Python 3.12 ou superior.

Motivo:

- linguagem simples para desenvolvimento rápido;
- boa integração com arquivos CSV;
- boa compatibilidade com Windows;
- ecossistema maduro para desktop, validação, testes e empacotamento.

---

### 2.2 Front-end desktop

Recomendação principal: **PySide6 / Qt for Python**.

Motivo:

- é o binding oficial do Qt para Python;
- permite criar aplicativo desktop real, não apenas uma interface web embutida;
- funciona bem no Windows;
- tem componentes maduros para tabelas, formulários, menus, janelas, diálogos e navegação;
- permite evoluir depois para uma interface mais profissional;
- é mais robusto que Tkinter para uma aplicação comercial com tabelas e telas de cadastro;
- é mais apropriado para desktop offline do que frameworks web.

Alternativas avaliadas:

| Opção | Avaliação |
|---|---|
| Tkinter | Simples, nativo no Python, mas limitado visualmente e menos confortável para aplicação grande. |
| CustomTkinter | Mais bonito que Tkinter, mas menos maduro que Qt para software com tabelas, filtros e fluxo complexo. |
| Flet | Interessante e rápido, mas adiciona dependência de runtime visual mais abstrato. Bom para protótipo, menos recomendado como primeira escolha comercial offline. |
| PyQt6 | Muito parecido com PySide6, mas PySide6 tende a ser melhor escolha por ser o binding oficial do Qt e ter licenciamento mais conveniente para muitos casos. |
| Web app local com FastAPI + browser | Funciona, mas aumenta complexidade sem necessidade neste MVP. |

Decisão: **PySide6**.

---

### 2.3 Back-end interno

Não recomendo criar API HTTP neste primeiro momento.

Em vez disso, usar uma arquitetura em camadas:

- UI chama casos de uso;
- casos de uso chamam serviços de domínio;
- serviços usam repositórios;
- repositórios leem/escrevem CSV.

Ou seja: existe “back-end”, mas ele é interno ao aplicativo, não um servidor.

Essa decisão evita:

- subir servidor local;
- lidar com portas;
- problemas de firewall;
- complexidade de API desnecessária;
- duplicação de DTOs para um sistema offline simples.

---

### 2.4 Persistência

Persistência local em CSVs.

Recomendação: usar **múltiplos CSVs bem definidos**, e não um CSV único.

Motivo:

Um único CSV ficaria ruim porque o sistema tem entidades diferentes:

- ingrediente;
- produção interna;
- prato;
- composição de prato;
- composição de produção;
- unidades de medida;
- configurações;
- histórico de preços.

Misturar tudo em uma planilha só deixaria a validação frágil, difícil de manter e fácil de quebrar no Excel.

Por outro lado, também não devemos criar “um milhão de CSVs”.

A melhor estrutura é um pequeno conjunto de CSVs relacionais, como se fossem tabelas simples.

---

## 3. Conceitos principais do sistema

### 3.1 Ingrediente

É algo comprado pronto.

Exemplos:

- alface;
- tomate;
- frango;
- parmesão;
- azeite;
- sal;
- farinha;
- ovo.

O ingrediente tem:

- nome;
- categoria;
- unidade de compra;
- quantidade comprada;
- preço pago;
- custo por unidade base;
- fornecedor opcional;
- data do último preço.

Exemplo:

O chef compra 1 kg de tomate por R$ 12,00.

O sistema precisa converter isso para:

- R$ 12,00 por kg;
- R$ 0,012 por grama.

---

### 3.2 Produção interna

É algo produzido dentro da cozinha e depois usado em pratos.

Exemplos:

- molho Caesar;
- croutons;
- caldo de legumes;
- massa fresca;
- maionese da casa;
- tempero da casa;
- frango desfiado temperado.

A produção interna tem custo próprio.

Exemplo:

Molho Caesar usa:

- parmesão;
- maionese;
- anchova;
- limão;
- azeite.

O sistema calcula o custo total da produção e o custo por grama/ml/unidade.

Depois, o molho Caesar pode ser usado como componente de uma salada Caesar.

---

### 3.3 Prato final

É o item servido/vendido para o cliente.

Exemplos:

- Salada Caesar;
- Burger da casa;
- Risoto de cogumelos;
- Pudim;
- Entrada de burrata.

Um prato pode usar:

- ingredientes comprados diretamente;
- produções internas;
- outros componentes cadastrados.

Exemplo:

Salada Caesar:

- alface romana;
- frango grelhado;
- parmesão;
- croutons da casa;
- molho Caesar da casa.

---

### 3.4 Componente

Para simplificar a arquitetura, o sistema pode tratar tudo que entra em uma receita como um “componente”.

Existem dois tipos principais de componente:

- ingrediente;
- produção interna.

Isso permite que a tela de composição de prato seja mais simples.

Exemplo:

| Tipo de componente | Nome | Quantidade | Unidade |
|---|---:|---:|---|
| ingrediente | Alface romana | 120 | g |
| produção interna | Molho Caesar | 40 | g |
| produção interna | Croutons da casa | 25 | g |
| ingrediente | Parmesão | 15 | g |

---

## 4. Estrutura recomendada de CSVs

A pasta dos dados deve ser escolhida pelo usuário na primeira execução.

Exemplo:

```text
C:\Users\Usuario\Documents\ChefPricingData\
```

Dentro dela:

```text
ChefPricingData/
├── data/
│   ├── ingredients.csv
│   ├── preparations.csv
│   ├── preparation_components.csv
│   ├── dishes.csv
│   ├── dish_components.csv
│   ├── units.csv
│   ├── price_history.csv
│   └── app_settings.csv
├── backups/
│   ├── 2026-06-12_10-30-00/
│   └── 2026-06-13_09-15-00/
└── exports/
    ├── ficha_tecnica_salada_caesar.csv
    └── pratos_precificados.csv
```

---

## 5. Modelo dos CSVs

### 5.1 `ingredients.csv`

Ingredientes comprados.

```csv
id,name,category,purchase_unit,purchase_quantity,purchase_price,base_unit,base_quantity,cost_per_base_unit,waste_percent,supplier,last_price_date,active,notes
ing_001,Alface romana,Hortifruti,kg,1,18.00,g,1000,0.018,8,Fornecedor A,2026-06-12,true,
ing_002,Parmesão,Laticínios,kg,1,80.00,g,1000,0.080,0,Fornecedor B,2026-06-12,true,
```

Campos:

| Campo | Descrição |
|---|---|
| id | Identificador único. Não deve mudar. |
| name | Nome do ingrediente. |
| category | Categoria do ingrediente. |
| purchase_unit | Unidade de compra: kg, g, l, ml, un. |
| purchase_quantity | Quantidade comprada. |
| purchase_price | Preço pago pela compra. |
| base_unit | Unidade base usada nos cálculos. |
| base_quantity | Quantidade convertida para unidade base. |
| cost_per_base_unit | Custo por g/ml/un. |
| waste_percent | Percentual de perda. |
| supplier | Fornecedor. |
| last_price_date | Data do último preço. |
| active | Se o ingrediente está ativo. |
| notes | Observações. |

Regra de cálculo:

```text
cost_per_base_unit = purchase_price / base_quantity
```

Se houver perda:

```text
effective_cost = cost_per_base_unit / (1 - waste_percent / 100)
```

---

### 5.2 `preparations.csv`

Produções internas.

```csv
id,name,category,yield_quantity,yield_unit,total_cost,cost_per_yield_unit,active,notes
prep_001,Molho Caesar,Molhos,1000,g,35.00,0.035,true,
prep_002,Croutons da casa,Complementos,500,g,12.50,0.025,true,
```

Campos:

| Campo | Descrição |
|---|---|
| id | Identificador único. |
| name | Nome da produção interna. |
| category | Categoria. |
| yield_quantity | Rendimento final. |
| yield_unit | Unidade do rendimento. |
| total_cost | Custo total calculado. |
| cost_per_yield_unit | Custo por unidade de rendimento. |
| active | Se está ativa. |
| notes | Observações. |

Regra:

```text
cost_per_yield_unit = total_cost / yield_quantity
```

---

### 5.3 `preparation_components.csv`

Componentes de cada produção interna.

```csv
id,preparation_id,component_type,component_id,quantity,unit,loss_percent,notes
pc_001,prep_001,ingredient,ing_002,80,g,0,Parmesão
pc_002,prep_001,ingredient,ing_010,120,g,0,Maionese
pc_003,prep_001,ingredient,ing_011,40,ml,0,Limão
```

Campos:

| Campo | Descrição |
|---|---|
| id | Identificador único da linha. |
| preparation_id | ID da produção interna. |
| component_type | ingredient ou preparation. |
| component_id | ID do ingrediente ou de outra produção. |
| quantity | Quantidade usada. |
| unit | Unidade usada. |
| loss_percent | Perda específica na receita. |
| notes | Observações. |

Observação importante:

No MVP, eu recomendo permitir que produção interna use apenas ingredientes.

Depois, numa versão 2, permitir que uma produção interna use outra produção interna.

Isso evita recursividade complexa logo no começo.

---

### 5.4 `dishes.csv`

Pratos finais.

```csv
id,name,category,serving_size,serving_unit,total_cost,desired_food_cost_percent,suggested_price,manual_price,profit_margin,active,notes
dish_001,Salada Caesar,Saladas,1,portion,11.80,30,39.33,42.00,30.20,true,
```

Campos:

| Campo | Descrição |
|---|---|
| id | Identificador único. |
| name | Nome do prato. |
| category | Categoria do prato. |
| serving_size | Tamanho da porção. |
| serving_unit | Unidade da porção. |
| total_cost | Custo total calculado. |
| desired_food_cost_percent | Percentual desejado de custo. |
| suggested_price | Preço sugerido. |
| manual_price | Preço definido manualmente. |
| profit_margin | Margem estimada. |
| active | Se o prato está ativo. |
| notes | Observações. |

Regra de preço sugerido:

```text
suggested_price = total_cost / (desired_food_cost_percent / 100)
```

Exemplo:

```text
total_cost = 11.80
desired_food_cost_percent = 30

suggested_price = 11.80 / 0.30
suggested_price = 39.33
```

---

### 5.5 `dish_components.csv`

Componentes de cada prato.

```csv
id,dish_id,component_type,component_id,quantity,unit,loss_percent,notes
dc_001,dish_001,ingredient,ing_001,120,g,8,Alface romana
dc_002,dish_001,preparation,prep_001,40,g,0,Molho Caesar
dc_003,dish_001,preparation,prep_002,25,g,0,Croutons
dc_004,dish_001,ingredient,ing_002,15,g,0,Parmesão
```

Campos:

| Campo | Descrição |
|---|---|
| id | Identificador único da linha. |
| dish_id | ID do prato. |
| component_type | ingredient ou preparation. |
| component_id | ID do ingrediente ou da produção. |
| quantity | Quantidade usada no prato. |
| unit | Unidade usada. |
| loss_percent | Perda específica. |
| notes | Observações. |

---

### 5.6 `units.csv`

Tabela de unidades aceitas e conversões.

```csv
id,name,type,to_base_factor,base_unit,active
unit_kg,kg,mass,1000,g,true
unit_g,g,mass,1,g,true
unit_l,l,volume,1000,ml,true
unit_ml,ml,volume,1,ml,true
unit_un,un,count,1,un,true
```

Campos:

| Campo | Descrição |
|---|---|
| id | ID da unidade. |
| name | Nome da unidade. |
| type | mass, volume ou count. |
| to_base_factor | Fator de conversão para unidade base. |
| base_unit | g, ml ou un. |
| active | Se está ativa. |

---

### 5.7 `price_history.csv`

Histórico de preços dos ingredientes.

```csv
id,ingredient_id,purchase_unit,purchase_quantity,purchase_price,supplier,price_date,notes
ph_001,ing_001,kg,1,18.00,Fornecedor A,2026-06-12,
ph_002,ing_001,kg,1,20.00,Fornecedor A,2026-06-19,
```

Motivo para ter histórico:

- entender variação de custo;
- recalcular pratos quando preço muda;
- evitar perder o preço anterior;
- gerar relatórios depois.

---

### 5.8 `app_settings.csv`

Configurações simples do aplicativo.

```csv
key,value
data_version,1
currency,BRL
decimal_separator,.
default_food_cost_percent,30
backup_on_startup,true
```

---

## 6. Por que não usar apenas um CSV?

Não recomendo um CSV único porque o software tem relacionamentos.

Um prato tem vários componentes.

Uma produção interna tem vários componentes.

Um ingrediente pode aparecer em vários pratos.

Se tudo ficar em um CSV só, os dados vão ficar repetidos e inconsistentes.

Exemplo ruim:

```csv
dish_name,ingredient_name,ingredient_price,preparation_name,preparation_cost
Salada Caesar,Alface,18.00,Molho Caesar,35.00
Salada Caesar,Parmesão,80.00,Molho Caesar,35.00
```

Problemas:

- o nome do prato repete;
- o custo do molho repete;
- se mudar o nome do molho, tem que mudar várias linhas;
- se editar no Excel, pode quebrar fácil;
- fica difícil validar.

A estrutura com 7 ou 8 CSVs é um equilíbrio bom:

- não é banco de dados;
- continua abrindo no Excel;
- é organizada;
- é validável;
- é performática para um MVP;
- permite crescimento.

---

## 7. Estrutura de pastas do monorepo

```text
chef-pricing-app/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── csv_schema.md
│   ├── pricing_rules.md
│   └── user_flows.md
│
├── src/
│   └── chef_pricing/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── frontend/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── main_window.py
│       │   ├── navigation.py
│       │   │
│       │   ├── views/
│       │   │   ├── dashboard_view.py
│       │   │   ├── ingredients_view.py
│       │   │   ├── preparations_view.py
│       │   │   ├── dishes_view.py
│       │   │   ├── dish_editor_view.py
│       │   │   ├── reports_view.py
│       │   │   └── settings_view.py
│       │   │
│       │   ├── viewmodels/
│       │   │   ├── ingredients_vm.py
│       │   │   ├── preparations_vm.py
│       │   │   ├── dishes_vm.py
│       │   │   └── settings_vm.py
│       │   │
│       │   ├── widgets/
│       │   │   ├── money_input.py
│       │   │   ├── percentage_input.py
│       │   │   ├── unit_selector.py
│       │   │   ├── component_table.py
│       │   │   └── validation_panel.py
│       │   │
│       │   └── resources/
│       │       ├── icons/
│       │       └── styles/
│       │           └── main.qss
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   │
│       │   ├── use_cases/
│       │   │   ├── create_ingredient.py
│       │   │   ├── update_ingredient_price.py
│       │   │   ├── create_preparation.py
│       │   │   ├── calculate_preparation_cost.py
│       │   │   ├── create_dish.py
│       │   │   ├── calculate_dish_cost.py
│       │   │   ├── suggest_dish_price.py
│       │   │   ├── validate_workspace.py
│       │   │   └── export_reports.py
│       │   │
│       │   ├── services/
│       │   │   ├── pricing_service.py
│       │   │   ├── unit_conversion_service.py
│       │   │   ├── validation_service.py
│       │   │   ├── backup_service.py
│       │   │   └── workspace_service.py
│       │   │
│       │   └── dto/
│       │       ├── ingredient_dto.py
│       │       ├── preparation_dto.py
│       │       ├── dish_dto.py
│       │       └── validation_result_dto.py
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   │
│       │   ├── models/
│       │   │   ├── ingredient.py
│       │   │   ├── preparation.py
│       │   │   ├── preparation_component.py
│       │   │   ├── dish.py
│       │   │   ├── dish_component.py
│       │   │   ├── unit.py
│       │   │   └── price_history.py
│       │   │
│       │   ├── value_objects/
│       │   │   ├── money.py
│       │   │   ├── percentage.py
│       │   │   ├── quantity.py
│       │   │   └── component_type.py
│       │   │
│       │   ├── rules/
│       │   │   ├── pricing_rules.py
│       │   │   ├── unit_rules.py
│       │   │   └── recipe_rules.py
│       │   │
│       │   └── exceptions.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   │
│       │   ├── storage/
│       │   │   ├── csv_reader.py
│       │   │   ├── csv_writer.py
│       │   │   ├── csv_schema.py
│       │   │   ├── csv_workspace.py
│       │   │   ├── atomic_file_writer.py
│       │   │   └── repositories/
│       │   │       ├── ingredient_repository.py
│       │   │       ├── preparation_repository.py
│       │   │       ├── dish_repository.py
│       │   │       ├── unit_repository.py
│       │   │       └── price_history_repository.py
│       │   │
│       │   ├── validation/
│       │   │   ├── csv_validator.py
│       │   │   ├── schema_validator.py
│       │   │   ├── relationship_validator.py
│       │   │   └── business_validator.py
│       │   │
│       │   └── logging/
│       │       └── logger.py
│       │
│       └── shared/
│           ├── constants.py
│           ├── id_generator.py
│           ├── date_utils.py
│           └── number_utils.py
│
├── tests/
│   ├── unit/
│   │   ├── test_pricing_service.py
│   │   ├── test_unit_conversion_service.py
│   │   ├── test_validation_service.py
│   │   └── test_recipe_rules.py
│   │
│   ├── integration/
│   │   ├── test_csv_repositories.py
│   │   ├── test_workspace_validation.py
│   │   └── test_dish_cost_calculation.py
│   │
│   └── fixtures/
│       └── sample_workspace/
│           └── data/
│               ├── ingredients.csv
│               ├── preparations.csv
│               ├── preparation_components.csv
│               ├── dishes.csv
│               ├── dish_components.csv
│               ├── units.csv
│               ├── price_history.csv
│               └── app_settings.csv
│
├── scripts/
│   ├── create_sample_workspace.py
│   ├── validate_workspace.py
│   └── build_windows_exe.py
│
├── packaging/
│   ├── pyinstaller/
│   │   └── chef_pricing.spec
│   └── windows/
│       └── installer_notes.md
│
└── data_templates/
    ├── ingredients.csv
    ├── preparations.csv
    ├── preparation_components.csv
    ├── dishes.csv
    ├── dish_components.csv
    ├── units.csv
    ├── price_history.csv
    └── app_settings.csv
```

---

## 8. Responsabilidade de cada camada

### 8.1 `frontend/`

Responsável por tudo que o usuário vê.

Não deve conter regra de negócio pesada.

Pode:

- renderizar telas;
- capturar clique;
- exibir tabela;
- mostrar erros;
- chamar ViewModels;
- abrir seletor de pasta;
- exibir mensagens de validação;
- mostrar custo e preço calculado.

Não deve:

- calcular custo de prato diretamente;
- manipular CSV diretamente;
- validar relacionamento entre arquivos;
- gerar IDs de domínio;
- aplicar regra fiscal ou financeira.

---

### 8.2 `frontend/views/`

Telas principais.

Sugestão de telas:

#### Dashboard

Mostra:

- quantidade de pratos cadastrados;
- quantidade de ingredientes;
- pratos sem preço;
- ingredientes sem preço;
- últimos preços alterados;
- alertas de CSV inválido.

#### Ingredientes

Funcionalidades:

- listar ingredientes;
- cadastrar ingrediente;
- editar preço;
- editar perda;
- ativar/inativar ingrediente;
- ver histórico de preço.

#### Produções internas

Funcionalidades:

- listar produções;
- cadastrar produção;
- montar composição;
- calcular custo total;
- calcular custo por unidade de rendimento.

#### Pratos

Funcionalidades:

- listar pratos;
- cadastrar prato;
- montar ficha técnica;
- adicionar ingredientes;
- adicionar produções internas;
- calcular custo;
- sugerir preço;
- preencher preço manual.

#### Relatórios

Possíveis relatórios:

- custo dos pratos;
- pratos com margem baixa;
- ingredientes mais usados;
- variação de preço de ingredientes;
- ficha técnica por prato.

#### Configurações

Funcionalidades:

- escolher pasta dos CSVs;
- definir moeda;
- definir percentual padrão de food cost;
- configurar backup automático;
- validar arquivos.

---

### 8.3 `frontend/viewmodels/`

Camada intermediária entre tela e aplicação.

Responsável por:

- preparar dados para exibição;
- converter dados da tela em DTOs;
- chamar use cases;
- receber mensagens de erro;
- devolver estado para a tela.

Exemplo:

```text
IngredientsView -> IngredientsViewModel -> CreateIngredientUseCase
```

---

### 8.4 `application/use_cases/`

Cada arquivo representa uma ação de usuário.

Exemplos:

#### `create_ingredient.py`

Responsável por:

- receber dados do ingrediente;
- validar campos obrigatórios;
- calcular custo por unidade base;
- gerar ID;
- salvar no repositório;
- retornar resultado.

#### `update_ingredient_price.py`

Responsável por:

- atualizar preço do ingrediente;
- recalcular custo base;
- criar linha no histórico de preços;
- indicar quais pratos foram afetados.

#### `create_preparation.py`

Responsável por:

- criar uma produção interna;
- salvar dados básicos;
- permitir depois adicionar componentes.

#### `calculate_preparation_cost.py`

Responsável por:

- buscar componentes da produção;
- calcular custo de cada componente;
- somar custo total;
- calcular custo por unidade de rendimento;
- atualizar `preparations.csv`.

#### `create_dish.py`

Responsável por:

- criar prato;
- definir categoria;
- definir food cost desejado;
- salvar prato inicial.

#### `calculate_dish_cost.py`

Responsável por:

- buscar componentes do prato;
- calcular custo de ingredientes;
- calcular custo de produções internas;
- somar custo total;
- atualizar `dishes.csv`.

#### `suggest_dish_price.py`

Responsável por:

- usar custo total;
- aplicar percentual desejado;
- sugerir preço de venda;
- opcionalmente arredondar para estratégia comercial.

#### `validate_workspace.py`

Responsável por:

- validar se todos os CSVs existem;
- validar colunas obrigatórias;
- validar tipos de dados;
- validar IDs duplicados;
- validar referências quebradas;
- validar números negativos;
- validar unidades incompatíveis;
- retornar lista de erros e avisos.

---

### 8.5 `application/services/`

Serviços reutilizáveis.

#### `pricing_service.py`

Responsável por:

- calcular custo de ingrediente usado em receita;
- calcular custo de produção interna;
- calcular custo de prato;
- calcular preço sugerido;
- calcular margem estimada.

Funções sugeridas:

```python
calculate_ingredient_usage_cost(...)
calculate_preparation_total_cost(...)
calculate_dish_total_cost(...)
calculate_suggested_price(...)
calculate_profit_margin(...)
```

---

#### `unit_conversion_service.py`

Responsável por:

- converter kg para g;
- converter l para ml;
- validar se unidades são compatíveis;
- impedir conversão inválida, como kg para ml.

Funções sugeridas:

```python
convert_to_base_unit(...)
convert_between_units(...)
assert_compatible_units(...)
```

---

#### `validation_service.py`

Responsável por:

- coordenar validações de schema;
- coordenar validações de relacionamento;
- coordenar validações de negócio;
- devolver resultado único para a UI.

---

#### `backup_service.py`

Responsável por:

- criar backup antes de salvar;
- criar backup ao abrir o app;
- restaurar backup se necessário.

---

#### `workspace_service.py`

Responsável por:

- criar pasta inicial;
- copiar templates de CSV;
- identificar caminho atual dos dados;
- verificar se a pasta escolhida é válida.

---

### 8.6 `domain/`

Aqui ficam os conceitos puros do negócio.

Essa camada não deve saber que existe CSV, PySide6, Excel ou Windows.

Ela deve representar:

- ingrediente;
- produção;
- prato;
- componente;
- dinheiro;
- percentual;
- quantidade;
- unidade.

---

### 8.7 `infrastructure/storage/`

Responsável por ler e escrever arquivos.

#### `csv_reader.py`

Responsável por:

- abrir arquivo CSV;
- ler linhas;
- respeitar encoding;
- retornar dicionários ou modelos;
- tratar arquivo ausente;
- tratar arquivo vazio.

#### `csv_writer.py`

Responsável por:

- escrever cabeçalho;
- escrever linhas;
- manter ordem das colunas;
- usar escrita segura;
- evitar corromper arquivo.

#### `atomic_file_writer.py`

Responsável por salvar com segurança.

Fluxo recomendado:

```text
1. escrever em arquivo temporário;
2. validar arquivo temporário;
3. substituir arquivo original;
4. se falhar, manter original.
```

Isso reduz risco de corromper CSV caso o app feche no meio da gravação.

#### `csv_workspace.py`

Responsável por:

- apontar para a pasta escolhida;
- encontrar os arquivos;
- criar templates;
- listar arquivos obrigatórios.

---

### 8.8 `infrastructure/storage/repositories/`

Cada repositório cuida de uma entidade.

Exemplo:

#### `ingredient_repository.py`

Funções:

```python
list_all()
get_by_id(ingredient_id)
get_by_name(name)
save(ingredient)
update(ingredient)
delete_or_deactivate(ingredient_id)
exists(ingredient_id)
```

#### `dish_repository.py`

Funções:

```python
list_all()
get_by_id(dish_id)
save(dish)
update(dish)
list_components(dish_id)
save_components(dish_id, components)
```

Importante:

No MVP, prefira “inativar” em vez de deletar.

Isso evita quebrar pratos antigos.

---

## 9. Validações necessárias

Como o usuário pode editar CSV no Excel, validação é parte central do sistema.

### 9.1 Validação de existência

Verificar se existem:

- `ingredients.csv`;
- `preparations.csv`;
- `preparation_components.csv`;
- `dishes.csv`;
- `dish_components.csv`;
- `units.csv`;
- `price_history.csv`;
- `app_settings.csv`.

Se algum não existir:

- informar erro;
- oferecer opção “recriar arquivo vazio com cabeçalho”.

---

### 9.2 Validação de colunas

Cada CSV deve ter exatamente as colunas esperadas.

Se faltar coluna:

- bloquear cálculo;
- mostrar qual arquivo está errado;
- mostrar qual coluna falta.

Se tiver coluna extra:

- pode permitir;
- mas mostrar aviso.

Recomendação:

- coluna faltando = erro;
- coluna extra = aviso.

---

### 9.3 Validação de tipos

Exemplos:

- preço precisa ser número;
- quantidade precisa ser número positivo;
- percentual precisa estar entre 0 e 100;
- data precisa estar em formato `YYYY-MM-DD`;
- `active` precisa ser `true` ou `false`.

---

### 9.4 Validação de relacionamento

Exemplos:

- `dish_components.dish_id` precisa existir em `dishes.csv`;
- `dish_components.component_id` precisa existir em `ingredients.csv` ou `preparations.csv`;
- `preparation_components.preparation_id` precisa existir em `preparations.csv`;
- `price_history.ingredient_id` precisa existir em `ingredients.csv`.

---

### 9.5 Validação de unidades

Exemplos:

Permitido:

```text
kg -> g
g -> g
l -> ml
ml -> ml
un -> un
```

Não permitido:

```text
kg -> ml
g -> un
l -> g
```

---

### 9.6 Validação de negócio

Exemplos:

- prato sem componente deve gerar aviso;
- ingrediente sem preço deve gerar erro;
- produção com rendimento zero deve gerar erro;
- food cost igual a zero deve gerar erro;
- prato com preço manual abaixo do custo deve gerar alerta;
- ingrediente inativo usado em prato ativo deve gerar aviso.

---

## 10. Regra de cálculo de custo

### 10.1 Custo de ingrediente usado

Exemplo:

Ingrediente:

```text
Parmesão
Custo por grama = R$ 0,08
```

Uso no prato:

```text
15 g
```

Custo:

```text
15 * 0,08 = R$ 1,20
```

Com perda de 10%:

```text
custo = quantidade * custo_unitario / (1 - perda / 100)
```

---

### 10.2 Custo de produção interna

Exemplo:

Molho Caesar:

| Componente | Quantidade | Custo unitário | Custo |
|---|---:|---:|---:|
| Parmesão | 80 g | R$ 0,08/g | R$ 6,40 |
| Maionese | 120 g | R$ 0,03/g | R$ 3,60 |
| Limão | 40 ml | R$ 0,02/ml | R$ 0,80 |

Custo total:

```text
6,40 + 3,60 + 0,80 = R$ 10,80
```

Rendimento:

```text
500 g
```

Custo por grama:

```text
10,80 / 500 = R$ 0,0216/g
```

---

### 10.3 Custo de prato

Exemplo:

Salada Caesar:

| Componente | Tipo | Quantidade | Custo unitário | Custo |
|---|---|---:|---:|---:|
| Alface | ingrediente | 120 g | R$ 0,018/g | R$ 2,16 |
| Molho Caesar | produção | 40 g | R$ 0,0216/g | R$ 0,86 |
| Croutons | produção | 25 g | R$ 0,025/g | R$ 0,63 |
| Parmesão | ingrediente | 15 g | R$ 0,080/g | R$ 1,20 |

Custo total:

```text
2,16 + 0,86 + 0,63 + 1,20 = R$ 4,85
```

---

### 10.4 Preço sugerido

Se o food cost desejado for 30%:

```text
preço sugerido = custo total / 0.30
```

Exemplo:

```text
4,85 / 0.30 = R$ 16,17
```

O sistema pode permitir arredondamento comercial:

- R$ 16,17 -> R$ 16,90;
- R$ 16,17 -> R$ 17,00;
- R$ 16,17 -> R$ 19,00.

Mas o arredondamento deve ser configurável.

---

## 11. Fluxo inicial do aplicativo

### 11.1 Primeira abertura

1. Usuário abre o aplicativo.
2. Sistema verifica se já existe pasta configurada.
3. Se não existir, mostra tela de boas-vindas.
4. Usuário escolhe onde salvar os dados.
5. Sistema cria a estrutura:

```text
data/
backups/
exports/
```

6. Sistema copia os templates CSV.
7. Sistema valida os arquivos.
8. Sistema abre o dashboard.

---

### 11.2 Aberturas seguintes

1. Sistema carrega a pasta configurada.
2. Sistema cria backup automático, se configurado.
3. Sistema valida todos os CSVs.
4. Se houver erro, mostra painel de problemas.
5. Se estiver tudo correto, abre dashboard.

---

## 12. Telas recomendadas para o MVP

### 12.1 Tela 1 — Configuração inicial

Objetivo:

- escolher pasta onde os CSVs serão salvos.

Campos:

- caminho da pasta;
- botão “Escolher pasta”;
- botão “Criar estrutura”.

---

### 12.2 Tela 2 — Dashboard

Cards:

- Ingredientes cadastrados;
- Produções internas;
- Pratos cadastrados;
- Pratos com custo desatualizado;
- Alertas de validação.

---

### 12.3 Tela 3 — Ingredientes

Tabela:

- nome;
- categoria;
- preço de compra;
- unidade de compra;
- custo por unidade base;
- perda;
- status.

Ações:

- novo ingrediente;
- editar ingrediente;
- atualizar preço;
- inativar.

---

### 12.4 Tela 4 — Produções internas

Tabela:

- nome;
- categoria;
- rendimento;
- custo total;
- custo por unidade;
- status.

Ações:

- nova produção;
- editar composição;
- recalcular custo.

---

### 12.5 Tela 5 — Pratos

Tabela:

- nome;
- categoria;
- custo;
- food cost desejado;
- preço sugerido;
- preço manual;
- margem estimada.

Ações:

- novo prato;
- editar ficha técnica;
- recalcular;
- exportar ficha técnica.

---

### 12.6 Tela 6 — Validação dos arquivos

Mostrar:

- arquivo;
- linha;
- campo;
- severidade;
- mensagem;
- sugestão de correção.

Exemplo:

```text
Arquivo: ingredients.csv
Linha: 12
Campo: purchase_price
Erro: valor inválido "abc"
Sugestão: informe um número, exemplo: 18.50
```

---

## 13. Convenções importantes

### 13.1 IDs

Não usar nome como identificador.

Usar IDs estáveis:

```text
ing_001
prep_001
dish_001
dc_001
```

Depois pode evoluir para UUID:

```text
ing_7f3a2c
```

Para o MVP, IDs legíveis ajudam muito no debug dos CSVs.

---

### 13.2 Números decimais

Recomendação técnica:

- salvar CSV com ponto decimal;
- exemplo: `18.50`;
- evitar vírgula decimal dentro do arquivo.

Motivo:

- reduz problema de parsing;
- facilita leitura pelo Python;
- evita ambiguidade com separador CSV.

Na interface, o sistema pode exibir conforme configuração regional depois.

---

### 13.3 Encoding

Salvar CSV como:

```text
UTF-8 with BOM
```

Motivo:

- costuma abrir melhor no Excel do Windows com acentos.

---

### 13.4 Separador

Para compatibilidade com Excel no Brasil, existem duas possibilidades:

Opção A:

```text
Separador: ,
Decimal: .
```

Mais simples para o Python.

Opção B:

```text
Separador: ;
Decimal: ,
```

Mais amigável para alguns Excels em português.

Recomendação para MVP:

```text
Separador: ,
Decimal: .
Encoding: UTF-8 with BOM
```

E depois, se necessário, criar exportação em formato regional.

---

## 14. Arquivos de configuração do projeto

### 14.1 `requirements.txt`

Sugestão inicial:

```txt
PySide6
pydantic
pandas
pytest
pyinstaller
python-dotenv
```

Observação:

- `pandas` é útil para leitura, análise e relatórios;
- para escrita controlada dos CSVs principais, eu prefiro o módulo `csv` do Python;
- `pydantic` deve validar dados;
- `pytest` deve testar regras de cálculo;
- `pyinstaller` deve gerar o executável Windows.

---

### 14.2 `pyproject.toml`

Sugestão:

```toml
[project]
name = "chef-pricing"
version = "0.1.0"
description = "Desktop app for restaurant dish costing and pricing"
requires-python = ">=3.12"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

---

## 15. Build para Windows

Objetivo:

Gerar um `.exe` para o usuário abrir sem instalar Python manualmente.

Comando base:

```bash
pyinstaller --noconfirm --windowed --name ChefPricing src/chef_pricing/main.py
```

Depois evoluir para arquivo `.spec`:

```text
packaging/pyinstaller/chef_pricing.spec
```

O build deve incluir:

- ícone;
- arquivos de estilo;
- templates de CSV;
- recursos visuais;
- dependências do PySide6.

---

## 16. Testes obrigatórios

### 16.1 Testes unitários

Testar:

- cálculo de custo de ingrediente;
- cálculo com perda;
- conversão de unidade;
- cálculo de produção interna;
- cálculo de prato;
- preço sugerido;
- margem estimada.

---

### 16.2 Testes de integração

Testar:

- leitura de CSV real;
- escrita de CSV real;
- validação de workspace;
- relação prato -> componentes;
- relação produção -> componentes;
- erro quando CSV é editado manualmente com dado inválido.

---

### 16.3 Casos de teste essenciais

#### Caso 1 — Ingrediente simples

Entrada:

```text
1 kg de tomate = R$ 12,00
```

Esperado:

```text
custo por g = R$ 0,012
```

---

#### Caso 2 — Ingrediente com perda

Entrada:

```text
1 kg de alface = R$ 18,00
perda = 10%
```

Esperado:

```text
custo efetivo por g = 0,018 / 0,90
```

---

#### Caso 3 — Prato com ingrediente e produção

Entrada:

```text
Salada Caesar usa alface + molho Caesar
```

Esperado:

```text
custo total = custo do alface usado + custo do molho usado
```

---

#### Caso 4 — CSV editado errado no Excel

Entrada:

```text
purchase_price = abc
```

Esperado:

```text
sistema bloqueia cálculo e mostra erro claro
```

---

## 17. Roadmap sugerido

### Fase 1 — Fundação

- criar estrutura do projeto;
- criar modelos de domínio;
- criar schemas CSV;
- criar leitura/escrita CSV;
- criar validação básica;
- criar cálculo de ingrediente;
- criar testes unitários.

---

### Fase 2 — Ingredientes

- tela de ingredientes;
- cadastro;
- edição;
- atualização de preço;
- histórico;
- validação.

---

### Fase 3 — Produções internas

- cadastro de produção;
- composição da produção;
- cálculo de custo;
- rendimento;
- custo por unidade.

---

### Fase 4 — Pratos

- cadastro de prato;
- composição do prato;
- cálculo de custo;
- preço sugerido;
- preço manual;
- margem estimada.

---

### Fase 5 — Workspace e CSV editável

- escolha de pasta;
- criação dos templates;
- validação ao abrir;
- painel de erros;
- backup automático.

---

### Fase 6 — Exportação e build

- exportar ficha técnica;
- exportar lista de pratos;
- gerar `.exe`;
- testar em Windows limpo.

---

## 18. Minha recomendação de MVP

Para não começar grande demais, eu construiria o MVP nesta ordem:

1. workspace local;
2. templates CSV;
3. validação dos CSVs;
4. cadastro de ingredientes;
5. cálculo de custo por unidade;
6. cadastro de produção interna;
7. composição de produção;
8. cadastro de prato;
9. composição de prato;
10. cálculo de custo;
11. preço sugerido;
12. exportação da ficha técnica;
13. build Windows.

Não começaria pela interface bonita.

Começaria pela regra de cálculo e persistência.

O sistema precisa ser confiável antes de ser bonito.

---

## 19. Decisão arquitetural final

A arquitetura recomendada é:

```text
PySide6 Desktop UI
        ↓
ViewModels
        ↓
Use Cases
        ↓
Domain Services
        ↓
Repositories
        ↓
CSV Storage
```

Resumo:

- front-end: PySide6;
- back-end: camada interna de aplicação, sem API HTTP;
- domínio: modelos e regras puras;
- armazenamento: múltiplos CSVs relacionais;
- validação: Pydantic + validadores próprios;
- testes: pytest;
- build: PyInstaller;
- sistema: offline, local, Windows-first.

---

## 20. Próximo passo recomendado

O próximo passo técnico é criar a primeira versão do repositório com:

- estrutura de pastas;
- `pyproject.toml`;
- templates CSV;
- modelos Pydantic;
- serviço de cálculo;
- repositórios CSV;
- testes unitários.

Antes de desenhar todas as telas, a prioridade deve ser validar a lógica central:

```text
ingrediente -> produção interna -> prato -> custo -> preço sugerido
```

Se essa espinha dorsal ficar sólida, a interface vira consequência.
