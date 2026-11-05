# Design

## Context

Veja `proposal.md` para a motivação e `specs/diagnostico-sincronia-lec/spec.md` para os requisitos formais.

Além de identificar pacientes ausentes em um dos sistemas ou cadastrados em especialidades diferentes (`EM_OUTRA_ESPECIALIDADE_NO_CC`), o diagnóstico precisa comparar os atributos clínicos/operacionais dos pacientes que estão **em ambos os sistemas na mesma especialidade**: **Swalis**, **Médico Responsável**, **Lateralidade** e **Judicialização**, permitindo avaliação individual e correção manual pelo usuário Gestão LEC, e garantindo que **todas** as ações executadas a partir de qualquer diagnóstico fiquem registradas no menu **Histórico** com `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"` e o usuário executor.

## Goals / Non-Goals

**Goals:**
- Comparar `Swalis`, `Médico Responsável`, `Lateralidade` e `Judicialização` entre a planilha do Sistema LEC e o estado ativo do Comunicação Cirúrgica para os pacientes presentes em ambos os sistemas (`em_ambos`), exibindo claramente o que está no CC e o que está no Sistema LEC.
- Garantir que divergências de informações (`DIVERGENCIA_DADOS_CADASTRAIS`) sejam avaliadas **individualmente** e corrigidas **manualmente** pelo usuário Gestão LEC através de um formulário individual no próprio modal (com atalho para preencher com o valor do LEC ou digitar/selecionar manualmente).
- Renomear a ação de baixa para **`"Excluir do CC"`** (`EXCLUIR_DO_CC`).
- Registrar todas as ações originadas no diagnóstico dentro da tabela `solicitacoes` com `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, `usuario = usuario_executor` e detalhes completos, usando `tipo = "EDITAR"` + `evento_tipo = "EXECUCAO"` + `status = "APROVADO"` para mudanças de especialidade ou de informações cadastrais/clínicas.

**Non-Goals:**
- Aplicar alterações automáticas em lote nas divergências de Swalis, médico responsável, lateralidade ou judicialização (estas exigem avaliação individual do gestor).

## Decisions

### 1. Comparação Inteligente de Swalis, Médico Responsável, Lateralidade e Judicialização
- **Resolução de Nome de Médico no CC**: No banco do Comunicação Cirúrgica, solicitações oriundas de cargas anteriores frequentemente armazenam o login EBSERH em `medico_responsavel` (ex.: `rafael.anlicoara`), enquanto a tabela `usuarios` mapeia `username -> nome` (`RAFAEL ANLICOARA`) e a planilha do Sistema LEC traz o nome completo (`RAFAEL ANLICOARA`). O helper `_reconstruct_cc_state` resolverá `medico_responsavel` usando o mapa da tabela `usuarios` antes de comparar com a planilha do Sistema LEC, evitando falsos positivos. Além disso, se no CC ainda constar um login `nome.sobrenome` sem nome completo na tabela `usuarios`, a comparação verificará se os tokens do login pertencem ao nome completo da planilha; apenas quando forem profissionais efetivamente diferentes (ou ausente em um dos sistemas) será apontada divergência.
- **Normalização de Lateralidade**: Nas planilhas do Sistema LEC, a coluna `Lateralidade` (índice 22) vem vazia (`None`) quando não aplicável, enquanto no CC o valor padrão é `"Indefinida"`. Portanto, valores vazios/`None`/`"NÃO SE APLICA"`/`"INDEFINIDA"` são tratados como equivalentes (`"Indefinida"`), apontando divergência somente quando houver diferença real (ex.: `"DIREITA"` no LEC vs `"Indefinida"` ou `"ESQUERDA"` no CC).
- **Pareamento de Procedimento para Pacientes com Múltiplos Procedimentos na Mesma Especialidade**: Quando um paciente possui mais de um procedimento na mesma especialidade, o comparador pareia a linha do CC com a linha do Sistema LEC pelo nome base do procedimento (`proc_base`) antes de comparar `Swalis`, `Médico Responsável`, `Lateralidade` e `Judicialização`.
- **Estrutura de `campos_divergentes`**: Cada item da categoria `DIVERGENCIA_DADOS_CADASTRAIS` incluirá um array `campos_divergentes`:
  ```json
  [
    { "campo": "Swalis", "chave": "swalis", "valor_cc": "C", "valor_lec": "B" },
    { "campo": "Médico Responsável", "chave": "medico_responsavel", "valor_cc": "JOAO SILVA", "valor_lec": "MARIA SOUZA" }
  ]
  ```

### 2. Avaliação Individual e Correção Manual (`EDITAR_INFORMACOES_NO_CC`)
- Na aba **🟡 Divergência de Informações (Swalis, Médico, Lateralidade, Judicialização)**, não há checkbox de lote. Cada linha exibe os badges comparativos (`CC: valor_cc` vs `LEC: valor_lec`) e o botão **`"Avaliar / Corrigir no CC"`**.
- Ao clicar em `"Avaliar / Corrigir no CC"`, abre-se um submodal de edição individual para aquele paciente/procedimento mostrando, para cada campo (`Swalis`, `Médico Responsável`, `Lateralidade`, `Judicialização`), o valor atual no CC, o valor informado na planilha do Sistema LEC (com botão rápido *"Usar valor do LEC"*) e o campo editável para o usuário Gestão LEC definir manualmente o valor correto e salvar.

### 3. Registro no Menu `Histórico` (`origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`)
Para que todas as ações apareçam perfeitamente no menu **Histórico** sob o filtro `Origem / Menu = "Pacientes"` e também reflitam na fila ativa de `Pacientes.vue`:
1. **Inclusão no CC (`INCLUIR_NO_CC`)**:
   - Cria `Solicitacao` com `tipo = "INSERIR"`, `status = "APROVADO"`, `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, `usuario = usuario_executor`, `perfil_executor = perfil_executor`, e `detalhes = "Inclusão realizada via Diagnóstico Comunicação Cirúrgica x Sistema LEC (#DIAG-...): paciente constava ativo na planilha do Sistema LEC."`.
