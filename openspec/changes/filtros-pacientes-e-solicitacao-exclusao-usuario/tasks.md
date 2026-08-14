# Tasks: Filtros de Judicialização e Swalis no Menu Pacientes e Fluxo de Solicitação de Exclusão de Usuários

- [x] 1. Backend (`src/routers/usuario.py`)
  - [x] 1.1 Atualizar `UserCreationRequestCreate` para suportar `tipo: Optional[str] = "CRIACAO"` (aceitando `"CRIACAO"`, `"EDICAO"`, `"EXCLUSAO"`).
  - [x] 1.2 Atualizar o endpoint `POST /api/usuarios/solicitacoes` para processar solicitações de exclusão (`tipo == "EXCLUSAO"`), realizando as devidas validações hierárquicas de perfil e armazenando a solicitação com `status = "PENDENTE"`.
  - [x] 1.3 Atualizar o endpoint `POST /api/usuarios/solicitacoes/{id}/aprovar` para, quando `tipo == "EXCLUSAO"`, localizar e excluir o usuário alvo (`User`) no banco de dados SQLite e atualizar a solicitação para `APROVADO`.
  - [x] 1.4 Atualizar o endpoint `POST /api/usuarios/solicitacoes/{id}/rejeitar` para tratar solicitações de exclusão sem apagar o usuário.

- [x] 2. Frontend Menu Pacientes (`frontend/src/views/Pacientes.vue`)
  - [x] 2.1 Adicionar referências reativas `filtroJudicializado` e `filtroSwalis`.
  - [x] 2.2 Adicionar os campos de seleção (select dropdowns) para **Judicialização** e **Swalis** na grade de filtros de `Pacientes.vue`.
  - [x] 2.3 Atualizar as propriedades computadas `pacientesProcessados` e `procedimentosFlat` para aplicar a filtragem por Judicialização e Swalis.

- [x] 3. Frontend Menu Perfis (`frontend/src/views/Perfis.vue`)
  - [x] 3.1 Atualizar a função `podeExcluirUsuario(user)` para permitir a ação de exclusão pelos perfis `EPO_GENERALISTA` e `ESPECIALIDADE`.
  - [x] 3.2 Atualizar a função `excluirUsuario(id)` ou criar handler para enviar a solicitação `POST /api/usuarios/solicitacoes` com `tipo: 'EXCLUSAO'` quando o perfil ativo for `EPO_GENERALISTA` ou `ESPECIALIDADE`.
  - [x] 3.3 Na lista de solicitações pendentes (aba **Solicitações**), renderizar a etiqueta vermelha `Exclusão` para solicitações do tipo `EXCLUSAO`.

- [x] 4. Verificação e Deploy
  - [x] 4.1 Testar os filtros de Judicialização e Swalis na tela de Pacientes.
  - [x] 4.2 Testar o envio de solicitação de exclusão por usuário com perfil ESPECIALIDADE/EPO GENERALISTA.
  - [x] 4.3 Testar a aprovação e rejeição de solicitação de exclusão por usuários ADMIN/GESTÃO LEC.
  - [x] 4.4 Realizar build e deploy das alterações para o ambiente local e VM.
