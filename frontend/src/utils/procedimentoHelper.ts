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
 * Remove duplicidades de uma lista de procedimentos aplicando a normalização de formato.
 */
export function desduplicarProcedimentos(procedimentos: string[]): string[] {
  if (!procedimentos || !Array.isArray(procedimentos)) return [];
  
  const mapNormalizado = new Map<string, string>();

  for (const proc of procedimentos) {
    if (!proc) continue;
    const formatado = formatarNomeProcedimento(proc);
    // Usa a versão formatada como chave e valor no map para desduplicar
    if (!mapNormalizado.has(formatado)) {
      mapNormalizado.set(formatado, formatado);
    }
  }

  return Array.from(mapNormalizado.values()).sort((a, b) => a.localeCompare(b, 'pt-BR'));
}
