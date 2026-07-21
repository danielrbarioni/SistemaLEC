<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-800">Interações com o Sistema LEC da Rede HU Brasil</h1>
      <span class="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">Assistencial → Gestão da LEC</span>
    </div>

    <!-- Formulário e Abas de Solicitação Unidos -->
    <Card v-if="perfisStore.perfilAtivo.tipo !== 'GESTAO_LEC'" class="overflow-hidden">
      <template #header>
        <div class="flex justify-between items-center w-full">
          <div class="flex items-center space-x-3">
            <h2 class="text-lg font-bold text-gray-800">Nova Solicitação de {{ tipoSolicitacaoNome }}</h2>
            <span class="px-2.5 py-0.5 bg-green-100 text-green-800 text-xs font-semibold rounded">ESPECIALIDADE</span>
          </div>
          <span class="text-xs text-gray-500">HC-UFPE</span>
        </div>
      </template>

      <!-- Abas de Solicitação integradas ao Card -->
      <div class="flex border-b border-gray-200 bg-gray-50 p-2 overflow-x-auto -mt-6 -mx-6 mb-6">
        <button 
          v-for="aba in abas" 
          :key="aba.id" 
          @click="selecionarAba(aba.id)"
          :class="[
            'flex-1 py-2.5 text-sm font-semibold rounded-md transition duration-200 whitespace-nowrap px-4',
            abaAtiva === aba.id 
              ? 'bg-paper-sidebar text-white shadow-sm' 
              : 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'
          ]"
        >
          <span class="flex items-center justify-center space-x-2">
            <component :is="aba.icon" class="h-4 w-4" />
            <span>{{ aba.nome }}</span>
          </span>
        </button>
      </div>

      <!-- Alerta indicando a origem dos dados quando buscados na Sede -->
      <div v-if="abaAtiva !== 'INSERIR' && formCarregadoDaSede" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-xs text-green-800 flex items-center space-x-2">
        <span>✅ Dados da solicitação ativa carregados com sucesso do <strong>Sistema LEC Sede</strong>.</span>
      </div>

      <form @submit.prevent="enviarSolicitacao" class="space-y-5">

        <!-- Linha de Busca/Identificação do Paciente -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-group">
            <label for="codigo_paciente" class="form-label font-semibold">Nº Prontuário <span class="text-red-500">*</span></label>
            <div class="flex space-x-2">
              <input 
                id="codigo_paciente" 
                v-model="form.codigo_paciente" 
                type="text" 
                placeholder="Prontuário" 
                class="form-control"
                required
              />
              <Button type="button" @click="buscarDados" :disabled="loadingBusca" variant="info" class="whitespace-nowrap">
                {{ loadingBusca ? '...' : 'Buscar' }}
              </Button>
            </div>
            <p class="text-xs text-gray-400 mt-1">
              {{ abaAtiva === 'INSERIR' ? 'Busca dados no AGHU' : 'Puxa dados do módulo Pacientes' }}
            </p>
          </div>

          <div class="form-group md:col-span-2">
            <label for="nome_paciente" class="form-label font-semibold">Nome Completo do Paciente <span class="text-red-500">*</span></label>
            <input 
              id="nome_paciente" 
              v-model="form.nome_paciente" 
              type="text" 
              placeholder="Preenchido automaticamente ao buscar prontuário..." 
              class="form-control bg-gray-100 cursor-not-allowed opacity-75"
              required
              disabled
            />
            <p class="text-xs text-gray-400 mt-1">Importado automaticamente do prontuário</p>
          </div>
        </div>

        <!-- Dados Cadastrais Adicionais (Data de Nascimento e Nome da Mãe) -->
        <div v-if="form.nome_paciente" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-group">
            <label class="form-label font-semibold">Data de Nascimento</label>
            <input
              type="text"
              :value="formatarData(form.dt_nascimento)"
              class="form-control bg-gray-100 cursor-not-allowed opacity-75"
              disabled
            />
          </div>
          <div class="form-group md:col-span-2">
            <label class="form-label font-semibold">Nome da Mãe</label>
            <input
              type="text"
              :value="form.nome_mae || '—'"
              class="form-control bg-gray-100 cursor-not-allowed opacity-75"
              disabled
            />
          </div>
        </div>
        <!-- Seleção de Procedimento (quando há múltiplos) -->
        <div v-if="abaAtiva !== 'INSERIR' && procedimentosPaciente.length > 1" class="p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <label class="form-label font-semibold text-amber-800">
            Qual procedimento deseja {{ abaAtiva === 'EDITAR' ? 'editar' : abaAtiva === 'EXCLUIR' ? 'excluir' : 'colocar em standby' }}?
          </label>
          <div class="mt-2 space-y-2">
            <label 
              v-for="(proc, idx) in procedimentosPaciente" 
              :key="idx" 
              class="flex items-center space-x-3 p-3 bg-white rounded-lg border border-amber-200 cursor-pointer hover:bg-amber-50 transition"
              :class="{ 'border-amber-500 bg-amber-50 ring-1 ring-amber-400': procedimentoSelecionadoParaEdicao === idx }"
            >
              <input 
                type="radio" 
                :value="idx" 
                v-model="procedimentoSelecionadoParaEdicao"
                class="h-4 w-4 text-amber-600"
                @change="preencherCamposDoProc(proc)"
              />
              <div class="text-sm">
                <div class="font-semibold text-gray-800">{{ proc.procedimento }}</div>
                <div class="text-xs text-gray-500">{{ proc.especialidade }} · Swalis: {{ proc.swallis || '—' }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- Linha 2: Especialidade + Procedimento (Fila) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="especialidade" class="form-label font-semibold">Especialidade <span class="text-red-500">*</span></label>
            <select
              id="especialidade"
              v-model="form.especialidade"
              class="form-control"
              :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': isEspecialidadeDisabled }"
              required
              @change="form.procedimento = ''"
              :disabled="isEspecialidadeDisabled"
            >
              <option value="" disabled>Selecione a especialidade...</option>
              <option v-for="esp in especialidades" :key="esp.nome" :value="esp.nome">
                {{ esp.nome }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label font-semibold">Procedimento (Fila de Espera) <span class="text-red-500">*</span></label>
            
            <!-- Mostra o procedimento originalmente cadastrado (como desabilitado) se não for INSERIR -->
            <div v-if="abaAtiva !== 'INSERIR'" class="mb-3">
              <input
                type="text"
                :value="form.procedimento_anterior || form.procedimento"
                class="form-control bg-gray-100 cursor-not-allowed opacity-75"
                disabled
              />
            </div>

            <!-- Pergunta Sim/Não se deseja alterar o procedimento (apenas na aba EDITAR se tiver paciente carregado) -->
            <div v-if="abaAtiva === 'EDITAR' && form.codigo_paciente" class="mb-3">
              <label class="block text-xs font-semibold text-gray-700 mb-1">
                Deseja alterar o Procedimento (Fila de Espera)?
              </label>
              <div class="flex items-center space-x-6 p-2.5 border border-gray-200 rounded-lg bg-gray-50 w-full md:w-1/2">
                <label class="flex items-center space-x-2 cursor-pointer select-none">
                  <input
                    type="radio"
                    name="desejaAlterar"
                    value="Sim"
                    v-model="desejaAlterarProcedimento"
                    class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500 cursor-pointer"
                  />
                  <span class="text-sm font-semibold text-gray-700">Sim</span>
                </label>
                <label class="flex items-center space-x-2 cursor-pointer select-none">
                  <input
                    type="radio"
                    name="desejaAlterar"
                    value="Não"
                    v-model="desejaAlterarProcedimento"
                    class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500 cursor-pointer"
                  />
                  <span class="text-sm font-semibold text-gray-700">Não</span>
                </label>
              </div>
            </div>

            <!-- Custom Searchable Dropdown de procedimento (Apenas na inclusão ou se o usuário selecionou Sim na edição) -->
            <div v-if="abaAtiva === 'INSERIR' || (abaAtiva === 'EDITAR' && desejaAlterarProcedimento === 'Sim')" class="relative">
              <input
                id="procedimento"
                type="text"
                v-model="form.procedimento"
                @focus="dropdownAberto = true"
                @blur="dropdownAberto = false"
                :placeholder="form.especialidade ? 'Digite para pesquisar o novo procedimento...' : 'Selecione a especialidade primeiro'"
                class="form-control pr-10"
                :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': !form.especialidade }"
                required
                :disabled="!form.especialidade"
                autocomplete="off"
              />
              
              <!-- Ícone de seta de dropdown -->
              <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              <!-- Lista flutuante de opções -->
              <div
                v-if="dropdownAberto && form.especialidade && procedimentosFiltrados.length > 0"
                class="absolute z-50 mt-1 w-full max-h-60 overflow-y-auto rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none text-sm border border-gray-200"
              >
                <div
                  v-for="proc in procedimentosFiltrados"
                  :key="proc"
                  @mousedown="selecionarProcedimento(proc)"
                  class="cursor-pointer select-none py-2 px-4 text-gray-900 hover:bg-blue-600 hover:text-white transition duration-150"
                  :class="{ 'bg-blue-50 font-semibold text-blue-900': form.procedimento === proc }"
                >
                  {{ proc }}
                </div>
              </div>
              
              <!-- Mensagem de nenhum resultado -->
              <div
                v-if="dropdownAberto && form.especialidade && procedimentosFiltrados.length === 0"
                class="absolute z-50 mt-1 w-full rounded-md bg-white py-2 px-4 shadow-lg ring-1 ring-black ring-opacity-5 text-sm text-gray-500 border border-gray-200"
              >
                Nenhum procedimento encontrado.
              </div>
            </div>
          </div>
        </div>

        <!-- Linha 3: Judicializado + Swalis + Médico Responsável -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">

          <!-- Judicializado -->
          <div class="form-group">
            <label class="form-label font-semibold">Judicializado? <span class="text-red-500">*</span></label>
            <div class="flex items-center space-x-6 mt-2 p-3 border border-gray-200 rounded-lg" :class="camposEdicaoBloqueados ? 'bg-gray-100 cursor-not-allowed opacity-75' : 'bg-gray-50'">
              <label class="flex items-center space-x-2" :class="camposEdicaoBloqueados ? 'cursor-not-allowed' : 'cursor-pointer'">
                <input
                  type="radio"
                  name="judicializado"
                  value="Sim"
                  v-model="form.judicializado"
                  class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  required
                  :disabled="camposEdicaoBloqueados"
                />
                <span class="text-sm font-medium text-gray-700">Sim</span>
              </label>
              <label class="flex items-center space-x-2" :class="camposEdicaoBloqueados ? 'cursor-not-allowed' : 'cursor-pointer'">
                <input
                  type="radio"
                  name="judicializado"
                  value="Não"
                  v-model="form.judicializado"
                  class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  :disabled="camposEdicaoBloqueados"
                />
                <span class="text-sm font-medium text-gray-700">Não</span>
              </label>
            </div>
            <div v-if="form.judicializado === 'Sim'" class="mt-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 font-medium">
              ⚠️ Paciente com determinação judicial — prioridade legal
            </div>
          </div>

          <!-- Swalis -->
          <div class="form-group">
            <label for="swallis" class="form-label font-semibold">
              Swalis (Priorização) <span class="text-red-500">*</span>
            </label>
            <select
              id="swallis"
              v-model="form.swallis"
              class="form-control"
              :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': camposEdicaoBloqueados }"
              required
              :disabled="camposEdicaoBloqueados"
            >
              <option value="" disabled>Selecione...</option>
              <option value="A1">A1 - Prioridade máxima</option>
              <option value="A2">A2 - Prioridade alta</option>
              <option value="B">B - Prioridade média</option>
              <option value="C">C - Prioridade baixa</option>
              <option value="D">D - Prioridade mínima</option>
            </select>
            <div v-if="form.swallis" class="mt-2 px-3 py-2 rounded-lg text-xs font-semibold" :class="swallisBadgeClass">
              Classificação: {{ getSwalisLabel(form.swallis) }}
            </div>
          </div>

          <!-- Médico Responsável -->
          <div class="form-group">
            <label for="medico_responsavel" class="form-label font-semibold">Médico Responsável <span class="text-red-500">*</span></label>
            <input
              id="medico_responsavel"
              v-model="form.medico_responsavel"
              type="text"
              list="medicos-lista"
              :placeholder="!especialidadeForm ? 'Selecione a especialidade primeiro' : 'Digite o nome do médico solicitante'"
              class="form-control"
              :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': camposEdicaoBloqueados || !especialidadeForm }"
              required
              :disabled="camposEdicaoBloqueados || !especialidadeForm"
            />
            <datalist id="medicos-lista">
              <option v-for="med in medicosDaEspecialidade" :key="med" :value="med">{{ med }}</option>
            </datalist>
          </div>
        </div>

        <!-- Aba STANDBY: Opções e Gestão de Standby Vigente -->
        <div v-if="abaAtiva === 'STANDBY'" class="space-y-4 mb-4">
          <!-- Alerta de Standby Vigente Existente -->
          <div v-if="standbyVigenteAtual" class="p-4 bg-purple-50 border border-purple-200 rounded-xl space-y-3">
            <div class="flex items-center space-x-2 text-purple-900 font-bold text-sm">
              <span class="text-lg">⏱️</span>
              <span>Standby Vigente Detectado para este procedimento!</span>
            </div>
            <div class="text-xs text-purple-800 space-y-1 pl-7">
              <p>
                <strong>Tempo restante atual:</strong> 
                <span class="font-extrabold text-purple-950 text-sm px-2 py-0.5 bg-purple-100 rounded border border-purple-300 ml-1">
                  {{ standbyVigenteAtual.tempoRestante }} dias
                </span>
                <span class="text-purple-600 font-medium ml-1">
                  (de {{ standbyVigenteAtual.tempoOriginal }} dias aprovados em {{ formatarData(standbyVigenteAtual.dataAprovacao) }})
                </span>
              </p>
            </div>

            <!-- Seleção da Ação de Standby -->
            <div class="pt-2 border-t border-purple-200/60 pl-7 space-y-2">
              <span class="text-xs font-bold text-purple-900 block">O que você deseja solicitar?</span>
              <div class="flex flex-wrap gap-4 text-xs">
                <label class="flex items-center space-x-2 cursor-pointer font-medium text-purple-900">
                  <input type="radio" v-model="opcaoStandbyVigente" value="ALTERAR" class="text-purple-600 focus:ring-purple-500" />
                  <span>Alterar tempo de standby</span>
                </label>
                <label class="flex items-center space-x-2 cursor-pointer font-medium text-purple-900">
                  <input type="radio" v-model="opcaoStandbyVigente" value="CANCELAR" class="text-purple-600 focus:ring-purple-500" />
                  <span>Solicitar cancelamento de standby</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Campo de Tempo de Standby (Novo ou Alteração) -->
          <div v-if="!standbyVigenteAtual || opcaoStandbyVigente === 'ALTERAR'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="form-group md:col-span-1">
              <label for="tempo_standby" class="form-label font-semibold">
                {{ standbyVigenteAtual ? 'Novo Tempo de Standby (em dias)' : 'Tempo de Standby (em dias)' }} <span class="text-red-500">*</span>
              </label>
              <input
                id="tempo_standby"
                v-model.number="form.tempo_standby"
                type="number"
                min="1"
                max="90"
                placeholder="Ex: 30"
                class="form-control text-lg font-bold text-center"
                :required="!standbyVigenteAtual || opcaoStandbyVigente === 'ALTERAR'"
              />
              <p class="text-xs text-red-500 mt-1 font-semibold">⚠️ Limite máximo permitido de 90 dias.</p>
            </div>
          </div>
        </div>

        <!-- Justificativa / Detalhes -->
        <div class="form-group">
          <label for="detalhes" class="form-label font-semibold">
            {{ labelDetalhes }} <span class="text-red-500">*</span>
          </label>
          <textarea 
            id="detalhes" 
            v-model="form.detalhes" 
            rows="3" 
            placeholder="Descreva a justificativa clínica para esta solicitação..." 
            class="form-control"
            required
          ></textarea>
        </div>

        <!-- Botões -->
        <div class="flex justify-end space-x-3 pt-2">
          <Button type="button" @click="limparFormulario" variant="secondary">
            Limpar
          </Button>
          <Button type="submit" :disabled="submitting" :variant="abaAtiva === 'STANDBY' && standbyVigenteAtual && opcaoStandbyVigente === 'CANCELAR' ? 'danger' : 'primary'">
            {{ submitting ? 'Enviando...' : (abaAtiva === 'STANDBY' && standbyVigenteAtual && opcaoStandbyVigente === 'CANCELAR' ? 'Solicitar Cancelamento' : 'Enviar Solicitação') }}
          </Button>
        </div>
      </form>
    </Card>

    <!-- Tabela de Solicitações Enviadas -->
    <Card class="overflow-hidden">
      <template #header>
        <div class="flex justify-between items-center w-full">
          <h2 class="text-lg font-bold text-gray-800">
            Acompanhamento das Solicitações — {{ tipoAcompanhamentoNome }}
          </h2>
        </div>
      </template>

      <!-- Abas de Acompanhamento das Solicitações -->
      <div class="flex border-b border-gray-200 bg-gray-50 p-2 overflow-x-auto -mt-6 -mx-6 mb-4">
        <button 
          v-for="aba in abasAcompanhamento" 
          :key="aba.id" 
          @click="abaAcompanhamentoAtiva = aba.id"
          :class="[
            'flex-1 py-2 text-xs font-bold rounded-md transition duration-200 whitespace-nowrap px-3',
            abaAcompanhamentoAtiva === aba.id 
              ? 'bg-indigo-600 text-white shadow-sm' 
              : 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'
          ]"
        >
          <span class="flex items-center justify-center space-x-1.5">
            <component :is="aba.icon" class="h-4 w-4" />
            <span>{{ aba.nome }}</span>
          </span>
        </button>
      </div>

      <!-- Filtros da Tabela -->
      <div class="p-4 bg-gray-50 border-b border-gray-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
        <!-- Especialidade -->
        <div class="form-group">
          <label for="filtroEsp" class="text-xs font-semibold text-gray-600 block mb-1">Especialidade</label>
          <input
            id="filtroEsp"
            type="text"
            v-model="filtroEsp"
            :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
            placeholder="Filtrar por especialidade..."
            class="form-control text-xs"
            :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
          />
        </div>

        <!-- Prontuário / Paciente -->
        <div class="form-group">
          <label for="filtroPac" class="text-xs font-semibold text-gray-600 block mb-1">Paciente / Prontuário</label>
          <input
            id="filtroPac"
            type="text"
            v-model="filtroPac"
            placeholder="Nome ou prontuário..."
            class="form-control text-xs"
          />
        </div>

        <!-- Judicialização -->
        <div class="form-group">
          <label for="filtroJud" class="text-xs font-semibold text-gray-600 block mb-1">Judicialização</label>
          <select id="filtroJud" v-model="filtroJud" class="form-control text-xs">
            <option value="">Todas</option>
            <option value="Sim">⚖️ Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>

        <!-- Swalis -->
        <div class="form-group">
          <label for="filtroSwalis" class="text-xs font-semibold text-gray-600 block mb-1">Swalis</label>
          <select id="filtroSwalis" v-model="filtroSwalis" class="form-control text-xs">
            <option value="">Todos</option>
            <option value="A1">A1 - Prioridade máxima</option>
            <option value="A2">A2 - Prioridade alta</option>
            <option value="B">B - Prioridade média</option>
            <option value="C">C - Prioridade baixa</option>
            <option value="D">D - Prioridade mínima</option>
          </select>
        </div>

        <!-- Médico Responsável -->
        <div class="form-group">
          <label for="filtroMed" class="text-xs font-semibold text-gray-600 block mb-1">Médico Responsável</label>
          <input
            id="filtroMed"
            type="text"
            v-model="filtroMed"
            list="filtro-medicos-lista"
            placeholder="Digite para pesquisar médico..."
            class="form-control text-xs"
          />
          <datalist id="filtro-medicos-lista">
            <option v-for="med in medicosConhecidos" :key="med" :value="med" />
          </datalist>
        </div>
      </div>

      <!-- Sub-abas: Pendentes e Concluídas -->
      <div class="flex border-b border-gray-200 bg-white px-6 py-2.5 space-x-2">
        <button
          @click="subAbaAcompanhamento = 'PENDENTE'"
          :class="[
            'px-4 py-1.5 text-xs font-bold rounded-full transition duration-200',
            subAbaAcompanhamento === 'PENDENTE'
              ? 'bg-amber-100 text-amber-900 border border-amber-300 shadow-sm'
              : 'text-gray-600 hover:bg-gray-100'
          ]"
        >
          ⏳ Solicitações Pendentes
        </button>
        <button
          @click="subAbaAcompanhamento = 'CONCLUIDO'"
          :class="[
            'px-4 py-1.5 text-xs font-bold rounded-full transition duration-200',
            subAbaAcompanhamento === 'CONCLUIDO'
              ? 'bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-sm'
              : 'text-gray-600 hover:bg-gray-100'
          ]"
        >
          ✅ Histórico Concluído (Aprovadas/Rejeitadas)
        </button>
      </div>

      <div v-if="loadingSolicitacoes" class="flex justify-center items-center py-6">
        <LoadingIndicator />
      </div>
      <div v-else-if="solicitacoesFiltradas.length === 0" class="text-center py-8 text-gray-500">
        Nenhuma solicitação encontrada para os filtros selecionados.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data / Hora</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Especialidade</th>
              <th v-if="abaAcompanhamentoAtiva !== 'EDITAR'" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Procedimento</th>
              <th v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Procedimento Anterior</th>
              <th v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Novo Procedimento</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário / Paciente</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Judicial</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Swalis</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Médico</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Info Extra</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
              <th v-if="subAbaAcompanhamento === 'CONCLUIDO'" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DATA/HORA AÇÃO</th>
              <th v-if="subAbaAcompanhamento !== 'CONCLUIDO'" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="solic in solicitacoesFiltradas" :key="solic.id">
              <td class="px-4 py-4 whitespace-nowrap text-xs font-mono text-gray-600">
                {{ formatarDataHora(solic.data_criacao) }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-gray-500 font-mono text-xs">#{{ solic.id }}</td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getTipoBadgeClass(solic.tipo)">{{ formatarTipo(solic.tipo) }}</span>
              </td>
              
              <!-- Especialidade (Comum a todos) -->
              <td class="px-4 py-4 text-gray-700 text-xs font-semibold">
                {{ solic.especialidade || '—' }}
              </td>
              
              <!-- Procedimento (Não EDITAR) -->
              <td v-if="abaAcompanhamentoAtiva !== 'EDITAR'" class="px-4 py-4 text-gray-700 text-xs">
                {{ solic.procedimento || '—' }}
              </td>
              
              <!-- Procedimento Anterior (EDITAR) -->
              <td v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-4 py-4 text-gray-500 text-xs italic">
                {{ solic.procedimento_anterior || '—' }}
              </td>
              
              <!-- Novo Procedimento (EDITAR) -->
              <td v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-4 py-4 text-xs">
                <div v-if="solic.procedimento === solic.procedimento_anterior || !solic.procedimento_anterior" class="text-gray-400 italic">
                  Não houve mudança
                </div>
                <div v-else class="font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 inline-block">
                  {{ solic.procedimento }}
                </div>
              </td>

              <!-- Prontuário / Paciente -->
              <td class="px-4 py-4 text-gray-700 text-xs">
                <div class="font-mono">{{ solic.codigo_paciente }}</div>
                <div class="font-medium">{{ solic.nome_paciente }}</div>
              </td>

              <!-- Judicial (com destaque se editado) -->
              <td class="px-4 py-4 whitespace-nowrap text-xs">
                <span 
                  v-if="solic.judicializado === 'Sim'" 
                  :class="[
                    'px-2 py-0.5 rounded-full font-semibold bg-amber-100 text-amber-800',
                    abaAcompanhamentoAtiva === 'EDITAR' && solic.judicializado !== obterEstadoAnterior(solic).judicializado ? 'ring-2 ring-yellow-400 font-bold bg-yellow-100 text-yellow-900 border border-yellow-300' : ''
                  ]"
                >
                  ⚖️ Sim
                </span>
                <span 
                  v-else 
                  :class="[
                    'text-gray-400',
                    abaAcompanhamentoAtiva === 'EDITAR' && solic.judicializado !== obterEstadoAnterior(solic).judicializado ? 'bg-yellow-100 text-yellow-800 font-bold px-1.5 py-0.5 rounded ring-2 ring-yellow-300' : ''
                  ]"
                >
                  Não
                </span>
              </td>

              <!-- Swalis (com destaque se editado) -->
              <td class="px-4 py-4 whitespace-nowrap">
                <span 
                  v-if="solic.swalis || solic.swallis || solic.Swalis" 
                  :title="getSwalisLabel(solic.swalis || solic.swallis || solic.Swalis)"
                  :class="[
                    getSwallisClass(solic.swalis || solic.swallis || solic.Swalis),
                    abaAcompanhamentoAtiva === 'EDITAR' && (solic.swalis || solic.swallis || solic.Swalis || '') !== obterEstadoAnterior(solic).swalis ? 'ring-2 ring-yellow-400 font-extrabold' : ''
                  ]"
                >
                  {{ solic.swalis || solic.swallis || solic.Swalis }}
                </span>
                <span 
                  v-else 
                  :class="[
                    'text-gray-400',
                    abaAcompanhamentoAtiva === 'EDITAR' && '' !== obterEstadoAnterior(solic).swalis ? 'bg-yellow-100 text-yellow-800 font-bold px-1.5 py-0.5 rounded ring-2 ring-yellow-300' : ''
                  ]"
                >
                  —
                </span>
              </td>

              <!-- Médico (com destaque se editado) -->
              <td 
                class="px-4 py-4 whitespace-nowrap text-xs"
                :class="[
                  abaAcompanhamentoAtiva === 'EDITAR' && solic.medico_responsavel !== obterEstadoAnterior(solic).medico_responsavel ? 'text-blue-700 font-bold bg-yellow-50 px-1 rounded ring-2 ring-yellow-300' : 'text-gray-600'
                ]"
              >
                {{ solic.medico_responsavel || '—' }}
              </td>

              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(solic.status)">{{ solic.status }}</span>
              </td>
              <td class="px-4 py-4 text-xs text-gray-600">
                <div v-if="solic.tempo_standby" class="font-semibold text-purple-700 bg-purple-50 px-2 py-1 rounded">
                  ⏱️ {{ solic.tempo_standby }} dias
                </div>
                <div v-else class="text-gray-400">—</div>
              </td>
              <!-- Descrição com botão modal -->
              <td class="px-4 py-4 whitespace-nowrap text-xs">
                <button 
                  type="button"
                  @click="abrirModalDescricao(solic)" 
                  class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded border border-indigo-200 transition cursor-pointer text-xs flex items-center space-x-1"
                  title="Clique para ver a justificativa completa"
                >
                  <span>📄 Ver Descrição</span>
                </button>
              </td>

              <!-- Data/Hora Ação (Condicional) -->
              <td v-if="subAbaAcompanhamento === 'CONCLUIDO'" class="px-4 py-4 whitespace-nowrap text-xs font-mono text-gray-600">
                {{ formatarDataHora(solic.data_acao) }}
              </td>

              <td v-if="subAbaAcompanhamento !== 'CONCLUIDO'" class="px-4 py-4 whitespace-nowrap text-xs">
                <div v-if="solic.status === 'PENDENTE' && (perfisStore.perfilAtivo.tipo === 'GESTAO_LEC' || perfisStore.perfilAtivo.tipo === 'ADMIN')" class="flex space-x-1">
                  <Button @click="atualizarStatus(solic.id, 'APROVADO')" variant="success" size="sm">
                    Aprovar
                  </Button>
                  <Button @click="atualizarStatus(solic.id, 'REJEITADO')" variant="danger" size="sm">Rejeitar</Button>
                </div>
                <span v-else class="text-gray-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Modal de Descrição / Justificativa -->
    <div v-if="modalDescricao.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4 border border-gray-200">
        <div class="flex justify-between items-start border-b border-gray-150 pb-3">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Justificativa da Solicitação</h3>
            <p class="text-xs text-gray-500">
              Solicitação #{{ modalDescricao.solic?.id }} · {{ formatarTipo(modalDescricao.solic?.tipo) }}
            </p>
          </div>
          <button @click="modalDescricao.aberto = false" class="text-gray-400 hover:text-gray-600 text-lg font-bold">
            ✕
          </button>
        </div>

        <div v-if="modalDescricao.solic" class="space-y-3 text-xs text-gray-700">
          <div class="grid grid-cols-2 gap-2 bg-gray-50 p-3 rounded-lg border border-gray-100">
            <div><span class="font-bold text-gray-500 uppercase text-[10px]">Paciente:</span> <br/><span class="font-bold text-gray-900">{{ modalDescricao.solic.nome_paciente }}</span></div>
            <div><span class="font-bold text-gray-500 uppercase text-[10px]">Prontuário:</span> <br/><span class="font-mono font-bold text-gray-900">#{{ modalDescricao.solic.codigo_paciente }}</span></div>
            <div><span class="font-bold text-gray-500 uppercase text-[10px]">Especialidade:</span> <br/><span class="font-medium text-gray-800">{{ modalDescricao.solic.especialidade }}</span></div>
            <div><span class="font-bold text-gray-500 uppercase text-[10px]">Procedimento:</span> <br/><span class="font-medium text-gray-800">{{ modalDescricao.solic.procedimento }}</span></div>
          </div>

          <div>
            <label class="block font-bold text-gray-800 text-xs mb-1">Descrição / Justificativa Clínica:</label>
            <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 text-xs leading-relaxed max-h-60 overflow-y-auto whitespace-pre-wrap font-medium">
              {{ modalDescricao.solic.detalhes || modalDescricao.solic.campos_modificados || 'Nenhuma justificativa detalhada foi fornecida.' }}
            </div>
          </div>
        </div>

        <div class="flex justify-end pt-2 border-t border-gray-100">
          <Button @click="modalDescricao.aberto = false" variant="primary" size="sm">
            Fechar
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { 
  UserPlusIcon, 
  TrashIcon, 
  PencilSquareIcon, 
  PauseIcon 
} from '@heroicons/vue/24/outline';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { usePerfisStore } from '../stores/perfis';
import { useAuthStore } from '../stores/auth';

