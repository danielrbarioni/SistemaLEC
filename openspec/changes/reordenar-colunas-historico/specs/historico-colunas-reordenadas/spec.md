## ADDED Requirements

### Requirement: Ordenação Correta das Colunas da Tabela no Menu Histórico
A tabela do menu Histórico SHALL apresentar exatamente 8 colunas com cabeçalhos e células alinhados na seguinte sequência:
1. Data/Hora
2. Origem/Menu
3. Prontuário/Paciente
4. Especialidade/Procedimento
5. Ação/Tipo
6. Solicitação ou Resposta
7. Status
8. Perfil executor/Usuário Executor

#### Scenario: Visualização correta dos dados no Histórico
- **WHEN** o usuário navega até a página de Histórico
- **THEN** a tabela exibe a coluna Data/Hora na 1ª posição
- **THEN** a coluna Origem/Menu é exibida na 2ª posição
- **THEN** a coluna Prontuário/Paciente é exibida na 3ª posição
- **THEN** a coluna Especialidade/Procedimento é exibida na 4ª posição
- **THEN** a coluna Ação/Tipo é exibida na 5ª posição
- **THEN** a coluna Solicitação ou Resposta (detalhes/justificativa) é exibida na 6ª posição
- **THEN** a coluna Status é exibida na 7ª posição
- **THEN** a coluna Perfil executor/Usuário Executor é exibida na 8ª posição
