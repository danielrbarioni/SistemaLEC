#!/usr/bin/env python3
"""
Script idempotente de saneamento de procedimentos genéricos e especialidades:
1) Atualiza os 239 pacientes da GINECOLOGIA GERAL com procedimentos genéricos (PROCEDIMENTO 706..983)
   para seus procedimentos oficiais do AGHU/LEC (<NOME DO PROCEDIMENTO> (ID <pci_seq>)).
2) Atualiza os 33 pacientes da DERMATOLOGIA com PROCEDIMENTO 966 para
   BIOPSIA DE PELE E PARTES MOLES (ID 966).
3) Atualiza o paciente da GERAL (Prontuário 11118031) com PROCEDIMENTO 326 para
   FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326).
4) Altera a especialidade dos 21 pacientes ativos da GERAL com
   CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26) para BARIÁTRICA.
5) Unifica ONCO - MASTO para ONCO-MASTO em todas as tabelas do banco.
"""
import os
import sys
import json
import sqlite3

GINECO_239_MAP = [
  {
    "sol_id": "SOL-FILA-5-14974760",
    "prontuario": 14974760,
    "old_proc": "PROCEDIMENTO 706",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-34-21980412",
    "prontuario": 21980412,
    "old_proc": "PROCEDIMENTO 707",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-20609657",
    "prontuario": 20609657,
    "old_proc": "PROCEDIMENTO 708",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-17034414",
    "prontuario": 17034414,
    "old_proc": "PROCEDIMENTO 709",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21120928",
    "prontuario": 21120928,
    "old_proc": "PROCEDIMENTO 710",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-14129081",
    "prontuario": 14129081,
    "old_proc": "PROCEDIMENTO 711",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-13945795",
    "prontuario": 13945795,
    "old_proc": "PROCEDIMENTO 712",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-17299397",
    "prontuario": 17299397,
    "old_proc": "PROCEDIMENTO 713",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21750948",
    "prontuario": 21750948,
    "old_proc": "PROCEDIMENTO 714",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21280896",
    "prontuario": 21280896,
    "old_proc": "PROCEDIMENTO 715",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21543806",
    "prontuario": 21543806,
    "old_proc": "PROCEDIMENTO 718",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-14390306",
    "prontuario": 14390306,
    "old_proc": "PROCEDIMENTO 719",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21528377",
    "prontuario": 21528377,
    "old_proc": "PROCEDIMENTO 720",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21906169",
    "prontuario": 21906169,
    "old_proc": "PROCEDIMENTO 721",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-20199782",
    "prontuario": 20199782,
    "old_proc": "PROCEDIMENTO 722",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-13165196",
    "prontuario": 13165196,
    "old_proc": "PROCEDIMENTO 723",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-5-21250022",
    "prontuario": 21250022,
    "old_proc": "PROCEDIMENTO 724",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-11317625",
    "prontuario": 11317625,
    "old_proc": "PROCEDIMENTO 725",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-11250255",
    "prontuario": 11250255,
    "old_proc": "PROCEDIMENTO 726",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-18920603",
    "prontuario": 18920603,
    "old_proc": "PROCEDIMENTO 727",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-21439690",
    "prontuario": 21439690,
    "old_proc": "PROCEDIMENTO 728",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-17721127",
    "prontuario": 17721127,
    "old_proc": "PROCEDIMENTO 729",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-20057295",
    "prontuario": 20057295,
    "old_proc": "PROCEDIMENTO 730",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-13467147",
    "prontuario": 13467147,
    "old_proc": "PROCEDIMENTO 731",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-16348138",
    "prontuario": 16348138,
    "old_proc": "PROCEDIMENTO 732",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-19627165",
    "prontuario": 19627165,
    "old_proc": "PROCEDIMENTO 733",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-19348762",
    "prontuario": 19348762,
    "old_proc": "PROCEDIMENTO 734",
    "new_proc": "VIDEOLAPAROSCOPIA (ID 824)"
  },
  {
    "sol_id": "SOL-FILA-5-18138404",
    "prontuario": 18138404,
    "old_proc": "PROCEDIMENTO 735",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-18320416",
    "prontuario": 18320416,
    "old_proc": "PROCEDIMENTO 736",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-15434814",
    "prontuario": 15434814,
    "old_proc": "PROCEDIMENTO 737",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-21460225",
    "prontuario": 21460225,
    "old_proc": "PROCEDIMENTO 742",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-21556634",
    "prontuario": 21556634,
    "old_proc": "PROCEDIMENTO 740",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-19121748",
    "prontuario": 19121748,
    "old_proc": "PROCEDIMENTO 743",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-21563994",
    "prontuario": 21563994,
    "old_proc": "PROCEDIMENTO 744",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-11277001",
    "prontuario": 11277001,
    "old_proc": "PROCEDIMENTO 745",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-16085482",
    "prontuario": 16085482,
    "old_proc": "PROCEDIMENTO 746",
    "new_proc": "HISTEROSCOPIA (DIAGNOSTICA) (ID 822)"
  },
  {
    "sol_id": "SOL-FILA-31-20775730",
    "prontuario": 20775730,
    "old_proc": "PROCEDIMENTO 748",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-20-16710972",
    "prontuario": 16710972,
    "old_proc": "PROCEDIMENTO 749",
    "new_proc": "EXERESE DE CISTO VAGINAL (ID 686)"
  },
  {
    "sol_id": "SOL-FILA-9-21821756",
    "prontuario": 21821756,
    "old_proc": "PROCEDIMENTO 750",
    "new_proc": "COLPOPERINEOPLASTIA POSTERIOR (ID 573)"
  },
  {
    "sol_id": "SOL-FILA-31-21638960",
    "prontuario": 21638960,
    "old_proc": "PROCEDIMENTO 751",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21334982",
    "prontuario": 21334982,
    "old_proc": "PROCEDIMENTO 752",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21919741",
    "prontuario": 21919741,
    "old_proc": "PROCEDIMENTO 754",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-21627948",
    "prontuario": 21627948,
    "old_proc": "PROCEDIMENTO 755",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-7-21647268",
    "prontuario": 21647268,
    "old_proc": "PROCEDIMENTO 758",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-31-16547119",
    "prontuario": 16547119,
    "old_proc": "PROCEDIMENTO 759",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-20-18864439",
    "prontuario": 18864439,
    "old_proc": "PROCEDIMENTO 760",
    "new_proc": "EXERESE DE CISTO VAGINAL (ID 686)"
  },
  {
    "sol_id": "SOL-FILA-31-21854021",
    "prontuario": 21854021,
    "old_proc": "PROCEDIMENTO 761",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-42-17442641",
    "prontuario": 17442641,
    "old_proc": "PROCEDIMENTO 762",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-42-12199584",
    "prontuario": 12199584,
    "old_proc": "PROCEDIMENTO 763",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-42-17020983",
    "prontuario": 17020983,
    "old_proc": "PROCEDIMENTO 764",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-11-11933220",
    "prontuario": 11933220,
    "old_proc": "PROCEDIMENTO 766",
    "new_proc": "HISTEROSCOPIA (DIAGNOSTICA) (ID 822)"
  },
  {
    "sol_id": "SOL-FILA-46-22011621",
    "prontuario": 22011621,
    "old_proc": "PROCEDIMENTO 768",
    "new_proc": "OOFORECTOMIA  OOFOROPLASTIA (ID 560)"
  },
  {
    "sol_id": "SOL-FILA-18-22219406",
    "prontuario": 22219406,
    "old_proc": "PROCEDIMENTO 769",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-46-11505443",
    "prontuario": 11505443,
    "old_proc": "PROCEDIMENTO 772",
    "new_proc": "OOFORECTOMIA  OOFOROPLASTIA (ID 560)"
  },
  {
    "sol_id": "SOL-FILA-37-21679444",
    "prontuario": 21679444,
    "old_proc": "PROCEDIMENTO 774",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-28-15150857",
    "prontuario": 15150857,
    "old_proc": "PROCEDIMENTO 775",
    "new_proc": "VIDEOLAPAROSCOPIA (ID 824)"
  },
  {
    "sol_id": "SOL-FILA-34-20401642",
    "prontuario": 20401642,
    "old_proc": "PROCEDIMENTO 776",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-37-21252283",
    "prontuario": 21252283,
    "old_proc": "PROCEDIMENTO 777",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-5-21492061",
    "prontuario": 21492061,
    "old_proc": "PROCEDIMENTO 843",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-14076533",
    "prontuario": 14076533,
    "old_proc": "PROCEDIMENTO 779",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-31-21432018",
    "prontuario": 21432018,
    "old_proc": "PROCEDIMENTO 780",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-28-21375225",
    "prontuario": 21375225,
    "old_proc": "PROCEDIMENTO 781",
    "new_proc": "HISTERECTOMIA C ANEXECTOMIA (UNI  BILATERAL) (ID 552)"
  },
  {
    "sol_id": "SOL-FILA-7-13416813",
    "prontuario": 13416813,
    "old_proc": "PROCEDIMENTO 782",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR C AMPUTACAO DE COLO (ID 544)"
  },
  {
    "sol_id": "SOL-FILA-7-20263604",
    "prontuario": 20263604,
    "old_proc": "PROCEDIMENTO 783",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR C AMPUTACAO DE COLO (ID 544)"
  },
  {
    "sol_id": "SOL-FILA-44-22090609",
    "prontuario": 22090609,
    "old_proc": "PROCEDIMENTO 784",
    "new_proc": "MIOMECTOMIA (ID 558)"
  },
  {
    "sol_id": "SOL-FILA-7-14650568",
    "prontuario": 14650568,
    "old_proc": "PROCEDIMENTO 785",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-22158315",
    "prontuario": 22158315,
    "old_proc": "PROCEDIMENTO 786",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-34-21677000",
    "prontuario": 21677000,
    "old_proc": "PROCEDIMENTO 787",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-7-14459069",
    "prontuario": 14459069,
    "old_proc": "PROCEDIMENTO 789",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-21827902",
    "prontuario": 21827902,
    "old_proc": "PROCEDIMENTO 790",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-14573794",
    "prontuario": 14573794,
    "old_proc": "PROCEDIMENTO 791",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-37-19356104",
    "prontuario": 19356104,
    "old_proc": "PROCEDIMENTO 793",
    "new_proc": "HISTEROSCOPIA CIRURGICA C RESSECTOSCOPIO (ID 557)"
  },
  {
    "sol_id": "SOL-FILA-37-19735844",
    "prontuario": 19735844,
    "old_proc": "PROCEDIMENTO 794",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-22178321",
    "prontuario": 22178321,
    "old_proc": "PROCEDIMENTO 795",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-20408274",
    "prontuario": 20408274,
    "old_proc": "PROCEDIMENTO 796",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-21923198",
    "prontuario": 21923198,
    "old_proc": "PROCEDIMENTO 797",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-21536818",
    "prontuario": 21536818,
    "old_proc": "PROCEDIMENTO 798",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-21773866",
    "prontuario": 21773866,
    "old_proc": "PROCEDIMENTO 799",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-22221915",
    "prontuario": 22221915,
    "old_proc": "PROCEDIMENTO 800",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-37-18275040",
    "prontuario": 18275040,
    "old_proc": "PROCEDIMENTO 801",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-28-22339899",
    "prontuario": 22339899,
    "old_proc": "PROCEDIMENTO 802",
    "new_proc": "HISTERECTOMIA C ANEXECTOMIA (UNI  BILATERAL) (ID 552)"
  },
  {
    "sol_id": "SOL-FILA-18-21460605",
    "prontuario": 21460605,
    "old_proc": "PROCEDIMENTO 804",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-34-21644877",
    "prontuario": 21644877,
    "old_proc": "PROCEDIMENTO 805",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-8-20468237",
    "prontuario": 20468237,
    "old_proc": "PROCEDIMENTO 806",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-21882337",
    "prontuario": 21882337,
    "old_proc": "PROCEDIMENTO 807",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-31-22293997",
    "prontuario": 22293997,
    "old_proc": "PROCEDIMENTO 808",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-8-17139460",
    "prontuario": 17139460,
    "old_proc": "PROCEDIMENTO 809",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-44-22303911",
    "prontuario": 22303911,
    "old_proc": "PROCEDIMENTO 810",
    "new_proc": "MIOMECTOMIA (ID 558)"
  },
  {
    "sol_id": "SOL-FILA-7-22353726",
    "prontuario": 22353726,
    "old_proc": "PROCEDIMENTO 811",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-31-22123004",
    "prontuario": 22123004,
    "old_proc": "PROCEDIMENTO 812",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-7-17654286",
    "prontuario": 17654286,
    "old_proc": "PROCEDIMENTO 813",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-5-14066070",
    "prontuario": 14066070,
    "old_proc": "PROCEDIMENTO 814",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-8-20637476",
    "prontuario": 20637476,
    "old_proc": "PROCEDIMENTO 815",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-44-16877698",
    "prontuario": 16877698,
    "old_proc": "PROCEDIMENTO 816",
    "new_proc": "MIOMECTOMIA (ID 558)"
  },
  {
    "sol_id": "SOL-FILA-5-10079572",
    "prontuario": 10079572,
    "old_proc": "PROCEDIMENTO 818",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-31-20513784",
    "prontuario": 20513784,
    "old_proc": "PROCEDIMENTO 819",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-19080563",
    "prontuario": 19080563,
    "old_proc": "PROCEDIMENTO 820",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-13090030",
    "prontuario": 13090030,
    "old_proc": "PROCEDIMENTO 821",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-5-21016399",
    "prontuario": 21016399,
    "old_proc": "PROCEDIMENTO 823",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-13523626",
    "prontuario": 13523626,
    "old_proc": "PROCEDIMENTO 825",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-17189010",
    "prontuario": 17189010,
    "old_proc": "PROCEDIMENTO 826",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-17633041",
    "prontuario": 17633041,
    "old_proc": "PROCEDIMENTO 827",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-5-13666938",
    "prontuario": 13666938,
    "old_proc": "PROCEDIMENTO 828",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-31-20870036",
    "prontuario": 20870036,
    "old_proc": "PROCEDIMENTO 829",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-7-18886606",
    "prontuario": 18886606,
    "old_proc": "PROCEDIMENTO 830",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-1-15150857",
    "prontuario": 15150857,
    "old_proc": "PROCEDIMENTO 831",
    "new_proc": "VIDEOLAPAROSCOPIA (ID 824)"
  },
  {
    "sol_id": "SOL-FILA-5-12464293",
    "prontuario": 12464293,
    "old_proc": "PROCEDIMENTO 832",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-46-21992466",
    "prontuario": 21992466,
    "old_proc": "PROCEDIMENTO 833",
    "new_proc": "OOFORECTOMIA  OOFOROPLASTIA (ID 560)"
  },
  {
    "sol_id": "SOL-FILA-31-21450754",
    "prontuario": 21450754,
    "old_proc": "PROCEDIMENTO 834",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-42-21101308",
    "prontuario": 21101308,
    "old_proc": "PROCEDIMENTO 835",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-7-20474920",
    "prontuario": 20474920,
    "old_proc": "PROCEDIMENTO 836",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-31-22097158",
    "prontuario": 22097158,
    "old_proc": "PROCEDIMENTO 837",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-5-10133197",
    "prontuario": 10133197,
    "old_proc": "PROCEDIMENTO 838",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-36-21128723",
    "prontuario": 21128723,
    "old_proc": "PROCEDIMENTO 839",
    "new_proc": "HISTERECTOMIA TOTAL AMPLIADA (WERTHEIN-MEIGS) (ID 556)"
  },
  {
    "sol_id": "SOL-FILA-7-14517170",
    "prontuario": 14517170,
    "old_proc": "PROCEDIMENTO 840",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-46-21689302",
    "prontuario": 21689302,
    "old_proc": "PROCEDIMENTO 841",
    "new_proc": "OOFORECTOMIA  OOFOROPLASTIA (ID 560)"
  },
  {
    "sol_id": "SOL-FILA-28-20640298",
    "prontuario": 20640298,
    "old_proc": "PROCEDIMENTO 842",
    "new_proc": "HISTERECTOMIA C ANEXECTOMIA (UNI  BILATERAL) (ID 552)"
  },
  {
    "sol_id": "SOL-FILA-9-21522172",
    "prontuario": 21522172,
    "old_proc": "PROCEDIMENTO 844",
    "new_proc": "COLPOPERINEOPLASTIA POSTERIOR (ID 573)"
  },
  {
    "sol_id": "SOL-FILA-7-18439638",
    "prontuario": 18439638,
    "old_proc": "PROCEDIMENTO 845",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-16517377",
    "prontuario": 16517377,
    "old_proc": "PROCEDIMENTO 846",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-21492053",
    "prontuario": 21492053,
    "old_proc": "PROCEDIMENTO 847",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-18673913",
    "prontuario": 18673913,
    "old_proc": "PROCEDIMENTO 848",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-18-17620733",
    "prontuario": 17620733,
    "old_proc": "PROCEDIMENTO 849",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-42-11765625",
    "prontuario": 11765625,
    "old_proc": "PROCEDIMENTO 850",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-42-14879738",
    "prontuario": 14879738,
    "old_proc": "PROCEDIMENTO 851",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-31-22142012",
    "prontuario": 22142012,
    "old_proc": "PROCEDIMENTO 852",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-5-20769907",
    "prontuario": 20769907,
    "old_proc": "PROCEDIMENTO 853",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-9-15834963",
    "prontuario": 15834963,
    "old_proc": "PROCEDIMENTO 854",
    "new_proc": "HISTEROSCOPIA (DIAGNOSTICA) (ID 822)"
  },
  {
    "sol_id": "SOL-FILA-7-19535566",
    "prontuario": 19535566,
    "old_proc": "PROCEDIMENTO 855",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-11076684",
    "prontuario": 11076684,
    "old_proc": "PROCEDIMENTO 856",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-13185764",
    "prontuario": 13185764,
    "old_proc": "PROCEDIMENTO 857",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-31-21486980",
    "prontuario": 21486980,
    "old_proc": "PROCEDIMENTO 858",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-34-15955925",
    "prontuario": 15955925,
    "old_proc": "PROCEDIMENTO 859",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-7-21957741",
    "prontuario": 21957741,
    "old_proc": "PROCEDIMENTO 860",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-23-22154744",
    "prontuario": 22154744,
    "old_proc": "PROCEDIMENTO 861",
    "new_proc": "EXERESE DE POLIPO DE UTERO (ID 549)"
  },
  {
    "sol_id": "SOL-FILA-34-11719465",
    "prontuario": 11719465,
    "old_proc": "PROCEDIMENTO 862",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-34-21885413",
    "prontuario": 21885413,
    "old_proc": "PROCEDIMENTO 863",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-5-21528666",
    "prontuario": 21528666,
    "old_proc": "PROCEDIMENTO 864",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-19707324",
    "prontuario": 19707324,
    "old_proc": "PROCEDIMENTO 865",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-17832916",
    "prontuario": 17832916,
    "old_proc": "PROCEDIMENTO 866",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-5-12079422",
    "prontuario": 12079422,
    "old_proc": "PROCEDIMENTO 867",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-10090595",
    "prontuario": 10090595,
    "old_proc": "PROCEDIMENTO 868",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-13713952",
    "prontuario": 13713952,
    "old_proc": "PROCEDIMENTO 869",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-5-21415815",
    "prontuario": 21415815,
    "old_proc": "PROCEDIMENTO 870",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-10123032",
    "prontuario": 10123032,
    "old_proc": "PROCEDIMENTO 871",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-31-13778436",
    "prontuario": 13778436,
    "old_proc": "PROCEDIMENTO 872",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-9-21910815",
    "prontuario": 21910815,
    "old_proc": "PROCEDIMENTO 873",
    "new_proc": "COLPOPERINEOPLASTIA POSTERIOR (ID 573)"
  },
  {
    "sol_id": "SOL-FILA-5-19561497",
    "prontuario": 19561497,
    "old_proc": "PROCEDIMENTO 874",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-7-21793880",
    "prontuario": 21793880,
    "old_proc": "PROCEDIMENTO 875",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-42-22098297",
    "prontuario": 22098297,
    "old_proc": "PROCEDIMENTO 876",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-42-22146518",
    "prontuario": 22146518,
    "old_proc": "PROCEDIMENTO 877",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-31-21926621",
    "prontuario": 21926621,
    "old_proc": "PROCEDIMENTO 878",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-31-18288381",
    "prontuario": 18288381,
    "old_proc": "PROCEDIMENTO 879",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-9-15370547",
    "prontuario": 15370547,
    "old_proc": "PROCEDIMENTO 880",
    "new_proc": "COLPOPERINEOPLASTIA POSTERIOR (ID 573)"
  },
  {
    "sol_id": "SOL-FILA-42-21135264",
    "prontuario": 21135264,
    "old_proc": "PROCEDIMENTO 881",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-31-14784995",
    "prontuario": 14784995,
    "old_proc": "PROCEDIMENTO 968",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-34-21734009",
    "prontuario": 21734009,
    "old_proc": "PROCEDIMENTO 883",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-46-19191832",
    "prontuario": 19191832,
    "old_proc": "PROCEDIMENTO 884",
    "new_proc": "OOFORECTOMIA  OOFOROPLASTIA (ID 560)"
  },
  {
    "sol_id": "SOL-FILA-7-21545736",
    "prontuario": 21545736,
    "old_proc": "PROCEDIMENTO 974",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-14873384",
    "prontuario": 14873384,
    "old_proc": "PROCEDIMENTO 887",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-22227839",
    "prontuario": 22227839,
    "old_proc": "PROCEDIMENTO 888",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-31-19871573",
    "prontuario": 19871573,
    "old_proc": "PROCEDIMENTO 967",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-28-22271910",
    "prontuario": 22271910,
    "old_proc": "PROCEDIMENTO 891",
    "new_proc": "HISTERECTOMIA C ANEXECTOMIA (UNI  BILATERAL) (ID 552)"
  },
  {
    "sol_id": "SOL-FILA-42-21509898",
    "prontuario": 21509898,
    "old_proc": "PROCEDIMENTO 892",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-34-21316310",
    "prontuario": 21316310,
    "old_proc": "PROCEDIMENTO 893",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-7-11002250",
    "prontuario": 11002250,
    "old_proc": "PROCEDIMENTO 894",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-5-21525233",
    "prontuario": 21525233,
    "old_proc": "PROCEDIMENTO 895",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-34-22184550",
    "prontuario": 22184550,
    "old_proc": "PROCEDIMENTO 896",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-31-22168322",
    "prontuario": 22168322,
    "old_proc": "PROCEDIMENTO 897",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-7-14085904",
    "prontuario": 14085904,
    "old_proc": "PROCEDIMENTO 898",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-23-20105748",
    "prontuario": 20105748,
    "old_proc": "PROCEDIMENTO 900",
    "new_proc": "EXERESE DE POLIPO DE UTERO (ID 549)"
  },
  {
    "sol_id": "SOL-FILA-7-12824504",
    "prontuario": 12824504,
    "old_proc": "PROCEDIMENTO 901",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-22332308",
    "prontuario": 22332308,
    "old_proc": "PROCEDIMENTO 902",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-22137251",
    "prontuario": 22137251,
    "old_proc": "PROCEDIMENTO 904",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-17802653",
    "prontuario": 17802653,
    "old_proc": "PROCEDIMENTO 905",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-18-22331847",
    "prontuario": 22331847,
    "old_proc": "PROCEDIMENTO 906",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-18-15851330",
    "prontuario": 15851330,
    "old_proc": "PROCEDIMENTO 907",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-7-21320775",
    "prontuario": 21320775,
    "old_proc": "PROCEDIMENTO 908",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-59-16953481",
    "prontuario": 16953481,
    "old_proc": "PROCEDIMENTO 909",
    "new_proc": "TRATAMENTO CIRURGICO DE INCONTINENCIA URINARIA POR VIA VAGINAL (ID 580)"
  },
  {
    "sol_id": "SOL-FILA-31-21902259",
    "prontuario": 21902259,
    "old_proc": "PROCEDIMENTO 910",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-63-19432582",
    "prontuario": 19432582,
    "old_proc": "PROCEDIMENTO 911",
    "new_proc": "VULVECTOMIA SIMPLES (ID 571)"
  },
  {
    "sol_id": "SOL-FILA-31-11166782",
    "prontuario": 11166782,
    "old_proc": "PROCEDIMENTO 912",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-7-11832797",
    "prontuario": 11832797,
    "old_proc": "PROCEDIMENTO 915",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-42-17930207",
    "prontuario": 17930207,
    "old_proc": "PROCEDIMENTO 916",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-7-14475032",
    "prontuario": 14475032,
    "old_proc": "PROCEDIMENTO 918",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-21408158",
    "prontuario": 21408158,
    "old_proc": "PROCEDIMENTO 919",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-7-22030803",
    "prontuario": 22030803,
    "old_proc": "PROCEDIMENTO 920",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-20834479",
    "prontuario": 20834479,
    "old_proc": "PROCEDIMENTO 921",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-7-18761411",
    "prontuario": 18761411,
    "old_proc": "PROCEDIMENTO 922",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-22156988",
    "prontuario": 22156988,
    "old_proc": "PROCEDIMENTO 923",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-4-20853032",
    "prontuario": 20853032,
    "old_proc": "PROCEDIMENTO 924",
    "new_proc": "CIRURGIAS COMPLEMENTARES DE REDESIGNACAO SEXUAL (ID 540)"
  },
  {
    "sol_id": "SOL-FILA-5-17992462",
    "prontuario": 17992462,
    "old_proc": "PROCEDIMENTO 925",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-34-22174353",
    "prontuario": 22174353,
    "old_proc": "PROCEDIMENTO 926",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-31-21179445",
    "prontuario": 21179445,
    "old_proc": "PROCEDIMENTO 927",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-5-21271895",
    "prontuario": 21271895,
    "old_proc": "PROCEDIMENTO 928",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-31-13929716",
    "prontuario": 13929716,
    "old_proc": "PROCEDIMENTO 929",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-44-21977574",
    "prontuario": 21977574,
    "old_proc": "PROCEDIMENTO 930",
    "new_proc": "MIOMECTOMIA (ID 558)"
  },
  {
    "sol_id": "SOL-FILA-7-21399027",
    "prontuario": 21399027,
    "old_proc": "PROCEDIMENTO 931",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-7-11213899",
    "prontuario": 11213899,
    "old_proc": "PROCEDIMENTO 932",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-11168051",
    "prontuario": 11168051,
    "old_proc": "PROCEDIMENTO 933",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-34-21014725",
    "prontuario": 21014725,
    "old_proc": "PROCEDIMENTO 935",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-46-18868141",
    "prontuario": 18868141,
    "old_proc": "PROCEDIMENTO 937",
    "new_proc": "OOFORECTOMIA  OOFOROPLASTIA (ID 560)"
  },
  {
    "sol_id": "SOL-FILA-34-22148514",
    "prontuario": 22148514,
    "old_proc": "PROCEDIMENTO 938",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-34-21904115",
    "prontuario": 21904115,
    "old_proc": "PROCEDIMENTO 940",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-18-22133060",
    "prontuario": 22133060,
    "old_proc": "PROCEDIMENTO 941",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-42-17376989",
    "prontuario": 17376989,
    "old_proc": "PROCEDIMENTO 942",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-18-22017404",
    "prontuario": 22017404,
    "old_proc": "PROCEDIMENTO 943",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-42-20615043",
    "prontuario": 20615043,
    "old_proc": "PROCEDIMENTO 944",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-31-20592697",
    "prontuario": 20592697,
    "old_proc": "PROCEDIMENTO 945",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-34-19100783",
    "prontuario": 19100783,
    "old_proc": "PROCEDIMENTO 946",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-34-22013353",
    "prontuario": 22013353,
    "old_proc": "PROCEDIMENTO 947",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-34-13325162",
    "prontuario": 13325162,
    "old_proc": "PROCEDIMENTO 964",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-24-22003826",
    "prontuario": 22003826,
    "old_proc": "PROCEDIMENTO 949",
    "new_proc": "EXTIRPACAO DE LESAO DE VULVA  PERINEO (POR ELETROCOAGULACAO OU FULGURACAO) (ID 577)"
  },
  {
    "sol_id": "SOL-FILA-37-21312533",
    "prontuario": 21312533,
    "old_proc": "PROCEDIMENTO 950",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-34-22191225",
    "prontuario": 22191225,
    "old_proc": "PROCEDIMENTO 951",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-5-11165313",
    "prontuario": 11165313,
    "old_proc": "PROCEDIMENTO 952",
    "new_proc": "CISTOSCOPIA E OU URETEROSCOPIA E OU URETROSCOPIA (ID 705)"
  },
  {
    "sol_id": "SOL-FILA-8-22207427",
    "prontuario": 22207427,
    "old_proc": "PROCEDIMENTO 953",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-9-14199491",
    "prontuario": 14199491,
    "old_proc": "PROCEDIMENTO 954",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-37-21244132",
    "prontuario": 21244132,
    "old_proc": "PROCEDIMENTO 955",
    "new_proc": "HISTERECTOMIA VIDEOLAPAROSCOPICA (ID 553)"
  },
  {
    "sol_id": "SOL-FILA-42-22170559",
    "prontuario": 22170559,
    "old_proc": "PROCEDIMENTO 956",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-7-22261747",
    "prontuario": 22261747,
    "old_proc": "PROCEDIMENTO 957",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-57-22313142",
    "prontuario": 22313142,
    "old_proc": "PROCEDIMENTO 958",
    "new_proc": "TRATAMENTO CIRURGICO DE FISTULA VESICO-VAGINAL (ID 575)"
  },
  {
    "sol_id": "SOL-FILA-7-17928482",
    "prontuario": 17928482,
    "old_proc": "PROCEDIMENTO 959",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-34-21380043",
    "prontuario": 21380043,
    "old_proc": "PROCEDIMENTO 960",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-31-11168051",
    "prontuario": 11168051,
    "old_proc": "PROCEDIMENTO 961",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-42-22115430",
    "prontuario": 22115430,
    "old_proc": "PROCEDIMENTO 962",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-18-21679998",
    "prontuario": 21679998,
    "old_proc": "PROCEDIMENTO 963",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-8-11076684",
    "prontuario": 11076684,
    "old_proc": "PROCEDIMENTO 965",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-42-22262067",
    "prontuario": 22262067,
    "old_proc": "PROCEDIMENTO 969",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-34-22042808",
    "prontuario": 22042808,
    "old_proc": "PROCEDIMENTO 972",
    "new_proc": "HISTERECTOMIA TOTAL (ID 545)"
  },
  {
    "sol_id": "SOL-FILA-18-22243083",
    "prontuario": 22243083,
    "old_proc": "PROCEDIMENTO 975",
    "new_proc": "EXCISAO TIPO 3 DO COLO UTERINO (ID 546)"
  },
  {
    "sol_id": "SOL-FILA-7-21878830",
    "prontuario": 21878830,
    "old_proc": "PROCEDIMENTO 976",
    "new_proc": "COLPOPERINEOPLASTIA ANTERIOR E POSTERIOR (ID 568)"
  },
  {
    "sol_id": "SOL-FILA-42-21968375",
    "prontuario": 21968375,
    "old_proc": "PROCEDIMENTO 977",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-21-22142939",
    "prontuario": 22142939,
    "old_proc": "PROCEDIMENTO 978",
    "new_proc": "EXERESE DE GLANDULA DE BARTHOLIN  SKENE (ID 569)"
  },
  {
    "sol_id": "SOL-FILA-63-22314686",
    "prontuario": 22314686,
    "old_proc": "PROCEDIMENTO 980",
    "new_proc": "VULVECTOMIA SIMPLES (ID 571)"
  },
  {
    "sol_id": "SOL-FILA-31-21458542",
    "prontuario": 21458542,
    "old_proc": "PROCEDIMENTO 981",
    "new_proc": "HISTERECTOMIA (POR VIA VAGINAL) (ID 517)"
  },
  {
    "sol_id": "SOL-FILA-42-22260962",
    "prontuario": 22260962,
    "old_proc": "PROCEDIMENTO 983",
    "new_proc": "LAQUEADURA TUBARIA (ID 551)"
  },
  {
    "sol_id": "SOL-FILA-5-13875836",
    "prontuario": 13875836,
    "old_proc": "PROCEDIMENTO 739",
    "new_proc": "HISTEROSCOPIA (DIAGNOSTICA) (ID 822)"
  },
  {
    "sol_id": "SOL-FILA-5-18589218",
    "prontuario": 18589218,
    "old_proc": "PROCEDIMENTO 767",
    "new_proc": "HISTEROSCOPIA (DIAGNOSTICA) (ID 822)"
  }
]

