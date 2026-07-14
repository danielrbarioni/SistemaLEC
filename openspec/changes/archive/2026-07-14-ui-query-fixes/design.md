## Context

Após a entrega inicial, foram solicitados refinamentos na busca do prontuário (para usar a coluna `prontuario` do AGHU em vez da coluna `codigo`) e na interface (desativar digitação manual do nome, remover textos de integração futura, filtrar a lista geral de pacientes para exibir apenas os que possuem solicitações e mudar o título da aba do navegador).

## Goals / Non-Goals

**Goals:**
- Ajustar os arquivos SQL de paciente no backend.
- Modificar o `HybridPacienteProvider` para obter apenas pacientes correspondentes a códigos em solicitações/status locais.
- Desabilitar a digitação manual de nome no formulário.
- Mudar o `<title>` no `index.html`.

**Non-Goals:**
- Criar novas tabelas no banco de dados.

## Decisions

- **Busca por Prontuário**: Ajustar a correspondência do prontuário para o campo `prontuario` na base PostgreSQL do AGHU.
- **Filtro de Lista**: Usar agregação de códigos no SQLite para filtrar a consulta dos dados cadastrais.

## Risks / Trade-offs

Sem riscos críticos identificados.
