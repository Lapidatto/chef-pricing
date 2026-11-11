# AGENTS.md — Chef Pricing (desktop offline)

## Contexto
Aplicação desktop **Python 3.12+, PySide6 e armazenamento local** para custos de receitas, preparações, pratos e precificação; não depende da infraestrutura AWS Lapidatto. Antes de editar, ler `README.md`, `pyproject.toml`, `src/`, `tests/`, contrato de workspace e scripts relevantes.

## Invariantes de dados
- Preservar cálculo de food cost, desperdício, rendimento, conversão de unidades, preço histórico, margem e recálculo em cascata. Valores devem ser determinísticos e adequados à precisão monetária do modelo existente.
- CSV relacional com UTF-8 BOM, tipos, IDs/chaves, schema e backups/recovery não podem corromper dados existentes. Migração exige compatibilidade, backup e caminho de recuperação testável.
- A UI PySide6 não deve concentrar regras de negócio; separar validação, persistência, cálculo e apresentação. Testar casos negativos e dados legados antes de mudar algoritmos.
- Usar `pytest` e validadores de workspace descritos no README quando pertinente; testes de exemplo não substituem prova contra arquivos do usuário.
- Não fazer upload/sync, sobrescrever dados reais ou criar arquitetura cloud por suposição. Build/instalador requer confirmação específica de plataforma e ferramentas.
