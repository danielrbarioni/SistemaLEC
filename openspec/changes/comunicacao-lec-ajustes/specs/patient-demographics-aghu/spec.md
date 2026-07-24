## MODIFIED Requirements

### Requirement: Busca de Dados Demográficos no AGHU para Inclusão
Na aba "Solicitar Inclusão" do menu Comunicação LEC, ao digitar o número do prontuário do paciente, o sistema DEVE buscar e preencher automaticamente Nome Completo, Data de Nascimento e Nome da Mãe a partir da integração com o AGHU (ou mock equivalente), sem cair no fallback genérico ("Paciente #prontuario") em condições normais de consulta.

#### Scenario: Preenchimento automático de dados do paciente via prontuário
- **WHEN** o usuário digita um número de prontuário válido na aba Solicitar Inclusão do menu Comunicação LEC
- **THEN** o sistema realiza a busca e preenche os campos Nome Completo, Data de Nascimento e Nome da Mãe com os dados retornados do AGHU

## ADDED Requirements

### Requirement: Restrição de Acesso ao Menu Comunicação LEC para Enfermeiros
O sistema DEVE impedir o acesso de usuários com a função Enfermeiro ao menu Comunicação LEC, informando que a funcionalidade é voltada aos perfis Médico e Residente.

#### Scenario: Enfermeiro tenta acessar o menu Comunicação LEC
- **WHEN** um usuário logado com perfil/função Enfermeiro tenta acessar a rota ou menu Comunicação LEC
- **THEN** o sistema bloqueia o acesso e exibe a mensagem informando que a funcionalidade é voltada aos perfis Médico e Residente

### Requirement: Acesso do perfil GESTÃO LEC às solicitações do Comunicação LEC
O sistema DEVE permitir que usuários com o perfil GESTÃO LEC acessem as abas de criação de solicitações (Solicitação de Inclusão, Edição, Standby e Exclusão) além da aba de Acompanhamento no menu Comunicação LEC.

#### Scenario: Usuário GESTÃO LEC acessa abas de solicitação
- **WHEN** um usuário com perfil GESTÃO LEC navega até o menu Comunicação LEC
- **THEN** o sistema disponibiliza o acesso completo às seções de Solicitação de Inclusão, Edição, Standby, Exclusão e Acompanhamento
