SELECT prontuario as codigo, nome, nome_social, dt_nascimento, nome_mae
FROM agh.aip_pacientes
WHERE nome IS NOT NULL
  AND length(trim(nome)) > 2
  AND nome NOT LIKE '.%'
  AND nome NOT LIKE ',%'
  AND nome NOT LIKE '-%'
ORDER BY COALESCE(NULLIF(trim(nome_social), ''), nome)
LIMIT 100;
