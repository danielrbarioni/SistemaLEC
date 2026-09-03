## ADDED Requirements

### Requirement: Identificação Exata do Procedimento em Edição para Múltiplos Procedimentos
Em pacientes que possuem mais de um procedimento na mesma especialidade (seja com cirurgiões diferentes ou procedimentos distintos), o sistema SHALL identificar e vincular a edição exatamente ao procedimento selecionado pelo usuário, garantindo que o cálculo de diff e a gravação da solicitação comparem e alterem apenas os campos do procedimento selecionado, sem gerar falsas alterações de cirurgião ou parâmetros de outros procedimentos do paciente.

#### Scenario: Edição de um procedimento em paciente com dois procedimentos de cirurgiões distintos
- **WHEN** o paciente possui Procedimento A com Cirurgião João e Procedimento B com Cirurgião Mateus, e o usuário seleciona o Procedimento A para editar apenas a categorização
- **THEN** a solicitação de edição gerada SHALL manter o cirurgião como João e NÃO SHALL indicar mudança de cirurgião no diff de aprovação nem no histórico

### Requirement: Carregamento Fiel da Categorização Aprovada na Edição
Quando um procedimento possuir uma categorização profissional previamente aprovada e vinculada no banco de dados, a abertura do formulário de edição desse procedimento SHALL preencher automaticamente o campo de categorização com a categoria atualmente atribuída, em vez de redefinir para "sem categorização".

#### Scenario: Reedição de procedimento com categorização já cadastrada
- **WHEN** um procedimento possui a categoria `"Cirurgia Complexa"` aprovada e o usuário clica em "Solicitar Edição" para esse procedimento
- **THEN** o campo de seleção de categorização profissional no formulário de edição SHALL iniciar selecionado com `"Cirurgia Complexa"`
