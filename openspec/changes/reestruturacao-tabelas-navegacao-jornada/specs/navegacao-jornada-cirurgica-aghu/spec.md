# Spec Delta

## Purpose

Reestrutura os painéis do módulo de Navegação da Jornada Cirúrgica em seis tabelas operacionais simétricas (Tabela 1.1 - Consulta EPO agendada, Tabela 1.2 - Consulta EPO não realizada, Tabela 2 - Consulta EPO realizada, Tabela 3.1 - APA agendada, Tabela 3.2 - APA não realizada e Tabela 4 - APA realizada), separando agendamentos para hoje/data futura das consultas não realizadas (faltas e agendamentos em data passada sem desfecho).

## ADDED Requirements

### Requirement: Separação das consultas EPO pendentes em Tabela 1.1 (agendada) e Tabela 1.2 (não realizada)
O sistema SHALL distribuir os pacientes no estágio de Consulta de Enfermagem Pré-Operatória (EPO) não concluída em duas tabelas distintas, ordenadas da data mais antiga para a mais recente: `Tabela 1.1 - Consulta EPO agendada` (contemplando somente consultas agendadas para hoje ou data futura) e `Tabela 1.2 - Consulta EPO não realizada` (contemplando faltas do paciente, faltas do profissional e consultas agendadas de data passada sem desfecho).

#### Scenario: Paciente com consulta EPO agendada para hoje ou data futura na Tabela 1.1
- **WHEN** o usuário visualiza a `Tabela 1.1 - Consulta EPO agendada`
- **THEN** o sistema exibe apenas os pacientes cuja consulta EPO mais recente está com status `Agendado` para hoje ou data futura (`dt_consulta >= hoje`), ordenados da data mais antiga para a mais recente

#### Scenario: Paciente com falta ou agendamento passado na Tabela 1.2
- **WHEN** o usuário visualiza a `Tabela 1.2 - Consulta EPO não realizada`
- **THEN** o sistema exibe os pacientes cuja consulta EPO mais recente possui status `Falta do paciente`, `Falta do profissional` ou `Agendado (Data Passada)`, permitindo filtrar individualmente por cada um desses status

### Requirement: Nomenclatura e composição da Tabela 2 (Consulta EPO realizada)
O sistema SHALL exibir o estágio de consultas EPO concluídas sob a nomenclatura `Tabela 2 - Consulta EPO realizada` (sem o sufixo `+ Exames/Pré-Op` no título), mantendo na tabela as colunas de cards de Exames Pré-Operatórios solicitados e Consultas Pré-Operatórias (`RIS`, `PPC`, `RCI`, `OHR`, `PPO`).

#### Scenario: Visualização da Tabela 2 - Consulta EPO realizada
- **WHEN** o usuário seleciona a `Tabela 2 - Consulta EPO realizada`
- **THEN** o sistema exibe o título `Tabela 2 — Consulta EPO realizada` e lista os pacientes no estágio EPO com status `Realizado`, acompanhados dos cards de exames pré-operatórios solicitados e consultas pré-operatórias

### Requirement: Separação da Avaliação Pré-Anestésica em Tabela 3.1 (APA agendada), Tabela 3.2 (APA não realizada) e Tabela 4 (APA realizada)
O sistema SHALL distribuir os pacientes no estágio de Avaliação Pré-Anestésica (APA) em três tabelas ordenadas da data mais antiga para a mais recente: `Tabela 3.1 - APA agendada` (somente APAs agendadas para hoje ou data futura), `Tabela 3.2 - APA não realizada` (faltas do paciente, faltas do profissional e APAs agendadas de data passada sem desfecho) e `Tabela 4 - APA realizada` (APAs com status `Realizado`).

#### Scenario: Visualização da Tabela 3.1 - APA agendada
- **WHEN** o usuário seleciona a `Tabela 3.1 - APA agendada`
- **THEN** o sistema exibe somente os pacientes no estágio APA cuja consulta mais recente possui status `Agendado` para hoje ou data futura (`dt_consulta >= hoje`)

#### Scenario: Visualização da Tabela 3.2 - APA não realizada
- **WHEN** o usuário seleciona a `Tabela 3.2 - APA não realizada`
- **THEN** o sistema exibe os pacientes no estágio APA cuja consulta mais recente possui status `Falta do paciente`, `Falta do profissional` ou `Agendado (Data Passada)`, permitindo filtrar por cada um desses status

#### Scenario: Visualização da Tabela 4 - APA realizada
- **WHEN** o usuário seleciona a `Tabela 4 - APA realizada`
- **THEN** o sistema exibe os pacientes no estágio APA com status `Realizado`, ordenados da data da APA mais antiga para a mais recente

### Requirement: Busca global de paciente atualizada para as 6 tabelas da jornada
O sistema SHALL pesquisar pacientes por prontuário ou nome em todas as 6 tabelas (`Tabela 1.1`, `Tabela 1.2`, `Tabela 2`, `Tabela 3.1`, `Tabela 3.2` e `Tabela 4`) e permitir navegar com um clique para a tabela correspondente já filtrada no prontuário.

#### Scenario: Localização de paciente na busca global das 6 tabelas
- **WHEN** o usuário digita um prontuário ou nome na Busca Global da Navegação
- **THEN** o sistema exibe em qual(is) das 6 tabelas (`1.1`, `1.2`, `2`, `3.1`, `3.2` ou `4`) o paciente se encontra com a respectiva nomenclatura atualizada
