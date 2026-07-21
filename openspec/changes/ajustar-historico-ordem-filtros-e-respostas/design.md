## Context

Refinamento da lógica de aprovação para manter 2 entradas no Histórico (Solicitação PENDENTE + Resposta APROVADO/REJEITADO) e ajuste da grade de filtros com suporte a especialidades dinâmicas do `usePerfisStore`.

## Goals / Non-Goals

**Goals:**
- Manter solicitação original como PENDENTE ao aprovar/rejeitar e criar o registro de Resposta.
- Reordenar os filtros em `Historico.vue` na ordem solicitada: Data De, Data Até, Origem/Menu, Prontuário/Paciente, Especialidade, Ação, Solicitação ou Resposta, Status, Usuário Executor.
- Carregar o filtro de Especialidades dinamicamente dos perfis cadastrados do tipo `ESPECIALIDADE`.
- Remover a palavra "Tipo" do cabeçalho da coluna e rótulo do filtro de Ação.

## Decisions

1. **Persistência de Respostas Independentes**:
   - Não alterar o atributo `status` da solicitação original para que ela continue registrada como PENDENTE.
   - Criar uma nova instância no banco com `evento_tipo = 'RESPOSTA'`, `status = 'APROVADO'` (ou `'REJEITADO'`).

2. **Dinamismo das Especialidades**:
   - Importar `usePerfisStore` em `Historico.vue` e extrair as especialidades únicas de perfis onde `tipo === 'ESPECIALIDADE'`.
