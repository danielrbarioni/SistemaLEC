## ADDED Requirements

### Requirement: Registro Independente da Resposta sem Alterar a Solicitação Original
O backend SHALL manter o registro original da Solicitação como `PENDENTE` e criar um novo registro no Histórico especificamente marcado com `evento_tipo = 'RESPOSTA'`, `status = 'APROVADO'` ou `'REJEITADO'`.

#### Scenario: Visualização do histórico com 2 linhas após aprovação
- **WHEN** uma solicitação é aprovada no acompanhamento da Gestão LEC
- **THEN** a linha original da Solicitação permanece no Histórico com status PENDENTE e badge Solicitação
- **THEN** uma nova linha de Resposta surge no Histórico com status APROVADO, badge Resposta e o Usuário Executor que realizou a baixa

### Requirement: Reordenação dos Filtros do Histórico
O menu Histórico SHALL apresentar a grade de filtros na seguinte sequência exata: Data De, Data Até, Origem/Menu, Prontuário/Paciente, Especialidade (dinâmica por perfis do tipo Especialidade Cirúrgica), Ação, Solicitação ou Resposta, Status, Usuário Executor.

#### Scenario: Exibição dos filtros reordenados
- **WHEN** o usuário abre a página de Histórico
- **THEN** os campos de filtro são exibidos na ordem configurada e o rótulo "Ação / Tipo" é alterado para "Ação"
