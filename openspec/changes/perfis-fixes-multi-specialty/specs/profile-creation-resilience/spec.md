## ADDED Requirements

### Requirement: Resiliência e Prevenção de Colisões na Criação de Perfis
O endpoint de criação de perfis SHALL validar a unicidade de forma robusta e gerar identificadores primários (`id`) seguros e sanitizados (sem acentos e sem caracteres inválidos). Caso o identificador padrão já exista devido a edições anteriores, o sistema SHALL resolver a colisão gerando um identificador único ou retornando um erro 400 amigável e informativo, nunca gerando erro 500 ou falha silenciosa.

#### Scenario: Criação de especialidade após edição de especialidade legada
- **WHEN** um usuário com permissão cria uma especialidade cujo nome coincidiria com o ID de um perfil anteriormente editado
- **THEN** o sistema SHALL processar a criação com identificador único válido e registrar a especialidade com sucesso.

#### Scenario: Mensagem amigável em caso de duplicidade real
- **WHEN** um usuário tenta cadastrar uma especialidade que já existe exatamente com o mesmo nome
- **THEN** o sistema SHALL retornar erro 400 com mensagem clara: "Já existe um perfil cadastrado para a especialidade informada."
