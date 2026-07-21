## ADDED Requirements

### Requirement: Gravação de Resposta como Novo Evento no Histórico
Quando uma solicitação for aprovada ou rejeitada por um gestor/administrador (ADMIN ou GESTÃO LEC), o sistema SHALL manter o registro original da solicitação e criar uma nova linha no Histórico representando o evento de Resposta.

#### Scenario: Avaliação de solicitação gera nova linha de Histórico
- **WHEN** um usuário ADMIN ou GESTÃO LEC aprova ou rejeita uma solicitação
- **THEN** o registro original da solicitação permanece gravado no Histórico
- **THEN** um novo registro de Resposta é inserido com a data/hora da decisão, o perfil executor e o usuário Ebserh responsável pela avaliação

### Requirement: Filtros de Busca Completos no Histórico
O menu Histórico de Solicitações/Respostas SHALL disponibilizar seletores e campos de texto para filtrar registros pelos seguintes parâmetros:
1. Especialidade
2. Data De
3. Data Até
4. Origem / Menu
5. Prontuário / Paciente (busca por texto)
6. Ação / Tipo
7. Solicitação ou Resposta (seletor)
8. Status
9. Usuário Executor (busca por texto em usuário Ebserh)

#### Scenario: Filtragem por múltiplos parâmetros
- **WHEN** o usuário seleciona ou digita valores nos filtros de busca do Histórico
- **THEN** a tabela exibe apenas os registros que satisfazem a todos os filtros informados simultaneamente
