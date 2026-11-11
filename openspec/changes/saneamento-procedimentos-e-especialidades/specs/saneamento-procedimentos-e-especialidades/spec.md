## ADDED Requirements

### Requirement: Saneamento de Procedimentos Genéricos da Ginecologia Geral, Dermatologia e Geral
O sistema DEVE corrigir todos os registros de pacientes e solicitações nas tabelas `solicitacoes` e `pacientes` que receberam nomenclatura genérica (`PROCEDIMENTO <N>`) na importação inicial e possuem procedimento correspondente identificado na base do Sistema LEC / AGHU:
1. **Ginecologia Geral (`239` pacientes)**: substituir `PROCEDIMENTO 706`..`PROCEDIMENTO 983` pelo procedimento oficial do AGHU no formato `<NOME DO PROCEDIMENTO> (ID <pci_seq>)` correspondente ao paciente no Sistema LEC.
2. **Dermatologia (`33` pacientes)**: substituir `PROCEDIMENTO 966` por `BIOPSIA DE PELE E PARTES MOLES (ID 966)`.
3. **Geral (`1` paciente — Prontuário `11118031`)**: substituir `PROCEDIMENTO 326` por `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)`.

#### Scenario: Atualização dos 239 pacientes da Ginecologia Geral
- **WHEN** a rotina de saneamento é executada sobre a base de dados do Comunicação Cirúrgica
- **THEN** os 239 pacientes da especialidade `GINECOLOGIA GERAL` mapeados na planilha do Sistema LEC têm seu campo `procedimento` atualizado para `<NOME AGHU> (ID <pci_seq>)` nas tabelas `solicitacoes` e `pacientes`
- **AND** os procedimentos genéricos `PROCEDIMENTO 706`..`PROCEDIMENTO 983` deixam de ser exibidos no filtro de procedimentos do menu `Pacientes`.

#### Scenario: Atualização dos 33 pacientes da Dermatologia e 1 paciente da Geral
- **WHEN** a rotina de saneamento é executada sobre a base de dados do Comunicação Cirúrgica
- **THEN** todos os 33 pacientes da `DERMATOLOGIA` com `PROCEDIMENTO 966` passam a ter o procedimento `BIOPSIA DE PELE E PARTES MOLES (ID 966)`
- **AND** o paciente da `GERAL` (Prontuário `11118031`) com `PROCEDIMENTO 326` passa a ter o procedimento `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)`
- **AND** `PROCEDIMENTO 966` e `PROCEDIMENTO 326` deixam de ser exibidos no filtro de procedimentos do menu `Pacientes`.

### Requirement: Reclassificação dos Pacientes de Cirurgia Bariátrica da Geral para Bariátrica
O sistema DEVE alterar a especialidade dos 21 pacientes ativos que estão na especialidade `GERAL` com o procedimento `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` para a especialidade `BARIÁTRICA`.

#### Scenario: Transferência dos 21 pacientes para Bariátrica
- **WHEN** a rotina de saneamento é executada
- **THEN** os 21 pacientes com procedimento `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` que estavam em `GERAL` têm sua `especialidade` atualizada para `BARIÁTRICA` nas tabelas `solicitacoes` e `pacientes`.

### Requirement: Propagação em Cascata ao Renomear Especialidade e Saneamento de `ONCO-MASTO`
Quando um perfil de especialidade (`tipo = 'ESPECIALIDADE'`) tiver seu nome de especialidade alterado através da edição de perfil (`PUT /api/perfis/{perfil_id}`), o sistema DEVE atualizar automaticamente todas as referências ao nome antigo da especialidade nas tabelas `usuarios`, `solicitacoes`, `pacientes` e `categorizacoes_profissionais`. Adicionalmente, todos os registros existentes com `especialidade = 'ONCO - MASTO'` DEVEM ser unificados para `'ONCO-MASTO'`, e registros de auditoria do menu `Usuários` NÃO DEVEM poluir os filtros do menu `Pacientes`.

#### Scenario: Unificação de ONCO - MASTO para ONCO-MASTO
- **WHEN** o usuário acessa o menu `Pacientes` e abre o filtro de Especialidade
- **THEN** apenas `ONCO-MASTO` é exibida (e nunca `ONCO - MASTO`).

#### Scenario: Renomeação futura de uma especialidade no menu Usuários
- **WHEN** um usuário `ADMIN` ou `GESTAO_LEC` edita o nome de uma especialidade existente no menu `Usuários` (aba Perfis)
- **THEN** o backend atualiza o nome da especialidade em `perfis`, `usuarios`, `solicitacoes`, `pacientes` e `categorizacoes_profissionais` na mesma transação
- **AND** o filtro de Especialidade do menu `Pacientes` exibe exclusivamente o novo nome da especialidade, migrando todos os pacientes e procedimentos vinculados para o novo nome.

