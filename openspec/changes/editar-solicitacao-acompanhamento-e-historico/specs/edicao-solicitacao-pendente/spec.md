## ADDED Requirements

### Requirement: Edição de Solicitação Pendente no Acompanhamento
O sistema SHALL permitir que usuários com perfis autorizados editem solicitações com status `PENDENTE` dos tipos `INSERIR`, `EDITAR` e `STANDBY` diretamente pela interface de Acompanhamento das Solicitações.

#### Scenario: Botão de edição disponível para solicitações pendentes
- **WHEN** o usuário visualizar a tabela de acompanhamento de solicitações pendentes dos tipos Inclusão, Edição ou Standby
- **THEN** o sistema SHALL exibir o botão "Editar" na coluna de Ações para cada solicitação pendente

#### Scenario: Bloqueio de edição para solicitações de exclusão
- **WHEN** o usuário visualizar solicitações do tipo Exclusão (`EXCLUIR`)
- **THEN** o sistema SHALL NÃO disponibilizar botão de edição, permitindo apenas a ação de cancelamento

#### Scenario: Carregamento dos dados no formulário em modo de edição
- **WHEN** o usuário clicar no botão "Editar" de uma solicitação pendente
- **THEN** o sistema SHALL alternar para a aba correspondente da solicitação, preencher os campos do formulário com os dados cadastrados, exibir banner de edição ativa e alterar o botão principal para "Salvar Alterações"

### Requirement: Preservação da Posição na Fila e Auditoria no Histórico
O sistema SHALL atualizar os dados da solicitação original mantendo a data e hora de criação originais, e registrar um novo evento de alteração no Histórico.

#### Scenario: Atualização dos dados preservando horário original de criação
- **WHEN** o usuário submeter as alterações de uma solicitação pendente
- **THEN** o sistema SHALL salvar os novos dados na solicitação existente, manter inalterado o valor de `data_criacao` original e preservar a ordem da solicitação na fila

#### Scenario: Registro do evento de alteração no Histórico
- **WHEN** uma solicitação for editada com sucesso
- **THEN** o sistema SHALL registrar no Histórico uma nova entrada com tipo de evento `ALTERACAO`, contendo a data/hora da edição e o usuário executor, permitindo visualizar tanto a solicitação inicial quanto a alteração realizada
