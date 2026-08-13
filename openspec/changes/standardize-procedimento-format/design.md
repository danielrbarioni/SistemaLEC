# Design: Padronizar Formato e Eliminar Duplicidades de Procedimentos

## Architecture Overview
Definição de lógica unificada de parse e formatação de procedimentos, garantindo consistência em todas as camadas (frontend e backend).

## Design Details

### 1. Regra de Formatação Padrão
Toda string de procedimento que contiver ID deve ser formatada como:
`NOME DO PROCEDIMENTO (ID XXX)`

Expressão regular/Lógica de Normalização:
- Capturar variações:
  - `NOME - ID XXX`
  - `NOME (ID XXX)`
  - `NOME (XXX)`
- Extrair o nome limpo em caixa alta (sem traços/parênteses residuais de ID) e o número do ID.
- Reconstruir como `${nomeLimpo} (ID ${id})`.

### 2. Frontend (`Pacientes.vue`, `InteracoesLec.vue`, `NavegacaoLec.vue`)
- Implementar helper reutilizável (ex.: em `string_helper.ts` ou funções utilitárias do Vue):
  - `formatarNomeProcedimento(str: string): string`
- Nos filtros de busca por procedimento:
  - Mapear a lista de procedimentos aplicando a normalização.
  - Aplicar `Array.from(new Set(...))` para remover itens duplicados.
- Na exibição dos dados dos pacientes e tabelas:
  - Passar a descrição do procedimento pelo helper de formatação.

### 3. Backend / Data Layer
- Garantir que os SQLs/provedores que obtêm procedimentos de especialidades retornem `NOME (ID XXX)` de forma limpa e consistente.
