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
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
      </div>
    </Card>

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
          class="border border-gray-200 rounded-lg p-5 bg-white shadow-sm hover:shadow-md transition-shadow duration-200"
        >
          <!-- Cabeçalho do Card do Paciente -->
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-150 pb-4 mb-4 gap-2">
            <div>
              <span class="font-mono text-xs text-gray-400">PRONTUÁRIO #{{ paciente.codigo }}</span>
              <h3 class="text-lg font-bold text-gray-900 mt-0.5">{{ paciente.nome }}</h3>
            </div>
            <div class="text-xs text-gray-500 space-y-0.5 md:text-right">
              <div><span class="font-semibold text-gray-700">Mãe:</span> {{ paciente.nome_mae || '—' }}</div>
              <div><span class="font-semibold text-gray-700">Nascimento:</span> {{ formatarData(paciente.dt_nascimento) }}</div>
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
                <!-- Status Badge -->
                <div class="absolute top-4 right-4 flex items-center space-x-1.5">
                  <span :class="getStatusBadgeClass(proc.status, proc.tempo_standby)">
                    {{ getStatusLabel(proc.status, proc.tempo_standby) }}
                  </span>
                </div>

                <div class="space-y-2 text-xs">
                  <div>
                    <span class="font-bold text-slate-800 text-sm block">{{ proc.procedimento || 'Procedimento não informado' }}</span>
                    <span class="text-[10px] font-semibold text-slate-500 uppercase">{{ proc.especialidade }}</span>
                  </div>

                  <div class="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200/60 mt-2">
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

const especialidades = [
  'Cardiologia',
  'Cirurgia Geral',
  'Ginecologia',
  'Neurocirurgia',
  'Oftalmologia',
  'Ortopedia',
  'Otorrinolaringologia',
  'Plástica',
  'Torácica',
  'Urologia'
];

watch(() => perfisStore.perfilAtivo, (newProfile) => {
  if (newProfile.tipo === 'ESPECIALIDADE' && newProfile.especialidade) {
    filtroEspecialidade.value = newProfile.especialidade;
  }
}, { immediate: true });

const carregarDados = async () => {
  loading.value = true;
  try {
    const [pacRes, solRes] = await Promise.all([
      api.get('/api/pacientes'),
      api.get('/api/solicitacoes')
    ]);
    basePacientes.value = pacRes.data;
    solicitacoes.value = solRes.data;
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
      procedimentos: p.procedimento ? [
        {
          especialidade: p.especialidade,
          procedimento: p.procedimento,
          judicializado: 'Não',
          Swalis: p.swalis || p.swallis || p.Swalis || '—',
          medico_responsavel: 'Não informado',
          status: 'ATIVO',
          tempo_standby: null
        }
      ] : []
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
      pac = {
        codigo: cod,
        nome: s.nome_paciente,
        dt_nascimento: '—',
        nome_mae: '—',
        procedimentos: []
      };
      pacMap.set(cod, pac);
    }

    if (s.tipo === 'INSERIR') {
      const exists = pac.procedimentos.find((p: any) => p.especialidade === s.especialidade && p.procedimento === s.procedimento);
      if (!exists) {
        pac.procedimentos.push({
          especialidade: s.especialidade,
          procedimento: s.procedimento,
          judicializado: s.judicializado || 'Não',
          Swalis: s.swalis || s.swallis || s.Swalis || s.Swallis || '—',
          medico_responsavel: s.medico_responsavel || 'Não informado',
          status: 'ATIVO',
          tempo_standby: null
        });
      } else {
        exists.judicializado = s.judicializado || 'Não';
        exists.Swalis = s.swalis || s.swallis || s.Swalis || s.Swallis || '—';
        exists.medico_responsavel = s.medico_responsavel || 'Não informado';
        exists.status = 'ATIVO';
        exists.tempo_standby = null;
      }
    } else if (s.tipo === 'EDITAR') {
      const targetProcName = s.procedimento_anterior || s.procedimento;
      const proc = pac.procedimentos.find((p: any) => p.especialidade === s.especialidade && p.procedimento === targetProcName);
      if (proc) {
        proc.procedimento = s.procedimento;
        proc.judicializado = s.judicializado || 'Não';
        const novoSwalis = s.swalis || s.swallis || s.Swalis || s.Swallis || '';
        proc.Swalis = novoSwalis || proc.Swalis || '—';
        proc.medico_responsavel = s.medico_responsavel || 'Não informado';
      }
    } else if (s.tipo === 'EXCLUIR') {
      pac.procedimentos = pac.procedimentos.filter((p: any) => !(p.especialidade === s.especialidade && p.procedimento === s.procedimento));
    } else if (s.tipo === 'STANDBY') {
      const proc = pac.procedimentos.find((p: any) => p.especialidade === s.especialidade && p.procedimento === s.procedimento);
      if (proc) {
        proc.status = 'STANDBY';
        proc.tempo_standby = calcularTempoStandbyRestante(s.tempo_standby || null, s.data_acao || s.data_criacao);
      }
    } else if (s.tipo === 'CANCELAR_STANDBY') {
      const proc = pac.procedimentos.find((p: any) => p.especialidade === s.especialidade && p.procedimento === s.procedimento);
      if (proc) {
        proc.status = 'ATIVO';
        proc.tempo_standby = null;
      }
    }
  }

  // Se o perfil ativo for ESPECIALIDADE, filtra obrigatoriamente essa especialidade tanto para o paciente quanto para os procedimentos
  const espAtiva = perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade
    ? perfisStore.perfilAtivo.especialidade.toLowerCase().trim()
    : (filtroEspecialidade.value ? filtroEspecialidade.value.toLowerCase().trim() : null);

  return Array.from(pacMap.values())
    .map(pac => {
      if (espAtiva) {
        return {
          ...pac,
          procedimentos: pac.procedimentos.filter((p: any) => p.especialidade && p.especialidade.toLowerCase().trim().includes(espAtiva))
        };
      }
      return pac;
    })
    .filter(pac => {
      if (pac.procedimentos.length === 0) return false;

      let matchBusca = true;
      if (buscaProntuario.value) {
        const query = buscaProntuario.value.toLowerCase();
        matchBusca = pac.codigo.includes(query) || pac.nome.toLowerCase().includes(query);
      }

      return matchBusca;
    });
});

onMounted(() => {
  carregarDados();
});
</script>
