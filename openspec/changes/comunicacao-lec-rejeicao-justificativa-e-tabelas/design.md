## Context

No menu **Comunicação LEC** (`InteracoesLec.vue`):
1. Quando a Gestão LEC rejeita uma solicitação, atualmente não há modal solicitando o motivo/justificativa clínica, e a solicitação é apenas marcada como `REJEITADO`.
2. Na sub-aba *Histórico Concluído (Aprovadas/Rejeitadas)*, os dados de solicitações concluídas listavam registros com `evento_tipo = "RESPOSTA"` isoladamente ou duplicados, e o botão `📄 Ver Descrição` exibia apenas os dados da solicitação original sem expor quem respondeu, quando respondeu e qual a justificativa da resposta/rejeição.
3. As tabelas do menu Comunicação LEC possuíam muitas colunas com larguras fixas ou `whitespace-nowrap`, gerando necessidade de rolagem horizontal incômoda.

## Goals / Non-Goals

**Goals:**
- **Modal de Rejeição**: Criar modal dedicado no frontend para captura obrigatória de `justificativa_rejeicao` antes de chamar o endpoint de atualização de status.
- **Backend**: Atualizar o endpoint `PUT /api/solicitacoes/{id_solicitacao}/status` (e `SolicitacaoSqliteProvider.atualizar_status_solicitacao`) para aceitar o campo opcional `justificativa` / `motivo_rejeicao` no payload da requisição, gravando esse texto no registro da resposta (`detalhes`) e na solicitação original (`justificativa_resposta`).
- **Unificação no Histórico Concluído**: Em `InteracoesLec.vue`, na sub-aba *Histórico Concluído*, desconsiderar linhas avulsas de `RESPOSTA` e unificar a solicitação com sua respectiva resposta (localizando a resposta pelo ID da solicitação original ou campos correspondentes), associando `data_acao`, `usuario_resposta`, `perfil_resposta` e `justificativa_resposta` no objeto da linha.
- **Modal de Descrição Completo**: Reformular o modal do botão `📄 Ver Descrição` para apresentar claramente dois blocos:
  1. *Dados da Solicitação*: Data/Hora, Solicitante (perfil/usuário), Prontuário, Paciente, Procedimento, Especialidade, Swalis, Judicialização e Justificativa da Solicitação.
  2. *Dados da Resposta (se concluída)*: Data/Hora da Ação, Executor da Resposta (perfil/usuário), Status (Aprovada/Rejeitada/Cancelada) e Justificativa da Rejeição / Observações da Gestão.
- **Layout Compacto e Barra de Rolagem Superior**:
  - Compactar padding, fontes e larguras das colunas para exibir as tabelas de Comunicação LEC sem scroll horizontal forçado em telas normais.
  - Implementar wrapper reutilizável com barra de rolagem sincronizada no topo para qualquer tabela que necessite de scroll horizontal.

**Non-Goals:**
- Alterar o menu Histórico Geral (`Historico.vue`), que continuará exibindo as duas linhas de auditoria (solicitação e resposta).

## Decisions

- **Decisão:** Manter a API REST compatível recebendo um body Pydantic opcional no endpoint de atualização de status:
  `class AtualizarStatusRequest(BaseModel): status: str, justificativa: Optional[str] = None`
  - *Razão:* Permite enviar a justificativa estruturada sem quebrar chamadas legadas que passam query params ou payload simples.
- **Decisão:** Na sub-aba *Histórico Concluído*, filtrar `s.evento_tipo !== 'RESPOSTA'` e associar os metadados da resposta daquele item:
  - *Razão:* Evita poluição de duas linhas na visão de acompanhamento da especialidade/gestão e reúne a história completa do procedimento em um único clique no modal de descrição.

## Risks / Trade-offs

- **[Risco]** Solicitações rejeitadas anteriormente sem justificativa gravada.
  - *Mitigação:* O modal exibirá *"Nenhuma justificativa detalhada registrada (rejeição anterior à implementação deste campo)"* caso o campo esteja vazio.
