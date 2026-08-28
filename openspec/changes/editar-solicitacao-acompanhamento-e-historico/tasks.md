## 1. Backend: Interface e Implementação dos Provedores

- [x] 1.1 Adicionar método `editar_solicitacao` na interface `SolicitacaoProviderInterface`.
- [x] 1.2 Implementar `editar_solicitacao` em `SolicitacaoSqliteProvider`: atualizar dados in-place mantendo `data_criacao` original e inserir evento de auditoria com `evento_tipo = 'ALTERACAO'`.
- [x] 1.3 Implementar `editar_solicitacao` em `SolicitacaoCsvProvider`.

## 2. Backend: Controller e Router

- [x] 2.1 Implementar `editar_solicitacao` em `solicitacao_controller.py` com validações de status `PENDENTE`, proibição para `EXCLUIR` e integridade de dados.
- [x] 2.2 Criar rota `PUT /api/solicitacoes/{id_solicitacao}` em `src/routers/solicitacao.py` com controle de permissão por perfil.

## 3. Frontend: Módulo de Solicitações LEC e Histórico

- [x] 3.1 Adicionar botão "Editar" na coluna de Ações para solicitações pendentes dos tipos `INSERIR`, `EDITAR` e `STANDBY` em `InteracoesLec.vue`.
- [x] 3.2 Implementar modo de edição visual no formulário (`modoEdicaoSolicitacao`, banner de destaque, botões "Salvar Alterações" e "Cancelar Edição").
- [x] 3.3 Conectar a submissão no modo de edição ao endpoint `PUT /api/solicitacoes/{id_solicitacao}`.
- [x] 3.4 Filtrar eventos `ALTERACAO` na tabela de acompanhamento em `InteracoesLec.vue` para exibir apenas as solicitações ativas atualizadas.
- [x] 3.5 Atualizar `Historico.vue` para exibir e filtrar eventos de `ALTERACAO` (Alteração) na linha do tempo.

## 4. Testes e Verificação

- [x] 4.1 Validar que a edição atualiza os dados da solicitação mantendo inalterados a `data_criacao` e a ordenação na fila.
- [x] 4.2 Validar que o Histórico exibe tanto a solicitação original quanto o evento de alteração com respectivos horários e usuários.
- [x] 4.3 Validar que solicitações do tipo Exclusão (`EXCLUIR`) ou com status concluído não podem ser editadas.
