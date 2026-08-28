## ADDED Requirements

### Requirement: Exibição da Data/Hora de Inserção no Menu Pacientes
O sistema SHALL exibir a data e hora de inserção na LEC para cada procedimento na tabela principal e no modal de detalhes do menu Pacientes.

#### Scenario: Visualização da data de inserção na tabela de pacientes
- **WHEN** o usuário acessa a tela de Pacientes
- **THEN** cada linha da tabela exibe a coluna "Data de Inserção" formatada no padrão `DD/MM/AAAA HH:mm` (ou `DD/MM/AAAA`).

#### Scenario: Visualização da data de inserção no modal de detalhes do paciente
- **WHEN** o usuário clica no prontuário ou nome de um paciente na tabela
- **THEN** o modal de detalhes exibe a "Data de Inserção" no quadro correspondente a cada procedimento vinculado ao paciente.

### Requirement: Reordenação Multi-Critério de Procedimentos
O sistema SHALL ordenar os procedimentos no menu Pacientes priorizando primeiro o nível de gravidade Swalis, em segundo lugar a data/hora de inserção mais antiga e, por fim, a ordem alfabética.

#### Scenario: Ordenação primária por Swalis
- **WHEN** múltiplos procedimentos estão listados
- **THEN** procedimentos com Swalis A1 aparecem antes de A2, que aparecem antes de B, C, D e procedimentos sem Swalis informado.

#### Scenario: Desempate cronológico por Data/Hora de Inserção
- **WHEN** dois procedimentos possuem a mesma classificação Swalis (ou ambos não possuem Swalis)
- **THEN** o procedimento com data e hora de inserção na LEC mais antiga (menor timestamp) é posicionado antes do procedimento com inserção mais recente.

#### Scenario: Desempate alfabético
- **WHEN** dois procedimentos possuem a mesma classificação Swalis e a mesma data/hora de inserção
- **THEN** os registros são ordenados alfabeticamente pelo nome do paciente (e subsequentemente pelo nome do procedimento) em conformidade com o idioma português (`pt-BR`).
