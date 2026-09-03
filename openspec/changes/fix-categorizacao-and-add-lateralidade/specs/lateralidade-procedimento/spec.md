## ADDED Requirements

### Requirement: Campo Lateralidade Cirúrgica em Procedimentos
O sistema SHALL armazenar a informação de Lateralidade para todos os procedimentos cirúrgicos dos pacientes e solicitações. Para procedimentos legados existentes no banco de dados que não possuíam essa informação, o sistema SHALL definir e exibir a lateralidade como `"Indefinida"`.

#### Scenario: Procedimento legado exibe lateralidade indefinida
- **WHEN** um usuário visualiza os dados ou o card de um procedimento cadastrado anteriormente sem lateralidade
- **THEN** o sistema SHALL exibir o valor `"Indefinida"` como lateralidade desse procedimento

### Requirement: Obrigatoriedade da Lateralidade na Inclusão e Edição
Ao criar uma nova solicitação de inclusão de procedimento (`INSERIR`) ou uma solicitação de alteração/edição (`EDITAR`), o campo `lateralidade` SHALL ser de preenchimento obrigatório pelo usuário, disponibilizando exatamente quatro opções válidas: `"lado esquerdo"`, `"lado direito"`, `"bilateral"` e `"não se aplica"`.

#### Scenario: Tentativa de inclusão sem selecionar lateralidade
- **WHEN** o usuário tentar submeter o formulário de inclusão sem selecionar uma das quatro opções de lateralidade
- **THEN** o sistema SHALL bloquear o envio e exibir mensagem de validação informando que a seleção de lateralidade é obrigatória

#### Scenario: Inclusão bem-sucedida com lateralidade
- **WHEN** o usuário seleciona `"lado direito"` e envia a solicitação de inclusão
- **THEN** o sistema SHALL registrar a solicitação com a lateralidade selecionada e, após aprovação, persistir `"lado direito"` no registro do paciente

### Requirement: Carregamento de Lateralidade na Edição de Procedimento
Ao abrir o formulário de edição para um procedimento existente, o campo de lateralidade SHALL ser automaticamente preenchido com a lateralidade atual do procedimento selecionado (seja uma das 4 opções ou `"Indefinida"` caso seja legado).

#### Scenario: Abertura do formulário de edição de procedimento existente
- **WHEN** o usuário seleciona um procedimento existente que possui lateralidade `"lado esquerdo"` para editar
- **THEN** o campo de seleção de lateralidade do formulário de edição SHALL ser inicializado com `"lado esquerdo"`
