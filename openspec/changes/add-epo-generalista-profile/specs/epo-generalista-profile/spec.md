## ADDED Requirements

### Requirement: Perfil Padrão EPO GENERALISTA
O sistema MUST disponibilizar o perfil padrão `EPO GENERALISTA` (`EPO_GENERALISTA`), posicionado na lista de perfis do menu Perfis abaixo de `GESTÃO LEC` e acima das `ESPECIALIDADES`, representado visualmente pela cor laranja.

#### Scenario: Visualização do perfil EPO GENERALISTA na lista de perfis
- **WHEN** o usuário acessa o menu Perfis
- **THEN** o perfil `EPO GENERALISTA` é exibido abaixo de `Gestão LEC` e acima das especialidades com badge na cor laranja

### Requirement: Comportamento de Enfermeiro e Permissões sem Filtro de Especialidade
O perfil `EPO GENERALISTA` MUST possuir as permissões assistenciais de Enfermeiro (bloqueio no menu Comunicação LEC) e MUST ter acesso aos dados globais sem filtro de especialidade automático nos menus liberados.

#### Scenario: Acesso ao menu Comunicação LEC por usuário EPO GENERALISTA
- **WHEN** um usuário com perfil `EPO GENERALISTA` tenta acessar o menu Comunicação LEC
- **THEN** o sistema exibe a mensagem/modal de Acesso Restrito voltado para Enfermeiros e bloqueia a criação/alteração de solicitações

#### Scenario: Consulta de Pacientes por usuário EPO GENERALISTA
- **WHEN** um usuário com perfil `EPO GENERALISTA` acessa o menu Pacientes
- **THEN** o sistema exibe por padrão os registros de todas as especialidades sem filtro automático restritivo
