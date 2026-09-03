## Context

O Sistema LEC gerencia pacientes cirúrgicos e suas solicitações de inclusão, edição e categorização profissional. Cada paciente no banco de dados (`pacientes`) pode possuir mais de um procedimento cirúrgico cadastrado na mesma ou em diferentes especialidades, com médicos responsáveis distintos.

Ao introduzir a categorização profissional e aprimorar a auditoria, foram identificados pontos de falha no rastreamento e identificação de procedimentos individuais em pacientes com múltiplos procedimentos, além da necessidade de introduzir o campo obrigatório de Lateralidade Cirúrgica.

## Goals / Non-Goals

**Goals:**
- **Precisão na Edição de Procedimentos**: Garantir que a edição de um procedimento de um paciente com múltiplos procedimentos atualize estritamente o procedimento selecionado, mantendo médico responsável, procedimento anterior e categorização consistentes sem diffs falsos.
- **Persistência e Carregamento de Categorização**: Garantir que a categorização previamente aprovada seja imediatamente carregada no formulário de edição do procedimento.
- **Campo Obrigatório de Lateralidade**: Adicionar o campo `lateralidade` no modelo de dados, com fallback `"Indefinida"` para todos os dados legados, e exigência estrita das 4 opções (`lado esquerdo`, `lado direito`, `bilateral`, `não se aplica`) em novas inclusões e edições.
- **Exibição Visual**: Apresentar a lateralidade nos cards de procedimentos das telas de Pacientes, Solicitações LEC e Histórico.

**Non-Goals:**
- Não alterar regras de negócio do Swalis ou do fluxo de aprovação da Gestão LEC além da inclusão dos campos e correções de baseline.

## Decisions

1. **Identificação Única do Procedimento em Edição (`id` e Chave Composta)**:
   - *Decisão*: Ao aprovar ou comparar um procedimento em `solicitacao.py` e `solicitacao_controller.py`, a busca do paciente alvo no banco de dados deve utilizar o `id` do procedimento quando disponível, ou a combinação exata de `(prontuario, especialidade, procedimento, medico_responsavel)`.
   - *Alternativa descartada*: Buscar apenas por `prontuario`, pois `select(Paciente).where(Paciente.prontuario == cod).first()` sempre recupera o primeiro procedimento cadastrado do paciente, gerando colisões graves em pacientes com múltiplos procedimentos.

2. **Modelo de Dados para Lateralidade**:
   - *Decisão*: Adicionar coluna `lateralidade TEXT DEFAULT 'Indefinida'` nas tabelas `pacientes` e `solicitacoes`.
   - *Validação*: Backend e frontend aceitam estritamente: `["lado esquerdo", "lado direito", "bilateral", "não se aplica"]` para novas submissões.
   - *Compatibilidade Legada*: Todos os registros já existentes no banco assumem `"Indefinida"` automaticamente, sem necessidade de recadastramento manual.

3. **Carregamento de Estado do Procedimento no Frontend**:
   - *Decisão*: Ao invocar `abrirModalEdicao(procedimento)`, transferir explicitamente todas as propriedades do procedimento selecionado (`procedimento.categorizacao`, `procedimento.lateralidade`, `procedimento.medico_responsavel`, etc.) para o formulário `formEdicao`, garantindo sincronização reativa imediata.

## Risks / Trade-offs

- **[Risco de Diffs em Procedimentos Legados sem Lateralidade]** → Procedimentos legados terão `"Indefinida"`. Na primeira edição, ao selecionar uma lateralidade real (ex: `"lado direito"`), o diff indicará corretamente `Lateralidade: Indefinida ➔ Lado Direito`.
- **[Risco de Migração SQLite]** → Script de migração seguro com `ALTER TABLE ... ADD COLUMN` e `UPDATE ... SET lateralidade = 'Indefinida' WHERE lateralidade IS NULL` executado localmente e na VM.
