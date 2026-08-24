## ADDED Requirements

### Requirement: Visualização Integral da Tabela de Usuários sem Barra de Rolagem
A tabela "Usuários Locais Cadastrados" no Menu Perfis SHALL ser renderizada com largura e layout responsivo adequados para que todas as colunas (`Nome / Username`, `Perfil ID`, `Especialidade`, `Função`, `Ações`) sejam exibidas simultaneamente sem ativar a barra de rolagem horizontal em resoluções padrão desktop.

#### Scenario: Visualização da lista de usuários locais cadastrados
- **WHEN** o usuário acessa o menu Perfis em um navegador com resolução desktop
- **THEN** a tabela de usuários cadastrados é apresentada com todas as colunas visíveis e sem barra de rolagem lateral horizontal.
