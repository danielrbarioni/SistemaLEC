## ADDED Requirements

### Requirement: Múltiplos Perfis para o Mesmo Usuário
O sistema SHALL permitir que um mesmo usuário Ebserh (`username`) seja cadastrado em mais de um perfil ou especialidade diferente, com funções específicas em cada perfil (ex: Médico em Cirurgia Geral e Médico em Cirurgia Plástica). A restrição de unicidade no cadastro de usuários SHALL ser aplicada exclusivamente ao par `(username, perfil_id)`.

#### Scenario: Cadastro do mesmo médico em segunda especialidade
- **WHEN** um administrador ou usuário de gestão cadastra o usuário `marcelo.mendonca` (já cadastrado em Oftalmologia) no perfil `CIRURGIA_GERAL`
- **THEN** o sistema SHALL criar o novo registro com sucesso, associando o usuário ao segundo perfil sem acusar duplicidade.

#### Scenario: Tentativa de cadastro duplicado no mesmo perfil
- **WHEN** um usuário tenta cadastrar o usuário `marcelo.mendonca` novamente no perfil `OFTALMOLOGIA`
- **THEN** o sistema SHALL rejeitar a operação informando que o usuário já está cadastrado neste mesmo perfil.

### Requirement: Alternância de Perfil pelo Usuário Multi-Especialidade
O sistema SHALL identificar no momento do login todos os perfis aos quais o usuário logado possui vínculo. Caso o usuário possua mais de um perfil ativo cadastrado, a interface SHALL disponibilizar um seletor de perfil (no cabeçalho superior e/ou no menu Perfis), permitindo que o usuário alterne instantaneamente seu perfil em uso sem necessidade de relogar.

#### Scenario: Alternância entre especialidades pelo médico
- **WHEN** um médico cadastrado em Cirurgia Geral e Cirurgia Plástica clica para alternar o perfil ativo para "Plástica"
- **THEN** o sistema SHALL atualizar o perfil ativo, ajustando as permissões, visualização de filas e formulários para o escopo da Cirurgia Plástica.
