## Context

O formulário do Sistema LEC necessita exibir procedimentos cirúrgicos de forma dinâmica a partir da base do AGHU quando a especialidade correspondente for selecionada. Para o piloto, utilizaremos a especialidade Plástica (ID 1884).

## Goals / Non-Goals

**Goals:**
- Adicionar endpoint `/api/especialidades/{id_especialidade}/procedimentos` no backend.
- Executar a query SQL fornecida filtrando por `ind_situacao = 'A'`.
- Chamar essa rota no frontend Vue sempre que a especialidade "Plástica" for selecionada e preencher o select.

**Non-Goals:**
- Implementar gerenciamento completo de especialidades/procedimentos locais no SQLite.

## Decisions

- Criar um arquivo SQL `src/providers/sql/paciente/procedimentos_especialidade.sql` com a consulta informada.
- Criar a rota FastAPI no arquivo de rotas apropriado.
- Adicionar watch ou event handler no select de especialidade do frontend.

## Risks / Trade-offs

- Se o banco AGHU estiver inacessível, o dropdown de procedimentos ficará vazio ou apresentará erro. O ideal é ter um fallback ou mensagem de aviso amigável.
