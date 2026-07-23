## Context

Após a carga dos dados da especialidade de Plástica a partir das planilhas da Sede:
1. A tabela `perfis` possui duas entradas para a especialidade Plástica (ex.: `PLÁSTICA` e `PLASTICA`).
2. A contagem exibida no card do menu Pacientes mostra 2.188 pacientes e 2.299 procedimentos (enquanto 2.364 solicitações foram inseridas).
3. Os registros de pacientes na tabela `pacientes` contêm nomes genéricos (ex.: "Paciente #21321823") e campos como `dt_nascimento` e `nome_mae` preenchidos com travessões ("—").

## Goals / Non-Goals

**Goals:**
- Unificar e sanitizar a tabela `perfis`, garantindo uma única entrada (`id: 'PLASTICA'`, `nome: 'PLÁSTICA'`).
- Corrigir a contagem total de procedimentos/solicitações exibida na tela de Pacientes para refletir com precisão os 2.364 registros.
- Atualizar os dados cadastrais dos pacientes na tabela `pacientes` (e `solicitacoes`) consultando o banco AGHU (PostgreSQL) pelo número do prontuário (`codigo`).

**Non-Goals:**
- Não alterar a estrutura das tabelas existentes do SQLite.

## Decisions

- **Higienização de Perfis:** Criar script/função SQL que remove registros duplicados de `perfis` mantendo a chave primária padronizada `'PLASTICA'`.
- **Ajuste dos Contadores:** Revisar a query/lógica nos controllers do backend (`src/routers/paciente.py` e `src/routers/solicitacao.py`) e no componente Vue (`Pacientes.vue`) para garantir que o número de procedimentos seja obtido diretamente da contagem de solicitações ativas (`COUNT(*)` de `solicitacoes`).
- **Enriquecimento via AGHU PostgreSQL:** Criar um script de atualização cadastral (`scratch/update_pacientes_aghu.py`) que conecta no PostgreSQL do AGHU via `POSTGRES_DSN`, realiza a busca dos pacientes pelo prontuário (`pac.prontuario IN (...)`) e atualiza as colunas `nome`, `dt_nascimento`, `nome_mae`, `cpf`, `sexo` nas tabelas `pacientes` e `solicitacoes`.

## Risks / Trade-offs

- [Risk] Nem todos os prontuários das planilhas da Plástica estarem cadastrados no banco PostgreSQL do AGHU.
  - *Mitigação:* Caso um prontuário não seja localizado no AGHU, manter o nome fallback ("Paciente #[PRONTUARIO]") sem interromper o script.
