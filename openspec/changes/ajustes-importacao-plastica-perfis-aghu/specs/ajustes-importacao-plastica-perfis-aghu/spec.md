## ADDED Requirements

### Requirement: Sanitização de Perfis Duplicados
O sistema DEVE possuir um único perfil cadastrado para a especialidade Plástica na tabela de perfis.

#### Scenario: Remoção de duplicatas de perfil
- **WHEN** o procedimento de higienização de perfis for executado
- **THEN** a tabela `perfis` conterá exatamente 1 registro para a especialidade Plástica com o ID `PLASTICA`.

### Requirement: Exibição Correta dos Contadores na Tela de Pacientes
O sistema DEVE exibir a contagem precisa do total de pacientes e do total de procedimentos/solicitações ativas.

#### Scenario: Visualização dos totais de pacientes e procedimentos
- **WHEN** o usuário acessar a tela de Pacientes
- **THEN** os cards de totalização exibirão a quantidade exata de pacientes cadastrados e o número total de solicitações vinculadas (2.364 solicitações).

### Requirement: Enriquecimento de Dados Cadastrais dos Pacientes via AGHU
O sistema DEVE buscar no banco de dados PostgreSQL do AGHU as informações reais do paciente (nome completo, data de nascimento, nome da mãe, CPF, sexo) a partir do número do prontuário.

#### Scenario: Atualização cadastral com dados do AGHU
- **WHEN** o script de sincronização com o AGHU for executado
- **THEN** os campos de nome, data de nascimento e nome da mãe dos pacientes serão atualizados no banco local com os dados provenientes do AGHU.
