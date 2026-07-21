## 1. Preservação de Solicitação e Registro Independente de Resposta

- [x] 1.1 Atualizar a API de atualização de status (`/api/solicitacoes/{id}/status`) para receber as informações do usuário avaliador e criar um novo registro no histórico para a Resposta (mantendo o registro original da Solicitação).
- [x] 1.2 Atualizar o frontend (`InteracoesLec.vue` e `Historico.vue`) para enviar os dados do perfil e usuário executor ao aprovar ou rejeitar uma solicitação.

## 2. Filtros Expandidos no Menu Histórico

- [x] 2.1 Em `frontend/src/views/Historico.vue`, adicionar a grade de filtros com os campos: Origem/Menu, Prontuário/Paciente, Ação/Tipo, Solicitação ou Resposta, Status e Usuário Executor.
- [x] 2.2 Atualizar a propriedade computada `solicitacoesFiltradas` em `Historico.vue` para aplicar a filtragem combinada de todos os campos.

## 3. Validação e Deploy

- [x] 3.1 Recompilar o frontend (`npm run build`), testar o fluxo de criação e resposta gerando duas linhas no histórico e validar os novos filtros.
- [x] 3.2 Atualizar o repositório Git e realizar o deploy na VM.
