# specialty-procedures-aghu Specification

## Purpose
TBD - created by archiving change specialty-procedures-aghu. Update Purpose after archive.
## Requirements
### Requirement: Carregamento dinâmico de procedimentos por especialidade
O sistema SHALL carregar dinamicamente do AGHU a lista de procedimentos cirúrgicos ativos da especialidade selecionada.

#### Scenario: Selecionar especialidade Plástica (ID 1884)
- **WHEN** o usuário selecionar a especialidade Plástica no formulário de Interações LEC
- **THEN** o sistema SHALL disparar uma requisição para buscar procedimentos ativos (`ind_situacao = 'A'`) da especialidade 1884 no AGHU
- **THEN** o dropdown de procedimento SHALL apresentar a lista resultante do AGHU

