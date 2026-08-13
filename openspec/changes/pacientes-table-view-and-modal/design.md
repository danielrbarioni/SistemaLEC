# Design: Reformular Visualização do Menu Pacientes para Tabela Compacta com Modal de Detalhes

## Architecture Overview
Adaptação da camada de apresentação em `Pacientes.vue` para desagregar a estrutura de procedimentos em linhas flat na tabela e controlar o estado de exibição do Modal de Detalhes do Paciente.

## Design Details

### 1. Modelagem Flat dos Dados para a Tabela (`procedimentosFlat`)
A partir da lista `pacientesFiltrados`, calcular uma lista plana onde cada item representa uma combinação única paciente-procedimento:
```typescript
interface LinhaProcedimentoFlat {
  codigo: string | number;
  nome: string;
  dt_nascimento?: string;
  nome_mae?: string;
  especialidade: string;
  procedimento: string;
  judicializado: string;
  Swalis: string;
  medico_responsavel: string;
  status?: string;
  tempo_standby?: number | null;
  pacienteCompleto: any;
}
```

### 2. Renderização da Tabela
Tabela responsiva com estilos Tailwind:
- `Prontuário`: exibido em fonte monospace, com suporte a clique.
- `Nome Completo`: destacado em negrito, com suporte a clique.
- `Especialidade`: tag visual por tipo.
- `Procedimento`: formatado com `formatarNomeProcedimento()`.
- `Judicialização`: destaque visual (ex.: Sim em destaque).
- `Swalis`: número ou '—'.
- `Médico Responsável`: nome limpo.

### 3. Componente Modal de Detalhes
Ao selecionar um paciente (`pacienteDetalhesModal = ref<any|null>(null)`):
- Exibir overlay escurecido com transição suave.
- **Cabeçalho do Modal**:
  - Prontuário, Nome Completo, Data de Nascimento (formatada `DD/MM/AAAA`) e Nome da Mãe.
- **Corpo do Modal**:
  - Loop nos procedimentos do paciente (`paciente.procedimentos`).
  - Cada procedimento é apresentado como um card/janela independente com grid visual para Especialidade, Procedimento (padronizado), Judicialização, Swalis e Médico Responsável.
