import api from './api';

export interface ImportacaoResultado {
  total_linhas: number;
  solicitacoes_criadas: number;
  solicitacoes_atualizadas: number;
  novos_medicos: Array<{ username: string; especialidade: string }>;
  erros: string[];
}

export interface CoberturaEspecialidadesLec {
  total_cadastradas_cc: number;
  total_importadas_no_diagnostico: number;
  especialidades_importadas: Array<{
    esp_key: string;
    especialidade: string;
    arquivos: string[];
    linhas_lec: number;
    prontuarios_lec: number;
  }>;
  especialidades_sem_planilha: Array<{
    esp_key: string;
    especialidade: string;
    pacientes_ativos_cc: number;
  }>;
  especialidades_nao_cadastradas_no_cc: Array<{
    esp_key: string;
    especialidade: string;
    arquivos: string[];
    linhas_lec: number;
    prontuarios_lec: number;
  }>;
  arquivos_duplicados: Array<{
    arquivo_ignorado: string;
    arquivo_mantido: string;
    especialidade: string;
    linhas_arquivo_ignorado: number;
    linhas_extras_consolidadas: number;
  }>;
}

export interface LinhaTabelaEspecialidadeLec {
  esp_key: string;
  especialidade: string;
  cadastrada_no_cc: boolean;
  arquivos: string[];
  lec_linhas: number;
  lec_prontuarios: number;
  cc_linhas: number;
  cc_prontuarios: number;
  em_ambos: number;
  so_no_lec: number;
  so_no_cc: number;
  divergencias_info?: number;
  percentual_sincronia: number;
}

export type CategoriaDivergenciaLec =
  | 'EXCLUSAO_APROVADA_CC_PENDENTE_LEC'
  | 'INCLUSAO_APROVADA_CC_PENDENTE_LEC'
  | 'EM_OUTRA_ESPECIALIDADE_NO_CC'
  | 'DIVERGENCIA_DADOS_CADASTRAIS'
  | 'INSERIDO_DIRETO_NO_LEC'
  | 'SAIU_DO_LEC_SEM_BAIXA_NO_CC'
  | 'SOLICITACAO_PENDENTE_NO_CC';

export interface CampoDivergenteLec {
  campo: string;
  chave: 'swalis' | 'medico_responsavel' | 'lateralidade' | 'judicializado' | string;
  valor_cc: string;
  valor_lec: string;
}

export interface ItemDivergenciaLec {
  item_id: string;
  categoria: CategoriaDivergenciaLec;
  origem_divergencia: string;
  prontuario: number;
  nome_paciente: string;
  especialidade: string;
  esp_key: string;
  especialidade_secundaria?: string | null;
  esp_key_secundaria?: string | null;
  procedimento: string;
  procedimento_cc?: string | null;
  medico_responsavel: string;
  swalis: string;
  lateralidade?: string;
  judicializado: string;
  data_referencia: string;
  detalhes_status: string;
  solicitacao_id_cc?: string | null;
  campos_divergentes?: CampoDivergenteLec[];
  valores_atuais_cc?: {
    swalis: string;
    medico_responsavel: string;
    lateralidade: string;
    judicializado: string;
  };
  valores_atuais_lec?: {
    swalis: string;
    medico_responsavel: string;
    lateralidade: string;
    judicializado: string;
  };
  acao_sugerida_cc:
    | 'INCLUIR_NO_CC'
    | 'EXCLUIR_DO_CC'
    | 'DAR_BAIXA_NO_CC'
    | 'TRANSFERIR_ESPECIALIDADE_NO_CC'
    | 'EDITAR_INFORMACOES_NO_CC'
    | 'NENHUMA_ACAO_NO_CC';
  sincronizado_no_cc: boolean;
  data_sincronizacao?: string | null;
  usuario_sincronizacao?: string | null;
}

export interface DiagnosticoLecResumo {
  id: string;
  data_criacao: string;
  usuario: string;
  arquivos_nomes: string[];
  total_arquivos_enviados: number;
  total_arquivos_duplicados: number;
  especialidades_importadas_count: number;
  especialidades_cadastradas_cc_count: number;
  especialidades_sem_planilha_count: number;
  especialidades_nao_cadastradas_cc_count: number;
  prontuarios_unicos_lec: number;
  prontuarios_unicos_cc: number;
  prontuarios_em_ambos: number;
  percentual_sincronia_global: number;
  total_divergencias: number;
  total_sincronizados_no_cc: number;
  contagem_categorias: Record<CategoriaDivergenciaLec, number>;
}

export interface DiagnosticoLecDetalhado extends DiagnosticoLecResumo {
  cobertura_especialidades: CoberturaEspecialidadesLec;
  tabela_especialidades: LinhaTabelaEspecialidadeLec[];
  divergencias: ItemDivergenciaLec[];
}

export async function importarPlanilhaPacientes(file: File, especialidade: string): Promise<ImportacaoResultado> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('especialidade', especialidade);

  const response = await api.post<ImportacaoResultado>('/api/pacientes/importar-excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function listarDiagnosticosLec(): Promise<DiagnosticoLecResumo[]> {
  const response = await api.get<DiagnosticoLecResumo[]>('/api/pacientes/diagnostico-lec');
  return response.data;
}

export async function obterDiagnosticoLec(diagnosticoId: string): Promise<DiagnosticoLecDetalhado> {
  const response = await api.get<DiagnosticoLecDetalhado>(`/api/pacientes/diagnostico-lec/${diagnosticoId}`);
  return response.data;
}

export async function criarDiagnosticoLec(files: File[]): Promise<DiagnosticoLecDetalhado> {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }

  const response = await api.post<DiagnosticoLecDetalhado>('/api/pacientes/diagnostico-lec', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function sincronizarItensDiagnosticoLec(
  diagnosticoId: string,
  itemIds: string[],
  acao?: string,
  dadosEdicao?: Record<string, any>
): Promise<{
  sincronizados_agora: number;
  total_sincronizados_no_cc: number;
  diagnostico: DiagnosticoLecDetalhado;
}> {
  const response = await api.post(`/api/pacientes/diagnostico-lec/${diagnosticoId}/sincronizar`, {
    item_ids: itemIds,
    acao: acao || null,
    dados_edicao: dadosEdicao || null,
  });
  return response.data;
}