BARIATRICA_21_PRONTUARIOS = [12374120, 14875322, 15944275, 17836214, 18711838, 18854075, 20171732, 20455861, 21375225, 21378351, 21793559, 21906805, 21914353, 21944871, 21956396, 21997051, 22142988, 22171771, 22209522, 22238018, 22244420]

DERMA_NEW_PROC = "BIOPSIA DE PELE E PARTES MOLES (ID 966)"
GERAL_326_NEW_PROC = "FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)"


def run_saneamento(db_path: str) -> dict:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Banco de dados não encontrado: {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    stats = {
        "gineco_solicitacoes_updated": 0,
        "gineco_pacientes_updated": 0,
        "derma_solicitacoes_updated": 0,
        "derma_pacientes_updated": 0,
        "geral_326_solicitacoes_updated": 0,
        "geral_326_pacientes_updated": 0,
        "bariatrica_solicitacoes_updated": 0,
        "bariatrica_pacientes_updated": 0,
        "onco_masto_updated": 0,
    }

    try:
        # 1) 239 pacientes da GINECOLOGIA GERAL
        for item in GINECO_239_MAP:
            sol_id = item["sol_id"]
            pront = item["prontuario"]
            old_proc = item["old_proc"]
            new_proc = item["new_proc"]

            cur.execute(
                """
                UPDATE solicitacoes
                SET procedimento = ?
                WHERE (id = ? OR (codigo_paciente = ? AND UPPER(TRIM(especialidade)) = 'GINECOLOGIA GERAL' AND UPPER(TRIM(procedimento)) = UPPER(?)))
                  AND procedimento != ?
                """,
                (new_proc, sol_id, pront, old_proc, new_proc),
            )
            stats["gineco_solicitacoes_updated"] += cur.rowcount

            cur.execute(
                """
                UPDATE solicitacoes
                SET procedimento_anterior = ?
                WHERE codigo_paciente = ?
                  AND UPPER(TRIM(especialidade)) = 'GINECOLOGIA GERAL'
                  AND UPPER(TRIM(procedimento_anterior)) = UPPER(?)
                """,
                (new_proc, pront, old_proc),
            )

            cur.execute(
                """
                UPDATE pacientes
                SET procedimento = ?
                WHERE codigo = ?
                  AND (UPPER(TRIM(procedimento)) = UPPER(?) OR UPPER(TRIM(procedimento)) LIKE 'PROCEDIMENTO %')
                """,
                (new_proc, pront, old_proc),
            )
            stats["gineco_pacientes_updated"] += cur.rowcount

        # 2) 33 pacientes da DERMATOLOGIA (PROCEDIMENTO 966 -> BIOPSIA DE PELE E PARTES MOLES (ID 966))
        cur.execute(
            """
            UPDATE solicitacoes
            SET procedimento = ?
            WHERE UPPER(TRIM(especialidade)) = 'DERMATOLOGIA'
              AND UPPER(TRIM(procedimento)) = 'PROCEDIMENTO 966'
            """,
            (DERMA_NEW_PROC,),
        )
        stats["derma_solicitacoes_updated"] += cur.rowcount

        cur.execute(
            """
            UPDATE solicitacoes
            SET procedimento_anterior = ?
            WHERE UPPER(TRIM(especialidade)) = 'DERMATOLOGIA'
              AND UPPER(TRIM(procedimento_anterior)) = 'PROCEDIMENTO 966'
            """,
            (DERMA_NEW_PROC,),
        )

        cur.execute(
            """
            UPDATE pacientes
            SET procedimento = ?
            WHERE UPPER(TRIM(especialidade)) = 'DERMATOLOGIA'
              AND UPPER(TRIM(procedimento)) = 'PROCEDIMENTO 966'
            """,
            (DERMA_NEW_PROC,),
        )
        stats["derma_pacientes_updated"] += cur.rowcount

        # 3) 1 paciente da GERAL (Prontuário 11118031, PROCEDIMENTO 326 -> FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326))
        cur.execute(
            """
            UPDATE solicitacoes
            SET procedimento = ?
            WHERE UPPER(TRIM(especialidade)) = 'GERAL'
              AND UPPER(TRIM(procedimento)) = 'PROCEDIMENTO 326'
            """,
            (GERAL_326_NEW_PROC,),
        )
        stats["geral_326_solicitacoes_updated"] += cur.rowcount

        cur.execute(
            """
            UPDATE solicitacoes
            SET procedimento_anterior = ?
            WHERE UPPER(TRIM(especialidade)) = 'GERAL'
              AND UPPER(TRIM(procedimento_anterior)) = 'PROCEDIMENTO 326'
            """,
            (GERAL_326_NEW_PROC,),
        )

        cur.execute(
            """
            UPDATE pacientes
            SET procedimento = ?
            WHERE UPPER(TRIM(especialidade)) = 'GERAL'
              AND UPPER(TRIM(procedimento)) = 'PROCEDIMENTO 326'
            """,
            (GERAL_326_NEW_PROC,),
        )
        stats["geral_326_pacientes_updated"] += cur.rowcount

        # 4) 21 pacientes ativos da GERAL com CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26) -> BARIÁTRICA
        placeholders = ",".join("?" for _ in BARIATRICA_21_PRONTUARIOS)
        cur.execute(
            f"""
            UPDATE solicitacoes
            SET especialidade = 'BARIÁTRICA'
            WHERE codigo_paciente IN ({placeholders})
              AND UPPER(TRIM(especialidade)) = 'GERAL'
              AND UPPER(TRIM(procedimento)) LIKE 'CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA%'
            """,
            BARIATRICA_21_PRONTUARIOS,
        )
        stats["bariatrica_solicitacoes_updated"] += cur.rowcount

        cur.execute(
            f"""
            UPDATE pacientes
            SET especialidade = 'BARIÁTRICA'
            WHERE codigo IN ({placeholders})
              AND UPPER(TRIM(especialidade)) = 'GERAL'
              AND UPPER(TRIM(procedimento)) LIKE 'CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA%'
            """,
            BARIATRICA_21_PRONTUARIOS,
        )
        stats["bariatrica_pacientes_updated"] += cur.rowcount

        # 5) Unificação ONCO - MASTO -> ONCO-MASTO em todas as tabelas
        for tbl in ("perfis", "usuarios", "solicitacoes", "pacientes", "categorizacoes_profissionais"):
            try:
                cur.execute(
                    f"""
                    UPDATE {tbl}
                    SET especialidade = 'ONCO-MASTO'
                    WHERE UPPER(TRIM(especialidade)) = 'ONCO - MASTO'
                    """
                )
                stats["onco_masto_updated"] += cur.rowcount
            except sqlite3.OperationalError:
                pass

        cur.execute(
            """
            UPDATE perfis
            SET nome = 'ONCO-MASTO'
            WHERE UPPER(TRIM(nome)) = 'ONCO - MASTO'
            """
        )
        stats["onco_masto_updated"] += cur.rowcount

        cur.execute(
            """
            UPDATE solicitacoes
            SET detalhes = REPLACE(detalhes, 'ONCO - MASTO', 'ONCO-MASTO')
            WHERE detalhes LIKE '%ONCO - MASTO%'
            """
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return stats


if __name__ == "__main__":
    target_db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
    result = run_saneamento(target_db)
    print(json.dumps(result, indent=2, ensure_ascii=False))
