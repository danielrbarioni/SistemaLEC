# Design: Exibição da Data/Hora de Inserção e Reordenação Multi-Critério no Menu Pacientes

## Architecture Overview
Ajuste na camada de visualização e transformação de dados em `frontend/src/views/Pacientes.vue`, capturando a propriedade `data_insercao` a partir das solicitações de inclusão (`tipo == 'INSERIR'`) ou fallback da base de pacientes, expondo-a na tabela e no modal de detalhes e aplicando um algoritmo de ordenação hierárquico multi-critério.

## Detailed Design

### 1. Mapeamento da Data/Hora de Inserção (`todosPacientesMap`)
Ao iterar pelas solicitações aprovadas no `todosPacientesMap`:
- No evento `s.tipo === 'INSERIR'`:
  - Armazena `data_insercao: s.data_criacao` (data/hora original de entrada na LEC).
- No evento `s.tipo === 'EDITAR'`:
  - Preserva o valor de `data_insercao` previamente definido no procedimento.
- No fallback para pacientes sem solicitações:
  - Define `data_insercao: baseMatch.data_hora_inicio || '—'`.

### 2. Formatação da Data/Hora de Inserção
Função `formatarDataHora(dataStr: string)`:
- Converte padrões comuns (`YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DDTHH:MM:SS`, `YYYY-MM-DD HH:MM` ou `DD/MM/AAAA HH:MM`) para o formato padrão legível `DD/MM/AAAA HH:mm`.

### 3. Ajuste de Layout na Tabela e no Modal

#### Tabela Principal (`procedimentosFlat`)
Nova coluna inserida:
- Cabeçalho: `<th class="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">Data de Inserção</th>`
- Linha:
```html
<td class="px-4 py-3 text-center whitespace-nowrap font-mono text-xs text-gray-700">
  {{ formatarDataHora(row.data_insercao) }}
</td>
```

#### Modal de Detalhes do Paciente
Dentro do quadro de cada procedimento, no grid de detalhes (`grid-cols-1 sm:grid-cols-4 gap-4`):
```html
<div>
  <span class="text-gray-400 font-semibold block uppercase text-[10px]">Data de Inserção</span>
  <span class="text-gray-900 font-mono font-medium mt-0.5 block">
    {{ formatarDataHora(proc.data_insercao) }}
  </span>
</div>
```

### 4. Algoritmo de Ordenação Hierárquico Multi-Critério

A ordenação em `procedimentosFlat` seguirá a seguinte prioridade sequencial:

#### Critério 1: Swalis (do mais crítico para o menos crítico)
Rank numérico atribuído:
- `A1` -> 1 (Prioridade máxima)
- `A2` -> 2 (Prioridade alta)
- `B`  -> 3 (Prioridade média)
- `C`  -> 4 (Prioridade baixa)
- `D`  -> 5 (Prioridade mínima)
- Qualquer outro / '—' / vazio -> 6

Se `rank(A) !== rank(B)`, retorna `rank(A) - rank(B)`.

#### Critério 2: Data/Hora de Inserção na LEC (do mais antigo para o mais recente)
Se `rank(A) === rank(B)`:
- Normaliza a data/hora para timestamp milissegundos:
  - Strings no formato ISO / `YYYY-MM-DD HH:MM:SS` são convertidas com `new Date(dataClean).getTime()`.
  - Registros sem data ('—' ou nulos) recebem timestamp infinito (`Infinity` / `9999-99-99 99:99`) para ficarem no final do grupo.
- Compara `timeA - timeB`. Se diferente, retorna `timeA - timeB`.

#### Critério 3: Ordem Alfabética (Nome do Paciente / Procedimento)
Se `timeA === timeB`:
- Compara nome do paciente: `nomeA.localeCompare(nomeB, 'pt-BR')`.
- Caso persistir empate de nomes, desempata pelo nome do procedimento: `procA.localeCompare(procB, 'pt-BR')`.
