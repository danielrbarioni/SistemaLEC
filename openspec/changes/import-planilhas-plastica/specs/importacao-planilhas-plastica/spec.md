## ADDED Requirements

### Requirement: Importação de Solicitações da Plástica a partir de Planilhas
O sistema DEVE ser capaz de ler as planilhas Excel `Fila sistema Sede Plástica.xlsx` e `Procedimentos Plástica.xlsx`, cruzar o `id_procedimento` com a descrição do procedimento e popular o banco de dados SQLite local.

#### Scenario: Cruzamento e importação bem-sucedida
- **WHEN** o script de importação for executado
- **THEN** todas as solicitações válidas da planilha da Sede serão inseridas com status `APROVADO` para a especialidade `Plástica` e figurarão nos menus Pacientes, Sistema LEC e Histórico.
