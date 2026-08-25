## ADDED Requirements

### Requirement: Sincronização Dinâmica de Procedimentos do AGHU por Especialidade
O sistema DEVE carregar a lista de procedimentos cirúrgicos cadastrados no AGHU para o(s) código(s) da especialidade selecionada no formulário de inclusão/edição/standby/exclusão e filtros de pesquisa.

#### Scenario: Seleção de Especialidade Cirúrgica no Formulário
- **WHEN** o usuário seleciona uma especialidade (ex: Plástica, Ortopedia, Geral, Urologia, etc.) no formulário de Comunicação LEC ou Pacientes
- **THEN** o sistema consulta os procedimentos do AGHU pelo código da especialidade correspondente e disponibiliza a lista para seleção e busca com autocompletação.

#### Scenario: Fallback para Procedimentos Históricos e Base
- **WHEN** o AGHU estiver indisponível ou retornar vazio para uma especialidade
- **THEN** o sistema combina os procedimentos históricos cadastrados na base local de solicitações e pacientes sem interromper o fluxo do usuário.
