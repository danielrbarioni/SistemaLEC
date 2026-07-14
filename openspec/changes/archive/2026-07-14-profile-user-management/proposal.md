## Why

Atualmente, o módulo de Perfis carece de restrições rígidas no cadastro de novos perfis e não oferece uma funcionalidade nativa para criação de novos usuários com controle de permissão baseado em papéis (RBAC). A adição de regras restritivas na criação de perfis e a criação da funcionalidade de criação de usuários por nível de acesso garantem a segurança e integridade do controle de perfis dentro da governança do Sistema LEC.

## What Changes

- Restrição de acesso à funcionalidade "Criar Perfil" apenas para usuários com perfil `ADMIN` e `GESTÃO LEC`.
- Correção de comportamento em "Criar Perfil": apenas será permitida a criação de perfis do tipo `Especialidade` (removendo opções de outros tipos e a paleta de seleção de cores, definindo a cor da especialidade criada de forma fixa como verde).
- Implementação da funcionalidade "Criar Usuário" com fluxo restrito por hierarquia de perfis:
  - `ADMIN`: pode criar usuários de qualquer perfil.
  - `GESTÃO LEC`: pode criar usuários do perfil `GESTÃO LEC` ou do tipo `Especialidade`.
  - `ESPECIALIDADE`: pode criar usuários vinculados unicamente à sua própria especialidade (ex: Plástica).

## Capabilities

### New Capabilities
- `user-creation`: Implementação do cadastro de novos usuários com restrições hierárquicas de perfil com base no usuário logado.

### Modified Capabilities
- `profile-creation-rules`: Modificação das regras e restrições de acesso/exibição na tela de criação de perfis existentes no sistema.

## Impact

- Modificações no frontend (módulo/tela de Perfis, formulário e controle de exibição de botões/campos).
- Ajustes no backend (endpoints de criação de perfil e novos endpoints de criação de usuário com validação de permissões).
- Atualizações no banco de dados SQLite local (tabela de usuários).
