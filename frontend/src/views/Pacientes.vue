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

        <!-- Filtros para Pacientes com Procedimentos ou Especialidades -->
        <div class="form-group grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 md:col-span-2 lg:col-span-4">
          <!-- Coluna Procedimentos -->
          <div class="flex flex-col gap-2">
            <label class="flex items-center space-x-2 cursor-pointer select-none bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg hover:bg-slate-100 transition shadow-sm">
              <input 
                type="checkbox" 
                v-model="filtroApenasUmProcedimento" 
                class="h-4 w-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500 cursor-pointer"
              />
              <span class="text-xs font-bold text-slate-700">Exibir apenas pacientes com 1 procedimento cadastrado</span>
            </label>

            <label class="flex items-center space-x-2 cursor-pointer select-none bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg hover:bg-slate-100 transition shadow-sm">
              <input 
                type="checkbox" 
                v-model="filtroApenasMultiplos" 
                class="h-4 w-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500 cursor-pointer"
              />
              <span class="text-xs font-bold text-slate-700">Exibir apenas pacientes com mais de 1 procedimento cadastrado</span>
            </label>
          </div>

          <!-- Coluna Especialidades -->
          <div class="flex flex-col gap-2">
            <label class="flex items-center space-x-2 cursor-pointer select-none bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg hover:bg-slate-100 transition shadow-sm">
              <input 
                type="checkbox" 
                v-model="filtroApenasUmaEspecialidade" 
                class="h-4 w-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500 cursor-pointer"
              />
              <span class="text-xs font-bold text-slate-700">Exibir apenas pacientes com 1 especialidade vinculada</span>
            </label>

            <label class="flex items-center space-x-2 cursor-pointer select-none bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg hover:bg-slate-100 transition shadow-sm">
              <input 
                type="checkbox" 
                v-model="filtroApenasMultiplasEspecialidades" 
                class="h-4 w-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500 cursor-pointer"
              />
              <span class="text-xs font-bold text-slate-700">Exibir apenas pacientes com mais de 1 especialidade vinculada</span>
            </label>
          </div>
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
              <th class="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">Data de Inserção</th>
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

              <!-- Procedimento Padronizado (Exibição Completa com Quebra de Linha Automática) -->
              <td class="px-4 py-3 text-gray-800 font-medium max-w-sm" :title="formatarNomeProcedimento(row.procedimento)">
                <div 
                  class="break-words whitespace-normal leading-snug"
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

              <!-- Data de Inserção -->
              <td class="px-4 py-3 text-center whitespace-nowrap font-mono text-xs text-gray-700">
                {{ formatarDataHora(row.data_insercao) }}
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
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs bg-slate-50 p-3.5 rounded-lg border border-slate-100">
                  <div>
                    <span class="text-gray-400 font-semibold block uppercase text-[10px]">Data de Inserção</span>
                    <span class="text-gray-900 font-mono font-medium mt-0.5 block">
                      {{ formatarDataHora(proc.data_insercao) }}
                    </span>
                  </div>

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
import { fetchProcedimentosAghuPorEspecialidade } from '../utils/especialidadeAghuMap';

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
const filtroApenasUmProcedimento = ref(false);
const filtroApenasMultiplos = ref(false);
const filtroApenasUmaEspecialidade = ref(false);
const filtroApenasMultiplasEspecialidades = ref(false);
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
  const norm = (str: string) => str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

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
      medicosSet.add(u.nome.trim().toUpperCase());
    }
  }

  // 2. Médicos presentes em solicitações/pacientes para essa especialidade (resolvendo username para nome completo se necessário)
  for (const s of solicitacoes.value) {
    if (s.especialidade && s.especialidade.toLowerCase().trim() === espLower && s.medico_responsavel) {
      const val = s.medico_responsavel.trim();
      if (val !== 'Não informado' && val !== '—') {
        const valNorm = norm(val);
        const userMatch = usuarios.value.find(u => {
          if (!u) return false;
          const uNameNorm = u.nome ? norm(u.nome) : '';
          const uUserNorm = u.username ? norm(u.username) : '';
          return uUserNorm === valNorm || uNameNorm === valNorm || (valNorm.length > 5 && uNameNorm.includes(valNorm)) || (uNameNorm.length > 5 && valNorm.includes(uNameNorm));
        });

        if (userMatch && userMatch.nome) {
          medicosSet.add(userMatch.nome.trim().toUpperCase());
        } else if (!val.includes('.')) {
          // Se não tiver ponto (padrão de username ebserh como nome.sobrenome), considera como nome
          medicosSet.add(val.toUpperCase());
        }
      }
    }
  }

  return Array.from(medicosSet).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