const toast = useToast();
const perfisStore = usePerfisStore();
const authStore = useAuthStore();

// Lista base de procedimentos por nome de especialidade
const procedimentosBaseMap: Record<string, string[]> = {
  'Cardiologia / Cirurgia Cardíaca': ['Revascularização do Miocárdio (Ponte de Safena)', 'Troca de Valva Aórtica', 'Troca de Valva Mitral', 'Implante de Marcapasso', 'Correção de CIA / CIV'],
  'Cirurgia Geral': ['Colecistectomia', 'Herniorrafia Inguinal', 'Apendicectomia', 'Gastrectomia', 'Colostomia'],
  'Ginecologia': ['Histerectomia', 'Miomectomia', 'Laparoscopia Diagnóstica', 'Colpoperineoplastia', 'Ooforectomia'],
  'Neurocirurgia': ['Craniectomia Descompressiva', 'Clipagem de Aneurisma', 'Derivação Ventrículo-Peritoneal', 'Microdiscectomia', 'Tumor Cerebral — Ressecção'],
  'Oftalmologia': ['Facoemulsificação (Catarata)', 'Trabeculectomia (Glaucoma)', 'Vitrectomia', 'Transplante de Córnea', 'Fotocoagulação a Laser'],
  'Ortopedia': ['Artroplastia Total de Quadril', 'Artroplastia Total de Joelho', 'Artroscopia de Joelho', 'Fixação de Fratura de Fêmur', 'Osteossíntese de Coluna'],
  'Otorrinolaringologia': ['Septoplastia', 'Amigdalectomia', 'Timpanoplastia', 'Adenoidectomia', 'Microcirurgia de Laringe'],
  'Plástica': ['Mamoplastia', 'Rinoplastia', 'Blefaroplastia', 'Reconstrução Mamária', 'Abdominoplastia'],
  'Torácica': ['Lobectomia', 'Pleuroscopia', 'Simpatectomia', 'Ressecção de Nódulo Pulmonar', 'Broncoscopia'],
  'Urologia': ['Prostatectomia Radical', 'Nefrectomia', 'Ureteroscopia', 'Litotripsia', 'Ressecção Transuretral de Próstata (RTUP)']
};

