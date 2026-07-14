SELECT 
    pci.seq AS id_procedimento,
    pci.descricao AS descricao,
    pci.ind_situacao AS situacao,
    esp.seq AS id_especialidade,
    esp.nome_especialidade AS especialidade
FROM agh.mbc_procedimento_cirurgicos pci
LEFT JOIN agh.mbc_especialidade_proc_cirgs epr ON pci.seq = epr.pci_seq
LEFT JOIN agh.agh_especialidades esp ON epr.esp_seq = esp.seq 
WHERE esp.seq = :id_especialidade AND pci.ind_situacao = 'A'
ORDER BY pci.descricao;
