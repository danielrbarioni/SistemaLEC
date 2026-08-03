## Context

A aplicação Sistema LEC utiliza SQLite como banco de dados de aplicação local e de solicitações (`data/app.db`). Durante operações de desenvolvimento e implantação, observou-se que a VM em homologação/produção perdia dados recentemente cadastrados (usuários adicionados, limpeza de solicitações de teste) após o deploy realizado a partir da máquina local.

**Causa Raiz Identificada:**
1. Os arquivos `app.db` e `data/app.db` foram em algum momento rastreados e commitados no repositório Git (`origin/main`).
2. O script de deploy na VM (`scratch/deploy_code_to_vm.py`) executava `git reset --hard origin/main`. Como o banco SQLite antigo fazia parte dos arquivos rastreados pelo Git, o `git reset --hard` forçava a restauração do banco antigo commitado no repositório remoto, sobrescrevendo a base viva da VM.
3. Existia ambiguidade entre dois arquivos de banco no projeto (`app.db` na raiz e `data/app.db`).

## Goals / Non-Goals

**Goals:**
- Desrastrear permanentemente arquivos `.db` no Git (`git rm --cached`).
- Atualizar o `.gitignore` para bloquear qualquer inclusão acidental de bancos de dados SQLite.
- Padronizar o caminho do banco de dados SQLite para `data/app.db`.
- Atualizar o script de deploy na VM para garantir que `data/app.db` fique protegido e intacto durante e após atualizações de código.
- Garantir a recuperação e manutenção dos usuários cadastrados e do histórico correto na VM.

**Non-Goals:**
- Migrar o banco de dados do sistema de SQLite para PostgreSQL/Oracle nesta etapa (mantém SQLite para solicitações/aplicação conforme arquitetura atual).

## Decisions

1. **Remoção dos arquivos de banco do Git Index**
   - **Decisão**: Executar `git rm --cached app.db data/app.db` no repositório local e realizar commit.
   - **Racional**: Bancos de dados de produção/homologação contêm dados dinâmicos e sensíveis e nunca devem residir no controle de versão de código fonte.

2. **Refatoração das Regras do `.gitignore`**
   - **Decisão**: Adicionar `*.db`, `app.db`, `data/*.db` ao `.gitignore`.
   - **Racional**: Impede que futuras alterações locais no banco entrem nos commits do Git.

3. **Ajuste dos Scripts de Deploy na VM**
   - **Decisão**: Atualizar `scratch/deploy_code_to_vm.py` para realizar backup de segurança automático do banco da VM antes do deploy e evitar o uso de `git reset --hard` sobre arquivos de dados.
   - **Racional**: Garante rollback imediato caso ocorra algum imprevisto e isola o diretório `/var/app/sistemalec/data/` de mutações pelo Git.

4. **Preservação dos Dados da VM**
   - **Decisão**: Inspecionar e validar os usuários e solicitações no banco atual da VM antes de consolidar a mudança.
   - **Racional**: Garante que os dois usuários adicionados e o histórico limpo continuem intactos na VM.

## Risks / Trade-offs

- **[Risco]** Perda acidental do banco durante a limpeza dos rastreados no Git.
  - → **Mitigação**: Fazer backup do `app.db` local e da VM antes de rodar qualquer comando de `git rm`.
- **[Risco]** Outros desenvolvedores executarem `git push` com banco.
  - → **Mitigação**: Regra no `.gitignore` e orientação clara sobre o isolamento do banco.
