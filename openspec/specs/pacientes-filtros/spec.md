# pacientes-filtros Specification

## Purpose
Fornece mecanismos de filtragem avançada de pacientes cadastrados no Sistema LEC, permitindo auditar e segmentar a fila cirúrgica por quantidade de procedimentos, especialidades vinculadas e detecção de procedimentos duplicados.

## Requirements

### Requirement: Filtro de pacientes com procedimento duplicado
O sistema SHALL permitir filtrar a lista de pacientes para exibir exclusivamente aqueles que possuem o mesmo procedimento cirúrgico cadastrado mais de uma vez na LEC.

#### Scenario: Ativação do filtro de procedimentos duplicados
- **WHEN** o usuário marca a opção "Exibir apenas pacientes com procedimento duplicado"
- **THEN** a tabela exibe apenas pacientes que possuam duas ou mais ocorrências do mesmo procedimento cirúrgico cadastrado

#### Scenario: Exclusividade entre filtros de procedimento
- **WHEN** o usuário marca a opção "Exibir apenas pacientes com procedimento duplicado"
- **THEN** as opções "Exibir apenas pacientes com 1 procedimento cadastrado" e "Exibir apenas pacientes com mais de 1 procedimento cadastrado" são desmarcadas

#### Scenario: Desativação do filtro
- **WHEN** o usuário desmarca a opção "Exibir apenas pacientes com procedimento duplicado"
- **THEN** a lista de pacientes deixa de filtrar por duplicidade de procedimentos

#### Scenario: Paciente com procedimentos distintos não é exibido
- **WHEN** o usuário ativa o filtro de procedimento duplicado e um paciente possui múltiplos procedimentos, porém todos com nomes diferentes
- **THEN** o paciente NÃO é exibido na lista filtrada
