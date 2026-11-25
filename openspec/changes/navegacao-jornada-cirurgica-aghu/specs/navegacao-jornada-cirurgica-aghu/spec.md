# Spec Delta

## Purpose

Disponibiliza o módulo de Navegação da Jornada Cirúrgica alimentado diretamente em modo leitura pelo AGHU, estruturado nas cinco tabelas de estágios (Consultas EPO Agendadas, Faltosas e Realizadas com Exames/Consultas Pré-Op, e Avaliações Pré-Anestésicas Não Realizadas e Realizadas), com busca global de paciente por prontuário e gerenciamento dinâmico das grades de consultas e grupos de exames pré-operatórios pela Gestão LEC.

## ADDED Requirements

### Requirement: Visibilidade do menu Navegação restrita ao perfil ADMIN
O sistema SHALL exibir o menu lateral Navegação e permitir o acesso à rota `/navegacao` exclusivamente quando o perfil ativo selecionado for `ADMIN`.

#### Scenario: Acesso ao menu Navegação pelo perfil ADMIN
- **WHEN** um usuário com perfil ativo `ADMIN` acessa o sistema e clica no menu Navegação
- **THEN** o sistema exibe os painéis operacionais da Navegação da Jornada Cirúrgica sem o bloqueio de "Funcionalidade em desenvolvimento"

### Requirement: Painéis de estágios de Consulta de Enfermagem Pré-Operatória (Tabelas 1, 2.1 e 2.2)
O sistema SHALL consultar no AGHU a consulta mais recente para cada par `(Prontuário + Grade EPO)` dentre as siglas de grades EPO configuradas (padrão inicial: `EPO`, `EPG`, `POO`, `OEP`, `POT`, `POF`) e distribuir os pacientes em: Tabela 1 (status Agendado), Tabela 2.1 (status Falta do paciente ou Falta do profissional) e Tabela 2.2 (status Realizado), ordenadas da data de consulta EPO mais antiga para a mais recente.

#### Scenario: Exibição e filtragem nas Tabelas 1 e 2.1
- **WHEN** o usuário visualiza a Tabela 1 (EPO Agendada) ou a Tabela 2.1 (EPO Faltosa)
- **THEN** o sistema exibe Nome do paciente, Prontuário, Grade da consulta EPO, Data da consulta EPO e Status da consulta EPO, permitindo filtrar por prontuário/nome, por grade(s) EPO e por intervalo de data da consulta EPO, ordenados da data mais antiga para a mais recente

#### Scenario: Exibição de exames e consultas pré-operatórias em cards na Tabela 2.2 (EPO Realizada)
- **WHEN** o usuário visualiza a Tabela 2.2 (Pacientes com consulta EPO realizada)
- **THEN** o sistema exibe, na linha de cada paciente, cards/badges compactos apenas para os exames pré-operatórios (dentre os grupos monitorados: Laboratório, Raio X, Espirometria, Ecocardiograma Transtorácico, Cintilografia Miocárdica, Ressonância Magnética, Holter 24h e Teste de Esteira) e consultas pré-operatórias (`RIS`, `PPC`, `RCI`, `OHR`, `PPO`) que foram ao menos solicitados/agendados para aquele paciente, mostrando o nome/sigla individual, o status mais recente e a respectiva data, além de permitir filtrar os pacientes por exame/consulta pré-op e situação de liberação

### Requirement: Painéis de estágios de Avaliação Pré-Anestésica (Tabelas 3.1 e 3.2)
O sistema SHALL consultar no AGHU a consulta mais recente para cada par `(Prontuário + Grade APA)` dentre as siglas de grades APA configuradas (padrão inicial: `ANE` e `TAN`) e distribuir os pacientes em: Tabela 3.1 (APA não realizada: status Agendado, Falta do paciente ou Falta do profissional, ordenada da data mais antiga para a mais recente) e Tabela 3.2 (APA realizada: status Realizado, ordenada da data mais recente para a mais antiga).

#### Scenario: Exibição e filtro de status na Tabela 3.1 (APA não realizada)
- **WHEN** o usuário visualiza a Tabela 3.1
- **THEN** o sistema exibe os pacientes com APA nos status Agendado, Falta do paciente ou Falta do profissional, permitindo filtrar por prontuário/nome, grade(s) da APA, intervalo de data e subconjunto desses status, ordenados da data de APA mais antiga para a mais recente

#### Scenario: Exibição na Tabela 3.2 (APA realizada)
- **WHEN** o usuário visualiza a Tabela 3.2
- **THEN** o sistema exibe os pacientes com APA no status Realizado, permitindo filtrar por prontuário/nome, grade(s) da APA e intervalo de data, ordenados da data de APA mais recente para a mais antiga

### Requirement: Busca global de paciente por prontuário em todos os estágios da jornada
O sistema SHALL permitir pesquisar um paciente específico por prontuário (ou nome) e indicar imediatamente em qual(is) das 5 tabelas/estágios (Tabelas 1, 2.1, 2.2, 3.1 e 3.2) o paciente se encontra.

#### Scenario: Paciente presente em uma ou mais tabelas da jornada cirúrgica
- **WHEN** o usuário pesquisa um prontuário na busca global da Navegação
- **THEN** o sistema exibe em quais tabelas/estágios o paciente consta atualmente (com a grade, data e status em cada estágio) e permite navegar diretamente para essas tabelas com o paciente filtrado

### Requirement: Gerenciamento dinâmico de grades de consultas e exames do circuito com busca no AGHU
O sistema SHALL permitir que usuários `ADMIN` e `GESTAO_LEC` visualizem e editem as grades de consultas (EPO, Pré-Operatórias e APA) e os grupos/siglas de exames pré-operatórios consultados na Navegação, oferecendo busca ao vivo diretamente no catálogo de grades/especialidades e exames do AGHU.

#### Scenario: Adição ou edição de grade de consulta ou exame via busca no AGHU
- **WHEN** o usuário abre a configuração do circuito cirúrgico na Navegação e pesquisa uma grade/sigla de especialidade ou exame no AGHU
- **THEN** o sistema lista as opções ativas encontradas no AGHU e permite incluí-las ou removê-las das categorias EPO, Consultas Pré-Op, APA ou dos Grupos de Exames Pré-Operatórios, atualizando imediatamente a consulta dos painéis