const procedimentosAghuMap = ref<Record<string, string[]>>({});
const carregandoProcedimentos = ref(false);

watch(espSelecionada, async (newEsp) => {
  filtroProcedimento.value = '';
  filtroMedico.value = '';
  if (!newEsp) return;

  const espTrim = newEsp.trim();
  if (!procedimentosAghuMap.value[espTrim]) {
    carregandoProcedimentos.value = true;
    try {
      const procs = await fetchProcedimentosAghuPorEspecialidade(espTrim);
      if (procs.length > 0) {
        procedimentosAghuMap.value[espTrim] = procs;
      }
    } catch (err) {
      console.error(`Erro ao buscar procedimentos do AGHU para ${espTrim}:`, err);
    } finally {
      carregandoProcedimentos.value = false;
    }
  }
}, { immediate: true });

watch(filtroApenasUmProcedimento, (val) => {
  if (val) filtroApenasMultiplos.value = false;
});

watch(filtroApenasMultiplos, (val) => {
  if (val) filtroApenasUmProcedimento.value = false;
});

watch(filtroApenasUmaEspecialidade, (val) => {
  if (val) filtroApenasMultiplasEspecialidades.value = false;
});

watch(filtroApenasMultiplasEspecialidades, (val) => {
  if (val) filtroApenasUmaEspecialidade.value = false;
});

