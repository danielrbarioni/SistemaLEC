## Context

O modulo "Sistema LEC" possui visualizações no frontend (Vue 3) e integração com o AGHU via endpoints backend. Atualmente, a rotulagem exibe "Sistema LEC", usuários com perfil Enfermeiro possuem acesso ao menu de comunicação, e o perfil GESTÃO LEC possui acesso apenas à visualização/acompanhamento. Além disso, a busca por prontuário na aba "Solicitar Inclusão" falhou em preencher o nome completo, data de nascimento e nome da mãe retornando um fallback ("Paciente #prontuario").

## Goals / Non-Goals

**Goals:**
- Atualizar a rotulagem do menu para "Comunicação LEC" em todos os locais da UI.
- Corrigir a chamada de busca por prontuário no AGHU na aba Solicitar Inclusão para trazer Nome Completo, Data de Nascimento e Nome da Mãe.
- Bloquear o acesso ao menu Comunicação LEC para o perfil/função Enfermeiro, informando que a área destina-se a Médico e Residente.
- Permitir que o perfil GESTÃO LEC acesse as abas de criação de solicitações (Inclusão, Edição, Standby e Exclusão) além da aba de Acompanhamento.

**Non-Goals:**
- Redesenhar a API do AGHU ou modificar tabelas do banco de dados local não relacionadas a permissões/rotas.

## Decisions

1. **Renomeação na Nav/Header & Views**:
   - Atualizar rótulos em `Sidebar.vue`, `Navbar.vue` e rotas do Vue Router de `Sistema LEC` para `Comunicação LEC`.

2. **Fix no Busca Prontuário AGHU na Inclusão**:
   - Verificar a rota de busca de prontuário (ex.: `/api/pacientes/{prontuario}` ou endpoint do AGHU) chamada pela view de Solicitar Inclusão.
   - Garantir que a integração utilize o mock/provider correto quando em ambiente local ou na VM, tratando a estrutura do JSON para preencher `nome`, `dataNascimento` e `nomeMae`.

3. **Restrição de Acesso Enfermeiro**:
   - No guard de rotas e na montagem do menu, checar se a role/função é Enfermeiro (`ENFERMEIRO` / `enfermeiro`).
   - Se for Enfermeiro tentar acessar `/comunicacao-lec`, redirecionar ou exibir modal/alerta informativo: *"Esta funcionalidade é restrita aos perfis Médico e Residente"*.

4. **Expansão de Acesso para GESTÃO LEC**:
   - Ajustar as diretivas/guards de permissão nas abas da tela `ComunicacaoLec.vue` (ou componente similar) para permitir que a role `GESTAO_LEC` / `gestao_lec` possa visualizar e submeter os formulários de Inclusão, Edição, Standby e Exclusão.

## Risks / Trade-offs

- [Integração AGHU indisponível ou inacessível no ambiente local] → Manter fallback controlado com tratamento de erro explicito, mas priorizando a conexão com a API Oracle/AGHU configurada na VM/env.
