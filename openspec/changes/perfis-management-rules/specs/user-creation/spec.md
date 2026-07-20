## ADDED Requirements

### Requirement: Filtros e Colunas da Seção de Usuários Locais Cadastrados
O sistema SHALL exibir uma tabela com os usuários cadastrados e disponibilizar filtros por:
- Especialidade (seleção)
- Função (Médico, Residente, Enfermeiro)
- Nome (busca textual)
Para usuários com perfil `ADMIN` ou `GESTÃO LEC`, um filtro adicional por "Perfil ID" (tipo de perfil) SHALL ser disponibilizado.
A tabela de usuários cadastrados SHALL possuir uma coluna "Função" para indicar a função do usuário (Médico, Residente, Enfermeiro) quando seu perfil for do tipo Especialidade.
Usuários com perfil do tipo `Especialidade` SHALL obrigatoriamente visualizar apenas os usuários da sua própria especialidade (filtro fixado e não alterável).

#### Scenario: Filtros para perfis ADMIN e GESTAO LEC
- **WHEN** um usuário ADMIN ou GESTÃO LEC visualiza a tabela de usuários cadastrados
- **THEN** ele pode utilizar os filtros de Especialidade, Função, Nome e Perfil ID, e visualizar todos os usuários cadastrados no sistema.

#### Scenario: Filtros para perfil ESPECIALIDADE
- **WHEN** um usuário com perfil Especialidade (ex: Plástica) visualiza a tabela de usuários cadastrados
- **THEN** o sistema exibe apenas os usuários vinculados à especialidade "Plástica" e o filtro de Especialidade fica fixado e desabilitado para alteração.

### Requirement: Fluxo de Solicitação de Criação de Usuário
O sistema SHALL permitir que usuários com perfil do tipo `Especialidade` criem solicitações de criação de usuários para sua própria especialidade.
A seção de criação de usuário no frontend para o perfil de `Especialidade` SHALL ser renomeada para "Solicitar Criação de Usuário" e o campo "Perfil de Acesso" SHALL ser obrigatoriamente preenchido e travado na especialidade do perfil do usuário logado.
O envio deste formulário criará uma solicitação de criação de usuário no estado `PENDENTE`.

#### Scenario: Especialidade solicita criação de usuário
- **WHEN** um usuário com perfil "Plástica" preenche o formulário "Solicitar Criação de Usuário" com os dados do novo usuário e envia
- **THEN** uma solicitação pendente para a especialidade "Plástica" é criada no banco de dados.

### Requirement: Fluxo de Aprovação de Solicitação por ADMIN e GESTÃO LEC
O sistema SHALL exibir duas abas no topo da seção de gerenciamento de usuários para perfis `ADMIN` e `GESTÃO LEC`:
1. "Criar Usuário": Formulário de criação direta de usuários.
2. "Solicitações de Criação de Usuário": Lista de solicitações de criação com ações de "Aprovar" e "Rejeitar".
A aba "Solicitações de Criação de Usuário" e o menu/módulo "Perfis" no cabeçalho ou menu lateral SHALL exibir um alerta vermelho (badge com o número de solicitações pendentes) caso existam solicitações no estado `PENDENTE`.

#### Scenario: Admin aprova solicitação pendente
- **WHEN** um usuário ADMIN acessa a aba "Solicitações de Criação de Usuário", clica em "Aprovar" em uma solicitação pendente
- **THEN** o sistema cria o usuário local correspondente e altera o status da solicitação para aprovado, decrementando o contador de solicitações pendentes.

## MODIFIED Requirements

### Requirement: Layout e Ordem dos Campos na Criação de Usuário
A interface de gerenciamento de perfis SHALL posicionar a seção de criação de perfis ("Criar Novo Perfil") acima da seção de criação/solicitação de usuários ("Criar Usuário" / "Solicitar Criação de Usuário").
O formulário de criação/solicitação de usuário SHALL apresentar os seguintes campos na ordem indicada:
1. Usuário (campo de texto para o nome de usuário Ebserh)
2. Nome completo
3. Perfil de Acesso (seleção do perfil correspondente)
4. Função (campo de seleção com as opções Médico, Residente e Enfermeiro, exibido condicionalmente quando o perfil de acesso selecionado for do tipo `Especialidade`)

#### Scenario: Visualização do formulário de Criar Usuário com Perfil de Especialidade selecionado
- **WHEN** o formulário "Criar Usuário" é acessado por um ADMIN ou GESTÃO LEC e um perfil do tipo Especialidade é selecionado
- **THEN** o campo "Função" é exibido com as opções Médico, Residente e Enfermeiro.

### Requirement: Controle de Acesso para Criação de Usuário
O sistema SHALL permitir a criação/vínculo de usuários locais Ebserh com base no perfil do usuário autenticado atual, aplicando as seguintes restrições:
- Usuários com perfil `ADMIN` SHALL poder criar diretamente usuários de qualquer perfil, e aprovar/rejeitar quaisquer solicitações de criação de usuário.
- Usuários com perfil `GESTÃO LEC` SHALL poder criar diretamente usuários dos perfis `GESTÃO LEC` ou do tipo `Especialidade`. Se o perfil selecionado for do tipo `Especialidade`, a especialidade correspondente SHALL ser fornecida. Eles também SHALL poder aprovar/rejeitar solicitações de criação do tipo `Especialidade`.
- Usuários com perfil do tipo `Especialidade` SHALL apenas poder solicitar a criação de usuários vinculados à sua própria especialidade (ex: Plástica) através do fluxo de solicitação pendente.

#### Scenario: Admin cria usuário diretamente
- **WHEN** um usuário autenticado com perfil `ADMIN` solicita a criação direta de um usuário com perfil `ADMIN`
- **THEN** o sistema processa, cria e salva o usuário local com sucesso imediato.
