## Context

Precisamos garantir que o usuário `daniel.barioni` exista no banco SQLite local (`data/app.db`) com o perfil `ADMIN` para fins de controle de acesso local e de desenvolvimento. A tabela `perfis` no SQLite local também precisa conter o perfil `ADMIN` para que a integridade referencial e o fluxo de dados funcionem adequadamente no backend e no frontend.

## Goals / Non-Goals

**Goals:**
- Criar um script de seed `scratch/seed_admin_daniel.py` que insere o perfil `ADMIN` na tabela `perfis` (se não existir) e o usuário `daniel.barioni` na tabela `usuarios` (se não existir) associado a esse perfil.
- Executar esse script para aplicar a semente no banco de dados SQLite local.

**Non-Goals:**
- Modificar o código de autenticação do backend ou os fluxos de login existentes.

## Decisions

1. **Script de Seed Independente:**
   Criar um script em `scratch/seed_admin_daniel.py` utilizando o módulo nativo `sqlite3` do Python para realizar as inserções diretas no banco de dados SQLite, evitando dependências extras durante o seed do banco de dados.

2. **Perfis a serem inseridos:**
   - ID: `ADMIN`, Nome: `Administrador`, Tipo: `ADMIN`, Cor: `azul`, Especialidade: `None`.

3. **Usuários a serem inseridos:**
   - Username: `daniel.barioni`, Nome: `Daniel Barioni`, Perfil: `ADMIN`, Especialidade: `None`.

## Risks / Trade-offs

- **[Risco]** Sobrescrever registros existentes → **Mitigação**: Utilizar cláusulas `INSERT OR IGNORE` ou verificar a existência antes de inserir para evitar duplicatas ou alterações indesejadas em registros existentes.
