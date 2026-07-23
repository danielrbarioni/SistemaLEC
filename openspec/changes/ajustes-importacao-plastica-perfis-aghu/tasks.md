## 1. Sanitização de Perfis

- [x] 1.1 Remover perfil duplicado da especialidade Plástica na tabela `perfis` do SQLite (`data/app.db`), mantendo apenas a chave primária `PLASTICA`.

## 2. Enriquecimento Cadastral via AGHU PostgreSQL

- [x] 2.1 Criar e executar o script Python `scratch/update_pacientes_aghu.py` para consultar o banco PostgreSQL do AGHU por prontuário e atualizar os dados cadastrais (nome, dt_nascimento, nome_mae, cpf, sexo) na tabela `pacientes` e `solicitacoes`.

## 3. Correção de Contadores na Tela de Pacientes

- [x] 3.1 Verificar e ajustar a rota backend (`src/routers/paciente.py` / `src/routers/solicitacao.py`) ou componente frontend (`Pacientes.vue`) para garantir que o total de procedimentos exiba corretamente a contagem total de solicitações (2.364 solicitações).

## 4. Validação

- [x] 4.1 Validar a remoção da duplicidade no menu Perfis do frontend.
- [x] 4.2 Validar a exibição dos nomes reais e dados cadastrais dos pacientes no menu Pacientes e no filtro de busca.
- [x] 4.3 Verificar a exatidão dos contadores de Pacientes e Procedimentos no frontend.

