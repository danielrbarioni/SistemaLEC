<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Pacientes cadastrados no Sistema LEC</h1>
      <div class="flex items-center space-x-3">
        <button 
          v-if="podeImportarPlanilha"
          @click="modalImportarAberto = true"
          class="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs px-3.5 py-2 rounded-lg transition shadow-sm"
        >
          <DocumentArrowUpIcon class="h-4 w-4" />
          <span>Importar Planilha</span>
        </button>
        <span class="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-semibold rounded-full border border-emerald-200">
          Gestão de Pacientes
        </span>
      </div>
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

        <!-- Filtro por Judicialização -->
        <div class="form-group">
          <label for="filtroJudicializado" class="form-label font-semibold">
            Filtrar por Judicialização
          </label>
          <select 
            id="filtroJudicializado" 
            v-model="filtroJudicializado" 
            class="form-control"
          >
            <option value="">Todas</option>
            <option value="Sim">Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>

        <!-- Filtro por Swalis -->
        <div class="form-group">
          <label for="filtroSwalis" class="form-label font-semibold">
            Filtrar por Swalis
          </label>
          <select 
            id="filtroSwalis" 
            v-model="filtroSwalis" 
            class="form-control"
          >
            <option value="">Todas</option>
            <option value="A1">A1 - Prioridade máxima</option>
            <option value="A2">A2 - Prioridade alta</option>
            <option value="B">B - Prioridade média</option>
            <option value="C">C - Prioridade baixa</option>
            <option value="D">D - Prioridade mínima</option>
            <option value="NENHUM">Sem Swalis / Não informado</option>
          </select>
        </div>

        <!-- Filtro para Pacientes com Mais de 1 Procedimento -->
        <div class="form-group flex items-center pt-2 md:col-span-2 lg:col-span-4">
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

    <!-- Lista de Pacientes no formato de Tabela Compacta (Uma linha por procedimento) -->
    <Card>
      <div v-if="loading" class="flex justify-center items-center py-12">
        <LoadingIndicator />
      </div>
      <div v-else-if="procedimentosFlat.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-base font-semibold text-gray-700">Nenhum paciente ou procedimento encontrado.</p>
        <p class="text-xs text-gray-400 mt-1">Tente ajustar os filtros de busca acima para encontrar os registros desejados.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Prontuário</th>
              <th class="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Nome Completo</th>
              <th class="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">Data de Nascimento</th>
              <th class="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Especialidade</th>
              <th class="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Procedimento</th>
              <th class="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">Judicialização</th>
              <th class="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">Swalis</th>
              <th class="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Médico Responsável</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="(row, idx) in procedimentosFlat" 
              :key="idx"
              class="hover:bg-slate-50 transition duration-150"
            >
              <!-- Prontuário Clicável -->
              <td class="px-4 py-3 whitespace-nowrap">
                <button 
                  @click="abrirModalPaciente(row.pacienteCompleto)"
                  class="font-mono font-bold text-indigo-600 hover:text-indigo-900 hover:underline cursor-pointer focus:outline-none"
                  title="Clique para ver todos os detalhes e procedimentos deste paciente"
                >
                  {{ row.codigo }}
                </button>
              </td>

              <!-- Nome Completo Clicável -->
              <td class="px-4 py-3 font-semibold text-gray-900">
                <button 
                  @click="abrirModalPaciente(row.pacienteCompleto)"
                  class="text-left font-bold text-gray-800 hover:text-indigo-600 hover:underline cursor-pointer focus:outline-none"
                  title="Clique para ver todos os detalhes e procedimentos deste paciente"
                >
                  {{ row.nome }}
                </button>
              </td>

              <!-- Data de Nascimento -->
              <td class="px-4 py-3 text-center whitespace-nowrap font-mono text-xs text-gray-700">
                {{ formatarData(row.dt_nascimento) }}
              </td>

              <!-- Especialidade -->
              <td class="px-4 py-3 whitespace-nowrap">
                <span class="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-md border border-slate-200">
                  {{ row.especialidade }}
                </span>
              </td>

              <!-- Procedimento Padronizado (Máximo 2 Linhas com ajuste dinâmico de fonte) -->
              <td class="px-4 py-3 text-gray-800 font-medium max-w-sm" :title="formatarNomeProcedimento(row.procedimento)">
                <div 
                  class="line-clamp-2 leading-tight break-words"
                  :class="formatarNomeProcedimento(row.procedimento).length > 60 ? 'text-xs' : 'text-sm'"
                >
                  {{ formatarNomeProcedimento(row.procedimento) || '—' }}
                </div>
              </td>

              <!-- Judicialização -->
              <td class="px-4 py-3 text-center whitespace-nowrap">
                <span 
                  :class="row.judicializado === 'Sim' ? 'bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded border border-amber-300' : 'text-gray-600 font-medium'"
                >
                  {{ row.judicializado }}
                </span>
              </td>

              <!-- Swalis -->
              <td class="px-4 py-3 text-center whitespace-nowrap font-mono text-xs">
                <span :class="getSwalisClass(row.Swalis)" :title="getSwalisLabel(row.Swalis)">
                  {{ row.Swalis }}
                </span>
              </td>

              <!-- Médico Responsável -->
              <td class="px-4 py-3 text-gray-700 font-medium whitespace-nowrap">
                {{ row.medico_responsavel || 'Não informado' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Modal Maior com Informações Cadastrais e Janelas por Procedimento -->
    <div 
      v-if="modalDetalhesAberto && pacienteSelecionadoModal" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
      @click.self="fecharModalPaciente"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full border border-gray-100 overflow-hidden flex flex-col max-h-[90vh] my-auto">
        <!-- Cabeçalho do Modal (Fundo Claro com Destaque no Nome) -->
        <div class="px-6 py-4 bg-slate-50 border-b border-gray-200 flex justify-between items-center shrink-0">
          <div>
            <span class="text-xs font-mono text-indigo-600 font-bold uppercase tracking-wider block">Detalhes do Paciente Cadastrado</span>
            <h2 class="text-2xl font-black text-slate-900 mt-0.5 flex items-center space-x-2">
              <span class="text-indigo-950">{{ pacienteSelecionadoModal.nome }}</span>
              <span class="text-sm font-mono text-slate-500 font-semibold bg-slate-200/80 px-2 py-0.5 rounded">({{ pacienteSelecionadoModal.codigo }})</span>
            </h2>
          </div>
          <button 
            @click="fecharModalPaciente"
            class="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg transition hover:bg-gray-200/60"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Corpo do Modal com Rolagem -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1 bg-slate-50/50">
          
          <!-- Bloco 1: Informações Cadastrais Principais -->
          <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 border-b pb-2">Informações Cadastrais</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <span class="text-xs text-gray-500 font-medium block">Nº Prontuário</span>
                <span class="font-mono font-bold text-gray-900 text-base">{{ pacienteSelecionadoModal.codigo }}</span>
              </div>
              <div>
                <span class="text-xs text-gray-500 font-medium block">Data de Nascimento</span>
                <span class="font-medium text-gray-900 text-sm">{{ formatarData(pacienteSelecionadoModal.dt_nascimento) }}</span>
              </div>
              <div>
                <span class="text-xs text-gray-500 font-medium block">Nome da Mãe</span>
                <span class="font-medium text-gray-900 text-sm">{{ pacienteSelecionadoModal.nome_mae || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Bloco 2: Janelas/Quadros por Procedimento -->
          <div class="space-y-4">
            <div class="space-y-1.5 border-b border-slate-200 pb-2">
              <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700">
                Especialidades Vinculadas ({{ totalEspecialidadesModal }})
              </h3>
              <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700">
                Procedimentos Vinculados ({{ pacienteSelecionadoModal.procedimentos.length }})
              </h3>
            </div>

            <div class="grid grid-cols-1 gap-4">
              <div 
                v-for="(proc, index) in pacienteSelecionadoModal.procedimentos" 
                :key="index"
                class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4 hover:border-slate-300 transition"
              >
                <!-- Cabeçalho da Janela de Procedimento -->
                <div class="flex justify-between items-start border-b border-gray-100 pb-3">
                  <div>
                    <span class="text-[11px] font-bold text-indigo-600 uppercase tracking-wider block mb-1">
                      procedimento {{ index + 1 }} - {{ proc.especialidade }}
                    </span>
                    <h4 class="text-base font-bold text-gray-900 leading-snug">
                      {{ formatarNomeProcedimento(proc.procedimento) || 'Procedimento não informado' }}
                    </h4>
                  </div>
                  <span :class="getStatusBadgeClass(proc.status, proc.tempo_standby)">
                    {{ getStatusLabel(proc.status, proc.tempo_standby) }}
                  </span>
                </div>

                <!-- Detalhes Específicos do Procedimento -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs bg-slate-50 p-3.5 rounded-lg border border-slate-100">
                  <div>
                    <span class="text-gray-400 font-semibold block uppercase text-[10px]">Judicialização</span>
                    <span :class="proc.judicializado === 'Sim' ? 'text-amber-800 font-bold bg-amber-100 px-1.5 py-0.5 rounded inline-block mt-0.5' : 'text-gray-800 font-medium'">
                      {{ proc.judicializado }}
                    </span>
                  </div>

                  <div>
                    <span class="text-gray-400 font-semibold block uppercase text-[10px]">Swalis</span>
                    <span :class="getSwalisClass(proc.Swalis)" :title="getSwalisLabel(proc.Swalis)" class="mt-0.5 inline-block">
                      {{ proc.Swalis }}
                    </span>
                  </div>

                  <div>
                    <span class="text-gray-400 font-semibold block uppercase text-[10px]">Médico Responsável</span>
                    <span class="text-gray-900 font-semibold mt-0.5 block truncate" :title="proc.medico_responsavel">
                      {{ proc.medico_responsavel || 'Não informado' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Rodapé do Modal -->
        <div class="px-6 py-3 bg-gray-100 border-t border-gray-200 flex justify-end shrink-0">
          <Button @click="fecharModalPaciente" variant="secondary">
            Fechar
          </Button>
        </div>
      </div>
    </div>

    <!-- Modal de Importação de Planilha Excel -->
    <ImportarPlanilhaPacientesModal
      :show="modalImportarAberto"
      @close="modalImportarAberto = false"
      @sucesso="onImportacaoSucesso"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { UserGroupIcon, ClipboardDocumentListIcon, DocumentArrowUpIcon } from '@heroicons/vue/24/outline';
import api from '../services/api';
import Card from '../components/Card.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { usePerfisStore } from '../stores/perfis';
import ImportarPlanilhaPacientesModal from '../components/ImportarPlanilhaPacientesModal.vue';
import { formatarNomeProcedimento, desduplicarProcedimentos } from '../utils/procedimentoHelper';

const toast = useToast();
const perfisStore = usePerfisStore();

const podeImportarPlanilha = computed(() => {
  const p = perfisStore.perfilAtivo;
  if (!p) return false;
  // Apenas perfis ADMIN ou GESTÃO LEC podem importar planilhas (nenhuma especialidade pode)
  if (p.tipo === 'ESPECIALIDADE') return false;
  return p.tipo === 'ADMIN' || p.tipo === 'GESTAO_LEC' || p.nome === 'Gestão LEC' || p.nome === 'GESTAO_LEC' || p.id === 'GESTAO_LEC';
});

const modalImportarAberto = ref(false);

function onImportacaoSucesso(resultado: any) {
  toast.success(`Planilha importada com sucesso! ${resultado.solicitacoes_criadas} solicitações criadas.`);
  carregarDados();
}

const basePacientes = ref<any[]>([]);
const solicitacoes = ref<any[]>([]);
const loading = ref(false);

const buscaProntuario = ref('');
const filtroEspecialidade = ref('');
const filtroProcedimento = ref('');
const filtroMedico = ref('');
const filtroJudicializado = ref('');
const filtroSwalis = ref('');
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
        .map((p: any) => p.id_procedimento ? `${p.descricao} (ID ${p.id_procedimento})` : p.descricao)
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
  return desduplicarProcedimentos(raw);
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
    solicitacoes.value = (solRes.data || []).filter((s: any) => {
      const codStr = String(s.codigo_paciente || s.codigo || s.prontuario || '').trim();
      const procStr = String(s.procedimento || '').toLowerCase().trim();
      const origStr = String(s.origem_menu || '').toLowerCase().trim();
      if (codStr === '0' || procStr.startsWith('perfil:') || origStr === 'perfis') {
        return false;
      }
      return true;
    });
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
  const resolverMedicoNome = (med: string) => {
    if (!med || med === 'Não informado' || med === '—') return med || 'Não informado';
    const clean = med.trim();
    const userMatch = usuarios.value.find(u => u.username?.toLowerCase() === clean.toLowerCase() || u.nome?.toLowerCase() === clean.toLowerCase());
    return userMatch?.nome?.trim() || clean;
  };

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

  // 2. Aplica as solicitações aprovadas em ordem cronológica (desconsiderando eventos de RESPOSTA para não duplicar)
  const approvedSolics = solicitacoes.value
    .filter(s => s.status === 'APROVADO' && s.evento_tipo !== 'RESPOSTA' && !s.is_resposta)
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
        medico_responsavel: resolverMedicoNome(s.medico_responsavel),
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
        proc.medico_responsavel = resolverMedicoNome(s.medico_responsavel);
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
          medico_responsavel: resolverMedicoNome(baseMatch.medico_responsavel),
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
        const procFiltroNorm = formatarNomeProcedimento(filtroProcedimento.value);
        procs = procs.filter((p: any) => p.procedimento && formatarNomeProcedimento(p.procedimento) === procFiltroNorm);
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

      if (filtroJudicializado.value) {
        procs = procs.filter((p: any) => (p.judicializado || 'Não') === filtroJudicializado.value);
      }

      if (filtroSwalis.value) {
        procs = procs.filter((p: any) => {
          const sw = (p.Swalis || p.swalis || p.swallis || '—').trim();
          if (filtroSwalis.value === 'NENHUM') {
            return sw === '—' || sw === '' || sw === 'Não informado';
          }
          return sw === filtroSwalis.value;
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

const modalDetalhesAberto = ref(false);
const pacienteSelecionadoModal = ref<any | null>(null);

function abrirModalPaciente(paciente: any) {
  pacienteSelecionadoModal.value = paciente;
  modalDetalhesAberto.value = true;
}

function fecharModalPaciente() {
  modalDetalhesAberto.value = false;
  pacienteSelecionadoModal.value = null;
}

// Mapeia os pacientes filtrados em linhas individuais de procedimento (Flat Table) com ordenação alfabética e por data de nascimento
const procedimentosFlat = computed(() => {
  const list: any[] = [];

  for (const pac of pacientesProcessados.value) {
    for (const proc of pac.procedimentos) {
      list.push({
        codigo: pac.codigo,
        nome: pac.nome,
        dt_nascimento: pac.dt_nascimento,
        nome_mae: pac.nome_mae,
        especialidade: proc.especialidade,
        procedimento: proc.procedimento,
        judicializado: proc.judicializado || 'Não',
        Swalis: proc.Swalis || proc.swalis || proc.swallis || '—',
        medico_responsavel: proc.medico_responsavel || 'Não informado',
        status: proc.status,
        tempo_standby: proc.tempo_standby,
        pacienteCompleto: pac
      });
    }
  }

  // Ordena primeiramente por Nome Completo (Ordem Alfabética em pt-BR)
  // Em caso de empate absoluto de Nome, ordena por Data de Nascimento (da mais antiga para a mais recente)
  return list.sort((a, b) => {
    const nomeA = (a.nome || '').trim();
    const nomeB = (b.nome || '').trim();
    const diffNome = nomeA.localeCompare(nomeB, 'pt-BR');

    if (diffNome !== 0) {
      return diffNome;
    }

    // Fallback de empate pelo nome: compara data de nascimento (AAAA-MM-DD ou DD/MM/AAAA)
    const parseData = (dStr: string) => {
      if (!dStr || dStr === '—') return '9999-99-99';
      if (dStr.includes('/')) {
        const parts = dStr.split('/');
        if (parts.length === 3) return `${parts[2]}-${parts[1]}-${parts[0]}`;
      }
      return dStr;
    };

    const dataA = parseData(a.dt_nascimento);
    const dataB = parseData(b.dt_nascimento);
    return dataA.localeCompare(dataB);
  });
});

const totalPacientes = computed(() => pacientesProcessados.value.length);
const totalProcedimentos = computed(() => procedimentosFlat.value.length);

const totalEspecialidadesModal = computed(() => {
  if (!pacienteSelecionadoModal.value || !pacienteSelecionadoModal.value.procedimentos) return 0;
  const espSet = new Set(
    pacienteSelecionadoModal.value.procedimentos
      .map((p: any) => (p.especialidade || '').trim())
      .filter(Boolean)
  );
  return espSet.size;
});

onMounted(() => {
  carregarDados();
});
</script>
