# remove-unused-menus Specification

## Purpose
TBD - created by archiving change remove-unused-menus. Update Purpose after archive.
## Requirements
### Requirement: Remoção de menus e redirecionamento da raiz
O sistema SHALL redirecionar a rota principal e omitir itens de navegação não utilizados.

#### Scenario: Acessar a raiz do sistema
- **WHEN** o usuário acessar a URL raiz `/`
- **THEN** o sistema SHALL redirecionar para a tela do Sistema LEC (`/interacoes`)

#### Scenario: Visualizar menu lateral
- **WHEN** o menu de navegação for renderizado
- **THEN** o sistema SHALL ocultar os links para Home, Exemplos e Admin

