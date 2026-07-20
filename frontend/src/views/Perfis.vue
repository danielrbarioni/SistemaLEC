<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Controle de Acessos e Usuários</h1>
      <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
        Configurações do Sistema
      </span>
    </div>

    <!-- Seletor de Perfil Ativo rápido (se necessário para debug/desenvolvimento) -->
    <div v-if="perfisStore.loading" class="text-center py-6 text-gray-500">
      <span class="inline-block animate-spin border-4 border-emerald-500 border-t-transparent w-8 h-8 rounded-full mr-2 align-middle"></span>
      Carregando dados...
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Lista de Perfis & Usuários -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Perfis Disponíveis -->
        <Card>
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">Perfis Disponíveis</h2>
          </template>

          <div class="divide-y divide-gray-200">
            <div 
              v-for="perf in perfisStore.perfis" 
              :key="perf.id" 
              class="py-4 flex items-center justify-between first:pt-0 last:pb-0"
            >
              <div class="flex items-center space-x-3">
                <!-- Indicador de Cor -->
                <span :class="[getCorClass(perf.tipo), 'inline-block w-3.5 h-3.5 rounded-full ring-4 ring-opacity-20 shrink-0']"></span>
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-gray-800">{{ perf.nome }}</span>
                    <span v-if="perfisStore.perfilAtivoId === perf.id" class="px-2 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-full">
                      Ativo
                    </span>
                  </div>
                  <div class="text-xs text-gray-500 mt-0.5">
                    Tipo: <span class="font-medium text-gray-700">{{ getTipoLabel(perf.tipo) }}</span>
                    <span v-if="perf.especialidade"> | Especialidade: <span class="font-medium text-gray-700">{{ perf.especialidade }}</span></span>
                  </div>
                </div>
              </div>

              <div class="flex items-center space-x-2">
                <Button 
                  v-if="perfisStore.perfilAtivoId !== perf.id"
                  @click="alterarPerfilAtivo(perf.id)"
                  variant="primary" 
                  size="sm"
                >
                  Ativar Perfil
                </Button>
                <span v-else class="text-xs font-semibold text-emerald-600 flex items-center space-x-1">
                  <span>✓ Ativo atualmente</span>
                </span>

                <!-- Ações para o Perfil -->
                <template v-if="podeEditarOuExcluirPerfil(perf)">
                  <button 
                    @click="iniciarEdicaoPerfil(perf)" 
                    class="text-indigo-600 hover:text-indigo-950 text-xs font-bold cursor-pointer px-2 py-1"
                  >
                    Editar
                  </button>
                  <button 
                    @click="excluirPerfil(perf)" 
                    class="text-red-600 hover:text-red-950 text-xs font-bold cursor-pointer px-2 py-1"
                  >
                    Excluir
                  </button>
                </template>
              </div>
            </div>
          </div>
        </Card>

        <!-- Detalhes do Perfil Ativo -->
        <Card class="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200">
          <h3 class="font-bold text-gray-800 text-sm mb-2">Comportamento do Perfil Ativo:</h3>
          <div class="text-xs text-gray-600 space-y-2">
            <p v-if="perfisStore.perfilAtivo.tipo === 'ADMIN'">
              <strong>ADMIN (Desenvolvedor/Manutenção):</strong> Possui acesso total ao formulário do Sistema LEC, visualiza solicitações de todas as especialidades e pode aprovar/rejeitar registros. Tem permissão para criar perfis e qualquer tipo de usuário.
            </p>
            <p v-else-if="perfisStore.perfilAtivo.tipo === 'GESTAO_LEC'">
              <strong>GESTÃO LEC (Equipe de Gestão):</strong> Responsável por receber e acompanhar as solicitações de todas as especialidades. O formulário de nova solicitação fica oculto. Pode aprovar ("Dar Baixa") ou rejeitar registros. Tem permissão para criar perfis e usuários do tipo GESTÃO LEC ou ESPECIALIDADE.
            </p>
            <p v-else>
              <strong>ESPECIALIDADE ({{ perfisStore.perfilAtivo.especialidade }}):</strong> Responsável por criar solicitações (inclusão, edição, exclusão, standby) apenas para a especialidade <strong>{{ perfisStore.perfilAtivo.especialidade }}</strong>. Visualiza no acompanhamento apenas as solicitações desta especialidade. Não pode aprovar/rejeitar registros. Tem permissão para criar usuários unicamente vinculados à sua própria especialidade.
            </p>
          </div>
        </Card>

        <!-- Usuários Cadastrados Localmente -->
        <Card>
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">
              {{ editingUserId ? (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' ? 'Solicitar Edição de Usuário' : 'Editar Usuário') : 'Usuários Locais Cadastrados' }}
            </h2>
          </template>

          <!-- Seção de Edição (Exibida em cima dos Usuários Locais Cadastrados) -->
          <div v-if="editingUserId" class="p-6">
            <form @submit.prevent="salvarUsuario" class="space-y-4 max-w-xl mx-auto">
              <div class="form-group">
                <label for="edit_usr_username" class="form-label font-semibold">Usuário (usuário Ebserh)</label>
                <input 
                  id="edit_usr_username" 
                  v-model="usuarioForm.username" 
                  type="text" 
                  class="form-control bg-gray-100 cursor-not-allowed"
                  disabled
                />
              </div>

              <div class="form-group">
                <label for="edit_usr_nome" class="form-label font-semibold">Nome completo <span class="text-red-500">*</span></label>
                <input 
                  id="edit_usr_nome" 
                  v-model="usuarioForm.nome" 
                  type="text" 
                  placeholder="Ex: Dr. João Silva" 
                  class="form-control"
                  required
                />
              </div>

              <div class="form-group">
                <label for="edit_usr_perfil" class="form-label font-semibold">Perfil de Acesso <span class="text-red-500">*</span></label>
                <select 
                  id="edit_usr_perfil" 
                  v-model="usuarioForm.perfil_id" 
                  class="form-control" 
                  required
                  :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' || editandoAdminOuGestao"
                  :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' || editandoAdminOuGestao }"
                >
                  <option value="" disabled>Selecione...</option>
                  <option v-for="perf in perfisFiltrados" :key="perf.id" :value="perf.id">
                    {{ perf.nome }} ({{ getTipoLabel(perf.tipo) }})
                  </option>
                </select>
              </div>

              <!-- Campo Função condicional -->
              <div v-if="exibirCampoFuncao" class="form-group">
                <label for="edit_usr_funcao" class="form-label font-semibold">Função <span class="text-red-500">*</span></label>
                <select id="edit_usr_funcao" v-model="usuarioForm.funcao" class="form-control" :required="exibirCampoFuncao">
                  <option value="" disabled>Selecione...</option>
                  <option value="Médico">Médico</option>
                  <option value="Residente">Residente</option>
                  <option value="Enfermeiro">Enfermeiro</option>
                </select>
              </div>

              <div class="flex space-x-2 pt-2">
                <Button type="submit" variant="primary" class="w-full justify-center">
                  {{ perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' ? 'Solicitar Edição' : 'Salvar' }}
                </Button>
                <Button 
                  type="button" 
                  variant="default" 
                  @click="cancelarEdicao" 
                  class="w-full justify-center"
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </div>

          <div v-else>
            <!-- Filtros de Usuários -->
            <div class="p-4 bg-gray-50 border-b border-gray-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              <div class="form-group">
                <label for="filtro_nome" class="text-xs font-semibold text-gray-500">Nome / Username</label>
                <input 
                  id="filtro_nome" 
                  v-model="filtros.nome" 
                  type="text" 
                  placeholder="Filtrar por nome..." 
                  class="form-control text-xs w-full"
                />
              </div>
              
              <div class="form-group">
                <label for="filtro_especialidade" class="text-xs font-semibold text-gray-500">Especialidade</label>
                <select 
                  id="filtro_especialidade" 
                  v-model="filtros.especialidade" 
                  class="form-control text-xs w-full"
                  :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
                  :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
                >
                  <option value="">Todas</option>
                  <option v-for="esp in uniqueEspecialidades" :key="esp" :value="esp">
                    {{ esp }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="filtro_funcao" class="text-xs font-semibold text-gray-500">Função</label>
                <select id="filtro_funcao" v-model="filtros.funcao" class="form-control text-xs w-full">
                  <option value="">Todas</option>
                  <option value="Médico">Médico</option>
                  <option value="Residente">Residente</option>
                  <option value="Enfermeiro">Enfermeiro</option>
                </select>
              </div>

              <div v-if="podeCriarPerfil" class="form-group">
                <label for="filtro_perfil_id" class="text-xs font-semibold text-gray-500">Perfil ID</label>
                <select id="filtro_perfil_id" v-model="filtros.perfil_id" class="form-control text-xs w-full">
                  <option value="">Todos</option>
                  <option v-for="p in uniquePerfisIds" :key="p" :value="p">
                    {{ p }}
                  </option>
                </select>
              </div>
            </div>

            <div v-if="usuariosFiltrados.length === 0" class="text-center py-6 text-gray-500 text-sm">
              Nenhum usuário correspondente aos filtros.
            </div>
            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Nome / Username</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Perfil ID</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Especialidade</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Função</th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Ações</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="user in usuariosFiltrados" :key="user.id">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-bold text-gray-800">{{ user.nome }}</div>
                      <div class="text-xs text-gray-500">@{{ user.username }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="px-2 py-1 text-xs font-semibold rounded bg-gray-100 text-gray-800 border border-gray-200">
                        {{ user.perfil_id }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ user.especialidade || '—' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ user.funcao || '—' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        v-if="podeEditarUsuario(user)"
                        @click="iniciarEdicao(user)" 
                        class="text-indigo-600 hover:text-indigo-900 font-semibold cursor-pointer mr-3"
                      >
                        Editar
                      </button>
                      <button 
                        v-if="podeExcluirUsuario(user)"
                        @click="excluirUsuario(user.id)" 
                        class="text-red-600 hover:text-red-900 font-semibold cursor-pointer"
                      >
                        Excluir
                      </button>
                      <span v-if="!podeEditarUsuario(user) && !podeExcluirUsuario(user)" class="text-xs text-gray-400 italic">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </div>

      <!-- Formulários de Criação (Lateral) -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Formulário: Criar Novo Perfil / Editar Perfil (No topo agora) -->
        <Card v-if="podeCriarPerfil">
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">{{ editingPerfilId ? 'Editar Perfil' : 'Criar Novo Perfil' }}</h2>
          </template>

          <form @submit.prevent="salvarPerfil" class="space-y-4">
            <div class="form-group">
              <label for="tipo_perfil" class="form-label font-semibold">Tipo</label>
              <input 
                id="tipo_perfil" 
                type="text" 
                :value="getTipoLabel(perfilForm.tipo)" 
                class="form-control bg-gray-100 cursor-not-allowed"
                disabled
              />
            </div>

            <div v-if="perfilForm.tipo === 'ESPECIALIDADE'" class="form-group">
              <label for="especialidade" class="form-label font-semibold">Nome da Especialidade <span class="text-red-500">*</span></label>
              <input 
                id="especialidade" 
                v-model="perfilForm.especialidade" 
                type="text" 
                placeholder="Ex: Plástica" 
                class="form-control"
                required
              />
            </div>

            <div v-if="perfilForm.tipo !== 'ESPECIALIDADE'" class="form-group">
              <label for="nome_perfil" class="form-label font-semibold">Nome do Perfil <span class="text-red-500">*</span></label>
              <input 
                id="nome_perfil" 
                v-model="perfilForm.nome" 
                type="text" 
                placeholder="Ex: ADMIN" 
                class="form-control"
                required
              />
            </div>

            <div class="flex space-x-2">
              <Button type="submit" variant="primary" class="w-full justify-center">
                {{ editingPerfilId ? 'Salvar' : 'Criar Perfil' }}
              </Button>
              <Button 
                v-if="editingPerfilId" 
                type="button" 
                variant="default" 
                @click="cancelarEdicaoPerfil" 
                class="w-full justify-center"
              >
                Cancelar
              </Button>
            </div>
          </form>
        </Card>

        <!-- Seção: Criar / Solicitar Criação de Usuário (Com Abas para Admin/Gestão) -->
        <Card v-if="!editingUserId">
          <template #header>
            <div v-if="podeCriarPerfil" class="w-full">
              <div class="flex border-b border-gray-200">
                <button 
                  type="button"
                  @click="activeTab = 'criar'" 
                  :class="[activeTab === 'criar' ? 'border-indigo-500 text-indigo-600 border-b-2' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'flex-1 pb-2 text-center font-bold text-sm cursor-pointer']"
                >
                  Criar Usuário
                </button>
                <button 
                  type="button"
                  @click="activeTab = 'solicitacoes'" 
                  :class="[activeTab === 'solicitacoes' ? 'border-indigo-500 text-indigo-600 border-b-2' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'flex-1 pb-2 text-center font-bold text-sm cursor-pointer relative']"
                >
                  Solicitações
                  <span v-if="solicitacoes.length > 0" class="ml-1 px-2 py-0.5 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                    {{ solicitacoes.length }}
                  </span>
                </button>
              </div>
            </div>
            <h2 v-else class="text-lg font-bold text-gray-800">
              Solicitar Criação de Usuário
            </h2>
          </template>

          <!-- Aba 1: Formulário de Criar/Solicitar -->
          <div v-if="!podeCriarPerfil || activeTab === 'criar'">
            <form @submit.prevent="salvarUsuario" class="space-y-4">
              <div class="form-group">
                <label for="usr_username" class="form-label font-semibold">Usuário (usuário Ebserh) <span class="text-red-500">*</span></label>
                <input 
                  id="usr_username" 
                  v-model="usuarioForm.username" 
                  type="text" 
                  placeholder="Ex: joao.silva" 
                  class="form-control"
                  required
                />
              </div>

              <div class="form-group">
                <label for="usr_nome" class="form-label font-semibold">Nome completo <span class="text-red-500">*</span></label>
                <input 
                  id="usr_nome" 
                  v-model="usuarioForm.nome" 
                  type="text" 
                  placeholder="Ex: Dr. João Silva" 
                  class="form-control"
                  required
                />
              </div>

              <div class="form-group">
                <label for="usr_perfil" class="form-label font-semibold">Perfil de Acesso <span class="text-red-500">*</span></label>
                <select 
                  id="usr_perfil" 
                  v-model="usuarioForm.perfil_id" 
                  class="form-control" 
                  required
                  :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
                  :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
                >
                  <option value="" disabled>Selecione...</option>
                  <option v-for="perf in perfisFiltrados" :key="perf.id" :value="perf.id">
                    {{ perf.nome }} ({{ getTipoLabel(perf.tipo) }})
                  </option>
                </select>
              </div>

              <!-- Campo Função condicional -->
              <div v-if="exibirCampoFuncao" class="form-group">
                <label for="usr_funcao" class="form-label font-semibold">Função <span class="text-red-500">*</span></label>
                <select id="usr_funcao" v-model="usuarioForm.funcao" class="form-control" :required="exibirCampoFuncao">
                  <option value="" disabled>Selecione...</option>
                  <option value="Médico">Médico</option>
                  <option value="Residente">Residente</option>
                  <option value="Enfermeiro">Enfermeiro</option>
                </select>
              </div>

              <div class="flex space-x-2">
                <Button type="submit" variant="primary" class="w-full justify-center">
                  {{ perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' ? 'Solicitar Criação' : 'Criar Usuário' }}
                </Button>
              </div>
            </form>
          </div>

          <!-- Aba 2: Lista de Solicitações Pendentes (ADMIN e GESTÃO LEC) -->
          <div v-else-if="podeCriarPerfil && activeTab === 'solicitacoes'" class="space-y-4">
            <div v-if="solicitacoes.length === 0" class="text-center py-6 text-gray-500 text-sm">
              Nenhuma solicitação pendente.
            </div>
            <div v-else class="space-y-3 max-h-[450px] overflow-y-auto pr-1">
              <div v-for="sol in solicitacoes" :key="sol.id" class="p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-2">
                <div class="flex justify-between items-start">
                  <div>
                    <h4 class="text-sm font-bold text-gray-800">{{ sol.nome }}</h4>
                    <p class="text-xs text-gray-500">@{{ sol.username }}</p>
                  </div>
                  <div class="flex flex-col items-end space-y-1">
                    <span class="px-1.5 py-0.5 text-[9px] font-bold bg-amber-100 text-amber-800 border border-amber-200 rounded">
                      PENDENTE
                    </span>
                    <span :class="[sol.tipo === 'EDICAO' ? 'bg-purple-100 text-purple-800 border border-purple-200' : 'bg-blue-100 text-blue-800 border border-blue-200', 'px-1.5 py-0.5 text-[9px] font-bold rounded']">
                      {{ sol.tipo === 'EDICAO' ? 'Edição' : 'Criação' }}
                    </span>
                  </div>
                </div>
                <div class="text-xs text-gray-600 space-y-0.5">
                  <p><strong>Perfil solicitado:</strong> <span class="font-semibold">{{ sol.perfil_id }}</span></p>
                  <p v-if="sol.especialidade"><strong>Especialidade:</strong> {{ sol.especialidade }}</p>
                  <p v-if="sol.funcao"><strong>Função:</strong> {{ sol.funcao }}</p>
                  
                  <div v-if="sol.tipo === 'EDICAO' && sol.campos_modificados" class="mt-2 p-2 bg-purple-50 border border-purple-100 rounded text-purple-950">
                    <p class="font-bold text-[10px] text-purple-800 uppercase tracking-wider">Campos alterados:</p>
                    <p class="text-[11px] mt-0.5 font-medium">{{ sol.campos_modificados }}</p>
                  </div>

                  <p class="text-[10px] text-gray-400 mt-1">Solicitado em: {{ formatData(sol.created_at) }}</p>
                </div>
                <div class="flex space-x-2 pt-1.5">
                  <button 
                    @click="aprovarSolicitacao(sol.id)" 
                    class="flex-1 py-1 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded transition cursor-pointer text-center"
                  >
                    Aprovar
                  </button>
                  <button 
                    @click="rejeitarSolicitacao(sol.id)" 
                    class="flex-1 py-1 text-xs font-bold text-red-600 hover:bg-red-50 border border-red-200 rounded transition cursor-pointer text-center"
                  >
                    Rejeitar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { usePerfisStore } from '../stores/perfis';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';

const toast = useToast();
const perfisStore = usePerfisStore();

const usuarios = ref<any[]>([]);
const solicitacoes = ref<any[]>([]);
const activeTab = ref('criar');
const editingUserId = ref<number | null>(null);
const editingPerfilId = ref<string | null>(null);

// Filtros da tabela
const filtros = ref({
  nome: '',
  especialidade: '',
  funcao: '',
  perfil_id: ''
});

// Formulários
const perfilForm = ref({
  nome: '',
  tipo: 'ESPECIALIDADE',
  especialidade: ''
});

const usuarioForm = ref({
  nome: '',
  username: '',
  perfil_id: '',
  funcao: ''
});

// Regras de Visualização/Permissão baseadas no perfil ativo
const podeCriarPerfil = computed(() => {
  const tipo = perfisStore.perfilAtivo.tipo;
  return tipo === 'ADMIN' || tipo === 'GESTAO_LEC';
});

// Dropdown dinâmico de perfis para criação de usuário conforme regras hierárquicas
const perfisFiltrados = computed(() => {
  const tipo = perfisStore.perfilAtivo.tipo;
  const esp = perfisStore.perfilAtivo.especialidade;

  if (tipo === 'ADMIN') {
    return perfisStore.perfis;
  } else if (tipo === 'GESTAO_LEC') {
    return perfisStore.perfis.filter(p => p.tipo === 'GESTAO_LEC' || p.tipo === 'ESPECIALIDADE');
  } else if (tipo === 'ESPECIALIDADE' && esp) {
    return perfisStore.perfis.filter(p => p.tipo === 'ESPECIALIDADE' && p.especialidade === esp);
  }
  return [];
});

const exibirCampoFuncao = computed(() => {
  const selectedPerfil = perfisStore.perfis.find(p => p.id === usuarioForm.value.perfil_id);
  return selectedPerfil?.tipo === 'ESPECIALIDADE';
});

const editandoAdminOuGestao = computed(() => {
  if (!editingUserId.value) return false;
  const user = usuarios.value.find(u => u.id === editingUserId.value);
  if (!user) return false;
  const perf = perfisStore.perfis.find(p => p.id === user.perfil_id);
  return perf?.tipo === 'ADMIN' || perf?.tipo === 'GESTAO_LEC';
});

// Filtros dinâmicos extraídos dos dados
const uniqueEspecialidades = computed(() => {
  const exps = perfisStore.perfis
    .map(p => p.especialidade)
    .filter((e): e is string => !!e);
  return Array.from(new Set(exps));
});

const uniquePerfisIds = computed(() => {
  const ids = perfisStore.perfis.map(p => p.id);
  return Array.from(new Set(ids));
});

// Tabela filtrada
const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(user => {
    // Filtro obrigatório para perfil ESPECIALIDADE
    if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE') {
      if (user.especialidade !== perfisStore.perfilAtivo.especialidade) {
        return false;
      }
    } else {
      if (filtros.value.especialidade && user.especialidade !== filtros.value.especialidade) {
        return false;
      }
    }

    if (filtros.value.nome) {
      const search = filtros.value.nome.toLowerCase();
      const matchNome = user.nome?.toLowerCase().includes(search);
      const matchUser = user.username?.toLowerCase().includes(search);
      if (!matchNome && !matchUser) return false;
    }

    if (filtros.value.funcao && user.funcao !== filtros.value.funcao) {
      return false;
    }

    if (podeCriarPerfil.value && filtros.value.perfil_id && user.perfil_id !== filtros.value.perfil_id) {
      return false;
    }

    return true;
  });
});

const loadUsuarios = async () => {
  try {
    const { data } = await api.get('/api/usuarios');
    usuarios.value = data;
  } catch (error) {
    console.error('Erro ao carregar usuários:', error);
  }
};

const loadSolicitacoes = async () => {
  if (!podeCriarPerfil.value) return;
  try {
    const { data } = await api.get('/api/usuarios/solicitacoes');
    solicitacoes.value = data;
  } catch (error) {
    console.error('Erro ao carregar solicitações:', error);
  }
};

const alterarPerfilAtivo = (id: string) => {
  perfisStore.setPerfilAtivo(id);
  toast.success('Perfil de utilização alterado!');
  cancelarEdicao();
  loadSolicitacoes();
};

const podeEditarOuExcluirPerfil = (perf: any) => {
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  if (tipoAtivo === 'ADMIN') return true;
  if (tipoAtivo === 'GESTAO_LEC') return perf.tipo === 'ESPECIALIDADE';
  return false;
};

const podeEditarUsuario = (user: any) => {
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  const espAtivo = perfisStore.perfilAtivo.especialidade;

  if (tipoAtivo === 'ADMIN') {
    const perf = perfisStore.perfis.find(p => p.id === user.perfil_id);
    return perf?.tipo === 'ADMIN' || perf?.tipo === 'GESTAO_LEC' || perf?.tipo === 'ESPECIALIDADE';
  }
  if (tipoAtivo === 'GESTAO_LEC') {
    const perf = perfisStore.perfis.find(p => p.id === user.perfil_id);
    return perf?.tipo === 'GESTAO_LEC' || perf?.tipo === 'ESPECIALIDADE';
  }
  if (tipoAtivo === 'ESPECIALIDADE') {
    return user.especialidade === espAtivo;
  }
  return false;
};

const podeExcluirUsuario = (user: any) => {
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  const espAtivo = perfisStore.perfilAtivo.especialidade;

  if (tipoAtivo === 'ADMIN') return true;
  if (tipoAtivo === 'GESTAO_LEC') {
    const perf = perfisStore.perfis.find(p => p.id === user.perfil_id);
    return perf?.tipo === 'ESPECIALIDADE';
  }
  if (tipoAtivo === 'ESPECIALIDADE') {
    return user.especialidade === espAtivo;
  }
  return false;
};

const iniciarEdicaoPerfil = (perf: any) => {
  editingPerfilId.value = perf.id;
  perfilForm.value.nome = perf.nome;
  perfilForm.value.tipo = perf.tipo;
  perfilForm.value.especialidade = perf.especialidade || '';
};

const cancelarEdicaoPerfil = () => {
  editingPerfilId.value = null;
  perfilForm.value.nome = '';
  perfilForm.value.tipo = 'ESPECIALIDADE';
  perfilForm.value.especialidade = '';
};

const salvarPerfil = async () => {
  if (perfilForm.value.tipo === 'ESPECIALIDADE' && !perfilForm.value.especialidade) {
    toast.error('Informe o nome da especialidade.');
    return;
  }
  if (perfilForm.value.tipo !== 'ESPECIALIDADE' && !perfilForm.value.nome) {
    toast.error('Informe o nome do perfil.');
    return;
  }

  try {
    const nomePerfil = perfilForm.value.tipo === 'ESPECIALIDADE' 
      ? perfilForm.value.especialidade.trim().toUpperCase() 
      : perfilForm.value.nome.trim().toUpperCase();

    if (editingPerfilId.value) {
      await api.put(`/api/perfis/${editingPerfilId.value}`, {
        nome: nomePerfil,
        especialidade: perfilForm.value.tipo === 'ESPECIALIDADE' ? perfilForm.value.especialidade.trim() : null
      });
      toast.success('Perfil atualizado com sucesso!');
    } else {
      await perfisStore.adicionarPerfil(
        nomePerfil,
        perfilForm.value.especialidade.trim()
      );
      toast.success('Perfil criado com sucesso!');
    }

    cancelarEdicaoPerfil();
    await perfisStore.fetchPerfis();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao salvar perfil.';
    toast.error(detail);
  }
};

const excluirPerfil = async (perf: any) => {
  if (!confirm(`Tem certeza que deseja excluir o perfil "${perf.nome}"?`) || !confirm("Confirma a exclusão deste perfil? Esta ação não poderá ser desfeita.")) {
    return;
  }
  try {
    await api.delete(`/api/perfis/${perf.id}`);
    toast.success('Perfil excluído com sucesso!');
    if (editingPerfilId.value === perf.id) {
      cancelarEdicaoPerfil();
    }
    await perfisStore.fetchPerfis();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao excluir perfil.';
    toast.error(detail);
  }
};

const iniciarEdicao = (user: any) => {
  editingUserId.value = user.id;
  usuarioForm.value.nome = user.nome;
  usuarioForm.value.username = user.username;
  usuarioForm.value.perfil_id = user.perfil_id;
  usuarioForm.value.funcao = user.funcao || '';
};

const cancelarEdicao = () => {
  editingUserId.value = null;
  usuarioForm.value.nome = '';
  usuarioForm.value.username = '';
  usuarioForm.value.funcao = '';
  if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE') {
    usuarioForm.value.perfil_id = perfisStore.perfilAtivo.id;
  } else {
    usuarioForm.value.perfil_id = '';
  }
};

const salvarUsuario = async () => {
  try {
    const payload = {
      nome: usuarioForm.value.nome,
      username: usuarioForm.value.username.trim(),
      perfil_id: usuarioForm.value.perfil_id,
      funcao: exibirCampoFuncao.value ? usuarioForm.value.funcao : null
    };

    if (editingUserId.value) {
      if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE') {
        const originalUser = usuarios.value.find(u => u.id === editingUserId.value);
        const diffs: string[] = [];
        if (originalUser) {
          if (originalUser.nome !== payload.nome) {
            diffs.push(`Nome: de "${originalUser.nome}" para "${payload.nome}"`);
          }
          if (originalUser.perfil_id !== payload.perfil_id) {
            const oldProf = perfisStore.perfis.find(p => p.id === originalUser.perfil_id)?.nome || originalUser.perfil_id;
            const newProf = perfisStore.perfis.find(p => p.id === payload.perfil_id)?.nome || payload.perfil_id;
            diffs.push(`Perfil: de "${oldProf}" para "${newProf}"`);
          }
          if ((originalUser.funcao || '') !== (payload.funcao || '')) {
            diffs.push(`Função: de "${originalUser.funcao || 'Nenhuma'}" para "${payload.funcao || 'Nenhuma'}"`);
          }
        }
        
        await api.post('/api/usuarios/solicitacoes', {
          ...payload,
          tipo: 'EDICAO',
          user_id: editingUserId.value,
          campos_modificados: diffs.join(', ')
        });
        toast.success('Solicitação de edição de usuário enviada com sucesso!');
      } else {
        await api.put(`/api/usuarios/${editingUserId.value}`, payload);
        toast.success('Usuário atualizado com sucesso!');
      }
    } else {
      if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE') {
        await api.post('/api/usuarios/solicitacoes', payload);
        toast.success('Solicitação de criação de usuário enviada com sucesso!');
      } else {
        await api.post('/api/usuarios', payload);
        toast.success('Usuário vinculado com sucesso!');
      }
    }

    cancelarEdicao();
    await loadUsuarios();
    await loadSolicitacoes();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao salvar usuário.';
    toast.error(detail);
  }
};

const excluirUsuario = async (id: number) => {
  if (!confirm('Tem certeza que deseja excluir este usuário?')) {
    return;
  }
  try {
    await api.delete(`/api/usuarios/${id}`);
    toast.success('Usuário excluído com sucesso!');
    if (editingUserId.value === id) {
      cancelarEdicao();
    }
    await loadUsuarios();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao excluir usuário.';
    toast.error(detail);
  }
};

const aprovarSolicitacao = async (id: number) => {
  if (!confirm('Confirma a aprovação desta solicitação de usuário?')) {
    return;
  }
  try {
    await api.post(`/api/usuarios/solicitacoes/${id}/aprovar`);
    toast.success('Solicitação aprovada com sucesso!');
    await loadSolicitacoes();
    await loadUsuarios();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao aprovar solicitação.';
    toast.error(detail);
  }
};

const rejeitarSolicitacao = async (id: number) => {
  if (!confirm('Confirma a rejeição desta solicitação de usuário?')) {
    return;
  }
  try {
    await api.post(`/api/usuarios/solicitacoes/${id}/rejeitar`);
    toast.success('Solicitação rejeitada com sucesso!');
    await loadSolicitacoes();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao rejeitar solicitação.';
    toast.error(detail);
  }
};

const formatData = (dateStr: string) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString('pt-BR');
};

const getCorClass = (tipo: string) => {
  switch (tipo) {
    case 'ADMIN': return 'bg-gray-400 ring-gray-400';
    case 'GESTAO_LEC': return 'bg-blue-500 ring-blue-500';
    case 'ESPECIALIDADE': return 'bg-green-500 ring-green-500';
    default: return 'bg-gray-400 ring-gray-400';
  }
};

const getTipoLabel = (tipo: string) => {
  switch (tipo) {
    case 'ADMIN': return 'ADMIN';
    case 'GESTAO_LEC': return 'Gestão da LEC';
    case 'ESPECIALIDADE': return 'Especialidade Cirúrgica';
    default: return tipo;
  }
};

// Monitora o perfil ativo para aplicar o filtro mandatório e definir perfil_id padrão no form
watch(() => perfisStore.perfilAtivo, (newPerfil) => {
  if (newPerfil.tipo === 'ESPECIALIDADE') {
    filtros.value.especialidade = newPerfil.especialidade || '';
    usuarioForm.value.perfil_id = newPerfil.id;
  } else {
    filtros.value.especialidade = '';
    usuarioForm.value.perfil_id = '';
  }
}, { immediate: true });

onMounted(async () => {
  await perfisStore.fetchPerfis();
  await loadUsuarios();
  await loadSolicitacoes();
});
</script>
