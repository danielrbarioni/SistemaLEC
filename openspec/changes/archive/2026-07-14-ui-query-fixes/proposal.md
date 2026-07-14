## Why

Ajustes adicionais no frontend e nas consultas de banco de dados do AGHU são necessários para refinar a experiência do usuário (UX), corrigir a listagem de pacientes (que não deve carregar todos os pacientes do AGHU), forçar o autopreenchimento desabilitando a digitação manual do nome e alterar o título da aba do navegador.

## What Changes

- **Filtro de Pacientes**: A listagem de pacientes na tela de Pacientes passa a trazer apenas os pacientes que já possuem alguma movimentação (solicitação ou status) cadastrada no LEC.
- **Busca por Prontuário**: Ajuste nas queries do AGHU para mapear e buscar pela coluna `prontuario` em vez de `codigo` do paciente.
- **Desativação de Campo de Nome**: O campo de Nome Completo do Paciente foi desabilitado e teve seu placeholder atualizado para "Preenchido automaticamente".
- **Título do Navegador**: O título da aba do navegador foi atualizado para "Gestão LEC HC-UFPE".

## Capabilities

### New Capabilities
- `ui-query-fixes`: Correções de UI e mapeamento de prontuário no banco de dados.

### Modified Capabilities
- `paciente`: Alteração na estratégia de listagem e busca por prontuário no AGHU.

## Impact

- **Backend**: Queries SQL e HybridPacienteProvider.
- **Frontend**: Visões de Interações LEC e título global no index.html.
