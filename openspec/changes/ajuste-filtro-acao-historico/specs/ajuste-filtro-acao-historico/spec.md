## ADDED Requirements

### Requirement: Remoção da Ação Solicitação APA do Filtro do Histórico
O menu **Histórico** NÃO DEVE exibir a opção `Solicitação APA` (`SOLICITAR_APA`) no dropdown do filtro **Ação** (`#filtroAcaoTipo`).

#### Scenario: Usuário abre o filtro Ação no menu Histórico
- **WHEN** o usuário acessa o menu `Histórico` e abre o seletor do filtro `Ação`
- **THEN** o grupo `Menu Solicitações LEC ou Pacientes` exibe apenas `Inclusão de Procedimento`, `Edição de Procedimento`, `Standby de Procedimento` e `Exclusão de Procedimento`, sem a opção `Solicitação APA`.

### Requirement: Inclusão e Estilização da Ação Edição de Perfil no Histórico
O menu **Histórico** DEVE disponibilizar a opção `Edição de Perfil` (`EDITAR_PERFIL`) no filtro **Ação** (dentro do grupo `Menu Usuários`), exibir o badge correspondente na tabela e no modal de detalhes com fundo lilás e letra azul (`bg-purple-100 text-blue-800 border border-purple-300`), e o backend DEVE registrar o evento `EDITAR_PERFIL` no histórico sempre que um perfil for editado.

#### Scenario: Visualização e filtragem de Edição de Perfil no Histórico
- **WHEN** um perfil é editado no menu `Usuários` ou o usuário seleciona `Edição de Perfil` no filtro `Ação` do menu `Histórico`
- **THEN** o registro é listado com o badge `Edição de Perfil` estilizado com fundo lilás (`bg-purple-100`), borda lilás (`border-purple-300`) e texto azul (`text-blue-800`).