const especialidades = computed(() => {
  const perfis = perfisStore.perfis;
  // Filtra apenas perfis com p.tipo === 'ESPECIALIDADE' e que possuem especialidade ou nome definido
  const perfisEspecialidade = perfis.filter(p => p.tipo === 'ESPECIALIDADE' || (p.especialidade && p.tipo !== 'ADMIN' && p.tipo !== 'GESTAO_LEC'));
  
  const listaEspecialidades = perfisEspecialidade
    .map(p => (p.especialidade || p.nome).trim())
    .filter((nome, index, self) => nome && self.indexOf(nome) === index)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'));

  // Se perfis ainda não foram carregados, retorna a lista padrão ordenada
  if (listaEspecialidades.length === 0) {
    return Object.keys(procedimentosBaseMap)
      .sort((a, b) => a.localeCompare(b, 'pt-BR'))
      .map(nome => ({
        nome,
        procedimentos: procedimentosBaseMap[nome] || []
      }));
  }

  return listaEspecialidades.map(nome => ({
    nome,
    procedimentos: procedimentosBaseMap[nome] || []
  }));
});

// -------------------------------------------------------
// Formulário
// -------------------------------------------------------
const form = ref({
  especialidade: '',
  procedimento: '',
  procedimento_anterior: '', // Armazena o procedimento original antes de editar
  codigo_paciente: '',
  nome_paciente: '',
  dt_nascimento: '',
  nome_mae: '',
  judicializado: '',
  swallis: '',
  medico_responsavel: '',
  detalhes: '',
  tempo_standby: undefined as number | undefined
});

