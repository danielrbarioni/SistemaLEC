## ADDED Requirements

### Requirement: Confirmação para Inclusão de Prontuário Não Localizado no AGHU
O sistema SHALL exibir diálogo de confirmação quando a busca de um prontuário na aba de Inclusão (`INSERIR`) não retornar registro do AGHU.

#### Scenario: Exibição da pergunta de confirmação
- **WHEN** o usuário digitar um prontuário na aba de Inclusão e clicar em Buscar (ou teclar Enter) e o prontuário não for encontrado no AGHU
- **THEN** o sistema SHALL exibir um diálogo modal com a pergunta: `"Número de prontuário não identificado no AGHU. Deseja continuar com a solicitação de inclusão desse prontuário mesmo assim?"` e as opções `"Inserir novo prontuário"` e `"Continuar"`

#### Scenario: Usuário opta por "Inserir novo prontuário"
- **WHEN** o usuário clicar na opção `"Inserir novo prontuário"` no diálogo de confirmação
- **THEN** o sistema SHALL fechar o diálogo, apagar o prontuário digitado e reiniciar os campos do formulário para nova digitação

#### Scenario: Usuário opta por "Continuar"
- **WHEN** o usuário clicar na opção `"Continuar"` no diálogo de confirmação
- **THEN** o sistema SHALL fechar o diálogo, manter o número do prontuário, preencher o nome do paciente com `'Prontuário <x> não identificado no AGHU'` e habilitar o formulário para preenchimento e envio da solicitação

### Requirement: Backend Permite Inclusão com Nome Padronizado
O backend SHALL permitir o registro e edição de solicitações do tipo `INSERIR` com prontuário não localizado no AGHU desde que possua a identificação informada pelo fluxo de confirmação.

#### Scenario: Criação de solicitação com nome de contingência
- **WHEN** o frontend enviar uma solicitação do tipo `INSERIR` para um prontuário não existente no AGHU com o nome `'Prontuário <x> não identificado no AGHU'`
- **THEN** o backend SHALL aceitar e registrar a solicitação com sucesso
