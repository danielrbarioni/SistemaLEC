## 1. Limpeza do Repositório Git e Configuração de `.gitignore`

- [x] 1.1 Remover `app.db` e `data/app.db` do Git index (`git rm --cached`).
- [x] 1.2 Atualizar `.gitignore` adicionando `*.db`, `app.db`, `data/*.db` para prevenir inclusões futuras.
- [x] 1.3 Fazer commit das alterações no repositório local e push para `origin/main`.

## 2. Ajuste e Proteção nos Scripts de Deploy da VM

- [x] 2.1 Atualizar `scratch/deploy_code_to_vm.py` e rotinas de deploy para proteger `/var/app/sistemalec/data/app.db`.
- [x] 2.2 Adicionar rotina de backup automático da base SQLite na VM antes do pull do código.
- [x] 2.3 Executar desrastreamento do banco no repositório remoto da VM.

## 3. Validação e Preservação dos Dados na VM

- [x] 3.1 Inspecionar o banco na VM e restaurar/garantir a presença dos dois usuários cadastrados e do histórico correto sem solicitações de teste.
- [x] 3.2 Executar um deploy completo de teste da máquina local para a VM e verificar que a base de dados permanece 100% preservada.
