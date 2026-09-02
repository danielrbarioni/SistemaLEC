## ADDED Requirements

### Requirement: Registro de criação e exclusão de perfis no Histórico
O sistema SHALL registrar eventos de auditoria no Histórico sempre que um perfil for criado ou excluído.
- Na criação de perfil: Ação SHALL ser "Criação de Perfil" (estilizada com tag lilás), Tipo de Evento SHALL ser "Execução" e a descrição/detalhes SHALL exibir o nome do perfil criado.
- Na exclusão de perfil: Ação SHALL ser "Exclusão de Perfil" (estilizada com tag lilás e texto vermelho), Tipo de Evento SHALL ser "Execução" e a descrição/detalhes SHALL exibir o nome do perfil excluído.

#### Scenario: Criação de perfil registrada no histórico
- **WHEN** um usuário com permissão administrativa cria um novo perfil no menu Perfis
- **THEN** o sistema grava um registro no histórico com origem "Perfis", ação "Criação de Perfil", tipo de evento "Execução", perfil/usuário executor e descrição com o nome do perfil criado.

#### Scenario: Exclusão de perfil registrada no histórico
- **WHEN** um usuário com permissão administrativa exclui um perfil no menu Perfis
- **THEN** o sistema grava um registro no histórico com origem "Perfis", ação "Exclusão de Perfil", tipo de evento "Execução", perfil/usuário executor e descrição com o nome do perfil excluído.

### Requirement: Registro de solicitações e respostas de criação/exclusão de usuários no Histórico
O sistema SHALL registrar no Histórico as solicitações e respostas de criação e exclusão de usuários realizadas no menu Perfis.
- Solicitação de criação de usuário: Ação SHALL ser "Criação de Usuário" (tag laranja claro), Tipo de Evento SHALL ser "Solicitação", descrição SHALL conter o usuário com criação solicitada.
- Solicitação de exclusão de usuário: Ação SHALL ser "Exclusão de Usuário" (tag laranja claro com texto vermelho), Tipo de Evento SHALL ser "Solicitação", descrição SHALL conter o usuário com exclusão solicitada.
- Resposta de solicitação de criação de usuário: Ação SHALL ser "Criação de Usuário" (tag laranja claro), Tipo de Evento SHALL ser "Resposta", descrição SHALL conter o usuário e se a solicitação foi aprovada ou rejeitada.
- Resposta de solicitação de exclusão de usuário: Ação SHALL ser "Exclusão de Usuário" (tag laranja claro com texto vermelho), Tipo de Evento SHALL ser "Resposta", descrição SHALL conter o usuário e se a solicitação de exclusão foi aprovada ou rejeitada.

#### Scenario: Solicitação de criação de usuário
- **WHEN** um usuário de especialidade solicita a criação de um usuário no menu Perfis
- **THEN** o sistema gera um registro no histórico com origem "Perfis", ação "Criação de Usuário" (laranja claro), tipo de evento "Solicitação" e status "PENDENTE".

#### Scenario: Resposta a solicitação de criação de usuário
- **WHEN** um administrador aprova ou rejeita a criação de um usuário
- **THEN** o sistema gera um registro no histórico com origem "Perfis", ação "Criação de Usuário" (laranja claro), tipo de evento "Resposta", status "APROVADO" ou "REJEITADO" e detalhes da decisão.

#### Scenario: Solicitação de exclusão de usuário
- **WHEN** um usuário de especialidade solicita a exclusão de um usuário no menu Perfis
- **THEN** o sistema gera um registro no histórico com origem "Perfis", ação "Exclusão de Usuário" (laranja claro com texto vermelho), tipo de evento "Solicitação" e status "PENDENTE".

#### Scenario: Resposta a solicitação de exclusão de usuário
- **WHEN** um administrador aprova ou rejeita a exclusão de um usuário
- **THEN** o sistema gera um registro no histórico com origem "Perfis", ação "Exclusão de Usuário" (laranja claro com texto vermelho), tipo de evento "Resposta", status "APROVADO" ou "REJEITADO" e detalhes da decisão.

### Requirement: Registro de criação e exclusão de categorizações profissionais no Histórico
O sistema SHALL registrar no Histórico a criação e a exclusão de categorizações de profissionais executadas no menu Perfis.
- Criação de categorização: Ação SHALL ser "Criação de Categorização" (tag marrom claro), Tipo de Evento SHALL ser "Execução" e descrição SHALL conter o profissional + especialidade com a categorização criada.
- Exclusão de categorização: Ação SHALL ser "Exclusão de Categorização" (tag marrom claro com texto vermelho), Tipo de Evento SHALL ser "Execução" e descrição SHALL conter o profissional + especialidade com a categorização excluída.

#### Scenario: Criação de categorização registrada no histórico
- **WHEN** um administrador ou gestão LEC cria ou define as categorias de um profissional em uma especialidade
- **THEN** o sistema registra no histórico origem "Perfis", ação "Criação de Categorização" (marrom claro), tipo de evento "Execução" e detalhamento do profissional e especialidade.

#### Scenario: Exclusão total de categorização registrada no histórico
- **WHEN** um administrador ou gestão LEC exclui a categorização de um profissional em uma especialidade
- **THEN** o sistema registra no histórico origem "Perfis", ação "Exclusão de Categorização" (marrom claro com texto vermelho), tipo de evento "Execução" e detalhamento do profissional e especialidade afetados.
