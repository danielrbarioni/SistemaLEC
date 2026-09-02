# historico-pacientes-importacao Specification

## Purpose
TBD - created by archiving change ajustes-historico-pacientes-e-perfis. Update Purpose after archive.
## Requirements
### Requirement: Registro e Visualização de Importação de Planilha do Menu Pacientes
O sistema SHALL registrar e exibir as importações de procedimentos via planilha originadas do menu Pacientes com:
- Origem / Menu: `"Pacientes"`
- Ação: `"Inclusão de Procedimento"` (tag verde)
- Tipo de Evento: `"Importação"` (tag verde clara)

#### Scenario: Visualização e filtro por origem Pacientes
- **WHEN** o usuário filtra por Origem / Menu = "Pacientes" no Histórico
- **THEN** o sistema exibe os procedimentos importados por planilha e outras ações de pacientes com a tag de origem "Pacientes".

#### Scenario: Visualização do tipo de evento Importação
- **WHEN** um registro de procedimento originado de importação de planilha é exibido no Histórico
- **THEN** a coluna Tipo de Evento exibe a badge "Importação" estilizada em tom verde claro.

