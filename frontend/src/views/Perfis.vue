<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Controle de Acessos e Usuários</h1>
      <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
        Configurações do Sistema
      </span>
    </div>

    <div v-if="perfisStore.loading" class="text-center py-6 text-gray-500">
      <span class="inline-block animate-spin border-4 border-emerald-500 border-t-transparent w-8 h-8 rounded-full mr-2 align-middle"></span>
      Carregando dados...
    </div>

    <div v-else class="space-y-6">
      <!-- Seção Superior: Perfis Disponíveis (Esquerda) e Formulários de Criação (Direita) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Coluna Esquerda: Perfis Disponíveis + Detalhes do Perfil Ativo -->
        <div :class="[perfisStore.perfilAtivo.tipo === 'NENHUM' || perfisStore.perfilAtivo.tipo === 'OBSERVADOR' || perfisStore.perfilAtivo.tipo === 'EPO_GENERALISTA' ? 'lg:col-span-12' : 'lg:col-span-7', 'space-y-6']">
          <!-- Perfis Disponíveis -->
          <Card>
            <template #header>
              <div class="flex justify-between items-center">
                <h2 class="text-lg font-bold text-gray-800">Perfis Disponíveis</h2>
                <span class="text-xs text-gray-500 font-medium">Total: {{ perfisOrdenados.length }}</span>
              </div>
            </template>

            <div class="divide-y divide-gray-200">
              <div 
                v-for="perf in perfisOrdenados" 
                :key="perf.id" 
                class="py-3.5 flex items-center justify-between first:pt-0 last:pb-0"
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
                    v-if="podeAtivarPerfil(perf)"
                    @click="alterarPerfilAtivo(perf.id)"
                    variant="primary" 
                    size="sm"
                  >
                    Ativar Perfil
                  </Button>
                  <span v-else-if="perfisStore.perfilAtivoId === perf.id" class="text-xs font-semibold text-emerald-600 flex items-center space-x-1">
                    <span>✓ Ativo</span>
                  </span>

                  <!-- Ações para o Perfil -->
                  <button 
                    v-if="podeEditarPerfil(perf)"
                    @click="iniciarEdicaoPerfil(perf)" 
                    class="text-indigo-600 hover:text-indigo-950 text-xs font-bold cursor-pointer px-1.5 py-1"
                  >
                    Editar
                  </button>
                  <button 
                    v-if="podeExcluirPerfil(perf)"
                    @click="excluirPerfil(perf)" 
                    class="text-red-600 hover:text-red-950 text-xs font-bold cursor-pointer px-1.5 py-1"
                  >
                    Excluir
                  </button>
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
              <p v-else-if="perfisStore.perfilAtivo.tipo === 'NENHUM' || perfisStore.perfilAtivo.tipo === 'OBSERVADOR'">
                <strong>NENHUM (Sem Perfil Atribuído):</strong> Possui acesso exclusivamente ao menu Perfis. Para ter acesso aos demais menus e funcionalidades do sistema, solicite a criação de usuário e vinculação a um perfil de acesso.
              </p>
              <p v-else>
                <strong>ESPECIALIDADE ({{ perfisStore.perfilAtivo.especialidade }}):</strong> Responsável por criar solicitações (inclusão, edição, exclusão, standby) apenas para a especialidade <strong>{{ perfisStore.perfilAtivo.especialidade }}</strong>. Visualiza no acompanhamento apenas as solicitações desta especialidade. Não pode aprovar/rejeitar registros. Tem permissão para criar usuários unicamente vinculados à sua própria especialidade.
              </p>
            </div>
          </Card>
        </div>

        <!-- Coluna Direita: Formulários de Criação (5 colunas) -->
        <div v-if="perfisStore.perfilAtivo.tipo !== 'NENHUM' && perfisStore.perfilAtivo.tipo !== 'OBSERVADOR' && perfisStore.perfilAtivo.tipo !== 'EPO_GENERALISTA'" class="lg:col-span-5 space-y-6">
          <!-- Formulário: Criar Novo Perfil / Editar Perfil -->
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
                    :disabled="!!editingUserId"
                    :class="{ 'bg-gray-100 cursor-not-allowed': !!editingUserId }"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="usr_nome" class="form-label font-semibold">Nome completo <span class="text-red-500">*</span></label>
                  <input 
                    id="usr_nome" 
                    v-model="usuarioForm.nome" 
                    type="text" 
                    placeholder="Ex: João Santos da Silva" 
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
                    :disabled="!!editingUserId || perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
                    :class="{ 'bg-gray-100 cursor-not-allowed': !!editingUserId || perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
                  >
                    <option value="" disabled>Selecione...</option>
                    <option v-for="perf in perfisFiltrados" :key="perf.id" :value="perf.id">
                      {{ perf.nome }} ({{ getTipoLabel(perf.tipo) }})
                    </option>
                  </select>
                  <p v-if="editingUserId" class="text-xs text-gray-500 mt-1 font-medium">O perfil de acesso não pode ser alterado durante a edição.</p>
                </div>

                <!-- Campo Função condicional -->
                <div v-if="exibirCampoFuncao" class="form-group">
                  <label for="usr_funcao" class="form-label font-semibold">Função <span class="text-red-500">*</span></label>
                  <select id="usr_funcao" v-model="usuarioForm.funcao" class="form-control" :required="exibirCampoFuncao">
                    <option value="" disabled>Selecione...</option>
                    <option value="Médico">Médico</option>
                    <option value="Residente">Residente</option>
                    <option value="Enfermeiro">Enfermeiro</option>
                    <option value="Administrativo">Administrativo</option>
                  </select>
                </div>

                <div class="flex flex-col space-y-2">
                  <Button type="submit" variant="primary" class="w-full justify-center">
                    {{ editingUserId ? 'Salvar Alterações' : (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' ? 'Solicitar Criação' : 'Criar Usuário') }}
                  </Button>
                  <Button v-if="editingUserId" type="button" variant="secondary" @click="cancelarEdicao" class="w-full justify-center">
                    Cancelar Edição
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
                      <p class="text-xs text-gray-500">{{ sol.username }}</p>
                    </div>
                    <div class="flex flex-col items-end space-y-1">
                      <span class="px-1.5 py-0.5 text-[9px] font-bold bg-amber-100 text-amber-800 border border-amber-200 rounded">
                        PENDENTE
                      </span>
                      <span :class="[sol.tipo === 'EXCLUSAO' ? 'bg-red-100 text-red-800 border border-red-200' : (sol.tipo === 'EDICAO' ? 'bg-purple-100 text-purple-800 border border-purple-200' : 'bg-blue-100 text-blue-800 border border-blue-200'), 'px-1.5 py-0.5 text-[9px] font-bold rounded']">
                        {{ sol.tipo === 'EXCLUSAO' ? 'Exclusão' : (sol.tipo === 'EDICAO' ? 'Edição' : 'Criação') }}
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

                    <div v-if="sol.tipo === 'EXCLUSAO'" class="mt-2 p-2 bg-red-50 border border-red-100 rounded text-red-950">
                      <p class="font-bold text-[10px] text-red-800 uppercase tracking-wider">Solicitação de Exclusão:</p>
                      <p class="text-[11px] mt-0.5 font-medium">Solicitada a exclusão do usuário {{ sol.nome }} ({{ sol.username }}).</p>
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

      <!-- Seção Inferior: Tabela de Usuários Cadastrados Localmente (100% Largura total, sem rolagem horizontal) -->
      <Card v-if="perfisStore.perfilAtivo.tipo !== 'NENHUM' && perfisStore.perfilAtivo.tipo !== 'OBSERVADOR'" class="w-full">
        <template #header>
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-bold text-gray-800">
              {{ editingUserId ? (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' ? 'Solicitar Edição de Usuário' : 'Editar Usuário') : 'Usuários Locais Cadastrados' }}
            </h2>
            <span class="text-xs font-semibold text-gray-600 bg-gray-100 px-3 py-1 rounded-full border border-gray-200">
              Total: {{ usuariosFiltrados.length }} cadastro(s)
            </span>
          </div>
        </template>

        <!-- Seção de Edição de Usuário -->
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
                placeholder="Ex: João Santos da Silva" 
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label for="edit_usr_perfil" class="form-label font-semibold">Perfil de Acesso <span class="text-red-500">*</span></label>
              <select 
                id="edit_usr_perfil" 
                v-model="usuarioForm.perfil_id" 
                class="form-control bg-gray-100 cursor-not-allowed" 
                required
                disabled
              >
                <option value="" disabled>Selecione...</option>
                <option v-for="perf in perfisStore.perfis" :key="perf.id" :value="perf.id">
                  {{ perf.nome }} ({{ getTipoLabel(perf.tipo) }})
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1 font-medium">O perfil de acesso não pode ser alterado durante a edição.</p>
            </div>

            <!-- Campo Função condicional -->
            <div v-if="exibirCampoFuncao" class="form-group">
              <label for="edit_usr_funcao" class="form-label font-semibold">Função <span class="text-red-500">*</span></label>
              <select id="edit_usr_funcao" v-model="usuarioForm.funcao" class="form-control" :required="exibirCampoFuncao">
                <option value="" disabled>Selecione...</option>
                <option value="Médico">Médico</option>
                <option value="Residente">Residente</option>
                <option value="Enfermeiro">Enfermeiro</option>
                <option value="Administrativo">Administrativo</option>
              </select>
            </div>

            <div class="flex space-x-2 pt-2">
              <Button type="submit" variant="primary" class="w-full justify-center">
                {{ perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' ? 'Solicitar Edição' : 'Salvar Alterações' }}
              </Button>
              <Button 
                type="button" 
                variant="secondary" 
                @click="cancelarEdicao" 
                class="w-full justify-center"
              >
                Cancelar Edição
              </Button>
            </div>
          </form>
        </div>

        <div v-else>
          <!-- Filtros de Usuários -->
          <div class="p-4 bg-gray-50 border-b border-gray-200 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="form-group">
              <label for="filtro_nome" class="text-xs font-semibold text-gray-500">Nome / Usuário Ebserh</label>
              <input 
                id="filtro_nome" 
                v-model="filtros.nome" 
                type="text" 
                placeholder="Filtrar por nome ou login..." 
                class="form-control text-xs w-full"
              />
            </div>

            <div class="form-group">
              <label for="filtro_perfil_id" class="text-xs font-semibold text-gray-500">Perfil ID</label>
              <select 
                id="filtro_perfil_id" 
                v-model="filtros.perfil_id" 
                class="form-control text-xs w-full"
                :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
                :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
              >
                <option value="">Todos</option>
                <option v-for="p in uniquePerfisIds" :key="p" :value="p">
                  {{ p }}
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
                <option value="Administrativo">Administrativo</option>
              </select>
            </div>
          </div>

          <div v-if="usuariosFiltrados.length === 0" class="text-center py-8 text-gray-500 text-sm">
            Nenhum usuário correspondente aos filtros.
          </div>
          <div v-else class="w-full overflow-x-auto max-h-[calc(100vh-320px)] overflow-y-auto border border-gray-100 rounded-lg">
            <table class="w-full table-auto divide-y divide-gray-200 border-separate border-spacing-0">
              <thead class="bg-gray-50 sticky top-0 z-10 shadow-sm">
                <tr>
                  <th scope="col" class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-1/4 border-b border-gray-200">Nome / Usuário Ebserh</th>
                  <th scope="col" class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-1/6 border-b border-gray-200">Perfil ID</th>
                  <th scope="col" class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-1/6 border-b border-gray-200">Especialidade</th>
                  <th scope="col" class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-1/6 border-b border-gray-200">Função</th>
                  <th scope="col" class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider w-1/6 border-b border-gray-200">Categorização</th>
                  <th scope="col" class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-right text-xs font-bold text-gray-600 uppercase tracking-wider w-1/6 border-b border-gray-200">Ações</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200 text-sm">
                <tr v-for="user in usuariosFiltrados" :key="user.id" class="hover:bg-gray-50/80 transition-colors">
                  <td class="px-4 py-3">
                    <div class="font-bold text-gray-900 leading-snug">{{ user.nome }}</div>
                    <div class="text-xs text-gray-500 font-mono">{{ user.username }}</div>
                  </td>
                  <td class="px-4 py-3">
                    <span class="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-800 border border-gray-200 inline-block">
                      {{ user.perfil_id }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-gray-700 font-medium">
                    {{ user.especialidade || '—' }}
                  </td>
                  <td class="px-4 py-3 text-gray-700">
                    {{ user.funcao || '—' }}
                  </td>
                  <td class="px-4 py-3 text-center">
                    <!-- Usuário com Categorização Cadastrada -->
                    <div 
                      v-if="obterCategorizacaoDoUsuario(user) && obterCategorizacaoDoUsuario(user).categorias?.length" 
                      class="flex items-center justify-center gap-1.5 flex-wrap"
                    >
                      <span 
                        v-for="catNome in obterCategorizacaoDoUsuario(user).categorias" 
                        :key="catNome"
                        class="inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-2xs"
                      >
                        🏷️ {{ catNome }}
                      </span>
                      <button
                        v-if="podeGerenciarCategorizacao"
                        type="button"
                        @click="abrirModalCategorizacao(user)"
                        class="p-1 text-indigo-600 hover:text-indigo-900 hover:bg-indigo-100 rounded transition cursor-pointer"
                        title="Gerenciar categorias deste médico"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                    </div>

                    <!-- Usuário sem Categorização, mas quem visualiza pode criar (ADMIN ou GESTÃO LEC) -->
                    <div v-else-if="podeGerenciarCategorizacao && user.funcao === 'Médico' && user.especialidade">
                      <button
                        type="button"
                        @click="abrirModalCategorizacao(user)"
                        class="px-2.5 py-1 text-xs font-medium rounded-lg bg-gray-50 hover:bg-indigo-50 text-gray-600 hover:text-indigo-700 border border-dashed border-gray-300 hover:border-indigo-300 transition cursor-pointer inline-flex items-center space-x-1"
                        title="Clique para criar categorização para este médico"
                      >
                        <span>+ Criar</span>
                      </button>
                    </div>

                    <!-- Sem Categorização (Usuários de Especialidades ou Funções sem categorização) -->
                    <span v-else class="text-xs text-gray-400">—</span>
                  </td>
                  <td class="px-4 py-3 text-right text-sm font-medium whitespace-nowrap">
                    <button 
                      v-if="podeEditarUsuario(user)"
                      @click="iniciarEdicao(user)" 
                      class="text-indigo-600 hover:text-indigo-900 font-semibold cursor-pointer mr-3 inline-flex items-center"
                    >
                      Editar usuário
                    </button>
                    <button 
                      v-if="podeExcluirUsuario(user)"
                      @click="excluirUsuario(user)" 
                      class="text-red-600 hover:text-red-900 font-semibold cursor-pointer inline-flex items-center"
                    >
                      Excluir usuário
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

    <!-- Modal de Gerenciamento de Categorização do Profissional -->
    <div 
      v-if="modalCategorizacao.aberto && podeGerenciarCategorizacao" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto"
      @click.self="fecharModalCategorizacao"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full border border-gray-100 overflow-hidden flex flex-col max-h-[90vh] my-auto">
        <!-- Cabeçalho do Modal -->
        <div class="px-6 py-4 bg-slate-50 border-b border-gray-200 flex justify-between items-center shrink-0">
          <div>
            <span class="text-xs font-mono text-indigo-600 font-bold uppercase tracking-wider block">Gestão de Categorização do Profissional</span>
            <h2 class="text-xl font-black text-slate-900 mt-0.5 flex items-center space-x-2">
              <span class="text-indigo-950">{{ modalCategorizacao.medico }}</span>
              <span class="text-xs font-semibold bg-indigo-100 text-indigo-800 px-2.5 py-0.5 rounded-full border border-indigo-200">
                {{ modalCategorizacao.especialidade }}
              </span>
            </h2>
          </div>
          <button 
            @click="fecharModalCategorizacao"
            class="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg transition hover:bg-gray-200/60"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Corpo do Modal -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1 bg-slate-50/50">
          
          <!-- Diálogo de Confirmação: Exclusão de Item Individual -->
          <div v-if="modalCategorizacao.confirmandoExclusaoItem" class="p-4 bg-red-50 border border-red-200 rounded-xl space-y-3">
            <div class="flex items-start space-x-2.5 text-red-800">
              <span class="text-lg">⚠️</span>
              <div class="text-xs leading-relaxed">
                <p class="font-bold text-sm text-red-900">Confirmar exclusão da categoria?</p>
                <p class="mt-1">
                  A exclusão da categoria <strong class="underline">{{ modalCategorizacao.confirmandoExclusaoItem.nome }}</strong> removerá essa categorização de <strong>todos os procedimentos vinculados a este médico nesta especialidade</strong>.
                </p>
              </div>
            </div>
            <div class="flex justify-end space-x-2 pt-1">
              <button 
                type="button" 
                @click="modalCategorizacao.confirmandoExclusaoItem = null" 
                class="px-3 py-1.5 text-xs font-semibold bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 cursor-pointer"
              >
                Cancelar
              </button>
              <button 
                type="button" 
                @click="confirmarExclusaoItem" 
                class="px-3 py-1.5 text-xs font-bold bg-red-600 hover:bg-red-700 text-white rounded-lg cursor-pointer"
              >
                Sim, Excluir Categoria
              </button>
            </div>
          </div>

          <!-- Diálogo de Confirmação: Exclusão Total da Categorização -->
          <div v-if="modalCategorizacao.confirmandoExclusaoTotal" class="p-4 bg-red-50 border border-red-200 rounded-xl space-y-3">
            <div class="flex items-start space-x-2.5 text-red-800">
              <span class="text-lg">⚠️</span>
              <div class="text-xs leading-relaxed">
                <p class="font-bold text-sm text-red-900">Excluir TODA a categorização deste médico?</p>
                <p class="mt-1">
                  Esta ação removerá todas as categorias cadastradas e desvinculará a categorização de <strong>todos os procedimentos</strong> deste médico na especialidade <strong>{{ modalCategorizacao.especialidade }}</strong>.
                </p>
              </div>
            </div>
            <div class="flex justify-end space-x-2 pt-1">
              <button 
                type="button" 
                @click="modalCategorizacao.confirmandoExclusaoTotal = false" 
                class="px-3 py-1.5 text-xs font-semibold bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 cursor-pointer"
              >
                Cancelar
              </button>
              <button 
                type="button" 
                @click="confirmarExclusaoTotal" 
                class="px-3 py-1.5 text-xs font-bold bg-red-600 hover:bg-red-700 text-white rounded-lg cursor-pointer"
              >
                Sim, Excluir Tudo
              </button>
            </div>
          </div>

          <!-- Formulário para Adicionar Nova Categoria -->
          <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm space-y-3">
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-600">Adicionar Nova Categoria</h3>
            <div class="flex space-x-2">
              <input 
                v-model="modalCategorizacao.novaCategoriaInput"
                type="text" 
                placeholder="Ex: Prioridade 1, Eletiva Simples, Complexa..." 
                class="form-control text-sm flex-1"
                @keyup.enter.prevent="adicionarCategoria"
              />
              <Button 
                type="button" 
                variant="primary" 
                size="sm" 
                @click="adicionarCategoria" 
                class="px-4 shrink-0"
              >
                + Adicionar
              </Button>
            </div>
          </div>

          <!-- Lista de Categorias Atuais -->
          <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm space-y-3">
            <div class="flex justify-between items-center border-b pb-2 border-gray-100">
              <h3 class="text-xs font-bold uppercase tracking-wider text-gray-600">
                Categorias Configuradas ({{ modalCategorizacao.categorias.length }})
              </h3>
              <span class="text-[11px] text-gray-400">Você pode renomear os nomes diretamente nos campos abaixo</span>
            </div>

            <div v-if="modalCategorizacao.categorias.length === 0" class="text-center py-6 text-gray-400 text-xs italic">
              Nenhuma categoria adicionada ainda. Utilize o campo acima para adicionar categorias.
            </div>

            <div v-else class="space-y-2.5 max-h-[250px] overflow-y-auto pr-1">
              <div 
                v-for="(cat, idx) in modalCategorizacao.categorias" 
                :key="cat.id" 
                class="flex items-center space-x-2 bg-slate-50 p-2 rounded-lg border border-slate-200 hover:border-indigo-200 transition"
              >
                <span class="text-xs font-bold text-gray-400 w-5 text-center">{{ idx + 1 }}.</span>
                <div class="flex-1 relative">
                  <input 
                    v-model="cat.nomeAtual" 
                    type="text" 
                    class="w-full text-xs font-semibold text-gray-800 bg-white border border-gray-300 rounded px-2.5 py-1.5 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    placeholder="Nome da categoria"
                  />
                  <span 
                    v-if="cat.nomeOriginal && cat.nomeOriginal !== cat.nomeAtual" 
                    class="text-[10px] text-indigo-600 font-bold mt-0.5 block"
                  >
                    Renomeando de: "{{ cat.nomeOriginal }}" (procedimentos existentes serão atualizados)
                  </span>
                </div>
                <button 
                  type="button" 
                  @click="solicitarExclusaoItem(cat, idx)"
                  class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition cursor-pointer"
                  title="Excluir esta categoria"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

        </div>

        <!-- Rodapé do Modal -->
        <div class="px-6 py-4 bg-gray-100 border-t border-gray-200 flex justify-between items-center shrink-0">
          <div>
            <button 
              v-if="modalCategorizacao.categorizacaoId"
              type="button" 
              @click="modalCategorizacao.confirmandoExclusaoTotal = true" 
              class="text-xs font-bold text-red-600 hover:text-red-800 hover:underline cursor-pointer"
            >
              🗑️ Excluir Toda a Categorização
            </button>
          </div>
          <div class="flex space-x-2">
            <Button @click="fecharModalCategorizacao" variant="secondary">
              Cancelar
            </Button>
            <Button 
              @click="salvarModalCategorizacao" 
              variant="primary"
              :disabled="modalCategorizacao.salvando"
            >
              {{ modalCategorizacao.salvando ? 'Salvando...' : 'Salvar Categorização' }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { usePerfisStore } from '../stores/perfis';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';

const toast = useToast();
const perfisStore = usePerfisStore();
const authStore = useAuthStore();

const usuarios = ref<any[]>([]);
const solicitacoes = ref<any[]>([]);
const activeTab = ref('criar');
const editingUserId = ref<number | null>(null);
const editingPerfilId = ref<string | null>(null);

// Filtros da tabela
const filtros = ref({
  nome: '',
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

// Permite ativar perfil se for ADMIN ou se o usuário logado possui vínculo com o perfil
const podeAtivarPerfil = (perf: any) => {
  if (perfisStore.perfilAtivoId === perf.id) return false;
  if (authStore.isAdmin) return true;
  return perfisStore.perfisDoUsuario.some(p => p.id === perf.id);
};

// Ordenação customizada de Perfis: 1) ADMIN, 2) GESTÃO LEC, 3) ESPECIALIDADES CIRÚRGICAS (alfabética)
const perfisOrdenados = computed(() => {
  return [...perfisStore.perfis].sort((a, b) => {
    const getPeso = (p: any) => {
      if (p.tipo === 'ADMIN') return 1;
      if (p.tipo === 'GESTAO_LEC') return 2;
      if (p.tipo === 'EPO_GENERALISTA' || p.id === 'EPO_GENERALISTA') return 3;
      if (p.tipo === 'ESPECIALIDADE') return 4;
      if (p.tipo === 'NENHUM' || p.tipo === 'OBSERVADOR') return 5;
      return 6;
    };
    const pesoA = getPeso(a);
    const pesoB = getPeso(b);
    if (pesoA !== pesoB) return pesoA - pesoB;

    const nomeA = (a.especialidade || a.nome || '').trim();
    const nomeB = (b.especialidade || b.nome || '').trim();
    return nomeA.localeCompare(nomeB, 'pt-BR');
  });
});

// Dropdown dinâmico de perfis para criação de usuário conforme regras hierárquicas
const perfisFiltrados = computed(() => {
  const tipo = perfisStore.perfilAtivo.tipo;
  const esp = perfisStore.perfilAtivo.especialidade;
  const base = perfisOrdenados.value.filter(p => p.tipo !== 'NENHUM' && p.id !== 'NENHUM' && p.tipo !== 'OBSERVADOR' && p.id !== 'OBSERVADOR');

  if (tipo === 'ADMIN') {
    return base;
  } else if (tipo === 'GESTAO_LEC') {
    return base.filter(p => p.tipo === 'GESTAO_LEC' || p.tipo === 'ESPECIALIDADE');
  } else if (tipo === 'ESPECIALIDADE' && esp) {
    return base.filter(p => p.tipo === 'ESPECIALIDADE' && p.especialidade === esp);
  }
  return [];
});

const exibirCampoFuncao = computed(() => {
  const selectedPerfil = perfisStore.perfis.find(p => p.id === usuarioForm.value.perfil_id);
  return selectedPerfil?.tipo === 'ESPECIALIDADE';
});

const uniquePerfisIds = computed(() => {
  return perfisOrdenados.value.map(p => p.id);
});

// Tabela filtrada e ordenada: 1) ADMIN, 2) GESTÃO LEC, 3) Especialidades (alfabética) e Usuários (alfabética)
const usuariosFiltrados = computed(() => {
  const lista = usuarios.value.filter(user => {
    // Filtro obrigatório para perfil ESPECIALIDADE
    if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE') {
      if (user.especialidade !== perfisStore.perfilAtivo.especialidade) {
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

    if (filtros.value.perfil_id) {
      const target = filtros.value.perfil_id.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      const userPerfId = (user.perfil_id || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      const userEsp = (user.especialidade || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      
      const perfObj = perfisStore.perfis.find(p => p.id === user.perfil_id);
      const perfNome = (perfObj?.nome || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

      if (userPerfId !== target && userEsp !== target && perfNome !== target) {
        return false;
      }
    }

    return true;
  });

  return lista.sort((a, b) => {
    const perfA = perfisStore.perfis.find(p => p.id === a.perfil_id) || { tipo: 'ESPECIALIDADE', especialidade: a.especialidade || '' };
    const perfB = perfisStore.perfis.find(p => p.id === b.perfil_id) || { tipo: 'ESPECIALIDADE', especialidade: b.especialidade || '' };

    const getPeso = (p: any) => {
      if (p.tipo === 'ADMIN') return 1;
      if (p.tipo === 'GESTAO_LEC') return 2;
      if (p.tipo === 'ESPECIALIDADE') return 3;
      if (p.tipo === 'OBSERVADOR') return 4;
      return 5;
    };

    const pesoA = getPeso(perfA);
    const pesoB = getPeso(perfB);

    if (pesoA !== pesoB) return pesoA - pesoB;

    // Se ambos forem ADMIN ou GESTÃO LEC, ordena por nome do usuário
    if (pesoA === 1 || pesoA === 2) {
      return (a.nome || '').localeCompare(b.nome || '', 'pt-BR');
    }

    // Se forem de especialidades, ordena primeiro por especialidade (alfabética)
    const espA = (a.especialidade || perfA.especialidade || '').trim();
    const espB = (b.especialidade || perfB.especialidade || '').trim();
    const diffEsp = espA.localeCompare(espB, 'pt-BR');
    if (diffEsp !== 0) return diffEsp;

    // Dentro da mesma especialidade, ordena por nome do usuário (alfabética)
    return (a.nome || '').localeCompare(b.nome || '', 'pt-BR');
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

const alterarPerfilAtivo = async (id: string) => {
  await perfisStore.setPerfilAtivo(id);
  toast.success('Perfil de utilização alterado!');
  cancelarEdicao();
  await loadSolicitacoes();
  await loadUsuarios();
};

const podeEditarPerfil = (perf: any) => {
  if (perf.tipo !== 'ESPECIALIDADE') return false;
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  return tipoAtivo === 'ADMIN' || tipoAtivo === 'GESTAO_LEC';
};

const podeExcluirPerfil = (perf: any) => {
  if (perf.tipo !== 'ESPECIALIDADE') return false;
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  return tipoAtivo === 'ADMIN' || tipoAtivo === 'GESTAO_LEC';
};

const isUsuarioEspecialidade = (user: any): boolean => {
  if (user.especialidade) return true;
  if (user.funcao) return true;
  const perf = perfisStore.perfis.find(p => p.id === user.perfil_id || p.id.toLowerCase() === (user.perfil_id || '').toLowerCase());
  return perf ? perf.tipo === 'ESPECIALIDADE' : (user.perfil_id !== 'ADMIN' && user.perfil_id !== 'GESTAO_LEC');
};

const podeEditarUsuario = (user: any) => {
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  const espAtivo = perfisStore.perfilAtivo.especialidade;

  if (tipoAtivo === 'OBSERVADOR' || tipoAtivo === 'NENHUM' || tipoAtivo === 'EPO_GENERALISTA') {
    return false;
  }
  if (tipoAtivo === 'ADMIN') {
    return true;
  }
  if (tipoAtivo === 'GESTAO_LEC') {
    return isUsuarioEspecialidade(user);
  }
  if (tipoAtivo === 'ESPECIALIDADE') {
    return user.especialidade === espAtivo;
  }
  return false;
};

const podeExcluirUsuario = (user: any) => {
  const tipoAtivo = perfisStore.perfilAtivo.tipo;
  const espAtivo = perfisStore.perfilAtivo.especialidade;

  if (tipoAtivo === 'OBSERVADOR' || tipoAtivo === 'NENHUM' || tipoAtivo === 'EPO_GENERALISTA') {
    return false;
  }
  if (tipoAtivo === 'ADMIN') {
    return true;
  }
  if (tipoAtivo === 'GESTAO_LEC') {
    return isUsuarioEspecialidade(user);
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
    const nomeEspecialidade = perfilForm.value.tipo === 'ESPECIALIDADE' 
      ? perfilForm.value.especialidade.trim().toUpperCase() 
      : undefined;

    if (editingPerfilId.value) {
      await api.put(`/api/perfis/${editingPerfilId.value}`, {
        nome: nomePerfil,
        especialidade: nomeEspecialidade
      });
      toast.success('Perfil atualizado com sucesso!');
    } else {
      await perfisStore.adicionarPerfil(
        nomePerfil,
        nomeEspecialidade
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
  usuarioForm.value.funcao = user.funcao || '';
  
  // Tenta encontrar o perfil exato pelo ID ou pela especialidade/nome
  const matchingPerfil = perfisStore.perfis.find(p => 
    p.id === user.perfil_id || 
    (p.especialidade && user.especialidade && p.especialidade.toLowerCase() === user.especialidade.toLowerCase()) ||
    (p.nome && user.perfil_id && p.nome.toLowerCase() === user.perfil_id.toLowerCase())
  );

  usuarioForm.value.perfil_id = matchingPerfil ? matchingPerfil.id : user.perfil_id;
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

const excluirUsuario = async (user: any) => {
  const tipoAtivo = perfisStore.perfilAtivo.tipo;

  if (tipoAtivo === 'EPO_GENERALISTA' || tipoAtivo === 'NENHUM' || tipoAtivo === 'OBSERVADOR') {
    return;
  }

  if (tipoAtivo === 'ESPECIALIDADE') {
    if (!confirm(`Tem certeza que deseja solicitar a exclusão do usuário "${user.nome}"?`)) {
      return;
    }
    try {
      await api.post('/api/usuarios/solicitacoes', {
        tipo: 'EXCLUSAO',
        user_id: user.id,
        username: user.username,
        nome: user.nome,
        perfil_id: user.perfil_id,
        funcao: user.funcao
      });
      toast.success('Solicitação de exclusão de usuário enviada com sucesso!');
      if (editingUserId.value === user.id) {
        cancelarEdicao();
      }
      await loadUsuarios();
      await loadSolicitacoes();
    } catch (error: any) {
      const detail = error.response?.data?.detail || 'Erro ao solicitar exclusão de usuário.';
      toast.error(detail);
    }
  } else {
    if (!confirm(`Tem certeza que deseja excluir o usuário "${user.nome}"?`)) {
      return;
    }
    try {
      await api.delete(`/api/usuarios/${user.id}`);
      toast.success('Usuário excluído com sucesso!');
      if (editingUserId.value === user.id) {
        cancelarEdicao();
      }
      await loadUsuarios();
      await loadSolicitacoes();
    } catch (error: any) {
      const detail = error.response?.data?.detail || 'Erro ao excluir usuário.';
      toast.error(detail);
    }
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
    await loadUsuarios();
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
    case 'EPO_GENERALISTA': return 'bg-orange-500 ring-orange-500';
    case 'ESPECIALIDADE': return 'bg-green-500 ring-green-500';
    case 'NENHUM':
    case 'OBSERVADOR': return 'bg-white ring-gray-300 border border-gray-300';
    default: return 'bg-gray-400 ring-gray-400';
  }
};

const getTipoLabel = (tipo: string) => {
  switch (tipo) {
    case 'ADMIN': return 'ADMIN';
    case 'GESTAO_LEC': return 'Gestão da LEC';
    case 'EPO_GENERALISTA': return 'EPO Generalista';
    case 'ESPECIALIDADE': return 'Especialidade Cirúrgica';
    case 'NENHUM':
    case 'OBSERVADOR': return 'Nenhum';
    default: return tipo;
  }
};

// ==================== GESTÃO DE CATEGORIZAÇÃO DO PROFISSIONAL ====================
const podeGerenciarCategorizacao = computed(() => {
  const tipo = perfisStore.perfilAtivo.tipo;
  const nome = perfisStore.perfilAtivo.nome;
  return tipo === 'ADMIN' || tipo === 'GESTAO_LEC' || nome === 'Gestão LEC' || nome === 'GESTAO_LEC';
});

const categorizacoes = ref<any[]>([]);

const loadCategorizacoes = async () => {
  try {
    const { data } = await api.get('/api/categorizacoes-profissionais');
    categorizacoes.value = data;
  } catch (error) {
    console.error('Erro ao carregar categorizacoes', error);
  }
};

const obterCategorizacaoDoUsuario = (user: any) => {
  if (!user.especialidade) return null;
  const userNome = (user.nome || '').trim().toUpperCase();
  const userUsername = (user.username || '').trim().toUpperCase();
  const espNorm = (user.especialidade || '').trim().toUpperCase();

  return categorizacoes.value.find(c => 
    c.especialidade === espNorm && (c.medico === userNome || c.medico === userUsername)
  );
};

const modalCategorizacao = ref({
  aberto: false,
  salvando: false,
  usuario: null as any,
  categorizacaoId: null as number | null,
  medico: '',
  especialidade: '',
  novaCategoriaInput: '',
  categorias: [] as { id: string; nomeOriginal: string; nomeAtual: string }[],
  confirmandoExclusaoItem: null as { nome: string; index: number } | null,
  confirmandoExclusaoTotal: false
});

const abrirModalCategorizacao = (user: any) => {
  if (!podeGerenciarCategorizacao.value) return;
  const userNome = user.nome || user.username;
  const esp = user.especialidade || '';
  const existing = obterCategorizacaoDoUsuario(user);

  modalCategorizacao.value.usuario = user;
  modalCategorizacao.value.medico = userNome;
  modalCategorizacao.value.especialidade = esp;
  modalCategorizacao.value.novaCategoriaInput = '';
  modalCategorizacao.value.confirmandoExclusaoItem = null;
  modalCategorizacao.value.confirmandoExclusaoTotal = false;

  if (existing) {
    modalCategorizacao.value.categorizacaoId = existing.id;
    modalCategorizacao.value.categorias = (existing.categorias || []).map((c: string, i: number) => ({
      id: `${i}-${Date.now()}-${Math.random()}`,
      nomeOriginal: c,
      nomeAtual: c
    }));
  } else {
    modalCategorizacao.value.categorizacaoId = null;
    modalCategorizacao.value.categorias = [];
  }

  modalCategorizacao.value.aberto = true;
};

const fecharModalCategorizacao = () => {
  modalCategorizacao.value.aberto = false;
  modalCategorizacao.value.confirmandoExclusaoItem = null;
  modalCategorizacao.value.confirmandoExclusaoTotal = false;
};

const adicionarCategoria = () => {
  const nome = modalCategorizacao.value.novaCategoriaInput.trim();
  if (!nome) return;

  const exists = modalCategorizacao.value.categorias.some(
    c => c.nomeAtual.toLowerCase().trim() === nome.toLowerCase()
  );
  if (exists) {
    toast.warning('Já existe uma categoria com este nome na lista.');
    return;
  }

  modalCategorizacao.value.categorias.push({
    id: `new-${Date.now()}-${Math.random()}`,
    nomeOriginal: '',
    nomeAtual: nome
  });
  modalCategorizacao.value.novaCategoriaInput = '';
};

const solicitarExclusaoItem = (cat: { id: string; nomeOriginal: string; nomeAtual: string }, index: number) => {
  if (cat.nomeOriginal) {
    modalCategorizacao.value.confirmandoExclusaoItem = {
      nome: cat.nomeOriginal,
      index
    };
  } else {
    modalCategorizacao.value.categorias.splice(index, 1);
  }
};

const confirmarExclusaoItem = () => {
  if (modalCategorizacao.value.confirmandoExclusaoItem) {
    const idx = modalCategorizacao.value.confirmandoExclusaoItem.index;
    modalCategorizacao.value.categorias.splice(idx, 1);
    modalCategorizacao.value.confirmandoExclusaoItem = null;
  }
};

const confirmarExclusaoTotal = async () => {
  if (!modalCategorizacao.value.categorizacaoId) {
    modalCategorizacao.value.categorias = [];
    fecharModalCategorizacao();
    return;
  }

  modalCategorizacao.value.salvando = true;
  try {
    await api.delete(`/api/categorizacoes-profissionais/${modalCategorizacao.value.categorizacaoId}`);
    toast.success('Categorização excluída com sucesso! Os procedimentos vinculados foram desvinculados.');
    await loadCategorizacoes();
    fecharModalCategorizacao();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao excluir categorização.';
    toast.error(detail);
  } finally {
    modalCategorizacao.value.salvando = false;
  }
};

const salvarModalCategorizacao = async () => {
  const cleanCats = modalCategorizacao.value.categorias
    .map(c => c.nomeAtual.trim())
    .filter(c => c.length > 0);

  if (cleanCats.length === 0) {
    toast.warning('Adicione ao menos uma categoria válida ou utilize a exclusão total.');
    return;
  }

  const renomeacoes: Record<string, string> = {};
  for (const c of modalCategorizacao.value.categorias) {
    if (c.nomeOriginal && c.nomeAtual.trim() && c.nomeOriginal !== c.nomeAtual.trim()) {
      renomeacoes[c.nomeOriginal] = c.nomeAtual.trim();
    }
  }

  modalCategorizacao.value.salvando = true;
  try {
    if (modalCategorizacao.value.categorizacaoId) {
      await api.put(`/api/categorizacoes-profissionais/${modalCategorizacao.value.categorizacaoId}`, {
        categorias: cleanCats,
        renomeacoes
      });
      toast.success('Categorização atualizada com sucesso!');
    } else {
      await api.post('/api/categorizacoes-profissionais', {
        medico: modalCategorizacao.value.medico,
        especialidade: modalCategorizacao.value.especialidade,
        categorias: cleanCats
      });
      toast.success('Categorização criada com sucesso!');
    }
    await loadCategorizacoes();
    fecharModalCategorizacao();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao salvar categorização.';
    toast.error(detail);
  } finally {
    modalCategorizacao.value.salvando = false;
  }
};

// Monitora o perfil ativo para aplicar o filtro mandatório e definir perfil_id padrão no form (se não estiver editando)
watch(() => perfisStore.perfilAtivo, (newPerfil) => {
  if (newPerfil.tipo === 'ESPECIALIDADE') {
    filtros.value.perfil_id = newPerfil.id;
    if (!editingUserId.value) {
      usuarioForm.value.perfil_id = newPerfil.id;
    }
  } else {
    filtros.value.perfil_id = '';
    if (!editingUserId.value) {
      usuarioForm.value.perfil_id = '';
    }
  }
}, { immediate: true });

onMounted(async () => {
  await perfisStore.fetchPerfis();
  await loadUsuarios();
  await loadSolicitacoes();
  await loadCategorizacoes();
});
</script>