2. **Exclusão do CC (`EXCLUIR_DO_CC`)**:
   - Cria `Solicitacao` com `tipo = "EXCLUIR"`, `status = "APROVADO"`, `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, `usuario = usuario_executor`, `perfil_executor = perfil_executor`, e `detalhes = "Exclusão realizada via Diagnóstico Comunicação Cirúrgica x Sistema LEC (#DIAG-...): paciente não consta mais na fila ativa do Sistema LEC."`.
3. **Mudança de Especialidade no CC (`TRANSFERIR_ESPECIALIDADE_NO_CC`)**:
   - Atualiza a especialidade da solicitação de inclusão base (para que `Pacientes.vue` mova o procedimento para a nova especialidade) E cria um registro de auditoria/execução `Solicitacao` com `tipo = "EDITAR"`, `status = "APROVADO"`, `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, `usuario = usuario_executor`, `perfil_executor = perfil_executor`, e `detalhes = "Especialidade: <esp_antiga> -> <esp_nova> | Justificativa: Alteração de especialidade realizada via Diagnóstico Comunicação Cirúrgica x Sistema LEC (#DIAG-...)."`.
4. **Edição Manual de Informações Divergentes no CC (`EDITAR_INFORMACOES_NO_CC`)**:
   - Cria um registro `Solicitacao` com `tipo = "EDITAR"`, `status = "APROVADO"`, `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, `usuario = usuario_executor`, `perfil_executor = perfil_executor`, preenchendo os novos valores (`swallis`, `medico_responsavel`, `lateralidade`, `judicializado`) e gravando em `detalhes` todas as mudanças no formato estruturado:
     `"Swalis (Priorização): C -> B; Lateralidade: Indefinida -> Direita | Justificativa: Adequação manual de informações divergentes via Diagnóstico Comunicação Cirúrgica x Sistema LEC (#DIAG-...)."`.
   - Tanto `Pacientes.vue` (que processa `s.tipo === 'EDITAR'` com `s.status === 'APROVADO'` e `s.evento_tipo !== 'RESPOSTA'`) quanto `Historico.vue` (que exibe os badges `antigo ➔ novo` e filtra por `Origem / Menu = Pacientes`, `Ação = Edição de Procedimento`, `Tipo de Evento = Execução`) funcionarão de forma 100% nativa!

## Risks / Trade-offs

- **[Risk] Diferença de grafia entre login e nome completo do médico na planilha do LEC** → **Mitigação**: Resolver `medico_responsavel` no CC através da tabela `usuarios` e comparar tokens normalizados antes de apontar divergência.
