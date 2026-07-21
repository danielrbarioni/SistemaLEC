## ADDED Requirements

### Requirement: Lista dinâmica de Especialidades no Sistema LEC a partir dos Perfis
O Sistema LEC DEVE carregar a lista de especialidades selecionáveis e filtráveis no menu Sistema LEC (Interações LEC) dinamicamente a partir dos perfis cadastrados no menu Perfis (`/api/perfis`), descontinuando o uso de listas estáticas hardcoded.

#### Scenario: Seleção de especialidades ativas
- **WHEN** o usuário abre o formulário de inclusão/edição ou filtro de especialidade no Sistema LEC
- **THEN** as opções exibidas no dropdown são geradas a partir da lista atual de especialidades dos perfis cadastrados no sistema
