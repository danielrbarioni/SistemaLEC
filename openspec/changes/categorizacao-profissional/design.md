## Context

O Sistema LEC gerencia filas cirúrgicas com base em especialidades, procedimentos padronizados, médicos responsáveis, critérios Swalis e priorização jurídica. Determinados médicos necessitam de subdivisões internas personalizadas para seus procedimentos (ex.: categorização por complexidade cirúrgica, técnicas específicas ou subdivisões de equipe). Como cada médico pode atuar em mais de uma especialidade (por exemplo, Cirurgia Geral e Cirurgia do Aparelho Digestivo), suas categorias devem ser isoladas por combinação de `(médico, especialidade)`.

## Goals / Non-Goals

**Goals:**
- Permitir que perfis `ADMIN` e `GESTAO_LEC` gerenciem (criem, editem, renomeiem e excluam) conjuntos de categorias para qualquer médico em uma especialidade específica.
- Exibir a nova coluna "Categorização" na tela de Perfis exclusivamente para administradores e Gestão LEC.
- Disponibilizar a seleção de categorias nos formulários de inclusão e edição de procedimentos no menu Solicitações LEC apenas quando o médico e a especialidade selecionados tiverem categorizações cadastradas.
- Sincronizar renomeações de categorias: ao alterar o nome de uma categoria, atualizar automaticamente todas as solicitações e pacientes classificados com o nome anterior para o novo nome.
- Tratar exclusão com confirmação e perda de vínculo: ao excluir uma categoria ou o conjunto de categorização, desvincular os procedimentos afetados (`categorizacao = NULL`).
- Tratar troca de médico responsável em edições: se um procedimento for editado trocando o médico responsável, a categorização é automaticamente zerada.
- Disponibilizar filtro dinâmico de categorização no menu Pacientes e exibir a categorização correspondente nos detalhes de cada procedimento.

**Non-Goals:**
- Tornar a categorização obrigatória (a classificação de um procedimento em uma categoria permanece estritamente opcional).
- Permitir que perfis sem privilégios administrativos criem ou excluam conjuntos de categorias no menu Perfis.

## Decisions

### 1. Modelo de Dados e Persistência
- **Tabela `categorizacoes_profissionais`**:
  - `id`: Chave primária (Integer auto-increment).
  - `medico`: String contendo o nome ou username padronizado do médico.
  - `especialidade`: String contendo o nome canônico da especialidade.
  - `categorias_json`: String/JSON com a lista ordenada de categorias (`["Categoria A", "Categoria B"]`).
  - `UniqueConstraint('medico', 'especialidade')`: Garante no máximo 1 conjunto de categorização por médico e especialidade.
- **Tabelas `solicitacoes` e `pacientes`**:
  - Adição da coluna `categorizacao` (`String`, `nullable=True`).
  - Valores existentes permanecem `NULL`.

### 2. Endpoints e Lógica de Negócio no Backend
- `GET /api/categorizacoes-profissionais`: Retorna a lista de categorizações cadastradas (suporta filtros por `medico` e `especialidade`).
- `POST /api/categorizacoes-profissionais`: Cria a categorização para um médico em uma especialidade (restrito a `ADMIN` e `GESTAO_LEC`).
- `PUT /api/categorizacoes-profissionais/{id}`:
  - Recebe a lista atualizada de categorias.
  - Compara a lista anterior com a nova para detectar renomeações e remoções:
    - Se uma categoria foi renomeada (ex.: de "Alta Complexidade" para "Nível 3"), executa update nas tabelas `solicitacoes` e `pacientes` para o respectivo médico e especialidade.
    - Se uma categoria foi removida, executa update setando `categorizacao = NULL` para os procedimentos que a utilizavam.
- `DELETE /api/categorizacoes-profissionais/{id}`:
  - Remove o registro de categorização e limpa (`categorizacao = NULL`) todos os procedimentos daquele médico e especialidade.
- **Validação de Edição de Solicitação**:
  - Ao alterar o campo `medico_responsavel` em uma solicitação existente, limpa o campo `categorizacao` caso o novo médico não seja idêntico ao anterior.

### 3. Interface no Frontend (Vue 3 / Tailwind)
- **Menu Perfis (`Perfis.vue`)**:
  - Nova coluna na tabela de usuários/médicos por especialidade exibindo:
    - Botão estilizado `+ Criar` (se não possuir categorias).
    - Botão `Gerenciar (N categorias)` (se já possuir categorias).
  - Modal de Gerenciamento de Categorias:
    - Título com Médico e Especialidade.
    - Input de texto para adicionar nova categoria à lista.
    - Edição inline dos nomes das categorias existentes.
    - Botão de exclusão por item com diálogo de confirmação claro.
    - Botão de exclusão total da categorização com alerta de impacto.
- **Menu Solicitações LEC (`InteracoesLec.vue`)**:
  - Observador reativo: ao selecionar/alterar o médico e a especialidade, carrega as categorias disponíveis.
  - Exibe campo `<select>` "Categorização Profissional" apenas se houver categorias cadastradas.
  - No modal de descrição/acompanhamento, inclui a visualização da categorização anterior e nova em solicitações de edição.
- **Menu Pacientes (`Pacientes.vue`)**:
  - Filtro extra "Categorização Profissional" exibido condicionalmente quando o médico e a especialidade filtrados possuírem categorias.
  - Modal de detalhes do paciente: inclusão da linha "Categorização" junto ao Médico Responsável no quadro de cada procedimento.

## Risks / Trade-offs

- **[Risco] Variação de grafia ou casing no nome do médico entre tabelas (`usuarios`, `solicitacoes`, `pacientes`)**:
  - → **Mitigação**: Normalização consistente (maiúsculas e remoção de espaços extras) e vinculação pelo username/nome canônico ao casar as categorias.
- **[Risco] Renomeação em cascata em grandes volumes de solicitações**:
  - → **Mitigação**: Execução de updates transacionais diretos via SQLAlchemy no backend dentro da mesma transação da atualização da categorização.
