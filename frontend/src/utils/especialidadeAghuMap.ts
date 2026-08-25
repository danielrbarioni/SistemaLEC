import api from '../services/api';

/**
 * Mapeamento dos códigos de especialidades do AGHU (seq da tabela agh.agh_especialidades)
 * para cada especialidade padronizada no Sistema LEC.
 */
export const ESPECIALIDADE_AGHU_MAP: Record<string, number[]> = {
  'PLÁSTICA': [1884],
  'ORTOPEDIA': [386, 1974, 1971, 1972, 1616, 1978, 1977],
  'GERAL': [33],
  'ONCOLÓGICA': [1847, 2080, 1466],
  'UROLOGIA': [556, 1420],
  'HEMODINÂMICA': [1270],
  'VASCULAR': [37],
  'APARELHO DIGESTIVO': [727],
  'RADIOLOGIA INTERVENCIONISTA': [2444],
  'PEDIÁTRICA': [1888, 1560],
  'OTORRINOLARINGOLOGIA': [392, 2450],
  'GINECOLOGIA GERAL': [1236, 1237, 1792],
  'GINECOLOGIA ENDOSCÓPICA': [1728, 1441],
  'OFTALMOLOGIA': [366, 2052],
  'NEUROCIRURGIA': [291],
  'TORÁCICA': [1886, 1436],
  'PROCTOLOGIA': [1450],
  'BUCOMAXILOFACIAL': [1461],
  'CABEÇA E PESCOÇO': [1242],
  'CARDÍACA': [2262, 17],
  'DERMATOLOGIA': [1602, 1426],
  'BARIÁTRICA': [1652, 2230, 2512],
  'MASTOLOGIA - ESPAÇO TRANS': [1745, 284, 1744, 2216],
};

// Cache em memória para evitar requisições repetidas ao AGHU durante a sessão
const procedimentosAghuCache = new Map<string, string[]>();

/**
 * Normaliza o nome da especialidade para matching no mapa
 */
export function normalizarNomeEspecialidade(nome: string): string {
  if (!nome) return '';
  return nome
    .toUpperCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

/**
 * Encontra os códigos do AGHU para uma dada especialidade
 */
export function getAghuIdsForEspecialidade(nomeEspecialidade: string): number[] {
  if (!nomeEspecialidade) return [];
  
  const direct = ESPECIALIDADE_AGHU_MAP[nomeEspecialidade.trim().toUpperCase()];
  if (direct && direct.length > 0) return direct;

  const targetNorm = normalizarNomeEspecialidade(nomeEspecialidade);
  for (const [esp, ids] of Object.entries(ESPECIALIDADE_AGHU_MAP)) {
    const keyNorm = normalizarNomeEspecialidade(esp);
    if (keyNorm === targetNorm || keyNorm.includes(targetNorm) || targetNorm.includes(keyNorm)) {
      return ids;
    }
  }

  return [];
}

/**
 * Busca procedimentos cadastrados no AGHU para a especialidade informada.
 * Formato retornado: "NOME DO PROCEDIMENTO (ID XXX)"
 */
export async function fetchProcedimentosAghuPorEspecialidade(nomeEspecialidade: string): Promise<string[]> {
  if (!nomeEspecialidade) return [];

  const cacheKey = normalizarNomeEspecialidade(nomeEspecialidade);
  if (procedimentosAghuCache.has(cacheKey)) {
    return procedimentosAghuCache.get(cacheKey) || [];
  }

  const ids = getAghuIdsForEspecialidade(nomeEspecialidade);
  if (ids.length === 0) {
    return [];
  }

  const procsSet = new Set<string>();

  try {
    const promises = ids.map(id => api.get(`/api/especialidades/${id}/procedimentos`));
    const results = await Promise.allSettled(promises);

    for (const res of results) {
      if (res.status === 'fulfilled' && Array.isArray(res.value.data)) {
        for (const item of res.value.data) {
          const descricao = (item.descricao || item.nome || '').trim();
          const idProc = item.id_procedimento || item.seq || item.id;
          if (descricao) {
            if (idProc) {
              procsSet.add(`${descricao.toUpperCase()} (ID ${idProc})`);
            } else {
              procsSet.add(descricao.toUpperCase());
            }
          }
        }
      }
    }

    const procsList = Array.from(procsSet).sort((a, b) => a.localeCompare(b, 'pt-BR'));
    procedimentosAghuCache.set(cacheKey, procsList);
    return procsList;
  } catch (error) {
    console.error(`Erro ao carregar procedimentos do AGHU para especialidade ${nomeEspecialidade}:`, error);
    return [];
  }
}
