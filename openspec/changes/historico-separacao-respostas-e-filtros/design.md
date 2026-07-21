## Context

Atualmente a atualização de status de uma solicitação no backend substitui os atributos da própria solicitação. Para manter o histórico auditável completo, cada decisão (aprovação/rejeição) deve ser registrada como uma nova ocorrência (linha de histórico), vinculada ao prontuário e solicitação de origem.

Além disso, o formulário de filtros em `Historico.vue` deve ser expandido de 3 para 8 filtros.

## Goals / Non-Goals

**Goals:**
- Criar um novo evento no histórico ao aprovar/rejeitar uma solicitação em vez de sobrescrever o envio original.
- Adicionar os filtros no `Historico.vue`: Origem/Menu, Prontuário/Paciente, Ação/Tipo, Solicitação/Resposta, Status e Usuário Executor.

**Non-Goals:**
- Alteração estrutural em outros módulos da aplicação.

## Decisions

1. **Separação de Eventos de Resposta**:
   - Ao executar a resposta de uma solicitação via `/api/solicitacoes/{id}/status`, a solicitação original é atualizada para manter o fluxo operacional e um novo registro com `is_resposta = True` (ou `tipo_evento = 'RESPOSTA'`) é adicionado com os dados do avaliador (perfil executor e usuário Ebserh).

2. **Interface de Filtros Expandida**:
   - Atualizar a lista de filtros em `Historico.vue` com grid responsivo e reatividade em `solicitacoesFiltradas`.
