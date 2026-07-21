## 1. Backend (Providers de Solicitação)

- [x] 1.1 Atualizar `SolicitacaoSqliteProvider.atualizar_status_solicitacao` para manter a linha da solicitação original (com `evento_tipo = 'SOLICITACAO'` e usuário solicitante original) e atualizar seu status para `APROVADO` ou `REJEITADO`.
- [x] 1.2 Inserir no mesmo método uma nova entidade de `Solicitacao` com `evento_tipo = 'RESPOSTA'`, `status` correspondente, data/hora da resposta e `usuario = usuario_executor` (quem respondeu).
- [x] 1.3 Garantir a mesma lógica no `SolicitacaoCsvProvider.atualizar_status_solicitacao`.

## 2. Frontend (Historico.vue)

- [x] 2.1 Garantir a renderização correta das duas linhas distintas (Solicitação e Resposta) na tabela e aplicação de filtros.

## 3. Validação e Deploy

- [x] 3.1 Recompilar o frontend (`npm run build`), testar o fluxo de aprovação/resposta e implantar na VM.