// Procedimentos filtrados pela especialidade selecionada
const procedimentosDaEspecialidade = computed(() => {
  const esp = especialidades.value.find(e => e.nome === form.value.especialidade);
  return esp ? esp.procedimentos : [];
});

// Médicos conhecidos extraídos das solicitações (para o autocomplete)
const medicosConhecidos = computed(() => {
  const nomes = solicitacoes.value
    .map(s => s.medico_responsavel)
    .filter(n => n && n !== '—' && n !== 'Não informado');
  return [...new Set(nomes)].sort();
});

// -------------------------------------------------------
// Abas
// -------------------------------------------------------
const abas = [
  { id: 'INSERIR', nome: 'Solicitar Inclusão', icon: UserPlusIcon },
  { id: 'EDITAR', nome: 'Solicitar Edição', icon: PencilSquareIcon },
  { id: 'STANDBY', nome: 'Solicitar Standby', icon: PauseIcon },
  { id: 'EXCLUIR', nome: 'Solicitar Exclusão', icon: TrashIcon }
];

const abaAtiva = ref('INSERIR');
const loadingBusca = ref(false);
const submitting = ref(false);
const loadingSolicitacoes = ref(false);
const solicitacoes = ref<any[]>([]);
const formCarregadoDaSede = ref(false);
const pacientesBase = ref<any[]>([]);

