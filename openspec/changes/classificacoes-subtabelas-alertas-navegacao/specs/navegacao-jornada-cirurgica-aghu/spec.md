# Spec Delta

## Purpose

Adiciona classificações operacionais por paciente nas tabelas da Navegação da Jornada Cirúrgica (Tabelas 1.2, 2, 3.2 e 4), segregando pacientes em subtabelas com alertas numéricos em vermelho para ações pendentes a serem ticadas, permitindo promover consultas realizadas sem baixa no AGHU (de 1.2 para 2 e de 3.2 para 4), respeitando o encadeamento temporal de novos eventos no AGHU, permitindo desfazer classificações e adicionando o monitoramento de consultas solicitadas pela APA na Tabela 4.

## ADDED Requirements

### Requirement: Segregação em subtabelas, alertas vermelhos e promoção nas Tabelas 1.2 e 3.2
O sistema SHALL permitir classificar pacientes da Lista Principal da `Tabela 1.2` (`Reagendar consulta EPO`, `Sem seguimento cirúrgico`, `Realizada (sem registro no AGHU)`) e da `Tabela 3.2` (`Reagendar consulta APA`, `Sem seguimento cirúrgico`, `Realizada (sem registro no AGHU)`), segregando-os em subtabelas com alerta vermelho para reagendamentos pendentes ou promovendo-os para a Lista Principal das Tabelas `2` e `4`.

#### Scenario: Classificação Reagendar consulta EPO na Tabela 1.2 ou Reagendar consulta APA na Tabela 3.2
- **WHEN** o usuário classifica um paciente da Lista Principal da `Tabela 1.2` como `Reagendar consulta EPO` (ou da `Tabela 3.2` como `Reagendar consulta APA`)
- **THEN** o paciente sai da Lista Principal, passa a constar na subtabela correspondente e incrementa o contador de alerta em vermelho até que a ação seja ticada como realizada na subtabela, permanecendo na subtabela até ocorrer novo evento no AGHU

#### Scenario: Classificação Realizada (sem registro no AGHU) na Tabela 1.2 ou Tabela 3.2
- **WHEN** o usuário classifica um paciente da `Tabela 1.2` (ou `Tabela 3.2`) como `Realizada (sem registro no AGHU)`
- **THEN** o paciente é enviado para a Lista Principal da `Tabela 2` (ou `Tabela 4`) com status equivalente ao de realizada e opção de desfazer a classificação

### Requirement: Segregação em subtabelas e alertas vermelhos nas Tabelas 2 e 4
O sistema SHALL permitir classificar pacientes da Lista Principal da `Tabela 2` (`Agendar consulta APA` e `Sem seguimento cirúrgico`) e da `Tabela 4` (`Paciente pronto no Sistema LEC` e `Sem seguimento cirúrgico`), segregando-os nas respectivas subtabelas e gerando alerta numérico em vermelho para `Agendar consulta APA` e `Paciente pronto no Sistema LEC` até que a ação seja ticada na subtabela.

#### Scenario: Classificação Agendar consulta APA na Tabela 2 ou Paciente pronto no Sistema LEC na Tabela 4
- **WHEN** o usuário classifica um paciente da Lista Principal da `Tabela 2` como `Agendar consulta APA` (ou da `Tabela 4` como `Paciente pronto no Sistema LEC`)
- **THEN** o paciente é movido para a subtabela correspondente, gera alerta vermelho de ação pendente e, após ser ticado como realizado, baixa o alerta vermelho permanecendo na subtabela até novo evento no AGHU ou saída da janela temporal

### Requirement: Encadeamento temporal automático e desfazimento de classificações
O sistema SHALL vincular cada classificação ao evento específico da consulta no AGHU (`numero_consulta` e `data_consulta`), retornando automaticamente o paciente para a Lista Principal caso ocorra uma nova consulta posterior no AGHU, e SHALL permitir desfazer manualmente qualquer classificação no próprio card da classificação.

#### Scenario: Novo evento no AGHU invalida classificação de evento anterior
- **WHEN** um paciente segregado em subtabela (ex.: `Sem seguimento cirúrgico` vinculado a uma consulta de `01/03/2026`) passa a ter uma nova consulta mais recente no AGHU (ex.: `01/08/2026`)
- **THEN** o sistema identifica que a classificação anterior pertence a um evento passado e exibe automaticamente o paciente na Lista Principal da tabela correspondente ao novo evento

#### Scenario: Desfazimento manual de classificação no card
- **WHEN** o usuário clica em desfazer classificação no card de um paciente em uma subtabela ou promovido via `Realizada (sem registro no AGHU)`
- **THEN** o sistema remove a classificação e retorna imediatamente o paciente para a Lista Principal e status em que estava antes

### Requirement: Monitoramento de Consultas solicitadas pela APA na Tabela 4
O sistema SHALL exibir na `Tabela 4 - APA realizada` a coluna `Consultas solicitadas pela APA` (com cards de sigla, nome completo da grade, status e data, além de filtros por situação e grade) e permitir configurar suas grades no modal `Consultas e Exames monitorados`.

#### Scenario: Configuração e exibição de consultas solicitadas pela APA na Tabela 4
- **WHEN** grades são adicionadas na categoria `Grades de Consultas Solicitadas pela APA` em `Consultas e Exames monitorados`
- **THEN** a `Tabela 4` exibe os cards das consultas solicitadas para cada paciente na coluna `Consultas solicitadas pela APA` e atualiza as opções dos filtros de situação e grade da `Tabela 4`
