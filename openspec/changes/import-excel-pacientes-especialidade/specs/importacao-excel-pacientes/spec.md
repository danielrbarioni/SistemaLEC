# Importação de Planilha Excel de Pacientes por Especialidade

## MUSTs

- O sistema **MUST** disponibilizar um botão de importação de planilha Excel no menu **Pacientes**, visível exclusivamente para usuários autenticados com o perfil **Gestão LEC**.
- O sistema **MUST** aceitar arquivos no formato `.xlsx` e `.xls` contendo as colunas especificadas: `id_fila`, `Prontuário`, `id_procedimento`, `medico_responsavel`, `id_motivo_status`, `id_especialidade`, `swalis`, `sin_judicializado`, `dth_indicação`.
- Caso o `medico_responsavel` informado na planilha não possua cadastro como usuário para aquela especialidade, o sistema **MUST** criar automaticamente o registro do usuário com o login EBSERH (`username`), deixando o `nome_completo` nulo (`None`).
- O sistema **MUST** utilizar o `username` como fallback para exibição em todas as telas (Pacientes, Comunicação LEC, Histórico) sempre que o `nome_completo` do médico for nulo.
- O sistema **MUST** desconsiderar as colunas `sin_oncologico` (E), `uti` (F) e `sin_rt` (H) durante o processamento da planilha.
