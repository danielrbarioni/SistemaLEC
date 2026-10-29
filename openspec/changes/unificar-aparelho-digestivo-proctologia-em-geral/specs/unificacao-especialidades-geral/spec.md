# Spec Delta

## Purpose

Garante que as especialidades Aparelho Digestivo e Proctologia sejam unificadas dentro da especialidade Geral em todo o sistema e no banco de dados SQLite, extinguindo os perfis separados e mantendo a consulta de procedimentos do AGHU de Geral vinculada ao código oficial de Cirurgia Geral (seq 33).

## ADDED Requirements

### Requirement: Unificação de perfis, usuários, pacientes e solicitações de Aparelho Digestivo e Proctologia em Geral
O sistema SHALL converter todos os registros de `Aparelho Digestivo` e `Proctologia` para `GERAL` nas tabelas de perfis, usuários, pacientes, solicitações e categorizações profissionais, removendo os perfis `Aparelho Digestivo` e `Proctologia` para que deixem de existir como especialidades separadas.

#### Scenario: Inicialização do sistema com registros de Aparelho Digestivo e Proctologia no banco
- **WHEN** a aplicação inicia e executa as migrações automáticas no banco de dados
- **THEN** o sistema SHALL migrar para `GERAL` todos os pacientes, solicitações e categorizações de `Aparelho Digestivo` e `Proctologia`
- **THEN** o sistema SHALL desduplicar os vínculos de usuários com `GERAL` e excluir os perfis `Aparelho Digestivo` e `Proctologia`

#### Scenario: Normalização de nomes de especialidades no backend e frontend
- **WHEN** qualquer rotina de normalização receber `Aparelho Digestivo` ou `Proctologia`
- **THEN** o sistema SHALL retornar `GERAL`

### Requirement: Manutenção do catálogo de procedimentos de Geral vinculado ao código 33 do AGHU
O sistema SHALL manter a especialidade `GERAL` mapeada exclusivamente ao código `33` (`CIRURGIA GERAL`) do AGHU após a extinção de `Aparelho Digestivo` e `Proctologia`.

#### Scenario: Consulta de procedimentos do AGHU para a especialidade Geral
- **WHEN** o usuário selecionar a especialidade `GERAL` para incluir ou editar um procedimento
- **THEN** o sistema SHALL consultar exclusivamente os procedimentos ativos da especialidade `33` (`CIRURGIA GERAL`) no AGHU

