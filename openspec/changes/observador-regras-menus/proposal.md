## Why

O perfil **OBSERVADOR** precisa ter suas permissões de visualização e ação refinadas de acordo com cada menu do Sistema LEC:
- **Comunicação LEC:** O usuário deve visualizar somente a seção "Acompanhamento das Solicitações" (com suporte a filtros), ocultando o formulário superior de envio de novas solicitações/alterações e bloqueando ações de aprovação/rejeição.
- **Navegação LEC:** Deve permitir navegação por especialidades e uso dos filtros, mas sem botão para solicitar APA.
- **Pacientes:** Acesso e consulta normais aos dados dos pacientes.
- **Histórico:** Acesso e consulta normais aos registros históricos.
- **Perfis:** Deve permitir visualizar a lista de perfis e usuários cadastrados, mas omitir/bloquear formulários e botões de adição/edição/exclusão/solicitação.

## What Changes

- **Frontend - Comunicação LEC (`InteracoesLec.vue`):** Ocultar o card de formulário de nova solicitação quando o perfil ativo for `OBSERVADOR`, exibindo diretamente a seção "Acompanhamento das Solicitações".
- **Frontend - Navegação LEC (`NavegacaoLec.vue`):** Permitir a utilização dos filtros e abas de especialidade, desabilitando/ocultando ações mutativas.
- **Frontend - Perfis (`Perfis.vue`):** Ocultar os formulários de cadastro/edição de usuário e botões de ação para o perfil `OBSERVADOR`.
- **Frontend - Pacientes & Histórico (`Pacientes.vue`, `Historico.vue`):** Garantir acesso normal em modo de consulta.

## Capabilities

### New Capabilities
- `observador-regras-menus`: Define o comportamento específico de exibição e bloqueio de ações para o perfil OBSERVADOR em cada menu do sistema.

### Modified Capabilities

## Impact

- `frontend/src/views/InteracoesLec.vue`: Ocultar formulário superior para perfil OBSERVADOR.
- `frontend/src/views/NavegacaoLec.vue`: Ocultar botões mutativos.
- `frontend/src/views/Perfis.vue`: Ocultar criação/edição de usuários.
- `frontend/src/views/Pacientes.vue` & `frontend/src/views/Historico.vue`: Manter exibição de consulta normal.
