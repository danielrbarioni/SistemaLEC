# Spec Delta

## Purpose

Garante a integridade da fila cirúrgica (LEC) bloqueando, com mensagens de erro claras, o envio ou atualização de solicitações duplicadas para a mesma dupla de paciente e procedimento nas operações de Inclusão, Edição, Standby e Exclusão.

## ADDED Requirements

### Requirement: Bloqueio de solicitação de inclusão para paciente e procedimento já cadastrados na fila
O sistema SHALL impedir a criação ou atualização de uma solicitação de inclusão (`INSERIR`) quando a dupla `paciente + procedimento` já existir ativamente no cadastro de `Pacientes`, exibindo mensagem de erro clara ao usuário.

#### Scenario: Tentativa de solicitar inclusão para paciente e procedimento já existentes em Pacientes
- **WHEN** o usuário tenta enviar uma solicitação de inclusão (`INSERIR`) para um paciente e procedimento cuja dupla já está ativa no banco de dados (`Pacientes`)
- **THEN** o sistema SHALL bloquear o envio da solicitação e exibir uma mensagem de erro informando que o paciente já possui este procedimento cadastrado em Pacientes

#### Scenario: Solicitação de inclusão de procedimento distinto para paciente já cadastrado
- **WHEN** o usuário envia uma solicitação de inclusão (`INSERIR`) para um paciente que já possui outro procedimento diferente na fila, mas não possui o procedimento solicitado nem solicitação pendente para ele
- **THEN** o sistema SHALL permitir o registro da solicitação normalmente

### Requirement: Bloqueio de solicitação de inclusão quando já houver inclusão pendente
O sistema SHALL impedir a criação ou atualização de uma solicitação de inclusão (`INSERIR`) quando já existir outra solicitação de inclusão com status `PENDENTE` para a mesma dupla `paciente + procedimento`, exibindo mensagem de erro clara.

#### Scenario: Tentativa de solicitar inclusão com outra solicitação de inclusão pendente para a mesma dupla
- **WHEN** o usuário tenta enviar uma solicitação de inclusão (`INSERIR`) para um paciente e procedimento que já possuem solicitação de inclusão com status `PENDENTE`
- **THEN** o sistema SHALL bloquear o envio e exibir uma mensagem de erro informando que já existe uma solicitação de inclusão pendente para este paciente e procedimento

### Requirement: Bloqueio de solicitação de edição quando já houver edição pendente
O sistema SHALL impedir a criação ou atualização de uma solicitação de edição (`EDITAR`) para uma dupla `paciente + procedimento` que já possua outra solicitação de edição com status `PENDENTE`, exibindo mensagem de erro clara.

#### Scenario: Tentativa de solicitar edição para paciente e procedimento com edição pendente
- **WHEN** o usuário tenta enviar uma solicitação de edição (`EDITAR`) para um paciente e procedimento que já possuem uma solicitação de edição com status `PENDENTE`
- **THEN** o sistema SHALL bloquear o envio e exibir uma mensagem de erro informando que já existe uma solicitação de edição pendente para este paciente e procedimento

#### Scenario: Tentativa de alterar procedimento na edição para um procedimento já existente ou com inclusão pendente
- **WHEN** o usuário tenta enviar uma solicitação de edição (`EDITAR`) alterando o procedimento para outro que o mesmo paciente já possui ativamente em `Pacientes` ou com inclusão pendente
- **THEN** o sistema SHALL bloquear o envio e exibir uma mensagem de erro informando a duplicidade da dupla paciente e procedimento

### Requirement: Bloqueio de solicitação de standby quando já houver standby pendente
O sistema SHALL impedir a criação ou atualização de uma solicitação de standby (`STANDBY` ou `CANCELAR_STANDBY`) para uma dupla `paciente + procedimento` que já possua solicitação de standby com status `PENDENTE`, exibindo mensagem de erro clara.

#### Scenario: Tentativa de solicitar standby para paciente e procedimento com standby pendente
- **WHEN** o usuário tenta enviar uma solicitação de standby para um paciente e procedimento que já possuem uma solicitação de standby com status `PENDENTE`
- **THEN** o sistema SHALL bloquear o envio e exibir uma mensagem de erro informando que já existe uma solicitação de standby pendente para este paciente e procedimento

### Requirement: Bloqueio de solicitação de exclusão quando já houver exclusão pendente
O sistema SHALL impedir a criação de uma solicitação de exclusão (`EXCLUIR`) para uma dupla `paciente + procedimento` que já possua solicitação de exclusão com status `PENDENTE`, exibindo mensagem de erro clara.

#### Scenario: Tentativa de solicitar exclusão para paciente e procedimento com exclusão pendente
- **WHEN** o usuário tenta enviar uma solicitação de exclusão (`EXCLUIR`) para um paciente e procedimento que já possuem uma solicitação de exclusão com status `PENDENTE`
- **THEN** o sistema SHALL bloquear o envio e exibir uma mensagem de erro informando que já existe uma solicitação de exclusão pendente para este paciente e procedimento