const filtroEsp = ref('');
const filtroProc = ref('');
const filtroPac = ref('');
const filtroJud = ref('');
const filtroSwalis = ref('');
const filtroMed = ref('');
const subAbaAcompanhamento = ref('PENDENTE');

const abaAcompanhamentoAtiva = ref('INSERIR');
const abasAcompanhamento = [
  { id: 'INSERIR', nome: 'Solicitações de Inclusão', icon: UserPlusIcon },
  { id: 'EDITAR', nome: 'Solicitações de Edição', icon: PencilSquareIcon },
  { id: 'STANDBY', nome: 'Solicitações de Standby', icon: PauseIcon },
  { id: 'EXCLUIR', nome: 'Solicitações de Exclusão', icon: TrashIcon }
];

// Para abas de ação com múltiplos procedimentos
const procedimentosPaciente = ref<any[]>([]);
const procedimentoSelecionadoParaEdicao = ref<number | null>(null);

const desejaAlterarProcedimento = ref('Não');
const dropdownAberto = ref(false);

const procedimentosFiltrados = computed(() => {
  const query = form.value.procedimento.toLowerCase().trim();
  if (!query) return procedimentosDaEspecialidade.value;
  return procedimentosDaEspecialidade.value.filter(p => 
    p.toLowerCase().includes(query)
  );
});

const selecionarProcedimento = (proc: string) => {
  form.value.procedimento = proc;
  dropdownAberto.value = false;
};

// Sincroniza o valor ao alternar "Sim/Não" no desejaAlterarProcedimento
watch(desejaAlterarProcedimento, (val) => {
  if (val === 'Não') {
    form.value.procedimento = form.value.procedimento_anterior;
  } else {
    form.value.procedimento = '';
  }
});

const isEspecialidadeDisabled = computed(() => {
  return camposDesabilitados.value || perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' || abaAtiva.value === 'EDITAR';
});

const especialidadeForm = computed(() => {
  if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade) {
    return perfisStore.perfilAtivo.especialidade;
  }
  return form.value.especialidade || '';
});

const usuariosLocais = ref<any[]>([]);

const carregarUsuariosLocais = async () => {
  try {
    const { data } = await api.get('/api/usuarios');
    usuariosLocais.value = data;
  } catch (error) {
    console.error('Erro ao carregar usuários para médicos responsáveis:', error);
  }
};

