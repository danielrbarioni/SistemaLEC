import api from './api';

export interface ImportacaoResultado {
  total_linhas: number;
  solicitacoes_criadas: number;
  solicitacoes_atualizadas: number;
  novos_medicos: Array<{ username: string; especialidade: string }>;
  erros: string[];
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
