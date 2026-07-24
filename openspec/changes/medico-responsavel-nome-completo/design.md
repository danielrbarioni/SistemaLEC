## Context

Atualmente, alguns registros de médicos responsáveis no banco de dados local contêm o username do usuário Ebserh (ex.: `joao.silva`) enquanto outros contêm o nome completo formatado (ex.: `João Santos da Silva`). Quando a aplicação lê ou solicita edições do médico responsável, a comparação falha ao detectar que se trata da mesma pessoa se um lado usar o username e o outro o nome completo. Além disso, as interfaces visuais do menu Pacientes e do menu Comunicação LEC exibem nomes em formatos inconsistentes.

## Goals / Non-Goals

**Goals:**
- Garantir que o médico responsável seja sempre exibido pelo nome completo em todas as telas (menu Pacientes, cards de paciente, abas de Comunicação LEC e históricos).
- Garantir que o dropdown/opções de médicos responsáveis apresente o nome completo e mapeie logins legados para o nome completo.
- Evitar falsos alertas de alteração de médico responsável quando o valor atual (username) corresponder ao mesmo médico selecionado (nome completo).
- Padronizar os dados armazenados e sincronizados de forma que o campo `medicoResponsavel` utilize o nome completo do médico.

**Non-Goals:**
- Alterar o identificador primário interno (`id` ou `cpf`/`login` no token JWT de autenticação).
- Alterar o comportamento de autenticação AD/LDAP.

## Decisions

### 1. Mapeamento e Normalização de Médicos no Backend/Services
- Criar um utilitário/helper de resolução de médicos que mapeia logins (ex.: `joao.silva`) para o nome completo correspondente cadastrado em `Perfis`/`Usuarios` ou no AGHU.
- Nos endpoints de listagem de pacientes, solicitações e opções de médicos, normalizar a propriedade `medicoResponsavel` para sempre retornar o Nome Completo.

### 2. Normalização e Tratamento no Frontend
- No frontend Vue (loja de perfis e componentes de solicitações), garantir que o médico responsável selecionado e o exibido utilizem o mesmo formato (Nome Completo).
- Na verificação de alterações da aba "Solicitar Edição", comparar o valor após normalização para evitar detectar diferença quando a variação for apenas entre login Ebserh e Nome Completo.

## Risks / Trade-offs

- [Registros antigos com login sem correspondência em Perfis] → Mitigation: Manter fallback gracioso que tenta buscar no AGHU ou formatar o login caso o perfil de usuário correspondente não seja encontrado.
