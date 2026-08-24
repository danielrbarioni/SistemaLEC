## Context

O Sistema LEC possui um módulo de controle de acessos (Menu Perfis) onde perfis (`ADMIN`, `GESTAO_LEC`, `ESPECIALIDADE`, `NENHUM`/`OBSERVADOR`) e vínculos de usuários locais são cadastrados e gerenciados no banco SQLite local (`data/app.db`).

Em ambiente real de uso, três problemas foram identificados:
1. **Layout e Responsividade da Tabela**: A tela divide o espaço horizontal em 2/3 para listagens e 1/3 para formulários (`grid-cols-3`), fazendo com que a tabela "Usuários Locais Cadastrados" exceda o espaço disponível e gere uma barra de rolagem horizontal desconfortável.
2. **Profissionais com Múltiplas Especialidades**: Médicos frequentemente atendem em mais de um serviço cirúrgico (ex: Cirurgia Geral e Plástica, Ginecologia Geral e Endoscópica). A tabela `usuarios` no banco de dados e os endpoints da API impõem uma restrição única global no campo `username` (`unique=True`), impedindo que o mesmo usuário Ebserh seja cadastrado em mais de uma especialidade. Além disso, o token JWT e a UI só suportam um perfil ativo selecionado por vez.
3. **Falha na Criação de Especialidades**: Ao tentar adicionar novas especialidades, o sistema falhou silenciosamente ou retornou erro 500 por violação de constraint de Primary Key (`id` duplicado em `perfis`) ou falta de sanitização/tratamento de exceção quando o nome da especialidade foi editado anteriormente ou continha caracteres divergentes.

## Goals / Non-Goals

**Goals:**
- Ajustar o layout visual do Menu Perfis para que a tabela de usuários locais cadastrados exiba todas as colunas sem nenhuma rolagem horizontal lateral, expandindo o container e reorganizando a disposição dos cards.
- Permitir que o mesmo `username` possa ser cadastrado em múltiplos perfis/especialidades diferentes (chave de unicidade `(username, perfil_id)`).
- Implementar suporte para que usuários com mais de um perfil cadastrado possam alternar dinamicamente entre seus perfis autorizados (tanto pelo seletor de perfil no topo quanto no menu Perfis), similar ao comportamento já disponível para administradores.
- Tornar a criação e edição de perfis em `src/routers/perfil.py` resiliente a colisões de ID, tratando duplicidades de chave primária e caracteres especiais de forma limpa.

**Non-Goals:**
- Alterar o mecanismo de autenticação AD/LDAP principal (o login continua validando as credenciais no AD/Ebserh).
- Permitir que usuários de perfil `NENHUM`/`OBSERVADOR` ou `ESPECIALIDADE` criem perfis globais ou de especialidades alheias (mantendo a matriz de permissões e hierarquias).

## Decisions

### 1. Reestruturação do Layout do Menu Perfis
- **Decisão:** Reorganizar o layout da view `frontend/src/views/Perfis.vue` de uma grade dividida 2/3 + 1/3 comprimida para um layout otimizado:
  - Ou seção de formulários no topo / lateral com largura ajustada (`max-w-full`), permitindo que a tabela de usuários ocupe 100% da largura útil sem overflow.
  - Ajustar padding e larguras das colunas da tabela (`Nome/Username`, `Perfil ID`, `Especialidade`, `Função`, `Ações`) com `table-fixed` ou `w-auto` controlado, garantindo visualização completa em telas desktop e notebooks sem barra de rolagem horizontal.
- **Alternativa Considerada:** Reduzir fontes e esconder colunas. *Rejeitado porque o usuário necessita ver todas as colunas.*

### 2. Chave de Unicidade Composta `(username, perfil_id)` e Múltiplos Perfis
- **Decisão:** No banco de dados SQLite (`usuarios`), alterar a restrição única para a combinação `(username, perfil_id)`.
- **Decisão no Backend (`auth.py` e `/api/usuarios`):**
  - No login (`auth.py`), ao buscar os registros na tabela `usuarios`, fazer `SELECT` de todas as linhas correspondentes ao `username` (ao invés de `fetchone`).
  - Incluir no payload do token / resposta de login a lista de todos os perfis associados ao usuário (`available_profiles`), e definir o perfil ativo inicial (por padrão, o primeiro ou o de maior privilégio).
  - Permitir endpoint ou troca no cliente de perfil ativo para qualquer perfil presente em sua lista autorizada.
- **Decisão no Frontend:**
  - O seletor de perfis no cabeçalho e na lista de perfis do menu Perfis passa a permitir que o usuário ative qualquer perfil que pertença a ele (e administradores continuam podendo alternar para qualquer perfil).
- **Alternativa Considerada:** Criar uma tabela relacional intermediária N:N `usuario_perfis`. *Rejeitado por adicionar complexidade desnecessária de migração no SQLite, quando múltiplos registros na tabela `usuarios` com `(username, perfil_id)` atendem perfeitamente ao histórico, função específica por especialidade (ex: Médico em Plástica, Residente em Geral) e migração contínua dos dados existentes.*

### 3. Geração Segura e Resiliente de IDs de Perfis
- **Decisão:** No endpoint `POST /api/perfis`:
  - Normalizar o `id` removendo acentos e caracteres especiais (ex: `GINECOLOGIA_ENDOSCÓPICA` → `GINECOLOGIA_ENDOSCOPICA`).
  - Verificar explicitamente se `Profile.id == perfil_id` OU `Profile.especialidade == especialidade` já existe. Se o `id` já existir com especialidade diferente (decorrente de edições passadas), anexar um sufixo ou ID único gerado.
  - Tratar exceções de integridade do banco e retornar erro 400 com mensagem explicativa em vez de falha 500.

## Risks / Trade-offs

- **[Risco]** Migração de schema no SQLite para alterar constraint UNIQUE de `username` para `(username, perfil_id)` sem perder os dados reais da tabela.
  - *Mitigação:* Usar migração segura criando tabela temporária ou script controlado com backup automático garantido.
- **[Risco]** Usuário logado em uma especialidade visualizar inadvertidamente dados de outra.
  - *Mitigação:* O backend e o frontend vinculam as consultas e solicitações ao `perfil_ativo` atual do token JWT / store, com validação no router.

## Migration Plan

1. Executar migração do banco SQLite atualizando a tabela `usuarios` para remover constraint única isolada de `username` e adicionar constraint única composta `(username, perfil_id)`.
2. Validar que nenhum registro de usuário existente seja modificado ou perdido.
3. Testar a criação de múltiplos vínculos para um mesmo médico (ex: 2 especialidades).
4. Testar a alternância de perfis pelo usuário multi-especialidade.
5. Testar a criação de novas especialidades sem erro de colisão.