const medicosDaEspecialidade = computed(() => {
  if (!especialidadeForm.value) return [];
  const espNorm = especialidadeForm.value.toLowerCase().trim();
  
  const medicosEncontrados = usuariosLocais.value
    .filter(u => {
      const isMedico = u.funcao === 'Médico';
      const matchEsp = u.especialidade && u.especialidade.toLowerCase().trim().includes(espNorm);
      return isMedico && matchEsp;
    })
    .map(u => u.nome);

  return Array.from(new Set(medicosEncontrados)).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

// Formulário
// -------------------------------------------------------


const selecionarAba = (id: string) => {
  abaAtiva.value = id;
  desejaAlterarProcedimento.value = 'Não';
  limparFormulario();
};

// Determina se os campos devem ser somente-leitura na aba selecionada
const camposDesabilitados = computed(() => {
  return abaAtiva.value === 'EXCLUIR' || abaAtiva.value === 'STANDBY';
});

// Bloqueia campos da aba EDITAR até que o prontuário do paciente seja carregado/puxado
const camposEdicaoBloqueados = computed(() => {
  if (abaAtiva.value === 'EDITAR') {
    return !formCarregadoDaSede.value;
  }
  return camposDesabilitados.value;
});

// Filtra a lista de solicitações de acordo com o perfil ativo, abas de acompanhamento, sub-abas e filtros de pesquisa
const solicitacoesFiltradas = computed(() => {
  let list = [...solicitacoes.value];
  
  // 1. Filtra pelo tipo correspondente à aba de acompanhamento (Inclusão, Edição, Standby, Exclusão)
  list = list.filter(s => s.tipo === abaAcompanhamentoAtiva.value);

  // 2. Filtra pelo status correspondente à sub-aba (PENDENTE ou CONCLUIDO)
  if (subAbaAcompanhamento.value === 'PENDENTE') {
    list = list.filter(s => s.status === 'PENDENTE');
  } else {
    list = list.filter(s => s.status === 'APROVADO' || s.status === 'REJEITADO');
  }

  // 3. Filtro de Especialidade (perfil restrito ou digitado)
  if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade) {
    const activeSpecialtyName = perfisStore.perfilAtivo.especialidade.toLowerCase();
    list = list.filter(s => 
      s.especialidade && s.especialidade.toLowerCase().includes(activeSpecialtyName)
    );
  } else if (filtroEsp.value) {
    const query = filtroEsp.value.toLowerCase().trim();
    list = list.filter(s => s.especialidade && s.especialidade.toLowerCase().includes(query));
  }

  // 4. Filtro de Procedimento
  if (filtroProc.value) {
    const query = filtroProc.value.toLowerCase().trim();
    list = list.filter(s => s.procedimento && s.procedimento.toLowerCase().includes(query));
  }

  // 5. Filtro de Prontuário / Paciente
  if (filtroPac.value) {
    const query = filtroPac.value.toLowerCase().trim();
    list = list.filter(s => 
      String(s.codigo_paciente).includes(query) || 
      (s.nome_paciente && s.nome_paciente.toLowerCase().includes(query))
    );
  }

  // 5. Filtro de Judicialização
  if (filtroJud.value) {
    list = list.filter(s => s.judicializado === filtroJud.value);
  }

  // 6. Filtro de Swalis
  if (filtroSwalis.value) {
    list = list.filter(s => {
      const sw = s.swalis || s.swallis || s.Swalis || '';
      return sw === filtroSwalis.value;
    });
  }

  // 7. Filtro de Médico Responsável
  if (filtroMed.value) {
    const query = filtroMed.value.toLowerCase().trim();
    list = list.filter(s => s.medico_responsavel && s.medico_responsavel.toLowerCase().includes(query));
  }

  // 8. Ordenação padrão
  if (subAbaAcompanhamento.value === 'PENDENTE') {
    // Da mais antiga para a mais nova (data_criacao ascendente)
    return list.sort((a, b) => {
      const dataA = a.data_criacao || '';
      const dataB = b.data_criacao || '';
      return dataA.localeCompare(dataB);
    });
  } else {
    // Da última respondida para a primeira (data_acao decrescente, fallback para data_criacao decrescente)
    return list.sort((a, b) => {
      const dataA = a.data_acao || a.data_criacao || '';
      const dataB = b.data_acao || b.data_criacao || '';
      return dataB.localeCompare(dataA);
    });
  }
});

// Trava a especialidade da nova solicitação caso o perfil ativo seja de uma especialidade específica
watch(() => perfisStore.perfilAtivo, (newProfile) => {
  if (newProfile.tipo === 'ESPECIALIDADE' && newProfile.especialidade) {
    const found = especialidades.value.find(e => e.nome.toLowerCase().includes(newProfile.especialidade!.toLowerCase()));
    const finalEsp = found ? found.nome : newProfile.especialidade;
    form.value.especialidade = finalEsp;
    filtroEsp.value = finalEsp;
  } else {
    form.value.especialidade = '';
    filtroEsp.value = '';
  }
}, { immediate: true });

watch(() => form.value.especialidade, async (newEsp) => {
  if (newEsp === 'Plástica') {
    try {
      const { data } = await api.get('/api/especialidades/1884/procedimentos');
      const procedimentosDoAghu = data.map((p: any) => p.descricao);
      const plast = especialidades.value.find(e => e.nome === 'Plástica');
      if (plast) {
        plast.procedimentos = procedimentosDoAghu;
      }
    } catch (err) {
      console.error('Erro ao buscar procedimentos da especialidade Plástica no AGHU:', err);
    }
  }
}, { immediate: true });

// Garante que "Pendentes" é a sub-aba ativa ao mudar de aba principal de acompanhamento
watch(abaAcompanhamentoAtiva, () => {
  subAbaAcompanhamento.value = 'PENDENTE';
});
const tipoSolicitacaoNome = computed(() => {
  const match = abas.find(a => a.id === abaAtiva.value);
  return match ? match.nome.replace('Solicitar ', '') : '';
});

const tipoAcompanhamentoNome = computed(() => {
  const match = abasAcompanhamento.find(a => a.id === abaAcompanhamentoAtiva.value);
  return match ? match.nome.replace('Solicitações de ', '') : '';
});

const labelDetalhes = computed(() => {
  switch (abaAtiva.value) {
    case 'INSERIR':  return 'Justificativa e indicação clínica para inclusão';
    case 'EDITAR':   return 'Justificativa para o(s) campo(s) editado(s)';
    case 'EXCLUIR':  return 'Motivo detalhado para a exclusão da lista de espera';
    case 'STANDBY':  return 'Motivo clínico ou administrativo para suspensão temporária (Standby)';
    default:         return 'Detalhes da solicitação';
  }
});

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

const swallisBadgeClass = computed(() => {
  switch (form.value.swallis) {
    case 'A1': return 'bg-red-100 text-red-800';
    case 'A2': return 'bg-orange-100 text-orange-800';
    case 'B':  return 'bg-yellow-100 text-yellow-800';
    case 'C':  return 'bg-blue-100 text-blue-800';
    case 'D':  return 'bg-gray-100 text-gray-700';
    default:   return 'bg-gray-100 text-gray-700';
  }
});

const formatarData = (dataStr: string) => {
  if (!dataStr) return '—';
  if (dataStr.includes('/')) return dataStr;
  try {
    const cleanStr = dataStr.includes('T') ? dataStr.split('T')[0] : dataStr.split(' ')[0];
    const parts = cleanStr.split('-');
    if (parts.length === 3) {
      const [ano, mes, dia] = parts;
      return `${dia}/${mes}/${ano}`;
    }
    return dataStr;
  } catch (e) {
    return dataStr;
  }
};

const formatarDataHora = (dataStr: string) => {
  if (!dataStr) return '—';
  try {
    const [data, hora] = dataStr.split(' ');
    const [ano, mes, dia] = data.split('-');
    return `${dia}/${mes}/${ano} ${hora.substring(0, 5)}`;
  } catch (e) {
    return dataStr;
  }
};

const limparFormulario = (manterCodigo = false) => {
  const codSalvo = manterCodigo ? form.value.codigo_paciente : '';
  form.value = {
    especialidade: '',
    procedimento: '',
    procedimento_anterior: '',
    codigo_paciente: codSalvo,
    nome_paciente: '',
    dt_nascimento: '',
    nome_mae: '',
    judicializado: '',
    swallis: '',
    medico_responsavel: '',
    detalhes: '',
    tempo_standby: undefined
  };
  formCarregadoDaSede.value = false;
  procedimentosPaciente.value = [];
  procedimentoSelecionadoParaEdicao.value = null;
  desejaAlterarProcedimento.value = 'Não';

  // Reaplica especialidade travada pelo perfil
  const profile = perfisStore.perfilAtivo;
  if (profile.tipo === 'ESPECIALIDADE' && profile.especialidade) {
    const found = especialidades.value.find(e => e.nome.toLowerCase().includes(profile.especialidade!.toLowerCase()));
    form.value.especialidade = found ? found.nome : profile.especialidade;
  }
};

// Preenche o formulário ao selecionar o procedimento para edição/exclusão/standby
const preencherCamposDoProc = (proc: any) => {
  form.value.procedimento_anterior = proc.procedimento;
  form.value.procedimento = proc.procedimento;
  form.value.especialidade = proc.especialidade;
  form.value.judicializado = proc.judicializado || 'Não';
  form.value.swallis = proc.swallis || '';
  form.value.medico_responsavel = proc.medico_responsavel || '';
  desejaAlterarProcedimento.value = 'Não';
};

// Busca unificada com base no prontuário e na aba selecionada
const buscarDados = async (isAutomatic = false) => {
  if (!form.value.codigo_paciente) {
    if (!isAutomatic) {
      toast.error('Por favor, digite o número do prontuário.');
    }
    return;
  }
  loadingBusca.value = true;
  formCarregadoDaSede.value = false;
  procedimentosPaciente.value = [];
  procedimentoSelecionadoParaEdicao.value = null;

  try {
    // 1. Busca dados cadastrais do paciente no AGHU (Cadastro de Pacientes)
    let pacData;
    try {
      const resp = await api.get(`/api/pacientes/${form.value.codigo_paciente}`);
      pacData = resp.data;
      form.value.nome_paciente = pacData.nome;
      form.value.dt_nascimento = pacData.dt_nascimento;
      form.value.nome_mae = pacData.nome_mae;
    } catch {
      toast.error('Paciente não encontrado no AGHU (Cadastro de Pacientes).');
      limparFormulario();
      return;
    }

    if (abaAtiva.value === 'INSERIR') {
      if (!isAutomatic) {
        toast.success(`Paciente localizado no AGHU: ${pacData.nome}`);
      }
    } else {
      // 2. EDITAR / EXCLUIR / STANDBY: Busca procedimentos do paciente no histórico de solicitações da LEC
      const { data: solicsData } = await api.get('/api/solicitacoes');
      const especialidadeAtual = perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade
        ? perfisStore.perfilAtivo.especialidade.toLowerCase()
        : null;

      const allSolics: any[] = solicsData;
      const codProntuario = String(form.value.codigo_paciente);

      const solicsDosPac = allSolics.filter(s => String(s.codigo_paciente) === codProntuario);
      
      // Verifica se o paciente possui inclusão no sistema LEC (solicitação de INSERIR ou paciente da base)
      const temInclusaoNaLec = solicsDosPac.some(s => s.tipo === 'INSERIR' || s.status === 'APROVADO');
      
      if (!temInclusaoNaLec && solicsDosPac.length === 0) {
        toast.error('Paciente não incluído no Sistema de Gestão LEC HC-UFPE');
        limparFormulario(true);
        return;
      }

      let procs: any[] = [];
      
      if (solicsDosPac.length > 0) {
        // Reconstrói a lista de procedimentos aprovados do paciente
        const procMap = new Map<string, any>();
        
        // Inicializa com o procedimento base cadastrado no AGHU/pacientes.csv
        if (pacData && pacData.procedimento) {
          const baseKey = `${pacData.especialidade}||${pacData.procedimento}`;
          procMap.set(baseKey, {
            especialidade: pacData.especialidade,
            procedimento: pacData.procedimento,
            judicializado: 'Não',
            swallis: pacData.swalis || pacData.swallis || pacData.Swalis || '—',
            medico_responsavel: 'Não informado',
            status: 'ATIVO'
          });
        }

        const approvedSolics = solicsDosPac
          .filter(s => s.status === 'APROVADO')
          .sort((a: any, b: any) => a.data_criacao.localeCompare(b.data_criacao));

        for (const s of approvedSolics) {
          const key = `${s.especialidade}||${s.procedimento}`;
          if (s.tipo === 'INSERIR') {
            procMap.set(key, {
              especialidade: s.especialidade,
              procedimento: s.procedimento,
              judicializado: s.judicializado || 'Não',
              swallis: s.swalis || s.swallis || s.Swalis || '—',
              medico_responsavel: s.medico_responsavel || 'Não informado',
              status: 'ATIVO'
            });
          } else if (s.tipo === 'EDITAR') {
            const oldKey = `${s.especialidade}||${s.procedimento_anterior || s.procedimento}`;
            const existing = procMap.get(oldKey);
            if (existing) {
              procMap.delete(oldKey);
              procMap.set(key, {
                ...existing,
                procedimento: s.procedimento,
                judicializado: s.judicializado || 'Não',
                swallis: s.swalis || s.swallis || s.Swalis || '—',
                medico_responsavel: s.medico_responsavel || 'Não informado'
              });
            }
          } else if (s.tipo === 'EXCLUIR') {
            procMap.delete(key);
          }
        }
        procs = Array.from(procMap.values());
      } else {
        // Fallback: Usa o procedimento do cadastro inicial do paciente
        if (pacData && pacData.procedimento) {
          procs = [{
            especialidade: pacData.especialidade,
            procedimento: pacData.procedimento,
            judicializado: 'Não',
            swallis: pacData.swalis || pacData.swallis || pacData.Swalis || '—',
            medico_responsavel: 'Não informado',
            status: 'ATIVO'
          }];
        }
      }

      // Filtra por especialidade se o perfil for ESPECIALIDADE
      if (especialidadeAtual) {
        procs = procs.filter(p => p.especialidade && p.especialidade.toLowerCase().includes(especialidadeAtual));
      }

      if (procs.length === 0) {
        if (!isAutomatic) {
          toast.error('Nenhum procedimento ativo encontrado para este paciente' + (especialidadeAtual ? ' nesta especialidade' : '') + '.');
        }
        limparFormulario();
        return;
      }

      procedimentosPaciente.value = procs;
      formCarregadoDaSede.value = true;

      // Se houver apenas um procedimento, preenchemos automaticamente
      if (procs.length === 1) {
        procedimentoSelecionadoParaEdicao.value = 0;
        preencherCamposDoProc(procs[0]);
        if (!isAutomatic) {
          toast.success(`Procedimento encontrado: ${procs[0].procedimento}`);
        }
      } else {
        if (!isAutomatic) {
          toast.info(`${procs.length} procedimentos encontrados para este paciente. Selecione qual deseja prosseguir.`);
        }
      }
    }
  } catch (error: any) {
    if (!isAutomatic) {
      toast.error('Ocorreu um erro ao buscar os dados.');
    }
    limparFormulario();
  } finally {
    loadingBusca.value = false;
  }
};

const carregarSolicitacoes = async () => {
  loadingSolicitacoes.value = true;
  try {
    const { data } = await api.get('/api/solicitacoes');
    solicitacoes.value = data;
  } catch (error) {
    toast.error('Erro ao carregar solicitações.');
  } finally {
    loadingSolicitacoes.value = false;
  }
};

const enviarSolicitacao = async () => {
  // Validação do Médico Responsável (deve ser um médico cadastrado na especialidade)
  if (abaAtiva.value === 'INSERIR' || abaAtiva.value === 'EDITAR') {
    const medDigitado = (form.value.medico_responsavel || '').trim();
    if (!medDigitado) {
      toast.error('O Médico Responsável é obrigatório.');
      return;
    }
    const medicosValidos = medicosDaEspecialidade.value;
    const isValido = medicosValidos.some(m => m.toLowerCase().trim() === medDigitado.toLowerCase());
    if (!isValido) {
      if (medicosValidos.length === 0) {
        toast.error(`Não há médicos cadastrados na especialidade "${especialidadeForm.value}". Crie um usuário com perfil médico nessa especialidade no menu Perfis.`);
      } else {
        toast.error(`O Médico Responsável "${medDigitado}" não é um médico cadastrado na especialidade ${especialidadeForm.value}. Selecione um médico da lista: ${medicosValidos.join(', ')}.`);
      }
      return;
    }
  }

  // Validação do limite de tempo do standby
  if (abaAtiva.value === 'STANDBY') {
    if (!form.value.tempo_standby || form.value.tempo_standby < 1 || form.value.tempo_standby > 90) {
      toast.error('O tempo de standby deve ser entre 1 e 90 dias.');
      return;
    }
  }

  // Valida que para EDITAR o procedimento foi selecionado e pelo menos um campo foi alterado
  if (abaAtiva.value === 'EDITAR') {
    if (procedimentosPaciente.value.length > 1 && procedimentoSelecionadoParaEdicao.value === null) {
      toast.error('Selecione qual procedimento deseja editar.');
      return;
    }
    const idx = procedimentoSelecionadoParaEdicao.value !== null ? procedimentoSelecionadoParaEdicao.value : 0;
    const orig = procedimentosPaciente.value[idx];
    if (orig) {
      const origSw = orig.swalis || orig.swallis || orig.Swalis || '';
      const formSw = form.value.swallis || '';
      const origMed = orig.medico_responsavel || '';
      const formMed = form.value.medico_responsavel || '';
      const origJud = orig.judicializado || 'Não';
      const formJud = form.value.judicializado || 'Não';
      const origProc = orig.procedimento || '';
      const formProc = form.value.procedimento || '';

      const alterado = (origSw !== formSw) || 
                       (origMed !== formMed) || 
                       (origJud !== formJud) || 
                       (origProc !== formProc);

      if (!alterado) {
        toast.error('Nenhuma alteração detectada. Modifique pelo menos um campo (Procedimento, Judicialização, Swalis, Médico Responsável) antes de enviar.');
        return;
      }
    }
  }

  let tipoFinal = abaAtiva.value;
  let tempoStandbyFinal = form.value.tempo_standby || undefined;

  if (abaAtiva.value === 'STANDBY' && standbyVigenteAtual.value && opcaoStandbyVigente.value === 'CANCELAR') {
    tipoFinal = 'CANCELAR_STANDBY';
    tempoStandbyFinal = undefined;
  }

  submitting.value = true;
  try {
    await api.post('/api/solicitacoes', {
      tipo: tipoFinal,
      especialidade: form.value.especialidade,
      procedimento: form.value.procedimento,
      codigo_paciente: form.value.codigo_paciente,
      nome_paciente: form.value.nome_paciente,
      judicializado: form.value.judicializado,
      swalis: form.value.swallis,
      swallis: form.value.swallis,
      medico_responsavel: form.value.medico_responsavel,
      detalhes: form.value.detalhes,
      tempo_standby: tempoStandbyFinal,
      perfil_executor: perfisStore.perfilAtivo.nome,
      usuario: authStore.user?.givenName?.[0] || authStore.user?.username || 'Usuário Sistema',
      procedimento_anterior: form.value.procedimento_anterior || undefined
    });
    toast.success('Solicitação registrada com sucesso!');
    limparFormulario();
    await carregarSolicitacoes();
  } catch (error) {
    toast.error('Erro ao registrar solicitação.');
  } finally {
    submitting.value = false;
  }
};

const atualizarStatus = async (id: string, status: string) => {
  const acaoText = status === 'APROVADO' ? 'aprovar (dar baixa na)' : 'rejeitar a';
  const confirmacao = window.confirm(`Tem certeza que deseja ${acaoText} solicitação?`);
  if (!confirmacao) return;

  try {
    await api.put(`/api/solicitacoes/${id}/status`, { status });
    toast.success(`Solicitação ${status.toLowerCase()} com sucesso!`);
    await carregarSolicitacoes();
  } catch (error) {
    toast.error('Erro ao atualizar status.');
  }
};

const opcaoStandbyVigente = ref('ALTERAR');

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

const standbyVigenteAtual = computed(() => {
  if (abaAtiva.value !== 'STANDBY' || !form.value.codigo_paciente || !form.value.procedimento) {
    return null;
  }
  const cod = String(form.value.codigo_paciente);
  const procName = form.value.procedimento;
  
  const historicoProc = solicitacoes.value
    .filter(s => String(s.codigo_paciente) === cod && s.procedimento === procName && s.status === 'APROVADO')
    .sort((a, b) => (b.data_acao || b.data_criacao || '').localeCompare(a.data_acao || a.data_criacao || ''));
    
  if (historicoProc.length > 0 && historicoProc[0].tipo === 'STANDBY') {
    const s = historicoProc[0];
    const tempoRestante = calcularTempoStandbyRestante(s.tempo_standby, s.data_acao || s.data_criacao);
    return {
      solicitacaoOriginal: s,
      tempoOriginal: s.tempo_standby,
      tempoRestante: tempoRestante,
      dataAprovacao: s.data_acao || s.data_criacao
    };
  }
  return null;
});

const modalDescricao = ref<{ aberto: boolean; solic: any }>({
  aberto: false,
  solic: null
});

const abrirModalDescricao = (solic: any) => {
  modalDescricao.value = {
    aberto: true,
    solic: solic
  };
};

const formatarTipo = (tipo: string) => {
  switch (tipo) {
    case 'INSERIR':          return 'Inclusão';
    case 'EDITAR':           return 'Edição';
    case 'EXCLUIR':          return 'Exclusão';
    case 'STANDBY':          return 'Standby';
    case 'CANCELAR_STANDBY': return 'Cancelamento de Standby';
    default:                 return tipo;
  }
};

const getTipoBadgeClass = (tipo: string) => {
  switch (tipo) {
    case 'INSERIR':          return 'px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800 border border-green-200';
    case 'EDITAR':           return 'px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200';
    case 'EXCLUIR':          return 'px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800 border border-red-200';
    case 'STANDBY':          return 'px-2 py-0.5 rounded text-xs font-semibold bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'CANCELAR_STANDBY': return 'px-2 py-0.5 rounded text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200';
    default:                 return 'px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 text-gray-800';
  }
};

const getSwallisClass = (swallis: string) => {
  const base = 'px-2 py-0.5 rounded font-bold text-xs';
  switch (swallis) {
    case 'A1': return `${base} bg-red-100 text-red-800`;
    case 'A2': return `${base} bg-orange-100 text-orange-800`;
    case 'B':  return `${base} bg-yellow-100 text-yellow-800`;
    case 'C':  return `${base} bg-blue-100 text-blue-800`;
    case 'D':  return `${base} bg-gray-100 text-gray-700`;
    default:   return `${base} bg-gray-100 text-gray-700`;
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'PENDENTE':  return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800';
    case 'APROVADO':  return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800';
    case 'REJEITADO': return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800';
    default:          return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800';
  }
};

const carregarPacientesBase = async () => {
  try {
    const { data } = await api.get('/api/pacientes');
    pacientesBase.value = data;
  } catch (error) {
    console.error('Erro ao carregar pacientes base', error);
  }
};

const obterEstadoAnterior = (solic: any) => {
  const pacienteBase = pacientesBase.value.find(p => String(p.prontuario) === String(solic.codigo_paciente));
  
  let estado = {
    especialidade: pacienteBase ? pacienteBase.especialidade : '',
    procedimento: pacienteBase ? pacienteBase.procedimento : '',
    judicializado: pacienteBase ? (pacienteBase.judicializado || 'Não') : 'Não',
    swalis: pacienteBase ? (pacienteBase.swalis || pacienteBase.swallis || pacienteBase.Swalis || '') : '',
    medico_responsavel: pacienteBase ? (pacienteBase.medico_responsavel || '') : ''
  };
  
  const aprovadasAnteriores = solicitacoes.value
    .filter(s => 
      String(s.codigo_paciente) === String(solic.codigo_paciente) && 
      s.status === 'APROVADO' && 
      s.data_criacao < solic.data_criacao
    )
    .sort((a, b) => a.data_criacao.localeCompare(b.data_criacao));
    
  for (const s of aprovadasAnteriores) {
    if (s.tipo === 'INSERIR') {
      estado.especialidade = s.especialidade;
      estado.procedimento = s.procedimento;
      estado.judicializado = s.judicializado || 'Não';
      estado.swalis = s.swalis || s.swallis || s.Swalis || '';
      estado.medico_responsavel = s.medico_responsavel || '';
    } else if (s.tipo === 'EDITAR') {
      if (s.especialidade) estado.especialidade = s.especialidade;
      if (s.procedimento) estado.procedimento = s.procedimento;
      if (s.judicializado) estado.judicializado = s.judicializado;
      const sw = s.swalis || s.swallis || s.Swalis;
      if (sw) estado.swalis = sw;
      if (s.medico_responsavel) estado.medico_responsavel = s.medico_responsavel;
    }
  }
  
  return estado;
};

onMounted(() => {
  carregarSolicitacoes();
  carregarPacientesBase();
  carregarUsuariosLocais();
});
</script>