const procedimentosOpcoes = computed(() => {
  const esp = espSelecionada.value;
  if (!esp) return [];

  const espLower = esp.toLowerCase().trim();

  let listFromAghu: string[] = [];
  for (const [key, list] of Object.entries(procedimentosAghuMap.value)) {
    const keyNorm = key.toLowerCase().trim();
    if (keyNorm === espLower || keyNorm.includes(espLower) || espLower.includes(keyNorm)) {
      listFromAghu = list;
      break;
    }
  }

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

  const raw = [...listFromAghu, ...extraProcs];
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

const norm = (str?: string) => str ? str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim() : '';

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

const formatarDataHora = (dataStr?: string) => {
  if (!dataStr || dataStr === '—' || dataStr === 'Não informado') return '—';
  try {
    const cleaned = String(dataStr).trim().replace('T', ' ');
    const parts = cleaned.split(' ');
    const dataPart = parts[0];
    const horaPart = parts[1] || '';

    let dia = '', mes = '', ano = '';
    if (dataPart.includes('-')) {
      const p = dataPart.split('-');
      if (p[0].length === 4) {
        [ano, mes, dia] = p;
      } else {
        [dia, mes, ano] = p;
      }
    } else if (dataPart.includes('/')) {
      const p = dataPart.split('/');
      if (p[0].length === 4) {
        [ano, mes, dia] = p;
      } else {
        [dia, mes, ano] = p;
      }
    } else {
      return dataStr;
    }

    let horaFormatada = '';
    if (horaPart) {
      const hParts = horaPart.split(':');
      if (hParts.length >= 2) {
        horaFormatada = `${hParts[0].padStart(2, '0')}:${hParts[1].padStart(2, '0')}`;
      }
    }

    const dataFormatada = `${dia.padStart(2, '0')}/${mes.padStart(2, '0')}/${ano}`;
    return horaFormatada ? `${dataFormatada} ${horaFormatada}` : dataFormatada;
  } catch (e) {
    return dataStr;
  }
};

const getSwalisPriorityRank = (swalisVal?: string): number => {
  if (!swalisVal) return 99;
  const clean = String(swalisVal).trim().toUpperCase();
  switch (clean) {
    case 'A1': return 1;
    case 'A2': return 2;
    case 'B':  return 3;
    case 'C':  return 4;
    case 'D':  return 5;
    default:   return 99;
  }
};

const parseDataHoraSort = (dStr?: string): number => {
  if (!dStr || dStr === '—' || dStr === 'Não informado') return Infinity;
  try {
    const cleaned = String(dStr).trim().replace('T', ' ');
    const parts = cleaned.split(' ');
    const dataPart = parts[0];
    const horaPart = parts[1] || '00:00:00';

    let ano = 9999, mes = 12, dia = 31;
    if (dataPart.includes('-')) {
      const p = dataPart.split('-');
      if (p[0].length === 4) {
        ano = parseInt(p[0], 10);
        mes = parseInt(p[1], 10);
        dia = parseInt(p[2], 10);
      } else {
        dia = parseInt(p[0], 10);
        mes = parseInt(p[1], 10);
        ano = parseInt(p[2], 10);
      }
    } else if (dataPart.includes('/')) {
      const p = dataPart.split('/');
      if (p[0].length === 4) {
        ano = parseInt(p[0], 10);
        mes = parseInt(p[1], 10);
        dia = parseInt(p[2], 10);
      } else {
        dia = parseInt(p[0], 10);
        mes = parseInt(p[1], 10);
        ano = parseInt(p[2], 10);
      }
    } else {
      const dt = new Date(cleaned);
      if (!isNaN(dt.getTime())) return dt.getTime();
      return Infinity;
    }

    const hParts = horaPart.split(':');
    const hh = parseInt(hParts[0], 10) || 0;
    const mm = parseInt(hParts[1], 10) || 0;
    const ss = parseInt(hParts[2], 10) || 0;

    const dt = new Date(ano, mes - 1, dia, hh, mm, ss);
    return isNaN(dt.getTime()) ? Infinity : dt.getTime();
  } catch (e) {
    return Infinity;
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

// 1. Mapa mestre com todos os pacientes e TODOS os seus procedimentos (sem filtros)
const todosPacientesMap = computed(() => {
  const norm = (str: string) => str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

  const resolverMedicoNome = (med: string) => {
    if (!med || med === 'Não informado' || med === '—') return med || 'Não informado';
    const clean = med.trim();
    if (!clean) return 'Não informado';

    const cleanNorm = norm(clean);
    const userMatch = usuarios.value.find(u => {
      if (!u) return false;
      const uNameNorm = u.nome ? norm(u.nome) : '';
      const uUserNorm = u.username ? norm(u.username) : '';
      return uUserNorm === cleanNorm || uNameNorm === cleanNorm || (cleanNorm.length > 5 && uNameNorm.includes(cleanNorm)) || (uNameNorm.length > 5 && cleanNorm.includes(uNameNorm));
    });

    const finalName = userMatch?.nome?.trim() || clean;
    return finalName && finalName !== 'Não informado' && finalName !== '—' ? finalName.toUpperCase() : finalName;
  };

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
        data_insercao: s.data_criacao || '—',
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
        if (!proc.data_insercao || proc.data_insercao === '—') {
          proc.data_insercao = s.data_criacao || '—';
        }
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
          data_insercao: baseMatch.data_hora_inicio || '—',
          medico_responsavel: resolverMedicoNome(baseMatch.medico_responsavel),
          status: 'ATIVO',
          tempo_standby: null
        });
      }
    }

    // Ordena os procedimentos de cada paciente também pelos critérios clínicos
    pac.procedimentos.sort((a: any, b: any) => {
      const rankA = getSwalisPriorityRank(a.Swalis || a.swalis || a.swallis);
      const rankB = getSwalisPriorityRank(b.Swalis || b.swalis || b.swallis);
      if (rankA !== rankB) return rankA - rankB;

      const timeA = parseDataHoraSort(a.data_insercao);
      const timeB = parseDataHoraSort(b.data_insercao);
      if (timeA !== timeB) return timeA - timeB;

      const procA = (a.procedimento || '').trim();
      const procB = (b.procedimento || '').trim();
      return procA.localeCompare(procB, 'pt-BR');
    });
  }

  return pacMap;
});

