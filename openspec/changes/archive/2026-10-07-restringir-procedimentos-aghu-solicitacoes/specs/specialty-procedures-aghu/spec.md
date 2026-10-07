# Spec Delta

## MODIFIED Requirements

### Requirement: Carregamento dinâmico de procedimentos por especialidade
O sistema SHALL carregar dinamicamente do AGHU a lista de procedimentos cirúrgicos ativos da especialidade selecionada e restringir o dropdown de novas solicitações e edições exclusivamente a esse catálogo oficial do AGHU.

#### Scenario: Selecionar especialidade Plástica (ID 1884)
- **WHEN** o usuário selecionar a especialidade Plástica no formulário de Interações LEC
- **THEN** o sistema SHALL disparar uma requisição para buscar procedimentos ativos (`ind_situacao = 'A'`) da especialidade 1884 no AGHU
- **THEN** o dropdown de procedimento SHALL apresentar a lista resultante do AGHU

#### Scenario: Restringir seleção a procedimentos oficiais do AGHU
- **WHEN** o usuário abrir o formulário de inclusão ou edição de Interações LEC
- **THEN** o sistema SHALL apresentar no dropdown de procedimento exclusivamente os procedimentos cirúrgicos ativos retornados pelo AGHU para a especialidade
- **THEN** o dropdown NÃO SHALL incluir procedimentos legados ou avulsos sem ID do histórico local

#### Scenario: Procedimento legado mantido em consultas e filtros
- **WHEN** o usuário consultar pacientes existentes no menu Pacientes
- **THEN** os procedimentos históricos já cadastrados permanecem com seus nomes originais
- **THEN** o filtro de procedimentos do menu Pacientes continua permitindo filtrar tanto procedimentos do AGHU quanto legados
