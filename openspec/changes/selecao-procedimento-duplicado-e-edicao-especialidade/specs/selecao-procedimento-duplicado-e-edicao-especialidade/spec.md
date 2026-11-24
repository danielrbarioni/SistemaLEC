# Spec Delta

## Purpose

Permite selecionar e diferenciar individualmente procedimentos duplicados (mesmo procedimento e mesma especialidade) nas solicitações de Edição, Standby e Exclusão, além de permitir a alteração da especialidade de um procedimento na aba Solicitar Edição conforme os perfis do usuário.

## ADDED Requirements

### Requirement: Seleção individualizada de procedimentos duplicados em Edição, Standby e Exclusão
O sistema SHALL listar individualmente todas as instâncias ativas de procedimentos de um paciente ao buscar seu prontuário nas abas Solicitar Edição, Solicitar Standby e Solicitar Exclusão, mesmo quando houver dois ou mais registros com o mesmo procedimento e a mesma especialidade, diferenciando cada opção por Swalis, Médico Responsável e Data/Hora de Inserção.

#### Scenario: Paciente com mesmo procedimento duplicado na mesma especialidade
- **WHEN** o usuário busca o prontuário de um paciente nas abas Solicitar Edição, Solicitar Standby ou Solicitar Exclusão e o paciente possui dois ou mais procedimentos ativos com o mesmo nome e na mesma especialidade
- **THEN** o sistema exibe a caixa de seleção perguntando qual procedimento deseja editar, colocar em standby ou excluir, apresentando cada instância separadamente com suas informações de Especialidade, Swalis, Médico Responsável, Data/Hora de Inserção, Lateralidade e Categorização

#### Scenario: Atuação exclusiva sobre a instância selecionada do procedimento duplicado
- **WHEN** o usuário seleciona uma das instâncias do procedimento duplicado e envia uma solicitação de Edição, Standby ou Exclusão (e a Gestão LEC posteriormente a aprova)
- **THEN** o sistema vincula a solicitação à instância selecionada e aplica a edição, o standby ou a exclusão exclusivamente sobre aquela instância, mantendo as demais instâncias do paciente inalteradas

### Requirement: Alteração de especialidade na aba Solicitar Edição
O sistema SHALL permitir a alteração do campo Especialidade na aba Solicitar Edição quando o usuário possuir perfil `ADMIN`, `GESTAO_LEC`, ou quando o usuário possuir perfil cadastrado tanto na especialidade atual do procedimento quanto na especialidade de destino selecionada.

#### Scenario: Alteração de especialidade por usuário ADMIN ou GESTÃO LEC
- **WHEN** um usuário com perfil ativo `ADMIN` ou `GESTAO_LEC` busca um paciente na aba Solicitar Edição
- **THEN** o campo Especialidade fica habilitado com todas as especialidades cadastradas disponíveis para seleção

#### Scenario: Alteração de especialidade por usuário com múltiplos perfis de especialidade
- **WHEN** um usuário com perfil ativo de `ESPECIALIDADE` que possui vínculo de usuário em duas ou mais especialidades (incluindo a especialidade atual do procedimento) busca um paciente na aba Solicitar Edição
- **THEN** o campo Especialidade fica habilitado exibindo apenas as especialidades nas quais o usuário possui perfil cadastrado

#### Scenario: Bloqueio de alteração de especialidade para usuário com perfil em apenas uma especialidade
- **WHEN** um usuário que possui perfil cadastrado em apenas uma especialidade busca um paciente na aba Solicitar Edição
- **THEN** o usuário permanece restrito à sua única especialidade cadastrada, sem poder transferir o procedimento para outra especialidade na qual não possui perfil

#### Scenario: Efetivação e rastreabilidade da alteração de especialidade
- **WHEN** uma solicitação de edição contendo alteração de especialidade é enviada e aprovada pela Gestão LEC
- **THEN** o sistema registra a especialidade anterior e a nova especialidade na solicitação, exibe a transição de especialidade no acompanhamento e no histórico, e atualiza a especialidade do procedimento do paciente na fila ativa
