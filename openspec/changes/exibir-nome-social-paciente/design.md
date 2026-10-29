# Design

## Context

Atualmente, as consultas SQL ao banco do AGHU (`agh.aip_pacientes`) selecionam apenas a coluna `nome` (nome civil), ignorando a coluna `nome_social`. Além disso, solicitações salvas no SQLite local armazenam o `nome_paciente` no momento da criação. Precisamos garantir que, sempre que existir `nome_social` preenchido no AGHU para um prontuário, ele seja exibido em vez do nome original e acompanhado da indicação de que se trata do nome social em todos os menus (`Solicitações LEC`, `Pacientes`, `Histórico`, `Navegação`, etc.). Veja `proposal.md` para a motivação completa.

## Goals / Non-Goals

**Goals:**
- Consultar `nome_social` em todas as leituras da tabela `agh.aip_pacientes` no PostgreSQL do AGHU.
- Padronizar a resolução do nome do paciente no backend para que, quando `nome_social` existir e não for vazio, o campo `nome` (e `nome_paciente`) seja formatado como `<NOME_SOCIAL> (Nome Social)`, acompanhado das propriedades `nome_social` e `possui_nome_social: true`, nunca expondo o nome civil original na interface.
- Garantir que tanto novas solicitações quanto solicitações/registros históricos já existentes no SQLite reflitam o nome social atualizado do AGHU na listagem de `Solicitações LEC`, `Pacientes` e `Histórico`.
- Exibir indicação clara na interface (sufixo `(Nome Social)` no texto do nome e badge visual nos campos/tabelas aplicáveis).

**Non-Goals:**
- Alterar dados diretamente no banco de dados PostgreSQL do AGHU (acesso estritamente somente leitura).
- Exibir o nome civil original ao lado do nome social (o requisito determina informar o nome social **ao invés** do nome original e indicar que se trata do nome social).

## Decisions

1. **Formatação Centralizada no Backend (`formatar_nome_paciente_aghu`)**:
   - **Decisão**: Criar uma função utilitária em `src/helpers/string_helper.py` (ex.: `resolver_nome_paciente(nome, nome_social)`) que verifica se `nome_social` possui conteúdo válido após `strip()`. Caso positivo, retorna `f"{nome_social_limpo} (Nome Social)"` (evitando duplicar o sufixo caso já contenha `(Nome Social)`).
   - **Racional**: Ao retornar `nome` já formatado como `<NOME_SOCIAL> (Nome Social)` em `/api/pacientes`, `/api/pacientes/{codigo}` e `/api/solicitacoes`, qualquer campo `<input>`, tabela, modal, toast ou exportação Excel em todo o sistema exibirá automaticamente o nome social com a indicação `(Nome Social)`, mesmo em componentes que apenas renderizam `pac.nome` ou `solic.nome_paciente`.
   - **Alternativa considerada**: Retornar apenas `nome_social` separado e exigir que cada template Vue concatene `(Nome Social)`. Rejeitada por ser propensa a omissões em modais secundários, toasts ou exportações Excel; porém, também enviaremos `nome_social` e `possui_nome_social: True` no payload JSON para permitir badges visuais extras no frontend.

2. **Enriquecimento Dinâmico de Solicitações com Dados do AGHU**:
   - **Decisão**:
     - Em `HybridPacienteProvider.listar_pacientes()` e `PacientePostgresProvider`, selecionar `nome, nome_social` de `agh.aip_pacientes` e aplicar `resolver_nome_paciente`.
     - Em `GET /api/solicitacoes` (`src/routers/solicitacao.py`) e nas telas `InteracoesLec.vue`, `Pacientes.vue` e `Historico.vue`, cruzar o `codigo_paciente` com os dados de pacientes do AGHU para que até solicitações antigas (gravadas antes do cadastro do nome social ou antes desta atualização) passem a exibir o Nome Social do paciente.
     - Em `criar_solicitacao` e `editar_solicitacao` (`src/controllers/solicitacao_controller.py`), validar/atualizar `solicitacao["nome_paciente"]` usando o nome resolvido pelo `paciente_provider` para todos os tipos de solicitação quando o prontuário existir no AGHU.

3. **Indicação Visual no Frontend**:
   - **Decisão**: Além do sufixo `(Nome Social)` presente na própria string do nome (que garante visibilidade em inputs desabilitados, opções de seleção, toasts e planilhas Excel), adicionar destaque visual (badge `Nome Social`) próximo ao rótulo/campo de nome em `Solicitações LEC` (`InteracoesLec.vue`), `Pacientes` (`Pacientes.vue`) e `Histórico` (`Historico.vue`) quando identificado que o paciente utiliza nome social.

## Risks / Trade-offs

- **[Risk] Solicitações antigas salvas no SQLite com o nome civil original** → **Mitigação**: Resolver dinamicamente o nome do paciente em `GET /api/solicitacoes` (e no mapeamento de pacientes em `Pacientes.vue`, `Historico.vue` e `InteracoesLec.vue`) priorizando o nome retornado pelo AGHU quando disponível.
- **[Risk] Duplicação do sufixo `(Nome Social)` em edições sucessivas** → **Mitigação**: A função `resolver_nome_paciente` verificará de forma idempotente se o sufixo `(Nome Social)` já está presente antes de anexá-lo.

