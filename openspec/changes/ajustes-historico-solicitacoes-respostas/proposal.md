## Why

O menu **Histórico** requer ajustes essenciais de título, rastreabilidade e identificação dos usuários:
1. O título atual ("Histórico de Solicitações") deve ser renomeado para **"Histórico de Solicitações/Respostas"**.
2. A coluna **Solicitação ou Resposta** deve indicar explicitamente a natureza do evento (se aquele registro se refere ao envio de uma solicitação ou a uma resposta/decisão de aprovação/rejeição emitida por ADMIN/GESTÃO LEC).
3. Na coluna **Perfil executor / Usuário Executor**, o nome do usuário exibido deve ser o nome de usuário (usuário Ebserh) cadastrado no sistema (ex: `nome.sobrenome`).

## What Changes

- **Renomeação de Título**: Alterar o título principal em `Historico.vue` para **"Histórico de Solicitações/Respostas"**.
- **Identificação do Evento (Solicitação vs. Resposta)**: Exibir claramente um indicador/badge na 6ª coluna discriminando se o evento foi uma *Solicitação* ou uma *Resposta*, acompanhado do texto de justificativa/resposta.
- **Exibição do Usuário Executor**: Garantir que a propriedade `usuario` exiba o nome de usuário Ebserh (ex: `nome.sobrenome`), com fallback apropriado caso não esteja presente.

## Capabilities

### New Capabilities
- `historico-solicitacoes-respostas-ajustes`: Atualização do título, discriminação entre Solicitação vs. Resposta e exibição do usuário Ebserh no Histórico.

### Modified Capabilities
(Nenhuma)

## Impact

- **Frontend**: `frontend/src/views/Historico.vue`.
- **Backend**: `src/routers/solicitacao.py`, `src/providers/implementations/solicitacao_sqlite_provider.py`.
