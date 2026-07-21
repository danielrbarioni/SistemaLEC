## 1. Ajustes no Backend

- [x] 1.1 Em `SolicitacaoSqliteProvider` e `SolicitacaoCsvProvider`, manter o registro da solicitação original e inserir novo registro para a Resposta.

## 2. Ajustes no Frontend (Historico.vue)

- [x] 2.1 Reordenar a grade de filtros: 1) Data De, 2) Data Até, 3) Origem/Menu, 4) Prontuário/Paciente, 5) Especialidade, 6) Ação, 7) Solicitação ou Resposta, 8) Status, 9) Usuário Executor.
- [x] 2.2 Carregar o filtro de Especialidade dinamicamente dos perfis do tipo `ESPECIALIDADE` via `usePerfisStore`.
- [x] 2.3 Alterar o rótulo do filtro e cabeçalho da tabela de "Ação / Tipo" para "Ação".
- [x] 2.4 Remover a palavra "Ebserh" do rótulo do filtro "Usuário Executor".

## 3. Validação e Deploy

- [x] 3.1 Recompilar o frontend (`npm run build`), validar o fluxo e realizar o deploy na VM.
