# Proposal: Reformular Visualização do Menu Pacientes para Tabela Compacta com Modal de Detalhes

## Summary
Substituição do layout de cards expansíveis no menu **Pacientes** por uma **tabela compacta e otimizada** (uma linha por procedimento). Clicar no Prontuário ou no Nome do paciente abrirá um modal interativo expansivo exibindo o cabeçalho completo do paciente e seus procedimentos divididos em quadros/janelas individuais.

## Why
Com milhares de registros no Sistema LEC, a exibição anterior baseada em cards extensos e agrupados ocupava um espaço excessivo em tela, dificultando a rolagem, a legibilidade rápida e a comparação dos dados dos pacientes. Uma visualização em linha por procedimento proporciona densidade de dados e alta performance de navegação.

## Key Changes
1. **Tabela Principal Compacta**:
   - Cada linha representa 1 procedimento de 1 paciente.
   - Colunas obrigatórias:
     - `Prontuário`
     - `Nome Completo`
     - `Especialidade`
     - `Procedimento`
     - `Judicialização`
     - `Swalis`
     - `Médico Responsável`
   - O Prontuário e o Nome do Paciente serão links/botões clicáveis.

2. **Modal de Detalhes do Paciente (Pop-up)**:
   - Ao clicar no Prontuário ou no Nome de qualquer linha da tabela:
     - Abre um modal amplo com as informações gerais do paciente: `Prontuário`, `Nome Completo`, `Data de Nascimento` e `Nome da Mãe`.
     - Para cada procedimento que o paciente possuir cadastrado, será renderizado um quadro/janela interno apresentando: `Especialidade`, `Procedimento`, `Judicialização`, `Swalis` e `Médico Responsável`.

3. **Invariância de Dados**:
   - O banco de dados (`app.db`) e os serviços do backend não serão alterados; trata-se puramente de uma evolução visual do frontend Vue 3.

## Impact & Scope
- Vue Components: `frontend/src/views/Pacientes.vue`.
