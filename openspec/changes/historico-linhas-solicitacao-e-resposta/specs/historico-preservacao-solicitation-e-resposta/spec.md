## ADDED Requirements

### Requirement: Preservação da Linha da Solicitação e Criação da Resposta
O sistema SHALL manter o registro da Solicitação original no histórico (com `evento_tipo = 'SOLICITACAO'`, data/hora original de envio e o usuário solicitante original), atualizando seu status de `PENDENTE` para `APROVADO` ou `REJEITADO` após a decisão na Gestão LEC. Simultaneamente, o sistema SHALL criar um novo registro independente para a Resposta (com `evento_tipo = 'RESPOSTA'`, data/hora exata da decisão, status `APROVADO` ou `REJEITADO` e o usuário executor que respondeu).

#### Scenario: Atualização de status com geração de duas linhas no histórico
- **WHEN** a Gestão LEC aprova ou rejeita uma solicitação pendente no sistema
- **THEN** a linha da solicitação original tem seu status atualizado para APROVADO ou REJEITADO mantendo o usuário solicitante original
- **AND** uma nova linha é criada no histórico com o evento RESPOSTA, data/hora atual e o usuário executor da aprovação/rejeição.
