## ADDED Requirements

### Requirement: Gestão de Categorizações por Médico e Especialidade
O sistema DEVE permitir que usuários com perfil `ADMIN` e `GESTAO_LEC` criem, visualizem, editem, renomeiem e excluam listas personalizadas de categorias para cada médico em cada especialidade em que ele atua.

#### Scenario: Visualização da coluna Categorização no Menu Perfis
- **WHEN** um usuário com perfil `ADMIN` ou `GESTAO_LEC` acessa o menu Perfis
- **THEN** uma coluna "Categorização" é exibida para os médicos, indicando se possuem ou não categorias cadastradas na especialidade com botão para criar ou gerenciar.

#### Scenario: Criação de categorias para um médico em uma especialidade
- **WHEN** o administrador abre o modal de categorização e insere uma lista de categorias para um médico e especialidade
- **THEN** o sistema salva o conjunto de categorias vinculado exclusivamente àquela combinação de médico e especialidade.

#### Scenario: Renomeação de uma categoria existente
- **WHEN** o administrador edita o nome de uma categoria existente para um médico e especialidade
- **THEN** o sistema atualiza o nome da categoria no conjunto e atualiza automaticamente todos os procedimentos (solicitações e registros de pacientes) vinculados àquela categoria anterior para o novo nome.

#### Scenario: Exclusão de categoria individual ou exclusão total
- **WHEN** o administrador solicita a exclusão de uma categoria ou de toda a categorização de um médico/especialidade
- **THEN** o sistema exibe um diálogo de confirmação alertando que os procedimentos vinculados perderão a categorização, e, após confirmação, desvincula os procedimentos (`categorizacao = NULL`).

---

### Requirement: Exibição e Seleção Condicional em Solicitações LEC
O sistema DEVE exibir o campo de seleção de "Categorização Profissional" nas abas de Inclusão e Edição de solicitações apenas quando o médico e a especialidade selecionados possuírem categorias cadastradas.

#### Scenario: Seleção de médico com categorização na inclusão/edição
- **WHEN** o usuário seleciona um médico e uma especialidade que possuem categorização cadastrada
- **THEN** o campo "Categorização Profissional" é exibido com as opções cadastradas para aquele médico na especialidade.

#### Scenario: Seleção de médico sem categorização
- **WHEN** o usuário seleciona um médico ou especialidade que não possui categorização cadastrada
- **THEN** o campo de categorização profissional permanece oculto.

#### Scenario: Alteração de médico em solicitação de edição
- **WHEN** uma solicitação de edição de procedimento altera o médico responsável
- **THEN** a categorização anterior é automaticamente removida do procedimento.

---

### Requirement: Filtragem e Exibição de Categorização no Menu Pacientes
O sistema DEVE disponibilizar filtro dinâmico de categorização no menu Pacientes quando o médico e a especialidade filtrados possuírem categorias, e exibir a categorização correspondente nos detalhes do procedimento.

#### Scenario: Filtro por categoria no menu Pacientes
- **WHEN** o usuário filtra uma especialidade e um médico responsável que possuem categorização
- **THEN** o filtro "Categorização Profissional" torna-se visível, permitindo filtrar a fila de pacientes por uma categoria específica.

#### Scenario: Exibição de categorização no modal de detalhes do paciente
- **WHEN** o usuário clica em um paciente/procedimento para visualizar os detalhes
- **THEN** o modal exibe o campo "Categorização" junto ao médico responsável, mostrando o nome da categoria atribuída ou "Sem categorização".