// 2. Lista de pacientes filtrados para a tabela principal
const pacientesProcessados = computed(() => {
  const pacMap = todosPacientesMap.value;

  // Se o perfil ativo for ESPECIALIDADE, filtra obrigatoriamente essa especialidade tanto para o paciente quanto para os procedimentos
  const espAtiva = (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo?.especialidade)
    ? perfisStore.perfilAtivo.especialidade.toLowerCase().trim()
    : (filtroEspecialidade.value ? filtroEspecialidade.value.toLowerCase().trim() : null);

  return Array.from(pacMap.values())
    .map(pac => {
      // Clona o array de procedimentos para não alterar o objeto mestre
      let procs = [...pac.procedimentos];

      if (espAtiva) {
        procs = procs.filter((p: any) => p.especialidade && p.especialidade.toLowerCase().trim().includes(espAtiva));
      }

      if (filtroProcedimento.value) {
        const procFiltroNorm = formatarNomeProcedimento(filtroProcedimento.value);
        procs = procs.filter((p: any) => p.procedimento && formatarNomeProcedimento(p.procedimento) === procFiltroNorm);
      }

      if (filtroMedico.value) {
        const medicoSelecionado = filtroMedico.value.toUpperCase().trim();
        const medicoNorm = norm(medicoSelecionado);

        procs = procs.filter((p: any) => {
          if (!p.medico_responsavel) return false;
          const mUpper = p.medico_responsavel.toUpperCase().trim();
          const mNorm = norm(mUpper);
          return mUpper === medicoSelecionado || mNorm === medicoNorm;
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

      // Total de especialidades únicas e procedimentos totais do paciente no sistema completo
      const todasEspecialidades = new Set(pac.procedimentos.map((p: any) => (p.especialidade || '').trim()).filter(Boolean));

      return {
        ...pac,
        procedimentos: procs,
        totalProcedimentosGerais: pac.procedimentos.length,
        totalEspecialidadesGerais: todasEspecialidades.size
      };
    })
    .filter(pac => {
      if (pac.procedimentos.length === 0) return false;
      
      // Filtro para procedimentos (1 ou múltiplos)
      if (filtroApenasUmProcedimento.value && pac.totalProcedimentosGerais !== 1) return false;
      if (filtroApenasMultiplos.value && pac.totalProcedimentosGerais <= 1) return false;

      // Filtro para especialidades (1 ou múltiplas)
      if (filtroApenasUmaEspecialidade.value && pac.totalEspecialidadesGerais !== 1) return false;
      if (filtroApenasMultiplasEspecialidades.value && pac.totalEspecialidadesGerais <= 1) return false;

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
  const cod = String(paciente?.codigo || paciente);
  // Sempre busca o registro completo e não-filtrado do paciente para exibir todas as especialidades e procedimentos no modal
  const pacienteCompleto = todosPacientesMap.value.get(cod) || paciente;
  pacienteSelecionadoModal.value = pacienteCompleto;
  modalDetalhesAberto.value = true;
}

function fecharModalPaciente() {
  modalDetalhesAberto.value = false;
  pacienteSelecionadoModal.value = null;
}

// Mapeia os pacientes filtrados em linhas individuais de procedimento (Flat Table)
// com ordenação hierárquica multi-critério:
// 1º Critério: Swalis (do mais crítico para o menos crítico)
// 2º Critério: Data/Hora de Inserção na LEC (do mais antigo para o mais recente)
// 3º Critério: Ordem Alfabética (Nome do Paciente e Procedimento)
const procedimentosFlat = computed(() => {
  const list: any[] = [];

  for (const pac of pacientesProcessados.value) {
    const pacMestre = todosPacientesMap.value.get(String(pac.codigo)) || pac;
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
        data_insercao: proc.data_insercao || '—',
        medico_responsavel: proc.medico_responsavel || 'Não informado',
        status: proc.status,
        tempo_standby: proc.tempo_standby,
        pacienteCompleto: pacMestre
      });
    }
  }

  return list.sort((a, b) => {
    // 1º Critério: Swalis (do mais crítico para o menos crítico: A1 > A2 > B > C > D > Sem Swalis)
    const rankA = getSwalisPriorityRank(a.Swalis);
    const rankB = getSwalisPriorityRank(b.Swalis);
    if (rankA !== rankB) {
      return rankA - rankB;
    }

    // 2º Critério: Data/Hora de Inserção na LEC (do mais antigo para o mais recente / ASC)
    const timeA = parseDataHoraSort(a.data_insercao);
    const timeB = parseDataHoraSort(b.data_insercao);
    if (timeA !== timeB) {
      return timeA - timeB;
    }

    // 3º Critério: Ordem Alfabética (Nome do Paciente em pt-BR)
    const nomeA = (a.nome || '').trim();
    const nomeB = (b.nome || '').trim();
    const diffNome = nomeA.localeCompare(nomeB, 'pt-BR');

    if (diffNome !== 0) {
      return diffNome;
    }

    // Fallback de desempate alfabético por nome do procedimento
    const procA = (a.procedimento || '').trim();
    const procB = (b.procedimento || '').trim();
    const diffProc = procA.localeCompare(procB, 'pt-BR');
    if (diffProc !== 0) {
      return diffProc;
    }

    // Fallback final: Data de Nascimento (da mais antiga para a mais recente)
    const parseDataNasc = (dStr: string) => {
      if (!dStr || dStr === '—') return '9999-99-99';
      if (dStr.includes('/')) {
        const parts = dStr.split('/');
        if (parts.length === 3) return `${parts[2]}-${parts[1]}-${parts[0]}`;
      }
      return dStr;
    };

    const dataA = parseDataNasc(a.dt_nascimento);
    const dataB = parseDataNasc(b.dt_nascimento);
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
