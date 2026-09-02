## Why

Atualmente, o Sistema LEC organiza os pacientes e procedimentos por especialidade, médico responsável, prioridade Swalis e judicialização, mas não oferece aos médicos uma forma personalizada de classificar os procedimentos de sua própria fila de acordo com seus critérios clínicos ou organizacionais específicos (por exemplo, subespecialidades internas, complexidade de técnica cirúrgica, urgência particular ou prioridades próprias).

A funcionalidade de **Categorização do Profissional** permite que médicos criem e gerenciem listas personalizadas de categorias por especialidade, possibilitando a classificação opcional de procedimentos e a filtragem ágil na tela de Pacientes.

## What Changes

1. **Gestão de Categorizações no Menu Perfis (Restrito a ADMIN e GESTÃO LEC)**:
   - Nova coluna **"Categorização"** na visualização de Perfis (visível apenas para perfis `ADMIN` e `GESTAO_LEC`).
   - Indicação se o médico possui ou não categorização criada na respectiva especialidade.
   - Modal para criar, editar, renomear e excluir categorias individuais ou a categorização completa do médico na especialidade.
   - Ao renomear uma categoria, todos os procedimentos já classificados sob ela são automaticamente atualizados para o novo nome.
   - Ao excluir uma categoria individual ou todas as categorias de um médico/especialidade, é exibida confirmação informando que os procedimentos vinculados perderão a categorização.

2. **Formulários de Solicitação LEC (Inclusão e Edição)**:
   - O campo opcional **"Categorização Profissional"** passa a ser exibido dinamicamente apenas quando a combinação de *Especialidade + Médico Responsável* selecionada possuir categorias cadastradas.
   - Na edição de uma solicitação, caso o médico responsável seja alterado, o procedimento perde automaticamente a categorização anterior.

3. **Menu Pacientes (Filtro e Detalhes)**:
   - O filtro **"Categorização Profissional"** é exibido apenas quando selecionada uma combinação de especialidade + médico que possua categorias cadastradas.
   - No modal de detalhes do paciente (ao clicar na linha do paciente/procedimento), exibe-se próximo ao Médico Responsável o campo **"Categorização"** (exibindo o nome da categoria ou *"Sem categorização"*).

4. **Base de Dados e Compatibilidade**:
   - Criação da tabela `categorizacoes_profissionais` e adição da coluna `categorizacao` nas tabelas `solicitacoes` e `pacientes`.
   - Procedimentos pré-existentes e solicitações pendentes iniciam sem categorização (`NULL` / vazio).

## Capabilities

### New Capabilities
- `professional-categorization`: Gerenciamento de listas de categorias personalizadas por médico e especialidade, aplicação opcional de categorias em solicitações de procedimentos, e filtragem avançada por categoria na tela de pacientes.

### Modified Capabilities
- `perfis-management`: Adição da coluna e modal de gerenciamento de categorizações do profissional para perfis administrativos.
- `solicitacoes-lec`: Suporte a seleção dinâmica e redefinição de categorização em inclusões e edições de procedimentos.
- `pacientes-view`: Inclusão de filtro dinâmico de categoria e exibição da categoria no modal de detalhes do procedimento.

## Impact

- **Backend**:
  - Modelos SQLAlchemy: novo modelo `CategorizacaoProfissional` em `src/models/categorizacao_profissional.py`; campos `categorizacao` em `src/models/solicitacao.py` e `src/models/paciente.py`.
  - Migração Alembic para atualizar o esquema de banco de dados no SQLite local e na VM.
  - Novos endpoints REST em `src/routers/categorizacao_profissional.py` (`GET`, `POST`, `PUT`, `DELETE`).
  - Atualização dos roteadores de solicitações e pacientes para manipulação do campo `categorizacao`.
- **Frontend**:
  - `frontend/src/views/Perfis.vue`: Coluna "Categorização" e modal de gerenciamento de categorias.
  - `frontend/src/views/InteracoesLec.vue`: Campo condicional nos formulários de inclusão/edição e exibição em modais de descrição/detalhes.
  - `frontend/src/views/Pacientes.vue`: Filtro condicional e exibição da categoria vinculada ao médico no modal de detalhes.
  - `frontend/src/services/api.ts` ou chamadas de serviço para integração com os novos endpoints.
