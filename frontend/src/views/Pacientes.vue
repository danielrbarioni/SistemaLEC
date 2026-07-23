<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Prontuário e Cadastro de Pacientes</h1>
      <span class="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-semibold rounded-full border border-emerald-200">
        Gestão de Pacientes
      </span>
    </div>

    <!-- Controles de Busca e Filtro -->
    <Card>
      <div class="grid grid-cols-1 gap-4" :class="espSelecionada ? 'md:grid-cols-4' : 'md:grid-cols-2'">
        <!-- Busca por Prontuário -->
        <div class="form-group">
          <label for="buscaProntuario" class="form-label font-semibold">Buscar por Prontuário ou Nome</label>
          <input 
            id="buscaProntuario" 
            v-model="buscaProntuario" 
            type="text" 
            placeholder="Digite o prontuário ou nome do paciente..." 
            class="form-control" 
          />
        </div>

        <!-- Filtro por Especialidade -->
        <div class="form-group">
          <label for="filtroEspecialidade" class="form-label font-semibold">Filtrar por Especialidade</label>
            <select 
              id="filtroEspecialidade" 
              v-model="filtroEspecialidade" 
              class="form-control"
              :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
              :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
            >
              <option value="">Todas</option>
              <option v-for="esp in especialidades" :key="esp" :value="esp">
                {{ esp }}
              </option>
            </select>
        </div>

        <!-- Filtro por Procedimento (Abre quando uma Especialidade for selecionada) -->
        <div v-if="espSelecionada" class="form-group">
          <label for="filtroProcedimento" class="form-label font-semibold">
            Filtrar por Procedimento
            <span v-if="carregandoProcedimentos" class="text-xs text-gray-400 font-normal ml-1">(carregando AGHU...)</span>
          </label>
          <select 
            id="filtroProcedimento" 
            v-model="filtroProcedimento" 
            class="form-control"
          >
            <option value="">Todos os Procedimentos</option>
            <option v-for="proc in procedimentosOpcoes" :key="proc" :value="proc">
              {{ proc }}
            </option>
          </select>
        </div>

        <!-- Filtro por Médico Responsável (Abre quando uma Especialidade for selecionada) -->
        <div v-if="espSelecionada" class="form-group">
          <label for="filtroMedico" class="form-label font-semibold">
            Filtrar por Médico Responsável
          </label>
          <select 
            id="filtroMedico" 
            v-model="filtroMedico" 
            class="form-control"
          >
            <option value="">Todos os Médicos</option>
            <option v-for="medico in medicosOpcoes" :key="medico" :value="medico">
              {{ medico }}
            </option>
          </select>
        </div>

        <!-- Filtro para Pacientes com Mais de 1 Procedimento -->
        <div class="form-group flex items-center pt-2" :class="espSelecionada ? 'md:col-span-4' : 'md:col-span-2'">
          <label class="flex items-center space-x-2 cursor-pointer select-none bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg hover:bg-slate-100 transition shadow-sm">
            <input 
              type="checkbox" 
              v-model="filtroApenasMultiplos" 
              class="h-4 w-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500 cursor-pointer"
            />
            <span class="text-xs font-bold text-slate-700">Exibir apenas pacientes com mais de 1 procedimento cadastrado</span>
          </label>
        </div>
      </div>
    </Card>

    <!-- Cards de Totais (Filtros Selecionados) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Total de Pacientes</span>
          <span class="text-2xl font-bold text-slate-800 mt-1 block">{{ totalPacientes }}</span>
        </div>
        <div class="p-3 bg-emerald-50 text-emerald-600 rounded-lg border border-emerald-100">
          <UserGroupIcon class="h-6 w-6" />
        </div>
      </div>

      <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Total de Procedimentos</span>
          <span class="text-2xl font-bold text-slate-800 mt-1 block">{{ totalProcedimentos }}</span>
        </div>
        <div class="p-3 bg-blue-50 text-blue-600 rounded-lg border border-blue-100">
          <ClipboardDocumentListIcon class="h-6 w-6" />
        </div>
      </div>
    </div>

    <!-- Lista de Pacientes -->
    <Card>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <LoadingIndicator />
      </div>
      <div v-else-if="pacientesProcessados.length === 0" class="text-center py-10 text-gray-500">
        Nenhum paciente encontrado.
      </div>
      <div v-else class="space-y-6">
        <div 
          v-for="paciente in pacientesProcessados" 
          :key="paciente.codigo" 
          class="border border-gray-200 rounded-lg p-5 bg-white shadow-sm hover:shadow-md transition-shadow duration-200 space-y-4"
        >
          <!-- Cabeçalho do Card do Paciente -->
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-150 pb-3 gap-2">
            <div>
              <span class="font-mono text-xs text-gray-400">PRONTUÁRIO #{{ paciente.codigo }}</span>
              <h3 class="text-lg font-bold text-gray-900 mt-0.5">{{ paciente.nome }}</h3>
            </div>
            <span class="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-md border border-slate-200">
              {{ paciente.procedimentos.length }} procedimento(s)
            </span>
          </div>

          <!-- Dados Cadastrais Adicionais (Data de Nascimento e Nome da Mãe - Estilo Sistema LEC) -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50/80 p-3.5 rounded-lg border border-gray-200">
            <div class="form-group">
              <label class="form-label text-xs font-semibold text-gray-600 block mb-1">Data de Nascimento</label>
              <input
                type="text"
                :value="formatarData(paciente.dt_nascimento)"
                class="form-control text-xs bg-white border-gray-300 cursor-not-allowed opacity-90 font-medium text-gray-800 w-full"
                disabled
              />
            </div>
            <div class="form-group md:col-span-2">
              <label class="form-label text-xs font-semibold text-gray-600 block mb-1">Nome da Mãe</label>
              <input
                type="text"
                :value="paciente.nome_mae || '—'"
                class="form-control text-xs bg-white border-gray-300 cursor-not-allowed opacity-90 font-medium text-gray-800 w-full"
                disabled
              />
            </div>
          </div>

          <!-- Procedimentos Vinculados -->
          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Procedimentos e Filas Associadas</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div 
                v-for="(proc, index) in paciente.procedimentos" 
                :key="index" 
                class="border border-slate-100 rounded-lg p-4 bg-slate-50 relative"
              >
                <!-- Cabeçalho do Card de Procedimento -->
                <div class="flex items-start justify-between gap-3 mb-2">
                  <div class="min-w-0 flex-1 pr-2">
                    <span 
                      class="font-bold text-slate-800 block leading-tight break-words"
                      :class="(proc.procedimento || '').length > 60 ? 'text-xs' : ((proc.procedimento || '').length > 35 ? 'text-[13px]' : 'text-sm')"
                    >
                      {{ proc.procedimento || 'Procedimento não informado' }}
                    </span>
                    <span class="text-[10px] font-semibold text-slate-500 uppercase block mt-1">{{ proc.especialidade }}</span>
                  </div>

                  <!-- Status Badge -->
                  <div class="shrink-0 flex items-center">
                    <span :class="getStatusBadgeClass(proc.status, proc.tempo_standby)">
                      {{ getStatusLabel(proc.status, proc.tempo_standby) }}
                    </span>
                  </div>
                </div>

                <div class="space-y-2 text-xs">
                  <div class="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200/60 mt-1">
                    <div>
                      <span class="text-[10px] text-gray-400 uppercase block font-semibold">Judicializado</span>
                      <span :class="proc.judicializado === 'Sim' ? 'text-amber-700 font-bold bg-amber-50 px-1.5 py-0.5 rounded' : 'text-gray-700 font-medium'">
                        {{ proc.judicializado }}
                      </span>
                    </div>
                    <div>
                      <span class="text-[10px] text-gray-400 uppercase block font-semibold">Swalis</span>
                      <span :class="getSwalisClass(proc.Swalis)" :title="getSwalisLabel(proc.Swalis)">
                        {{ proc.Swalis }}
                      </span>
                    </div>
                    <div>
                      <span class="text-[10px] text-gray-400 uppercase block font-semibold">Responsável</span>
                      <span class="text-gray-700 font-medium truncate block" :title="proc.medico_responsavel">
                        {{ proc.medico_responsavel }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { UserGroupIcon, ClipboardDocumentListIcon } from '@heroicons/vue/24/outline';
import api from '../services/api';
import Card from '../components/Card.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { usePerfisStore } from '../stores/perfis';

const toast = useToast();
const perfisStore = usePerfisStore();

const basePacientes = ref<any[]>([]);
const solicitacoes = ref<any[]>([]);
const loading = ref(false);

const buscaProntuario = ref('');
const filtroEspecialidade = ref('');
const filtroProcedimento = ref('');
const filtroMedico = ref('');
const filtroApenasMultiplos = ref(false);
const usuarios = ref<any[]>([]);

const espSelecionada = computed(() => {
  if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade) {
    return perfisStore.perfilAtivo.especialidade;
  }
  return filtroEspecialidade.value;
});

