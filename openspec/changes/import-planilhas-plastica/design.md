## Context

As duas planilhas referentes à especialidade Plástica foram disponibilizadas na pasta `data/`:
1. `Fila sistema Sede Plástica.xlsx`: contém a fila de solicitações com as colunas `id_fila`, `prontuario`, `id_procedimento`, `medico_responsavel`, `swalis`, `sin_judicializado`, `dth_indicacao`, etc.
2. `Procedimentos Plástica.xlsx`: contém a tabela de procedimentos com `id_procedimento`, `PROCEDIMENTO` (nome/descrição textual), `ESPECIALIDADE`, etc.

## Goals / Non-Goals

**Goals:**
- Cruzar `Fila sistema Sede Plástica.xlsx` com `Procedimentos Plástica.xlsx` através do campo `id_procedimento`.
- Garantir a presença do perfil `PLASTICA` na tabela `perfis` do SQLite.
- Inserir/Atualizar os pacientes na tabela `pacientes` e as solicitações aprovadas na tabela `solicitacoes`.
- Converter corretamente os tipos (`sin_judicializado` → "Sim"/"Não", `swalis` → "A1"/"A2"/"B"/"C"/"D", `dth_indicacao` → ISO Datetime string).

**Non-Goals:**
- Não importar especialidades que não sejam Plástica neste ciclo.

## Decisions

- **Cruzamento das planilhas:** Utilizar `pandas` para ler ambos os arquivos Excel e executar o `merge` no campo `id_procedimento`.
- **Mapeamento de colunas:**
  - `prontuario` → `codigo_paciente` (e registro em `pacientes.codigo`).
  - `PROCEDIMENTO` → `procedimento`.
  - `medico_responsavel` → `medico_responsavel`.
  - `swalis` → `swalis` / `swallis`.
  - `sin_judicializado` → True/False mapeado para 'Sim'/'Não'.
  - `dth_indicacao` → `data_criacao` e `data_acao`.
  - `status` → 'APROVADO' (para figurar nas filas ativas).
  - `tipo` → 'INSERIR'.

## Risks / Trade-offs

- [Risk] Prontuários nas solicitações que não possuem dados detalhados de nome/data de nascimento no AGHU local.
  - *Mitigação:* Usar fallback "Paciente Prontuário #[CODIGO]" caso o nome não seja encontrado no banco AGHU.
