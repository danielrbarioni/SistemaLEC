/**
 * Normaliza e padroniza a exibição de nomes de procedimentos cirúrgicos no formato:
 * NOME DO PROCEDIMENTO (ID XXX)
 * 
 * Remove duplicidades e variações de escrita como:
 * - "BIOPSIA DE PELE E PARTES MOLES - ID 966"
 * - "BIOPSIA DE PELE E PARTES MOLES (966)"
 * - "966 - BIOPSIA DE PELE E PARTES MOLES"
 * - "BIOPSIA DE PELE E PARTES MOLES (ID 966)"
 */
export function formatarNomeProcedimento(str: string): string {
  if (!str) return str || '';
  const s = str.trim();

  // 1. Tenta extrair ID do final com (ID XXX) ou (XXX)
  const matchParenId = s.match(/^(.+?)\s*\(\s*(?:ID\s*)?(\d+)\s*\)$/i);
  if (matchParenId) {
    const nome = matchParenId[1].trim().replace(/[-–—]\s*$/, '').trim();
    const id = matchParenId[2].trim();
    return `${nome.toUpperCase()} (ID ${id})`;
  }

  // 2. Tenta extrair ID do final com - ID XXX ou - XXX
  const matchDashRight = s.match(/^(.+?)\s*[-–—]\s*(?:ID\s*)?(\d+)$/i);
  if (matchDashRight) {
    const nome = matchDashRight[1].trim();
    const id = matchDashRight[2].trim();
    return `${nome.toUpperCase()} (ID ${id})`;
  }

  // 3. Tenta extrair ID do início com XXX - NOME
  const matchDashLeft = s.match(/^(\d+)\s*[-–—]\s*(.+)$/);
  if (matchDashLeft) {
    const id = matchDashLeft[1].trim();
    const nome = matchDashLeft[2].trim();
    return `${nome.toUpperCase()} (ID ${id})`;
  }

  return s.toUpperCase();
}

/**
 * Extrai o nome base do procedimento sem o sufixo (ID XXX) ou prefixos de ID
 */
export function extrairNomeBaseProcedimento(str: string): string {
  if (!str) return '';
  const s = str.trim();
  return s
    .replace(/\s*\(\s*(?:ID\s*)?\d+\s*\)$/i, '')
    .replace(/\s*[-–—]\s*(?:ID\s*)?\d+$/i, '')
    .replace(/^\d+\s*[-–—]\s*/, '')
    .trim()
    .toUpperCase();
}

/**
 * Remove duplicidades de uma lista de procedimentos aplicando a normalização de formato.
 * Sempre prioriza a versão completa que contém (ID XXX) sobre a versão sem ID.
 */
export function desduplicarProcedimentos(procedimentos: string[]): string[] {
  if (!procedimentos || !Array.isArray(procedimentos)) return [];
  
  // Mapa de chave normalizada (apenas nome base) para a melhor versão formatada (preferindo a que tem ID)
  const mapPorNomeBase = new Map<string, string>();

  for (const proc of procedimentos) {
    if (!proc) continue;
    const formatado = formatarNomeProcedimento(proc);
    const nomeBase = extrairNomeBaseProcedimento(formatado);
    const temId = /\(ID \d+\)$/.test(formatado);

    if (!mapPorNomeBase.has(nomeBase)) {
      mapPorNomeBase.set(nomeBase, formatado);
    } else {
      const existente = mapPorNomeBase.get(nomeBase)!;
      const existenteTemId = /\(ID \d+\)$/.test(existente);
      if (!existenteTemId && temId) {
        // A versão com ID substitui a versão sem ID!
        mapPorNomeBase.set(nomeBase, formatado);
      }
    }
  }

  return Array.from(mapPorNomeBase.values()).sort((a, b) => a.localeCompare(b, 'pt-BR'));
}
