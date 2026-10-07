# Spec Delta

## Purpose
Fornece rastreabilidade cronológica completa das ações realizadas para cada procedimento cirúrgico de um paciente no Sistema LEC, permitindo consultar datas, responsáveis e justificativas de inclusão, edições e períodos de standby.

## ADDED Requirements

### Requirement: Exibição da linha do tempo de ações por procedimento
O sistema SHALL exibir uma linha do tempo cronológica interativa para cada procedimento cirúrgico cadastrado do paciente dentro do modal de detalhes do menu Pacientes.

#### Scenario: Visualização da linha do tempo no card de procedimento
- **WHEN** o usuário abre o modal de detalhes de um paciente no menu Pacientes
- **THEN** cada card de procedimento exibe sua respectiva linha do tempo de ações ordenadas cronologicamente

### Requirement: Agregação de eventos históricos e justificativas
O sistema SHALL apresentar em cada evento da linha do tempo a data e hora, o tipo de ação, o responsável (usuário e perfil) e a justificativa textual registrada no momento da ação.

#### Scenario: Procedimento originado de importação ou inclusão manual
- **WHEN** o procedimento foi adicionado por importação de planilha Excel ou por solicitação de inserção
- **THEN** a linha do tempo exibe o evento de inclusão inicial contendo a data e os detalhes de inserção na fila

#### Scenario: Procedimento com solicitação de edição
- **WHEN** o procedimento passou por solicitações de alteração de dados
- **THEN** a linha do tempo exibe os eventos de alteração com datas, campos modificados e as justificativas informadas

#### Scenario: Procedimento submetido a standby ou retorno de standby
- **WHEN** o procedimento foi colocado em standby ou reativado
- **THEN** a linha do tempo exibe a data da ação, o prazo em dias e a justificativa registrada

### Requirement: Preservação de integridade de dados e integração contínua
A agregação da linha do tempo SHALL utilizar os registros existentes de solicitações e pacientes sem alterar o schema do banco de dados, incorporando novas ações futuras de forma automática e transparente.

#### Scenario: Registro de nova ação no sistema
- **WHEN** qualquer nova solicitação para o procedimento é criada ou atualizada no sistema
- **THEN** o evento é refletido na linha do tempo do procedimento correspondente sem modificações estruturais no banco de dados
