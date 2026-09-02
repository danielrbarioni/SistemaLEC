## 1. Banco de Dados e Modelos

- [ ] 1.1 Criar o modelo SQLAlchemy `CategorizacaoProfissional` em `src/models/categorizacao_profissional.py` com campos `id`, `medico`, `especialidade` e `categorias_json`.
- [ ] 1.2 Atualizar os modelos `Solicitacao` (`src/models/solicitacao.py`) e `Paciente` (`src/models/paciente.py`) adicionando a coluna `categorizacao`.
- [ ] 1.3 Criar e aplicar script de migração Alembic para adicionar a tabela `categorizacoes_profissionais` e a coluna `categorizacao`.

## 2. Endpoints e Regras de Negócio no Backend

- [ ] 2.1 Criar o roteador `src/routers/categorizacao_profissional.py` com rotas `GET`, `POST`, `PUT`, `DELETE` protegidas para perfis `ADMIN` e `GESTAO_LEC`.
- [ ] 2.2 Implementar lógica em cascata no `PUT` e `DELETE`: renomear ocorrências de categorias alteradas e desvincular (`NULL`) ocorrências de categorias excluídas nas tabelas de solicitações e pacientes.
- [ ] 2.3 Atualizar os roteadores e providers de solicitações (`src/routers/solicitacao.py`, `solicitacao_sqlite_provider.py`) para persistir `categorizacao` e resetar a categorização ao trocar de médico responsável na edição.
- [ ] 2.4 Registrar o novo roteador em `src/main.py`.

## 3. Frontend - Menu Perfis

- [ ] 3.1 Adicionar a coluna "Categorização" na tabela de usuários/médicos em `frontend/src/views/Perfis.vue`, visível apenas para `ADMIN` e `GESTAO_LEC`.
- [ ] 3.2 Implementar o modal de gerenciamento de categorizações com adição item a item, renomeação inline, exclusão individual com confirmação e exclusão total com alerta.

## 4. Frontend - Menu Solicitações LEC

- [ ] 4.1 Adicionar o campo "Categorização Profissional" nos formulários de inclusão e edição em `frontend/src/views/InteracoesLec.vue`, exibido dinamicamente apenas para combinações de médico e especialidade com categorias cadastradas.
- [ ] 4.2 Garantir a limpeza automática do campo de categorização caso o médico seja alterado durante a edição de uma solicitação.
- [ ] 4.3 Atualizar os modais de visualização/descrição para exibir o valor anterior e novo da categorização quando editada.

## 5. Frontend - Menu Pacientes

- [ ] 5.1 Adicionar filtro condicional "Categorização Profissional" em `frontend/src/views/Pacientes.vue`, exibido quando selecionada especialidade e médico com categorias.
- [ ] 5.2 Exibir a linha "Categorização" (mostrando o nome da categoria ou "Sem categorização") junto ao Médico Responsável no modal de detalhes do paciente.

## 6. Validação, Build e Deploy na VM

- [ ] 6.1 Validar localmente todo o fluxo de ponta a ponta (criação de categorias, inclusão de solicitação categorizada, edição, renomeação em cascata e filtros).
- [ ] 6.2 Executar build de produção do frontend (`npm run build`).
- [ ] 6.3 Executar migração do banco na VM e realizar o deploy da nova versão preservando todos os dados da base de produção.
