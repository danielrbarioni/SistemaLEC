## Context

O menu Histórico centraliza o acompanhamento e auditoria de ações realizadas no Sistema LEC. Anteriormente, apenas solicitações ligadas a procedimentos eram exibidas com a identificação de menu "Sistema LEC". Ações do menu Perfis (gestão de perfis, aprovação/rejeição de usuários e categorizações de profissionais) eram gerenciadas de forma isolada, e o filtro no Histórico não permitia visualizá-las de maneira categorizada e uniforme.

## Goals / Non-Goals

**Goals:**
- Ajustar a origem padrão para "Solicitações LEC" para procedimentos gerados no módulo de interações.
- Gravar eventos de auditoria na tabela de histórico/solicitações para:
  - Criação e exclusão de perfis.
  - Solicitação e resposta (aprovação/rejeição) de criação de usuários.
  - Solicitação e resposta (aprovação/rejeição) de exclusão de usuários.
  - Criação e exclusão de categorizações de profissionais.
- Padronizar as tags visuais e cores especificadas:
  - Criação de perfil: tag lilás, tipo "Execução".
  - Exclusão de perfil: tag lilás com texto vermelho, tipo "Execução".
  - Criação de usuário: tag laranja claro, tipo "Solicitação" ou "Resposta".
  - Exclusão de usuário: tag laranja claro com texto vermelho, tipo "Solicitação" ou "Resposta".
  - Criação de categorização: tag marrom claro, tipo "Execução".
  - Exclusão de categorização: tag marrom claro com texto vermelho, tipo "Execução".
- Renomear ações de procedimentos para "Inclusão de Procedimento", "Edição de Procedimento", "Standby de Procedimento", "Exclusão de Procedimento", mantendo as cores verde, azul, amarelo e vermelho.

**Non-Goals:**
- Modificar o fluxo de permissões ou regras de aprovação já vigentes nos módulos Perfis e Solicitações.

## Decisions

### 1. Modelo de Eventos e Persistência no Backend
- As ações do menu Perfis serão registradas através de um helper de auditoria (`registrar_evento_historico`) que grava registros na tabela `solicitacoes` (ou modelo correspondente), utilizando:
  - `origem_menu`: `"Perfis"`.
  - `codigo_paciente`: `"0"` ou `"—"` (indicativo de evento administrativo sem prontuário).
  - `nome_paciente`: `"—"`.
  - `tipo`: Códigos padronizados (`CRIAR_PERFIL`, `EXCLUIR_PERFIL`, `CRIAR_USUARIO`, `EXCLUIR_USUARIO`, `CRIAR_CATEGORIZACAO`, `EXCLUIR_CATEGORIZACAO`).
  - `evento_tipo`: `"EXECUCAO"`, `"SOLICITACAO"` ou `"RESPOSTA"`.
  - `detalhes`: Texto descritivo com o elemento criado, excluído, solicitado ou respondido.
  - `perfil_executor`: Perfil ativo de quem executou a ação.
  - `usuario`: Login Ebserh do executor.
  - `data_criacao`: Timestamp atual formatado.

### 2. Tratamento no Frontend (`Historico.vue`)
- **Filtro de Origem / Menu**:
  - Opções: "Todas", "Solicitações LEC", "Perfis", "Pacientes".
  - Tratamento retrocompatível para registros legados com "Sistema LEC".
- **Filtro e Formatação de Ações**:
  - Exibição com formatador reativo `formatarTipo(tipo)` e estilização `getTipoBadgeClass(tipo)`.
  - Inclusão dos tipos administrativos de Perfis no dropdown de filtros de Ação.
- **Tipo de Evento**:
  - Renderização de badges "Execução", "Solicitação", "Resposta" e "Alteração" conforme o tipo de evento do registro.

## Risks / Trade-offs

- **[Risco] Poluição de registros sem prontuário na listagem geral do Histórico**:
  - → **Mitigação**: Colunas "Prontuário / Paciente" e "Especialidade / Procedimento" exibem `"—"` ou o detalhe contextual de forma limpa, e os filtros de "Origem / Menu" e "Ação" permitem isolar exatamente a visualização desejada.
