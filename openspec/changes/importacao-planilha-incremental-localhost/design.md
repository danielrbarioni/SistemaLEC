## Context

O Gestor LEC necessita realizar o carregamento de planilhas de fila por especialidade (como a planilha de banco de dados da Plástica) utilizando o ambiente local (**localhost**). As importações anteriores continham 2.364 solicitações e a nova planilha contém 2.518 registros.

## Goals / Non-Goals

**Goals:**
- Manter o banco da máquina virtual (VM) estritamente preservado e intocado.
- Realizar a comparação incremental em memória (chave primária `solic_id` + chave composta `(codigo_paciente, procedimento)`).
- Atualizar solicitações já cadastradas e adicionar unicamente as solicitações excedentes.
- Assegurar que o upload via interface web (`/api/pacientes/importar-excel`) funcione sem erros de drag-and-drop e sem HTTP 405.

**Non-Goals:**
- Sincronizar o banco de dados local com a máquina virtual da produção nesta fase.

## Decisions

1. **Restrição de Execução ao Localhost**:
   - Todas as requisições de importação e alterações de banco ocorrem no SQLite local `data/app.db` durante os testes do gestor.

2. **Mapeamento de Comparação Inteligente**:
   - `existing_solic_by_key[(codigo_paciente, procedimento)]`: Permite identificar solicitações preexistentes independentemente de variações no prefixo do ID.

## Risks / Trade-offs

- **[Risk] Arquivos abertos por acidente no navegador ao soltar fora da caixa** → *Mitigation*: Adicionados ouvintes `window.addEventListener('drop', preventDefault)` no modal.
