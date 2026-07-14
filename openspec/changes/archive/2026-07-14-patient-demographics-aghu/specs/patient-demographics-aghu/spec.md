## ADDED Requirements

### Requirement: Exibição de Data de Nascimento e Nome da Mãe do paciente
O sistema SHALL exibir a data de nascimento e o nome da mãe do paciente como campos somente leitura logo abaixo da identificação básica.

#### Scenario: Buscar prontuário e visualizar dados adicionais
- **WHEN** o usuário buscar as informações de um prontuário válido no Sistema LEC
- **THEN** o sistema SHALL preencher e exibir os campos de Data de Nascimento e Nome da Mãe retornados da API
- **THEN** esses campos SHALL estar desabilitados para edição manual