const especialidades = computed(() => {
  const perfis = perfisStore.perfis;
  const lista = perfis
    .filter(p => p.tipo === 'ESPECIALIDADE' || (p.especialidade && p.tipo !== 'ADMIN' && p.tipo !== 'GESTAO_LEC'))
    .map(p => (p.especialidade || p.nome).trim())
    .filter((nome, index, self) => nome && self.indexOf(nome) === index)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'));

  return lista;
});

const medicosOpcoes = computed(() => {
  const esp = espSelecionada.value;
  if (!esp) return [];

  const espLower = esp.toLowerCase().trim();

  // Encontra perfis da especialidade cirúrgica selecionada
  const perfisEspIds = new Set(
    perfisStore.perfis
      .filter(p => p.tipo === 'ESPECIALIDADE' && (p.especialidade || p.nome).toLowerCase().trim() === espLower)
      .map(p => p.id)
  );

  const medicosSet = new Set<string>();

  // 1. Médicos da tabela de usuários associados ao perfil da especialidade com a função Médico
  for (const u of usuarios.value) {
    const perfMatch = perfisEspIds.has(u.perfil_id);
    const espMatch = u.especialidade && u.especialidade.toLowerCase().trim() === espLower;
    const isMedico = u.funcao === 'Médico' || (u.funcao && u.funcao.toLowerCase().includes('médico'));

    if ((perfMatch || espMatch) && isMedico && u.nome) {
      medicosSet.add(u.nome.trim());
    }
  }

  // 2. Médicos presentes em solicitações/pacientes para essa especialidade (resolvendo username para nome completo se necessário)
  for (const s of solicitacoes.value) {
    if (s.especialidade && s.especialidade.toLowerCase().trim() === espLower && s.medico_responsavel) {
      const val = s.medico_responsavel.trim();
      if (val !== 'Não informado' && val !== '—') {
        const userMatch = usuarios.value.find(u => u.username?.toLowerCase() === val.toLowerCase() || u.nome?.toLowerCase() === val.toLowerCase());
        if (userMatch && userMatch.nome) {
          medicosSet.add(userMatch.nome.trim());
        } else if (!val.includes('.')) {
          // Se não tiver ponto (padrão de username ebserh como nome.sobrenome), considera como nome
          medicosSet.add(val);
        }
      }
    }
  }

  return Array.from(medicosSet).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

const procedimentosBaseMap: Record<string, string[]> = {
  'Cardiologia': ['Revascularização do Miocárdio (Ponte de Safena)', 'Troca de Valva Aórtica', 'Troca de Valva Mitral', 'Implante de Marcapasso', 'Correção de CIA / CIV'],
  'Cirurgia Geral': ['Colecistectomia', 'Herniorrafia Inguinal', 'Apendicectomia', 'Gastrectomia', 'Colostomia'],
  'Ginecologia': ['Histerectomia', 'Miomectomia', 'Laparoscopia Diagnóstica', 'Colpoperineoplastia', 'Ooforectomia'],
  'Neurocirurgia': ['Craniectomia Descompressiva', 'Clipagem de Aneurisma', 'Derivação Ventrículo-Peritoneal', 'Microdiscectomia', 'Tumor Cerebral — Ressecção'],
  'Oftalmologia': ['Facoemulsificação (Catarata)', 'Trabeculectomia (Glaucoma)', 'Vitrectomia', 'Transplante de Córnea', 'Fotocoagulação a Laser'],
  'Ortopedia': ['Artroplastia Total de Quadril', 'Artroplastia Total de Joelho', 'Artroscopia de Joelho', 'Fixação de Fratura de Fêmur', 'Osteossíntese de Coluna'],
  'Otorrinolaringologia': ['Septoplastia', 'Amigdalectomia', 'Timpanoplastia', 'Adenoidectomia', 'Microcirurgia de Laringe'],
  'Plástica': [],
  'Torácica': ['Lobectomia', 'Pleuroscopia', 'Simpatectomia', 'Ressecção de Nódulo Pulmonar', 'Broncoscopia'],
  'Urologia': ['Prostatectomia Radical', 'Nefrectomia', 'Ureteroscopia', 'Litotripsia', 'Ressecção Transuretral de Próstata (RTUP)']
};

const procedimentosAghuMap = ref<Record<string, string[]>>({});
const carregandoProcedimentos = ref(false);

function formatarNomeProcedimento(str: string): string {
  if (!str) return str;
  const s = str.trim();
  const matchLeft = s.match(/^(\d+)\s*[-–—]\s*(.+)$/);
  if (matchLeft) {
    return `${matchLeft[2].trim()} - ID ${matchLeft[1]}`;
  }
  const matchRight = s.match(/^(.+?)\s*[-–—]\s*(?:ID\s*)?(\d+)$/i);
  if (matchRight) {
    return `${matchRight[1].trim()} - ID ${matchRight[2]}`;
  }
  return s;
}

watch(espSelecionada, async (newEsp) => {
  filtroProcedimento.value = '';
  filtroMedico.value = '';
  if (!newEsp) return;

  const espNorm = newEsp.toLowerCase().trim();
  if ((espNorm.includes('plástica') || espNorm.includes('plastica')) && !procedimentosAghuMap.value['Plástica']) {
    carregandoProcedimentos.value = true;
    try {
      const { data } = await api.get('/api/especialidades/1884/procedimentos');
      const procs = data
        .map((p: any) => p.id_procedimento ? `${p.descricao} - ID ${p.id_procedimento}` : p.descricao)
        .filter(Boolean);
      if (procs.length > 0) {
        procedimentosAghuMap.value['Plástica'] = procs;
      }
    } catch (err) {
      console.error('Erro ao buscar procedimentos do AGHU para Plástica:', err);
    } finally {
      carregandoProcedimentos.value = false;
    }
  }
}, { immediate: true });

const procedimentosOpcoes = computed(() => {
  const esp = espSelecionada.value;
  if (!esp) return [];

  const espLower = esp.toLowerCase().trim();
  const listFromAghu = procedimentosAghuMap.value['Plástica'] || [];
  const listFromBase = procedimentosBaseMap[esp] || [];

  const extraProcs: string[] = [];

  for (const p of basePacientes.value) {
    if (p.especialidade && p.especialidade.toLowerCase().trim().includes(espLower) && p.procedimento) {
      extraProcs.push(p.procedimento);
    }
  }
  for (const s of solicitacoes.value) {
    if (s.especialidade && s.especialidade.toLowerCase().trim().includes(espLower) && s.procedimento) {
      extraProcs.push(s.procedimento);
    }
  }

  const raw = [...listFromAghu, ...listFromBase, ...extraProcs];
  const formatted = raw.map(formatarNomeProcedimento);
  const combined = Array.from(new Set(formatted));
  return combined.sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

watch(() => perfisStore.perfilAtivo, (newProfile) => {
  if (newProfile.tipo === 'ESPECIALIDADE' && newProfile.especialidade) {
    filtroEspecialidade.value = newProfile.especialidade;
  }
}, { immediate: true });

const carregarDados = async () => {
  loading.value = true;
  try {
    const [pacRes, solRes, usrRes] = await Promise.all([
      api.get('/api/pacientes'),
      api.get('/api/solicitacoes'),
      api.get('/api/usuarios'),
      perfisStore.fetchPerfis()
    ]);
    basePacientes.value = pacRes.data;
    solicitacoes.value = solRes.data;
    usuarios.value = usrRes.data;
  } catch (error) {
    toast.error('Erro ao obter os dados dos pacientes.');
  } finally {
    loading.value = false;
  }
};

const formatarData = (dataStr: string) => {
  if (!dataStr || dataStr === '—') return '—';
  try {
    const apenasData = dataStr.includes('T') ? dataStr.split('T')[0] : dataStr.split(' ')[0];
    const partes = apenasData.split('-');
    if (partes.length === 3) {
      const [ano, mes, dia] = partes;
      return `${dia}/${mes}/${ano}`;
    }
    return dataStr;
  } catch (e) {
    return dataStr;
  }
};

const calcularTempoStandbyRestante = (tempoOriginal: number | null, dataStr?: string) => {
  if (!tempoOriginal || tempoOriginal <= 0) return null;
  if (!dataStr) return tempoOriginal;
  try {
    const dataInicio = new Date(dataStr.includes('T') ? dataStr : dataStr.replace(' ', 'T'));
    if (isNaN(dataInicio.getTime())) return tempoOriginal;
    const agora = new Date();
    const diffMs = agora.getTime() - dataInicio.getTime();
    const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDias <= 0) return tempoOriginal;
    return Math.max(0, tempoOriginal - diffDias);
  } catch (e) {
    return tempoOriginal;
  }
};

const getStatusBadgeClass = (status: string, _tempo?: number | null) => {
  if (status === 'STANDBY') {
    return 'px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200';
  }
  return 'px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-800 border border-green-200';
};

const getStatusLabel = (status: string, tempo: number | null) => {
  if (status === 'STANDBY') {
    return `Standby (${tempo !== null && tempo !== undefined ? tempo : '—'}d)`;
  }
  return 'Ativo na fila';
};

const getSwalisLabel = (code: string) => {
  switch (code) {
    case 'A1': return 'A1 - Prioridade máxima';
    case 'A2': return 'A2 - Prioridade alta';
    case 'B':  return 'B - Prioridade média';
    case 'C':  return 'C - Prioridade baixa';
    case 'D':  return 'D - Prioridade mínima';
    default:   return code || '—';
  }
};

const getSwalisClass = (Swalis: string) => {
  switch (Swalis) {
    case 'A1': return 'text-red-700 font-bold bg-red-50 px-1.5 py-0.5 rounded';
    case 'A2': return 'text-orange-700 font-bold bg-orange-50 px-1.5 py-0.5 rounded';
    case 'B':  return 'text-yellow-700 font-bold bg-yellow-50 px-1.5 py-0.5 rounded';
    case 'C':  return 'text-blue-700 font-bold bg-blue-50 px-1.5 py-0.5 rounded';
    case 'D':  return 'text-gray-700 font-medium';
    default:   return 'text-gray-700 font-medium';
  }
};

const pacientesProcessados = computed(() => {
  // 1. Inicializa o mapa com pacientes da base
  const pacMap = new Map<string, any>();
  
  for (const p of basePacientes.value) {
    const cod = String(p.codigo);
    pacMap.set(cod, {
      codigo: cod,
      nome: p.nome,
      dt_nascimento: p.dt_nascimento,
      nome_mae: p.nome_mae,
      procedimentos: []
    });
  }

  // 2. Aplica as solicitações aprovadas em ordem cronológica
  const approvedSolics = solicitacoes.value
    .filter(s => s.status === 'APROVADO')
    .sort((a, b) => a.data_criacao.localeCompare(b.data_criacao));

  for (const s of approvedSolics) {
    const cod = String(s.codigo_paciente);
    let pac = pacMap.get(cod);
    if (!pac) {
      const baseMatch = basePacientes.value.find((bp: any) => String(bp.codigo) === cod || bp.nome?.toLowerCase().trim() === s.nome_paciente?.toLowerCase().trim());
      pac = {
        codigo: cod,
        nome: s.nome_paciente,
        dt_nascimento: s.dt_nascimento || s.data_nascimento || baseMatch?.dt_nascimento || '—',
        nome_mae: s.nome_mae || baseMatch?.nome_mae || '—',
        procedimentos: []
      };
      pacMap.set(cod, pac);
    } else {
      if ((!pac.dt_nascimento || pac.dt_nascimento === '—') && (s.dt_nascimento || s.data_nascimento)) {
        pac.dt_nascimento = s.dt_nascimento || s.data_nascimento;
      }
      if ((!pac.nome_mae || pac.nome_mae === '—') && s.nome_mae) {
        pac.nome_mae = s.nome_mae;
      }
      if (s.nome_paciente && pac.nome.startsWith('Paciente #')) {
        pac.nome = s.nome_paciente;
      }
    }

    if (s.tipo === 'INSERIR') {
      pac.procedimentos.push({
        id: s.id,
        especialidade: s.especialidade,
        procedimento: s.procedimento,
        judicializado: s.judicializado || 'Não',
        Swalis: s.swalis || s.swallis || s.Swalis || s.Swallis || '—',
        medico_responsavel: s.medico_responsavel || 'Não informado',
        status: 'ATIVO',
        tempo_standby: null
      });
    } else if (s.tipo === 'EDITAR') {
      const targetProcName = s.procedimento_anterior || s.procedimento;
      const proc = pac.procedimentos.find((p: any) => (s.id && p.id === s.id) || (p.especialidade === s.especialidade && p.procedimento === targetProcName));
      if (proc) {
        proc.procedimento = s.procedimento;
        proc.judicializado = s.judicializado || 'Não';
        const novoSwalis = s.swalis || s.swallis || s.Swalis || s.Swallis || '';
        proc.Swalis = novoSwalis || proc.Swalis || '—';
        proc.medico_responsavel = s.medico_responsavel || 'Não informado';
      }
    } else if (s.tipo === 'EXCLUIR') {
      pac.procedimentos = pac.procedimentos.filter((p: any) => !( (s.id && p.id === s.id) || (p.especialidade === s.especialidade && p.procedimento === s.procedimento) ));
    } else if (s.tipo === 'STANDBY') {
      const proc = pac.procedimentos.find((p: any) => (s.id && p.id === s.id) || (p.especialidade === s.especialidade && p.procedimento === s.procedimento));
      if (proc) {
        proc.status = 'STANDBY';
        proc.tempo_standby = calcularTempoStandbyRestante(s.tempo_standby || null, s.data_acao || s.data_criacao);
      }
    } else if (s.tipo === 'CANCELAR_STANDBY') {
      const proc = pac.procedimentos.find((p: any) => (s.id && p.id === s.id) || (p.especialidade === s.especialidade && p.procedimento === s.procedimento));
      if (proc) {
        proc.status = 'ATIVO';
        proc.tempo_standby = null;
      }
    }
  }

  // Fallback para pacientes sem solicitações mas com procedimento na base
  for (const pac of pacMap.values()) {
    if (pac.procedimentos.length === 0) {
      const baseMatch = basePacientes.value.find((bp: any) => String(bp.codigo) === pac.codigo);
      if (baseMatch && baseMatch.procedimento) {
        pac.procedimentos.push({
          especialidade: baseMatch.especialidade,
          procedimento: baseMatch.procedimento,
          judicializado: 'Não',
          Swalis: baseMatch.swalis || baseMatch.swallis || '—',
          medico_responsavel: 'Não informado',
          status: 'ATIVO',
          tempo_standby: null
        });
      }
    }
  }

  // Se o perfil ativo for ESPECIALIDADE, filtra obrigatoriamente essa especialidade tanto para o paciente quanto para os procedimentos
  const espAtiva = (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo?.especialidade)
    ? perfisStore.perfilAtivo.especialidade.toLowerCase().trim()
    : (filtroEspecialidade.value ? filtroEspecialidade.value.toLowerCase().trim() : null);

  return Array.from(pacMap.values())
    .map(pac => {
      let procs = pac.procedimentos;

      if (espAtiva) {
        procs = procs.filter((p: any) => p.especialidade && p.especialidade.toLowerCase().trim().includes(espAtiva));
      }

      if (filtroProcedimento.value) {
        const procLower = filtroProcedimento.value.toLowerCase().trim();
        procs = procs.filter((p: any) => p.procedimento && p.procedimento.toLowerCase().trim() === procLower);
      }

      if (filtroMedico.value) {
        const medicoSelecionado = filtroMedico.value.toLowerCase().trim();
        const userMatch = usuarios.value.find(u => u.nome?.toLowerCase().trim() === medicoSelecionado);
        const usernameMatch = userMatch?.username?.toLowerCase().trim();

        procs = procs.filter((p: any) => {
          if (!p.medico_responsavel) return false;
          const mLower = p.medico_responsavel.toLowerCase().trim();
          return mLower === medicoSelecionado || (usernameMatch && mLower === usernameMatch);
        });
      }

      return {
        ...pac,
        procedimentos: procs
      };
    })
    .filter(pac => {
      if (pac.procedimentos.length === 0) return false;
      if (filtroApenasMultiplos.value && pac.procedimentos.length <= 1) return false;

      let matchBusca = true;
      if (buscaProntuario.value) {
        const query = buscaProntuario.value.toLowerCase();
        matchBusca = pac.codigo.includes(query) || pac.nome.toLowerCase().includes(query);
      }

      return matchBusca;
    });
});

const totalPacientes = computed(() => pacientesProcessados.value.length);
const totalProcedimentos = computed(() => {
  return pacientesProcessados.value.reduce((acc, pac) => acc + (pac.procedimentos ? pac.procedimentos.length : 0), 0);
});

onMounted(() => {
  carregarDados();
});
</script>
