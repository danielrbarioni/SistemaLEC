<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-800">Interações com o Sistema LEC da Rede HU Brasil</h1>
      <span class="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">Assistencial → Gestão da LEC</span>
    </div>

    <!-- Modal de Alerta de Acesso Restrito para Enfermeiros -->
    <div v-if="isEnfermeiro" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full border border-gray-100 overflow-hidden p-6 text-center space-y-4">
        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 text-red-600">
          <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900">Acesso Restrito</h3>
        <p class="text-sm text-gray-600 leading-relaxed">
          A funcionalidade do menu <strong>Solicitações LEC</strong> é voltada exclusivamente para os perfis <strong>Médico</strong> e <strong>Residente</strong>.
        </p>
        <div class="pt-2">
          <Button @click="router.push('/pacientes')" variant="primary" class="w-full justify-center">
            Ir para Pacientes
          </Button>
        </div>
      </div>
    </div>

    <!-- Formulário e Abas de Solicitação Unidos (Oculto para perfil OBSERVADOR, NENHUM ou Enfermeiro) -->
    <Card v-if="!isEnfermeiro && perfisStore.perfilAtivo.tipo !== 'OBSERVADOR' && perfisStore.perfilAtivo.tipo !== 'NENHUM'" class="overflow-hidden">
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

      <!-- Alerta de Modo de Edição de Solicitação Pendente -->
      <div v-if="modoEdicaoSolicitacao" class="mb-4 p-4 bg-amber-50 border-2 border-amber-300 rounded-xl text-xs text-amber-900 flex items-center justify-between shadow-sm">
        <div class="flex items-center space-x-2">
          <span class="text-base">✏️</span>
          <div>
            <span class="font-bold text-sm block">Modo de Edição de Solicitação #{{ solicitacaoEmEdicaoId }}</span>
            <span>Você está editando uma solicitação pendente. Modifique os dados necessários e clique em <strong>"Salvar Alterações"</strong>.</span>
          </div>
        </div>
        <button 
          type="button" 
          @click="cancelarEdicaoSolicitacao" 
          class="px-3 py-1.5 bg-white border border-amber-300 hover:bg-amber-100 text-amber-800 font-bold rounded-lg text-xs transition cursor-pointer"
        >
          ✕ Cancelar Edição
        </button>
      </div>

      <!-- Alerta indicando a origem dos dados quando buscados na Sede -->
      <div v-if="!modoEdicaoSolicitacao && abaAtiva !== 'INSERIR' && formCarregadoDaSede" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-xs text-green-800 flex items-center space-x-2">
        <span>✅ Dados da solicitação ativa carregados com sucesso da <strong>Solicitações LEC Sede</strong>.</span>
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
                @keydown.enter.prevent="buscarDados(false)"
                required
              />
              <Button type="button" @click="() => buscarDados(false)" :disabled="loadingBusca || !form.codigo_paciente" variant="info" class="whitespace-nowrap">
                {{ loadingBusca ? '...' : 'Buscar' }}
              </Button>
            </div>
            <p class="text-xs mt-1" :class="abaAtiva === 'INSERIR' && pacienteValidadoNoAghu ? (form.nome_paciente.includes('não identificado no AGHU') ? 'text-amber-600 font-semibold' : 'text-green-600 font-semibold') : 'text-gray-400'">
              {{ abaAtiva === 'INSERIR' 
                ? (pacienteValidadoNoAghu 
                    ? (form.nome_paciente.includes('não identificado no AGHU') ? '⚠️ Prontuário não localizado no AGHU (Confirmado para inclusão)' : '✓ Paciente validado no AGHU') 
                    : 'Digite o prontuário e clique em "Buscar" para validar no AGHU') 
                : 'Puxa dados do módulo Pacientes' 
              }}
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
              <option v-for="med in medicosDaEspecialidade" :key="med" :value="med" />
            </datalist>
          </div>
        </div>

        <!-- Categorização do Profissional (Exibida dinamicamente se o médico+especialidade tiver categorias cadastradas) -->
        <div v-if="categoriasDoMedicoSelecionado.length > 0 && (abaAtiva === 'INSERIR' || abaAtiva === 'EDITAR')" class="form-group bg-indigo-50/70 p-3.5 rounded-xl border border-indigo-200">
          <label for="categorizacao" class="form-label font-bold text-indigo-950 flex items-center space-x-1.5">
            <span>🏷️ Categorização do Profissional (Opcional)</span>
            <span class="text-[11px] font-normal text-indigo-600">— Classificação clínica definida pelo médico</span>
          </label>
          <select
            id="categorizacao"
            v-model="form.categorizacao"
            class="form-control bg-white"
            :disabled="camposEdicaoBloqueados"
          >
            <option value="">Sem categorização (Não classificado)</option>
            <option v-for="cat in categoriasDoMedicoSelecionado" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
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
          <Button 
            v-if="modoEdicaoSolicitacao" 
            type="button" 
            @click="cancelarEdicaoSolicitacao" 
            variant="secondary"
          >
            Cancelar Edição
          </Button>
          <Button 
            v-else 
            type="button" 
            @click="limparFormulario" 
            variant="secondary" 
            :disabled="(perfisStore.perfilAtivo.tipo as string) === 'OBSERVADOR'"
          >
            Limpar
          </Button>
          <Button 
            type="submit" 
            :disabled="submitting || (perfisStore.perfilAtivo.tipo as string) === 'OBSERVADOR' || (abaAtiva === 'INSERIR' && !pacienteValidadoNoAghu)" 
            :variant="modoEdicaoSolicitacao ? 'warning' : (abaAtiva === 'STANDBY' && standbyVigenteAtual && opcaoStandbyVigente === 'CANCELAR' ? 'danger' : 'primary')"
          >
            {{ (perfisStore.perfilAtivo.tipo as string) === 'OBSERVADOR' ? 'Somente Leitura' : (submitting ? 'Salvando...' : (modoEdicaoSolicitacao ? 'Salvar Alterações da Solicitação' : (abaAtiva === 'STANDBY' && standbyVigenteAtual && opcaoStandbyVigente === 'CANCELAR' ? 'Solicitar Cancelamento' : 'Enviar Solicitação'))) }}
          </Button>
        </div>
      </form>
    </Card>

    <!-- Tabela de Solicitações Enviadas (Oculta para Enfermeiro) -->
    <Card v-if="!isEnfermeiro" class="overflow-hidden">
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
            'flex-1 py-2 text-xs font-bold rounded-md transition duration-200 whitespace-nowrap px-3 flex items-center justify-center space-x-2',
            abaAcompanhamentoAtiva === aba.id 
              ? 'bg-indigo-600 text-white shadow-sm' 
              : 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'
          ]"
        >
          <span class="flex items-center space-x-1.5">
            <component :is="aba.icon" class="h-4 w-4" />
            <span>{{ aba.nome }}</span>
          </span>
          <span 
            v-if="contagemPendenciasPorTipo[aba.id] > 0"
            :class="[
              'px-2 py-0.5 text-[11px] font-bold rounded-full transition-colors',
              abaAcompanhamentoAtiva === aba.id
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'bg-red-600 text-white'
            ]"
          >
            {{ contagemPendenciasPorTipo[aba.id] }}
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
            list="filtro-especialidades-lista"
            :disabled="perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
            placeholder="Digite para pesquisar especialidade..."
            class="form-control text-xs"
            :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
          />
          <datalist id="filtro-especialidades-lista">
            <option v-for="esp in especialidadesFiltroLista" :key="esp" :value="esp" />
          </datalist>
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
      <div v-else class="relative">
        <!-- Barra de Rolagem Superior Sincronizada -->
        <div 
          ref="topScrollRef" 
          class="overflow-x-auto overflow-y-hidden h-2.5 bg-slate-100 border-b border-slate-200" 
          @scroll="onTopScroll"
          v-show="temOverflowHorizontal"
        >
          <div :style="{ width: larguraTabela + 'px', height: '1px' }"></div>
        </div>

        <div 
          ref="tableContainerRef" 
          class="overflow-x-auto" 
          @scroll="onBottomScroll"
        >
          <table ref="tableRef" class="min-w-full divide-y divide-gray-200 text-xs">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Data / Hora</th>
                <th class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">ID</th>
                <th class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Tipo</th>
                <th class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Especialidade</th>
                <th v-if="abaAcompanhamentoAtiva !== 'EDITAR'" class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider min-w-[260px] max-w-sm">Procedimento</th>
                <th v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider min-w-[320px] max-w-md">Procedimento Anterior</th>
                <th v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider min-w-[320px] max-w-md">Novo Procedimento</th>
                <th class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider">Prontuário / Paciente</th>
                <th class="px-3 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Judicial</th>
                <th class="px-3 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Swalis</th>
                <th class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider">Médico</th>
                <th class="px-3 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Status</th>
                <th v-if="abaAcompanhamentoAtiva === 'STANDBY'" class="px-3 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Tempo Standby</th>
                <th class="px-3 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Descrição</th>
                <th v-if="subAbaAcompanhamento === 'CONCLUIDO'" class="px-3 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">DATA/HORA AÇÃO</th>
                <th v-if="subAbaAcompanhamento !== 'CONCLUIDO'" class="px-3 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="solic in solicitacoesFiltradas" :key="solic.id" class="hover:bg-slate-50 transition duration-150">
                <!-- Data/Hora Criação -->
                <td class="px-3 py-2.5 whitespace-nowrap font-mono text-[11px] text-gray-600">
                  {{ formatarDataHora(solic.data_criacao) }}
                </td>

                <!-- ID -->
                <td class="px-3 py-2.5 whitespace-nowrap text-gray-500 font-mono text-[11px]">#{{ solic.id }}</td>

                <!-- Tipo -->
                <td class="px-3 py-2.5 whitespace-nowrap">
                  <span :class="getTipoBadgeClass(solic.tipo)">{{ formatarTipo(solic.tipo) }}</span>
                </td>
                
                <!-- Especialidade -->
                <td class="px-3 py-2.5 text-gray-700 font-semibold whitespace-nowrap">
                  {{ solic.especialidade || '—' }}
                </td>
                
                <!-- Procedimento (Não EDITAR) -->
                <td v-if="abaAcompanhamentoAtiva !== 'EDITAR'" class="px-3 py-2.5 text-gray-800 font-medium min-w-[260px] max-w-sm break-words whitespace-normal leading-snug" :title="solic.procedimento">
                  {{ solic.procedimento || '—' }}
                </td>
                
                <!-- Procedimento Anterior (EDITAR) -->
                <td v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-3 py-2.5 text-gray-500 italic min-w-[320px] max-w-md break-words whitespace-normal leading-snug" :title="solic.procedimento_anterior">
                  {{ solic.procedimento_anterior || '—' }}
                </td>
                
                <!-- Novo Procedimento (EDITAR) -->
                <td v-if="abaAcompanhamentoAtiva === 'EDITAR'" class="px-3 py-2.5 min-w-[320px] max-w-md">
                  <div v-if="solic.procedimento === solic.procedimento_anterior || !solic.procedimento_anterior" class="text-gray-400 italic" title="Não houve mudança">
                    Não houve mudança
                  </div>
                  <div v-else class="font-bold text-blue-700 bg-blue-50 px-2.5 py-1.5 rounded border border-blue-200 block max-w-full break-words whitespace-normal leading-snug" :title="solic.procedimento">
                    {{ solic.procedimento }}
                  </div>
                </td>

                <!-- Prontuário / Paciente -->
                <td class="px-3 py-2.5 text-gray-700">
                  <div class="font-mono font-bold text-indigo-900">#{{ solic.codigo_paciente }}</div>
                  <div class="font-medium text-gray-800 truncate max-w-[180px]" :title="solic.nome_paciente">{{ solic.nome_paciente }}</div>
                </td>

                <!-- Judicial -->
                <td class="px-3 py-2.5 text-center whitespace-nowrap">
                  <span 
                    v-if="solic.judicializado === 'Sim'" 
                    :class="[
                      'px-2 py-0.5 rounded-full font-semibold bg-amber-100 text-amber-800 text-[10px]',
                      abaAcompanhamentoAtiva === 'EDITAR' && solic.judicializado !== obterEstadoAnterior(solic).judicializado ? 'ring-2 ring-yellow-400 font-bold bg-yellow-100 text-yellow-900 border border-yellow-300' : ''
                    ]"
                  >
                    ⚖️ Sim
                  </span>
                  <span 
                    v-else 
                    :class="[
                      'text-gray-400 text-[11px]',
                      abaAcompanhamentoAtiva === 'EDITAR' && solic.judicializado !== obterEstadoAnterior(solic).judicializado ? 'bg-yellow-100 text-yellow-800 font-bold px-1.5 py-0.5 rounded ring-2 ring-yellow-300' : ''
                    ]"
                  >
                    Não
                  </span>
                </td>

                <!-- Swalis -->
                <td class="px-3 py-2.5 text-center whitespace-nowrap font-mono text-xs">
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
                      'text-gray-400 text-[11px]',
                      abaAcompanhamentoAtiva === 'EDITAR' && '' !== obterEstadoAnterior(solic).swalis ? 'bg-yellow-100 text-yellow-800 font-bold px-1.5 py-0.5 rounded ring-2 ring-yellow-300' : ''
                    ]"
                  >
                    —
                  </span>
                </td>

                <!-- Médico Responsável -->
                <td 
                  class="px-3 py-2.5 whitespace-nowrap text-xs"
                  :class="[
                    abaAcompanhamentoAtiva === 'EDITAR' && solic.medico_responsavel !== obterEstadoAnterior(solic).medico_responsavel ? 'text-blue-700 font-bold bg-yellow-50 px-1 rounded ring-2 ring-yellow-300' : 'text-gray-700 font-medium'
                  ]"
                >
                  {{ solic.medico_responsavel || '—' }}
                </td>

                <!-- Status -->
                <td class="px-3 py-2.5 text-center whitespace-nowrap">
                  <span :class="getStatusBadgeClass(solic.status)">{{ solic.status }}</span>
                </td>

                <!-- Tempo Standby (Apenas na aba STANDBY) -->
                <td v-if="abaAcompanhamentoAtiva === 'STANDBY'" class="px-3 py-2.5 text-center text-xs text-gray-600 whitespace-nowrap">
                  <div v-if="solic.tempo_standby" class="font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 inline-block">
                    ⏱️ {{ solic.tempo_standby }}d
                  </div>
                  <div v-else class="text-gray-400">—</div>
                </td>

                <!-- Descrição com botão modal -->
                <td class="px-3 py-2.5 text-center whitespace-nowrap">
                  <button 
                    type="button"
                    @click="abrirModalDescricao(solic)" 
                    class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded border border-indigo-200 transition cursor-pointer text-xs flex items-center space-x-1 mx-auto"
                    title="Clique para ver todos os detalhes da solicitação e da resposta"
                  >
                    <span>📄 Ver Descrição</span>
                  </button>
                </td>

                <!-- Data/Hora Ação (Condicional para Concluídos) -->
                <td v-if="subAbaAcompanhamento === 'CONCLUIDO'" class="px-3 py-2.5 whitespace-nowrap font-mono text-[11px] text-gray-700">
                  {{ formatarDataHora(solic.data_acao) }}
                </td>

                <!-- Ações (Condicional para Pendentes) -->
                <td v-if="subAbaAcompanhamento !== 'CONCLUIDO'" class="px-3 py-2.5 text-center whitespace-nowrap">
                  <div v-if="solic.status === 'PENDENTE' && (perfisStore.perfilAtivo?.tipo === 'GESTAO_LEC' || perfisStore.perfilAtivo?.tipo === 'ADMIN')" class="flex items-center justify-center space-x-1.5">
                    <Button 
                      v-if="solic.tipo !== 'EXCLUIR'" 
                      @click="iniciarEdicaoSolicitacao(solic)" 
                      variant="secondary" 
                      size="sm" 
                      title="Editar dados desta solicitação pendente"
                    >
                      ✏️ Editar
                    </Button>
                    <Button @click="atualizarStatus(solic.id, 'APROVADO')" variant="success" size="sm">
                      Aprovar
                    </Button>
                    <Button @click="abrirModalRejeicao(solic)" variant="danger" size="sm">
                      Rejeitar
                    </Button>
                  </div>
                  <div v-else-if="solic.status === 'PENDENTE' && perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE'" class="flex items-center justify-center space-x-1.5">
                    <Button 
                      v-if="solic.tipo !== 'EXCLUIR'" 
                      @click="iniciarEdicaoSolicitacao(solic)" 
                      variant="secondary" 
                      size="sm" 
                      title="Editar dados desta solicitação pendente"
                    >
                      ✏️ Editar
                    </Button>
                    <Button @click="solicitarCancelamento(solic)" variant="danger" size="sm">
                      Cancelar
                    </Button>
                  </div>
                  <div v-else-if="solic.status === 'PENDENTE' && solic.tipo !== 'EXCLUIR' && (perfisStore.perfilAtivo?.tipo as string) !== 'OBSERVADOR'" class="flex justify-center">
                    <Button @click="iniciarEdicaoSolicitacao(solic)" variant="secondary" size="sm" title="Editar dados desta solicitação pendente">
                      ✏️ Editar
                    </Button>
                  </div>
                  <span v-else class="text-gray-400">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>

    <!-- Modal de Descrição / Detalhes Completos da Solicitação e Resposta -->
    <div v-if="modalDescricao.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-xl w-full p-6 space-y-4 border border-gray-200">
        <div class="flex justify-between items-start border-b border-gray-150 pb-3">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Detalhes da Solicitação</h3>
            <p class="text-xs text-gray-500">
              Solicitação #{{ modalDescricao.solic?.id }} · {{ formatarTipo(modalDescricao.solic?.tipo) }}
            </p>
          </div>
          <button @click="modalDescricao.aberto = false" class="text-gray-400 hover:text-gray-600 text-lg font-bold p-1">
            ✕
          </button>
        </div>

        <div v-if="modalDescricao.solic" class="space-y-4 text-xs text-gray-700 max-h-[70vh] overflow-y-auto pr-1">
          <!-- Bloco 1: Dados da Solicitação Inicial -->
          <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2.5">
            <span class="text-[11px] font-bold text-indigo-700 uppercase tracking-wider block border-b border-slate-200 pb-1">
              📌 Dados da Solicitação
            </span>

            <!-- Resumo das Alterações Solicitadas (apenas para solicitações de EDITAR) -->
            <div v-if="modalDescricao.solic.tipo === 'EDITAR'" class="p-3 bg-amber-50/90 border border-amber-200 rounded-lg space-y-2">
              <div class="flex items-center space-x-1.5 text-amber-900 font-bold text-xs border-b border-amber-200/80 pb-1">
                <span>✏️</span>
                <span>Campos Alterados nesta Solicitação de Edição:</span>
              </div>
              <div v-if="obterListaMudancas(modalDescricao.solic).length > 0" class="space-y-1.5">
                <div 
                  v-for="mudanca in obterListaMudancas(modalDescricao.solic)" 
                  :key="mudanca.campo"
                  class="flex flex-col sm:flex-row sm:items-center text-xs text-amber-950 bg-white/80 p-2 rounded-md border border-amber-200/70"
                >
                  <span class="font-bold text-amber-900 sm:w-44 shrink-0">{{ mudanca.campo }}:</span>
                  <div class="flex items-center space-x-1.5 flex-wrap">
                    <span class="text-gray-500 line-through text-[11px]">{{ mudanca.anterior || '—' }}</span>
                    <span class="font-bold text-blue-800 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 text-xs">
                      ➔ {{ mudanca.novo }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-else class="text-gray-500 italic text-[11px]">
                Nenhum campo estrutural alterado (apenas justificativa clínica).
              </div>
            </div>

            <!-- Grade de Campos da Solicitação -->
            <div class="grid grid-cols-2 gap-2.5 text-xs">
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Data/Hora Solicitação:</span>
                <span class="font-mono font-medium text-gray-900">{{ formatarDataHora(modalDescricao.solic.data_criacao) }}</span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Usuário Solicitante:</span>
                <span class="font-medium text-gray-900">
                  {{ modalDescricao.solic.usuario || '—' }} 
                  <span v-if="modalDescricao.solic.perfil_executor" class="text-[10px] text-gray-500 font-normal">({{ modalDescricao.solic.perfil_executor }})</span>
                </span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Paciente:</span>
                <span class="font-bold text-gray-900">{{ modalDescricao.solic.nome_paciente }}</span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Nº Prontuário:</span>
                <span class="font-mono font-bold text-gray-900">#{{ modalDescricao.solic.codigo_paciente }}</span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Especialidade:</span>
                <div v-if="modalDescricao.solic.tipo === 'EDITAR' && obterMudancaCampo(modalDescricao.solic, 'especialidade')" class="space-y-0.5">
                  <div class="text-[11px] text-gray-500 line-through">{{ obterMudancaCampo(modalDescricao.solic, 'especialidade')?.anterior }}</div>
                  <div class="font-semibold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 inline-block text-xs">
                    ➔ {{ modalDescricao.solic.especialidade }}
                  </div>
                </div>
                <span v-else class="font-semibold text-gray-800">{{ modalDescricao.solic.especialidade }}</span>
              </div>

              <!-- Procedimento -->
              <div class="col-span-2">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Procedimento:</span>
                <div v-if="modalDescricao.solic.tipo === 'EDITAR' && (modalDescricao.solic.procedimento_anterior && modalDescricao.solic.procedimento_anterior !== modalDescricao.solic.procedimento)" class="space-y-1 p-2 bg-blue-50/40 rounded border border-blue-100">
                  <div class="text-[11px] text-gray-600 flex items-start space-x-1.5">
                    <span class="font-bold text-gray-400 shrink-0">Anterior:</span>
                    <span class="line-through text-gray-500">{{ modalDescricao.solic.procedimento_anterior }}</span>
                  </div>
                  <div class="text-xs text-blue-900 flex items-start space-x-1.5">
                    <span class="font-bold text-blue-700 shrink-0">Novo:</span>
                    <span class="font-bold text-blue-800 bg-blue-100/70 px-2 py-0.5 rounded border border-blue-300 inline-block">{{ modalDescricao.solic.procedimento }}</span>
                  </div>
                </div>
                <span v-else class="font-semibold text-gray-800">{{ modalDescricao.solic.procedimento }}</span>
              </div>

              <!-- Judicialização -->
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Judicialização:</span>
                <div v-if="modalDescricao.solic.tipo === 'EDITAR' && obterMudancaCampo(modalDescricao.solic, 'judicializado')" class="space-y-0.5">
                  <div class="text-[11px] text-gray-500 line-through">{{ obterMudancaCampo(modalDescricao.solic, 'judicializado')?.anterior }}</div>
                  <div class="font-bold text-amber-800 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 inline-block text-xs">
                    ➔ {{ modalDescricao.solic.judicializado }}
                  </div>
                </div>
                <span v-else class="font-medium text-gray-800">{{ modalDescricao.solic.judicializado || 'Não' }}</span>
              </div>

              <!-- Swalis -->
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Swalis:</span>
                <div v-if="modalDescricao.solic.tipo === 'EDITAR' && obterMudancaCampo(modalDescricao.solic, 'swalis')" class="space-y-0.5">
                  <div class="text-[11px] text-gray-500 line-through">{{ obterMudancaCampo(modalDescricao.solic, 'swalis')?.anterior }}</div>
                  <div class="font-bold text-blue-800 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 inline-block text-xs">
                    ➔ {{ modalDescricao.solic.swalis || modalDescricao.solic.swallis || modalDescricao.solic.Swalis }}
                  </div>
                </div>
                <span v-else class="font-medium text-gray-800">{{ modalDescricao.solic.swalis || modalDescricao.solic.swallis || modalDescricao.solic.Swalis || '—' }}</span>
              </div>

              <!-- Médico Responsável -->
              <div class="col-span-2">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Médico Responsável:</span>
                <div v-if="modalDescricao.solic.tipo === 'EDITAR' && obterMudancaCampo(modalDescricao.solic, 'medico_responsavel')" class="space-y-0.5">
                  <div class="text-[11px] text-gray-500 line-through">{{ obterMudancaCampo(modalDescricao.solic, 'medico_responsavel')?.anterior }}</div>
                  <div class="font-bold text-blue-800 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 inline-block text-xs">
                    ➔ {{ modalDescricao.solic.medico_responsavel }}
                  </div>
                </div>
                <span v-else class="font-medium text-gray-800">{{ modalDescricao.solic.medico_responsavel || '—' }}</span>
              </div>

              <!-- Categorização do Profissional -->
              <div class="col-span-2">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Categorização do Profissional:</span>
                <div v-if="modalDescricao.solic.tipo === 'EDITAR' && obterMudancaCampo(modalDescricao.solic, 'categorizacao')" class="space-y-0.5">
                  <div class="text-[11px] text-gray-500 line-through">{{ obterMudancaCampo(modalDescricao.solic, 'categorizacao')?.anterior }}</div>
                  <div class="font-bold text-indigo-800 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-200 inline-block text-xs">
                    ➔ {{ modalDescricao.solic.categorizacao || 'Sem categorização' }}
                  </div>
                </div>
                <span v-else-if="modalDescricao.solic.categorizacao" class="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200 inline-block text-xs">
                  🏷️ {{ modalDescricao.solic.categorizacao }}
                </span>
                <span v-else class="text-gray-400 italic">Sem categorização</span>
              </div>
            </div>

            <div class="pt-2 border-t border-slate-200/80">
              <label class="block font-bold text-gray-700 text-[11px] mb-1">Justificativa / Indicação Clínica:</label>
              <div class="p-2.5 bg-white border border-slate-200 rounded-lg text-slate-800 text-xs leading-relaxed whitespace-pre-wrap font-medium">
                {{ modalDescricao.solic.detalhes || modalDescricao.solic.campos_modificados || 'Nenhuma justificativa detalhada foi fornecida.' }}
              </div>
            </div>
          </div>

          <!-- Bloco 2: Dados da Resposta da Gestão LEC (se concluída/respondida) -->
          <div 
            v-if="modalDescricao.solic.status !== 'PENDENTE' || modalDescricao.solic.dados_resposta" 
            class="p-3.5 rounded-xl border space-y-2.5"
            :class="modalDescricao.solic.status === 'REJEITADO' ? 'bg-red-50/70 border-red-200' : modalDescricao.solic.status === 'APROVADO' ? 'bg-emerald-50/70 border-emerald-200' : 'bg-gray-50 border-gray-200'"
          >
            <div 
              class="flex justify-between items-center border-b pb-1"
              :class="modalDescricao.solic.status === 'REJEITADO' ? 'border-red-200' : modalDescricao.solic.status === 'APROVADO' ? 'border-emerald-200' : 'border-gray-200'"
            >
              <span 
                class="text-[11px] font-bold uppercase tracking-wider"
                :class="modalDescricao.solic.status === 'REJEITADO' ? 'text-red-800' : modalDescricao.solic.status === 'APROVADO' ? 'text-emerald-800' : 'text-gray-700'"
              >
                💬 Resposta da Gestão LEC
              </span>
              <span :class="getStatusBadgeClass(modalDescricao.solic.status)">{{ modalDescricao.solic.status }}</span>
            </div>

            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Data/Hora da Resposta:</span>
                <span class="font-mono font-medium text-gray-900">
                  {{ formatarDataHora(modalDescricao.solic.dados_resposta?.data_hora || modalDescricao.solic.data_acao || modalDescricao.solic.data_criacao) }}
                </span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Respondido por:</span>
                <span class="font-medium text-gray-900">
                  {{ modalDescricao.solic.dados_resposta?.usuario || 'Gestão LEC' }}
                  <span v-if="modalDescricao.solic.dados_resposta?.perfil" class="text-[10px] text-gray-500 font-normal">({{ modalDescricao.solic.dados_resposta.perfil }})</span>
                </span>
              </div>
            </div>

            <div class="pt-2 border-t" :class="modalDescricao.solic.status === 'REJEITADO' ? 'border-red-200' : 'border-slate-200'">
              <label 
                class="block font-bold text-xs mb-1"
                :class="modalDescricao.solic.status === 'REJEITADO' ? 'text-red-900' : 'text-gray-700'"
              >
                {{ modalDescricao.solic.status === 'REJEITADO' ? 'Justificativa / Motivo da Rejeição:' : 'Observações da Resposta:' }}
              </label>
              <div 
                class="p-2.5 bg-white border rounded-lg text-xs leading-relaxed whitespace-pre-wrap font-medium"
                :class="modalDescricao.solic.status === 'REJEITADO' ? 'border-red-300 text-red-950 font-semibold' : 'border-slate-200 text-slate-800'"
              >
                {{ extrairJustificativaResposta(modalDescricao.solic) }}
              </div>
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

    <!-- Modal de Justificativa Obrigatória de Rejeição -->
    <div v-if="modalRejeicao.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 border border-gray-200">
        <div class="flex justify-between items-start border-b border-gray-150 pb-3">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Rejeitar Solicitação</h3>
            <p class="text-xs text-gray-500">
              Solicitação #{{ modalRejeicao.solic?.id }} · {{ formatarTipo(modalRejeicao.solic?.tipo) }}
            </p>
          </div>
          <button @click="fecharModalRejeicao" class="text-gray-400 hover:text-gray-600 text-lg font-bold p-1">
            ✕
          </button>
        </div>

        <div v-if="modalRejeicao.solic" class="space-y-3 text-xs text-gray-700">
          <div class="bg-red-50 p-3 rounded-lg border border-red-100 text-red-900 space-y-1">
            <div><span class="font-bold">Paciente:</span> {{ modalRejeicao.solic.nome_paciente }} (#{{ modalRejeicao.solic.codigo_paciente }})</div>
            <div><span class="font-bold">Especialidade:</span> {{ modalRejeicao.solic.especialidade }}</div>
            <div>
              <span class="font-bold">Procedimento:</span> 
              <span v-if="modalRejeicao.solic.tipo === 'EDITAR' && modalRejeicao.solic.procedimento_anterior && modalRejeicao.solic.procedimento_anterior !== modalRejeicao.solic.procedimento">
                <span class="line-through text-red-700/80 mr-1">{{ modalRejeicao.solic.procedimento_anterior }}</span>
                <span class="font-bold">➔ {{ modalRejeicao.solic.procedimento }}</span>
              </span>
              <span v-else>{{ modalRejeicao.solic.procedimento }}</span>
            </div>
          </div>

          <div class="space-y-1">
            <label for="justificativa_rejeicao" class="block font-bold text-gray-800 text-xs">
              Motivo / Justificativa da Rejeição <span class="text-red-500">*</span>
            </label>
            <textarea
              id="justificativa_rejeicao"
              v-model="modalRejeicao.justificativa"
              rows="3"
              placeholder="Descreva detalhadamente o motivo pelo qual esta solicitação está sendo rejeitada..."
              class="form-control text-xs"
              :class="{ 'border-red-500 ring-1 ring-red-500': modalRejeicao.erro }"
            ></textarea>
            <p v-if="modalRejeicao.erro" class="text-red-600 text-[11px] font-semibold">
              {{ modalRejeicao.erro }}
            </p>
          </div>
        </div>

        <div class="flex justify-end space-x-2 pt-3 border-t border-gray-100">
          <Button @click="fecharModalRejeicao" variant="secondary" size="sm">
            Voltar
          </Button>
          <Button @click="confirmarRejeicao" variant="danger" size="sm" :disabled="submittingRejeicao">
            {{ submittingRejeicao ? 'Rejeitando...' : 'Confirmar Rejeição' }}
          </Button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação de Cancelamento -->
    <div v-if="modalCancelar.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4 border border-gray-200">
        <div class="flex justify-between items-start border-b border-gray-150 pb-3">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Confirmar Cancelamento</h3>
            <p class="text-xs text-gray-500">
              Solicitação #{{ modalCancelar.solic?.id }} · {{ formatarTipo(modalCancelar.solic?.tipo) }}
            </p>
          </div>
          <button @click="modalCancelar.aberto = false" class="text-gray-400 hover:text-gray-600 text-lg font-bold">
            ✕
          </button>
        </div>

        <div v-if="modalCancelar.solic" class="space-y-3 text-xs text-gray-700">
          <p class="text-sm text-gray-800">
            Tem certeza que deseja cancelar esta solicitação?
          </p>

          <div class="bg-red-50 p-3 rounded-lg border border-red-100 text-red-900 space-y-1">
            <div><span class="font-bold">Paciente:</span> {{ modalCancelar.solic.nome_paciente }}</div>
            <div><span class="font-bold">Prontuário:</span> #{{ modalCancelar.solic.codigo_paciente }}</div>
            <div>
              <span class="font-bold">Procedimento:</span> 
              <span v-if="modalCancelar.solic.tipo === 'EDITAR' && modalCancelar.solic.procedimento_anterior && modalCancelar.solic.procedimento_anterior !== modalCancelar.solic.procedimento">
                <span class="line-through text-red-700/80 mr-1">{{ modalCancelar.solic.procedimento_anterior }}</span>
                <span class="font-bold">➔ {{ modalCancelar.solic.procedimento }}</span>
              </span>
              <span v-else>{{ modalCancelar.solic.procedimento }}</span>
            </div>
            <div><span class="font-bold">Especialidade:</span> {{ modalCancelar.solic.especialidade }}</div>
          </div>
          
          <p class="text-gray-500 italic text-[11px]">
            Esta ação não poderá ser desfeita e a solicitação será movida para o histórico como cancelada.
          </p>
        </div>

        <div class="flex justify-end space-x-2 pt-3 border-t border-gray-100">
          <Button @click="modalCancelar.aberto = false" variant="secondary" size="sm">
            Voltar
          </Button>
          <Button @click="confirmarCancelamento" variant="danger" size="sm">
            Sim, Cancelar Solicitação
          </Button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação para Prontuário Não Identificado no AGHU -->
    <div v-if="modalConfirmacaoProntuarioNaoLocalizado.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 border border-gray-200">
        <div class="flex items-start space-x-3">
          <div class="p-2.5 bg-amber-100 text-amber-800 rounded-full text-xl flex-shrink-0">
            ⚠️
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-900">Atenção: Prontuário não localizado</h3>
            <p class="text-xs text-gray-500 mt-0.5">
              Prontuário <strong>#{{ modalConfirmacaoProntuarioNaoLocalizado.prontuario }}</strong>
            </p>
          </div>
        </div>

        <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-2">
          <p class="font-medium text-xs leading-relaxed">
            Número de prontuário não identificado no AGHU. Deseja continuar com a solicitação de inclusão desse prontuário mesmo assim?
          </p>
          <p class="text-[11px] text-amber-700 italic">
            Caso continue, o nome do paciente será registrado como "Prontuário {{ modalConfirmacaoProntuarioNaoLocalizado.prontuario }} não identificado no AGHU".
          </p>
        </div>

        <div class="flex justify-end space-x-2 pt-2 border-t border-gray-150">
          <Button @click="confirmarInserirNovoProntuario" variant="secondary" size="sm">
            Inserir novo prontuário
          </Button>
          <Button @click="confirmarContinuarSemAghu" variant="primary" size="sm">
            Continuar
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
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
import { formatarNomeProcedimento, desduplicarProcedimentos } from '../utils/procedimentoHelper';
import { fetchProcedimentosAghuPorEspecialidade } from '../utils/especialidadeAghuMap';

const toast = useToast();
const router = useRouter();
const perfisStore = usePerfisStore();
const authStore = useAuthStore();

const isEnfermeiro = computed(() => {
  const perfilNome = perfisStore.perfilAtivo?.nome?.toLowerCase() || '';
  const perfilTipo = perfisStore.perfilAtivo?.tipo || '';
  const userRole = (authStore.user as any)?.funcao?.toLowerCase() || '';
  return perfilTipo === 'EPO_GENERALISTA' || perfilNome.includes('epo generalista') || perfilNome.includes('enfermeiro') || userRole.includes('enfermeiro');
});

const especialidades = computed(() => {
  const perfis = perfisStore.perfis;
  const lista = perfis
    .filter(p => p.tipo === 'ESPECIALIDADE' || (p.especialidade && p.tipo !== 'ADMIN' && p.tipo !== 'GESTAO_LEC'))
    .map(p => (p.especialidade || p.nome).trim())
    .filter((nome, index, self) => nome && self.indexOf(nome) === index)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'));

  return lista.map(nome => ({
    nome,
    procedimentos: []
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
  tempo_standby: undefined as number | undefined,
  categorizacao: ''
});

const pacienteValidadoNoAghu = ref(false);
const modoEdicaoSolicitacao = ref(false);
const solicitacaoEmEdicaoId = ref<string | null>(null);

const modalConfirmacaoProntuarioNaoLocalizado = ref({
  aberto: false,
  prontuario: ''
});

const confirmarInserirNovoProntuario = () => {
  modalConfirmacaoProntuarioNaoLocalizado.value.aberto = false;
  form.value.codigo_paciente = '';
  limparFormulario();
};

const confirmarContinuarSemAghu = () => {
  const cod = modalConfirmacaoProntuarioNaoLocalizado.value.prontuario || form.value.codigo_paciente;
  modalConfirmacaoProntuarioNaoLocalizado.value.aberto = false;
  form.value.nome_paciente = `Prontuário ${cod} não identificado no AGHU`;
  form.value.dt_nascimento = '';
  form.value.nome_mae = '';
  pacienteValidadoNoAghu.value = true;
  toast.info(`Prosseguindo com a solicitação para o Prontuário #${cod}.`);
};

// Invalida a busca e limpa os dados do paciente ao alterar o número do prontuário
watch(() => form.value.codigo_paciente, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    pacienteValidadoNoAghu.value = false;
    form.value.nome_paciente = '';
    form.value.dt_nascimento = '';
    form.value.nome_mae = '';
    formCarregadoDaSede.value = false;
    procedimentosPaciente.value = [];
    procedimentoSelecionadoParaEdicao.value = null;
  }
});

const procedimentosAghuMap = ref<Record<string, string[]>>({});
const carregandoProcedimentosAghu = ref(false);

watch(() => form.value.especialidade, async (newEsp) => {
  if (!newEsp) return;
  const espTrim = newEsp.trim();
  if (!procedimentosAghuMap.value[espTrim]) {
    carregandoProcedimentosAghu.value = true;
    try {
      const procs = await fetchProcedimentosAghuPorEspecialidade(espTrim);
      if (procs.length > 0) {
        procedimentosAghuMap.value[espTrim] = procs;
      }
    } catch (err) {
      console.error(`Erro ao buscar procedimentos do AGHU para ${espTrim}:`, err);
    } finally {
      carregandoProcedimentosAghu.value = false;
    }
  }
}, { immediate: true });

// Procedimentos filtrados pela especialidade selecionada (unindo AGHU e histórico com preferência rigorosa ao ID do AGHU)
const procedimentosDaEspecialidade = computed(() => {
  const espName = form.value.especialidade ? form.value.especialidade.trim() : '';
  if (!espName) return [];
  const espNorm = espName.toLowerCase();

  // Lista obtida dinamicamente do AGHU para a especialidade
  let listFromAghu: string[] = [];
  for (const [key, list] of Object.entries(procedimentosAghuMap.value)) {
    const keyNorm = key.toLowerCase().trim();
    if (keyNorm === espNorm || keyNorm.includes(espNorm) || espNorm.includes(keyNorm)) {
      listFromAghu = list;
      break;
    }
  }

  const extraProcs: string[] = [];
  for (const s of solicitacoes.value) {
    if (s.especialidade && s.procedimento) {
      const sEspNorm = s.especialidade.toLowerCase().trim();
      if (sEspNorm.includes(espNorm) || espNorm.includes(sEspNorm)) {
        extraProcs.push(s.procedimento);
      }
    }
  }
  for (const p of pacientesBase.value) {
    if (p.especialidade && p.procedimento) {
      const pEspNorm = p.especialidade.toLowerCase().trim();
      if (pEspNorm.includes(espNorm) || espNorm.includes(pEspNorm)) {
        extraProcs.push(p.procedimento);
      }
    }
  }

  const raw = [...listFromAghu, ...extraProcs];
  return desduplicarProcedimentos(raw);
});

// Lista de especialidades dos perfis criados no menu Perfis (para a caixa de listagem de Especialidade)
const especialidadesFiltroLista = computed(() => {
  const perfis = perfisStore.perfis;
  const lista = perfis
    .filter(p => p.tipo === 'ESPECIALIDADE' || (p.especialidade && p.tipo !== 'ADMIN' && p.tipo !== 'GESTAO_LEC'))
    .map(p => (p.especialidade || p.nome).trim())
    .filter((nome, index, self) => nome && self.indexOf(nome) === index)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'));

  return lista;
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

// Contagem de solicitações PENDENTES por tipo (respeitando o filtro de especialidade do perfil ativo)
const contagemPendenciasPorTipo = computed(() => {
  const counts: Record<string, number> = {
    INSERIR: 0,
    EDITAR: 0,
    STANDBY: 0,
    EXCLUIR: 0
  };

  const activeSpecialty = (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo?.especialidade)
    ? perfisStore.perfilAtivo.especialidade.toLowerCase()
    : null;

  solicitacoes.value.forEach(s => {
    if (s.status === 'PENDENTE') {
      if (!activeSpecialty || (s.especialidade && s.especialidade.toLowerCase().includes(activeSpecialty))) {
        if (counts[s.tipo] !== undefined) {
          counts[s.tipo]++;
        }
      }
    }
  });

  return counts;
});

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

// Categorizações do Profissional
const categorizacoes = ref<any[]>([]);

const carregarCategorizacoes = async () => {
  try {
    const { data } = await api.get('/api/categorizacoes-profissionais');
    categorizacoes.value = data;
  } catch (error) {
    console.error('Erro ao carregar categorizacoes:', error);
  }
};

const categoriasDoMedicoSelecionado = computed(() => {
  const med = (form.value.medico_responsavel || '').trim().toUpperCase();
  const esp = (especialidadeForm.value || '').trim().toUpperCase();
  if (!med || !esp) return [];

  const found = categorizacoes.value.find(c =>
    c.especialidade === esp && (c.medico === med || med.includes(c.medico) || c.medico.includes(med))
  );
  return found ? (found.categorias || []) : [];
});

// Quando troca o médico responsável na edição, limpa a categorização
watch(() => form.value.medico_responsavel, (novoMedico, antigoMedico) => {
  if (antigoMedico && novoMedico && antigoMedico.trim().toUpperCase() !== novoMedico.trim().toUpperCase()) {
    form.value.categorizacao = '';
  }
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
  // Separamos todas as respostas para mapeamento rápido de dados da resposta
  const respostasMap = new Map<string, any>();
  const respostasPorChave = new Map<string, any>();

  for (const s of solicitacoes.value) {
    if (s.evento_tipo === 'RESPOSTA' || s.is_resposta) {
      if (s.detalhes && s.detalhes.includes('#')) {
        const match = s.detalhes.match(/#([a-zA-Z0-9_-]+)/);
        if (match && match[1]) {
          respostasMap.set(match[1], s);
        }
      }
      const key = `${s.codigo_paciente}||${s.tipo}||${s.especialidade}||${s.procedimento}`;
      respostasPorChave.set(key, s);
    }
  }

  // Apenas solicitações originais (desconsidera linhas avulsas de RESPOSTA ou ALTERAÇÃO na listagem)
  let list = solicitacoes.value.filter(s => s.evento_tipo !== 'RESPOSTA' && !s.is_resposta && s.evento_tipo !== 'ALTERACAO' && s.evento_tipo !== 'EDICAO');
  
  // 1. Filtra pelo tipo correspondente à aba de acompanhamento (Inclusão, Edição, Standby, Exclusão)
  list = list.filter(s => s.tipo === abaAcompanhamentoAtiva.value);

  // 2. Filtra pelo status correspondente à sub-aba (PENDENTE ou CONCLUIDO)
  if (subAbaAcompanhamento.value === 'PENDENTE') {
    list = list.filter(s => s.status === 'PENDENTE');
  } else {
    list = list.filter(s => s.status === 'APROVADO' || s.status === 'REJEITADO' || s.status === 'CANCELADO');
  }

  // 3. Associa os dados da resposta a cada solicitação
  list = list.map(s => {
    const resp = respostasMap.get(s.id) || respostasPorChave.get(`${s.codigo_paciente}||${s.tipo}||${s.especialidade}||${s.procedimento}`);
    return {
      ...s,
      dados_resposta: resp ? {
        data_hora: resp.data_criacao || resp.data_acao,
        usuario: resp.usuario || resp.username,
        perfil: resp.perfil_executor,
        detalhes: resp.detalhes,
        status: s.status
      } : null,
      data_acao: resp?.data_criacao || resp?.data_acao || s.data_acao || s.data_criacao
    };
  });

  // 4. Filtro de Especialidade (perfil restrito ou digitado)
  if (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo?.especialidade) {
    const activeSpecialtyName = (perfisStore.perfilAtivo.especialidade || '').toLowerCase();
    list = list.filter(s => 
      s.especialidade && s.especialidade.toLowerCase().includes(activeSpecialtyName)
    );
  } else if (filtroEsp.value) {
    const query = filtroEsp.value.toLowerCase().trim();
    list = list.filter(s => s.especialidade && s.especialidade.toLowerCase().includes(query));
  }

  // 5. Filtro de Procedimento
  if (filtroProc.value) {
    const query = formatarNomeProcedimento(filtroProc.value);
    list = list.filter(s => s.procedimento && formatarNomeProcedimento(s.procedimento) === query);
  }

  // 6. Filtro de Prontuário / Paciente
  if (filtroPac.value) {
    const query = filtroPac.value.toLowerCase().trim();
    list = list.filter(s => 
      String(s.codigo_paciente).includes(query) || 
      (s.nome_paciente && s.nome_paciente.toLowerCase().includes(query))
    );
  }

  // 7. Filtro de Judicialização
  if (filtroJud.value) {
    list = list.filter(s => s.judicializado === filtroJud.value);
  }

  // 8. Filtro de Swalis
  if (filtroSwalis.value) {
    list = list.filter(s => {
      const sw = s.swalis || s.swallis || s.Swalis || '';
      return sw === filtroSwalis.value;
    });
  }

  // 9. Filtro de Médico Responsável
  if (filtroMed.value) {
    const query = filtroMed.value.toLowerCase().trim();
    list = list.filter(s => s.medico_responsavel && s.medico_responsavel.toLowerCase().includes(query));
  }

  // 10. Ordenação padrão
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
  if (newProfile?.tipo === 'ESPECIALIDADE' && newProfile?.especialidade) {
    const espTarget = newProfile.especialidade || '';
    const found = especialidades.value.find(e => e.nome.toLowerCase().includes(espTarget.toLowerCase()));
    const finalEsp = found ? found.nome : newProfile.especialidade;
    form.value.especialidade = finalEsp;
    filtroEsp.value = finalEsp;
  } else {
    form.value.especialidade = '';
    filtroEsp.value = '';
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
  modoEdicaoSolicitacao.value = false;
  solicitacaoEmEdicaoId.value = null;
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
    tempo_standby: undefined,
    categorizacao: ''
  };
  pacienteValidadoNoAghu.value = false;
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

const iniciarEdicaoSolicitacao = (solic: any) => {
  modoEdicaoSolicitacao.value = true;
  solicitacaoEmEdicaoId.value = String(solic.id);
  abaAtiva.value = solic.tipo;
  
  form.value = {
    especialidade: solic.especialidade || '',
    procedimento: solic.procedimento || '',
    procedimento_anterior: solic.procedimento_anterior || '',
    codigo_paciente: String(solic.codigo_paciente || ''),
    nome_paciente: solic.nome_paciente || '',
    dt_nascimento: '',
    nome_mae: '',
    judicializado: solic.judicializado || 'Não',
    swallis: solic.swallis || solic.swalis || '',
    medico_responsavel: solic.medico_responsavel || '',
    detalhes: solic.detalhes || '',
    tempo_standby: solic.tempo_standby || undefined,
    categorizacao: solic.categorizacao || ''
  };

  pacienteValidadoNoAghu.value = true;
  formCarregadoDaSede.value = true;
  if (solic.tipo === 'EDITAR' && solic.procedimento_anterior && solic.procedimento !== solic.procedimento_anterior) {
    desejaAlterarProcedimento.value = 'Sim';
  } else {
    desejaAlterarProcedimento.value = 'Não';
  }

  if (solic.tipo === 'STANDBY') {
    opcaoStandbyVigente.value = 'NOVO';
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
  toast.info(`Editando solicitação #${solic.id}. Altere os dados e clique em "Salvar Alterações".`);
};

const cancelarEdicaoSolicitacao = () => {
  modoEdicaoSolicitacao.value = false;
  solicitacaoEmEdicaoId.value = null;
  limparFormulario();
  toast.info('Edição cancelada.');
};

// Preenche o formulário ao selecionar o procedimento para edição/exclusão/standby
const preencherCamposDoProc = (proc: any) => {
  form.value.procedimento_anterior = proc.procedimento;
  form.value.procedimento = proc.procedimento;
  form.value.especialidade = proc.especialidade;
  form.value.judicializado = proc.judicializado || 'Não';
  form.value.swallis = proc.swallis || '';
  form.value.categorizacao = proc.categorizacao || '';
  
  const med = proc.medico_responsavel || '';
  const userMatch = usuariosLocais.value.find(u => u.username?.toLowerCase() === med.trim().toLowerCase() || u.nome?.toLowerCase() === med.trim().toLowerCase());
  form.value.medico_responsavel = userMatch?.nome?.trim() || med;
  
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

  let pacData: any = null;
  try {
    if (abaAtiva.value === 'INSERIR') {
      // 1. Busca dados cadastrais do paciente no AGHU (Cadastro de Pacientes)
      try {
        const resp = await api.get(`/api/pacientes/${form.value.codigo_paciente}`);
        pacData = resp.data;
        if (!pacData || !pacData.nome || String(pacData.nome).toLowerCase().startsWith('paciente #')) {
          throw new Error('Paciente não encontrado');
        }
        form.value.nome_paciente = pacData.nome;
        form.value.dt_nascimento = pacData.dt_nascimento;
        form.value.nome_mae = pacData.nome_mae;
        pacienteValidadoNoAghu.value = true;
        if (!isAutomatic) {
          toast.success(`Paciente localizado no AGHU: ${pacData.nome}`);
        }
      } catch {
        pacienteValidadoNoAghu.value = false;
        // Abre o diálogo de confirmação para o usuário
        modalConfirmacaoProntuarioNaoLocalizado.value = {
          aberto: true,
          prontuario: String(form.value.codigo_paciente)
        };
        return;
      }
    } else {
      // 2. EDITAR / EXCLUIR / STANDBY: Tenta buscar dados do AGHU se existirem
      try {
        const resp = await api.get(`/api/pacientes/${form.value.codigo_paciente}`);
        pacData = resp.data;
        if (pacData && pacData.nome && !String(pacData.nome).toLowerCase().startsWith('paciente #')) {
          form.value.nome_paciente = pacData.nome;
          form.value.dt_nascimento = pacData.dt_nascimento;
          form.value.nome_mae = pacData.nome_mae;
        }
      } catch {
        // Ignora erro do AGHU nas outras abas
      }

      // Busca procedimentos do paciente no histórico de solicitações da LEC
      const { data: solicsData } = await api.get('/api/solicitacoes');
      const especialidadeAtual = (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo?.especialidade)
        ? perfisStore.perfilAtivo.especialidade.toLowerCase()
        : null;

      const allSolics: any[] = solicsData;
      const codProntuario = String(form.value.codigo_paciente);

      const solicsDosPac = allSolics.filter(s => String(s.codigo_paciente) === codProntuario);
      
      // Verifica se o paciente possui inclusão no sistema LEC (solicitação de INSERIR ou paciente da base)
      const temInclusaoNaLec = solicsDosPac.some(s => s.tipo === 'INSERIR' || s.status === 'APROVADO');
      
      if (!temInclusaoNaLec && solicsDosPac.length === 0) {
        toast.error('Paciente não incluído no Sistema de Comunicação Cirúrgica HC-UFPE');
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

    const norm = (str: string) => str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

    const resolverMedicoNome = (med: string) => {
      if (!med || med === 'Não informado' || med === '—') return med || '';
      const clean = med.trim();
      if (!clean) return '';

      const cleanNorm = norm(clean);
      const userMatch = usuariosLocais.value.find(u => {
        if (!u) return false;
        const uNameNorm = u.nome ? norm(u.nome) : '';
        const uUserNorm = u.username ? norm(u.username) : '';
        return uUserNorm === cleanNorm || uNameNorm === cleanNorm || (cleanNorm.length > 5 && uNameNorm.includes(cleanNorm)) || (uNameNorm.length > 5 && cleanNorm.includes(uNameNorm));
      });

      const finalName = userMatch?.nome?.trim() || clean;
      return finalName && finalName !== 'Não informado' && finalName !== '—' ? finalName.toUpperCase() : finalName;
    };

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
          medico_responsavel: resolverMedicoNome(s.medico_responsavel),
          categorizacao: s.categorizacao || '',
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
            medico_responsavel: resolverMedicoNome(s.medico_responsavel),
            categorizacao: s.categorizacao !== undefined ? (s.categorizacao || '') : (existing.categorizacao || '')
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
            categorizacao: pacData.categorizacao || '',
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
  // Validação da Inclusão: obriga que o paciente tenha sido buscado no AGHU ou confirmado pelo usuário
  if (abaAtiva.value === 'INSERIR') {
    const nomePac = (form.value.nome_paciente || '').trim();
    if (!pacienteValidadoNoAghu.value || !nomePac) {
      toast.error('Por favor, clique no botão "Buscar" e confirme a localização ou identificação do prontuário antes de enviar a solicitação.');
      return;
    }
  }

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
      const origCat = orig.categorizacao || '';
      const formCat = form.value.categorizacao || '';

      const alterado = (origSw !== formSw) || 
                       (origMed !== formMed) || 
                       (origJud !== formJud) || 
                       (origProc !== formProc) ||
                       (origCat !== formCat);

      if (!alterado) {
        toast.error('Nenhuma alteração detectada. Modifique pelo menos um campo (Procedimento, Judicialização, Swalis, Médico Responsável, Categorização) antes de enviar.');
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

  if (perfisStore.perfilAtivo.tipo === 'OBSERVADOR') {
    toast.error('Usuários com perfil OBSERVADOR possuem acesso apenas para visualização.');
    return;
  }

  submitting.value = true;
  try {
    if (modoEdicaoSolicitacao.value && solicitacaoEmEdicaoId.value) {
      await api.put(`/api/solicitacoes/${solicitacaoEmEdicaoId.value}`, {
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
        perfil_executor: perfisStore.perfilAtivo.tipo,
        usuario: authStore.user?.username || 'Usuário Sistema',
        procedimento_anterior: form.value.procedimento_anterior || undefined,
        categorizacao: form.value.categorizacao || ''
      });
      toast.success('Solicitação atualizada com sucesso!');
    } else {
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
        perfil_executor: perfisStore.perfilAtivo.tipo,
        usuario: authStore.user?.username || 'Usuário Sistema',
        procedimento_anterior: form.value.procedimento_anterior || undefined,
        categorizacao: form.value.categorizacao || ''
      });
      toast.success('Solicitação registrada com sucesso!');
    }
    modoEdicaoSolicitacao.value = false;
    solicitacaoEmEdicaoId.value = null;
    limparFormulario();
    await carregarSolicitacoes();
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Erro ao processar solicitação.';
    toast.error(errorMsg);
  } finally {
    submitting.value = false;
  }
};

const atualizarStatus = async (id: string, status: string, skipConfirm: boolean = false, justificativa: string = "") => {
  if (!skipConfirm) {
    const acaoText = status === 'APROVADO' ? 'aprovar (dar baixa na)' : (status === 'CANCELADO' ? 'cancelar a' : 'rejeitar a');
    const confirmacao = window.confirm(`Tem certeza que deseja ${acaoText} solicitação?`);
    if (!confirmacao) return;
  }

  try {
    const perfil_executor = perfisStore.perfilAtivo?.tipo || 'GESTAO_LEC';
    const usuario = authStore.user?.username || 'Usuário Sistema';
    await api.put(`/api/solicitacoes/${id}/status`, { 
      status, 
      perfil_executor, 
      usuario, 
      justificativa 
    });
    const statusMsg = status === 'CANCELADO' ? 'cancelada' : status.toLowerCase();
    toast.success(`Solicitação ${statusMsg} com sucesso!`);
    await carregarSolicitacoes();
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Erro ao atualizar status.';
    toast.error(errorMsg);
  }
};

// Modal de Rejeição com Justificativa Obrigatória
const modalRejeicao = ref<{
  aberto: boolean;
  solic: any;
  justificativa: string;
  erro: string;
}>({
  aberto: false,
  solic: null,
  justificativa: '',
  erro: ''
});

const submittingRejeicao = ref(false);

const abrirModalRejeicao = (solic: any) => {
  modalRejeicao.value = {
    aberto: true,
    solic: solic,
    justificativa: '',
    erro: ''
  };
};

const fecharModalRejeicao = () => {
  modalRejeicao.value.aberto = false;
  modalRejeicao.value.solic = null;
  modalRejeicao.value.justificativa = '';
  modalRejeicao.value.erro = '';
};

const confirmarRejeicao = async () => {
  if (!modalRejeicao.value.justificativa.trim()) {
    modalRejeicao.value.erro = 'Por favor, informe detalhadamente a justificativa para a rejeição.';
    return;
  }
  if (!modalRejeicao.value.solic) return;

  submittingRejeicao.value = true;
  try {
    const perfil_executor = perfisStore.perfilAtivo?.tipo || 'GESTAO_LEC';
    const usuario = authStore.user?.username || 'Usuário Sistema';
    await api.put(`/api/solicitacoes/${modalRejeicao.value.solic.id}/status`, {
      status: 'REJEITADO',
      perfil_executor,
      usuario,
      justificativa: modalRejeicao.value.justificativa.trim()
    });
    toast.success('Solicitação rejeitada com sucesso!');
    fecharModalRejeicao();
    await carregarSolicitacoes();
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Erro ao rejeitar solicitação.';
    toast.error(errorMsg);
  } finally {
    submittingRejeicao.value = false;
  }
};

const modalCancelar = ref<{ aberto: boolean; solic: any }>({
  aberto: false,
  solic: null
});

const solicitarCancelamento = (solic: any) => {
  modalCancelar.value = {
    aberto: true,
    solic: solic
  };
};

const confirmarCancelamento = async () => {
  if (!modalCancelar.value.solic) return;
  const solicId = modalCancelar.value.solic.id;
  modalCancelar.value.aberto = false;
  modalCancelar.value.solic = null;
  await atualizarStatus(solicId, 'CANCELADO', true);
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

const extrairJustificativaResposta = (solic: any) => {
  if (!solic) return '—';
  const detalhes = solic.dados_resposta?.detalhes || '';
  if (detalhes.includes('Justificativa:')) {
    return detalhes.split('Justificativa:')[1].trim();
  }
  if (detalhes.includes('Motivo:')) {
    return detalhes.split('Motivo:')[1].trim();
  }
  if (detalhes) {
    return detalhes;
  }
  return solic.status === 'REJEITADO' 
    ? 'Nenhuma justificativa detalhada registrada (rejeição anterior à implementação deste campo).' 
    : 'Solicitação processada e concluída com sucesso.';
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
    case 'CANCELADO': return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800 border border-gray-200';
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
  if (!solic) return { especialidade: '', procedimento: '', judicializado: 'Não', swalis: '', medico_responsavel: '', categorizacao: '' };
  const pacienteBase = pacientesBase.value.find(p => String(p.prontuario || p.codigo) === String(solic.codigo_paciente));
  
  let estado = {
    especialidade: pacienteBase ? pacienteBase.especialidade : '',
    procedimento: pacienteBase ? pacienteBase.procedimento : '',
    judicializado: pacienteBase ? (pacienteBase.judicializado || 'Não') : 'Não',
    swalis: pacienteBase ? (pacienteBase.swalis || pacienteBase.swallis || pacienteBase.Swalis || '') : '',
    medico_responsavel: pacienteBase ? (pacienteBase.medico_responsavel || '') : '',
    categorizacao: pacienteBase ? (pacienteBase.categorizacao || '') : ''
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
      estado.categorizacao = s.categorizacao || '';
    } else if (s.tipo === 'EDITAR') {
      if (s.especialidade) estado.especialidade = s.especialidade;
      if (s.procedimento) estado.procedimento = s.procedimento;
      if (s.judicializado) estado.judicializado = s.judicializado;
      const sw = s.swalis || s.swallis || s.Swalis;
      if (sw) estado.swalis = sw;
      if (s.medico_responsavel) estado.medico_responsavel = s.medico_responsavel;
      if (s.categorizacao !== undefined) estado.categorizacao = s.categorizacao || '';
    }
  }
  
  if (solic.procedimento_anterior) {
    estado.procedimento = solic.procedimento_anterior;
  }
  
  return estado;
};

const obterMudancaCampo = (solic: any, campo: string) => {
  if (!solic || solic.tipo !== 'EDITAR') return null;
  const estAnt = obterEstadoAnterior(solic);
  
  if (campo === 'procedimento') {
    const ant = (solic.procedimento_anterior || estAnt.procedimento || '').trim();
    const novo = (solic.procedimento || '').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'judicializado') {
    const ant = (estAnt.judicializado || 'Não').trim();
    const novo = (solic.judicializado || 'Não').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'swalis') {
    const ant = (estAnt.swalis || '').trim();
    const novo = (solic.swalis || solic.swallis || solic.Swalis || '').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'medico_responsavel') {
    const ant = (estAnt.medico_responsavel || '').trim();
    const novo = (solic.medico_responsavel || '').trim();
    if (ant && novo && ant.toLowerCase() !== novo.toLowerCase()) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'especialidade') {
    const ant = (estAnt.especialidade || '').trim();
    const novo = (solic.especialidade || '').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'categorizacao') {
    const ant = (estAnt.categorizacao || '').trim();
    const novo = (solic.categorizacao || '').trim();
    if (ant !== novo) {
      return { anterior: ant || 'Sem categorização', novo: novo || 'Sem categorização' };
    }
  }
  return null;
};

const obterListaMudancas = (solic: any) => {
  if (!solic || solic.tipo !== 'EDITAR') return [];
  const mudancas: { campo: string; anterior: string; novo: string }[] = [];
  
  const mProc = obterMudancaCampo(solic, 'procedimento');
  if (mProc) {
    mudancas.push({ campo: 'Procedimento (Fila)', anterior: mProc.anterior, novo: mProc.novo });
  }
  
  const mEsp = obterMudancaCampo(solic, 'especialidade');
  if (mEsp) {
    mudancas.push({ campo: 'Especialidade', anterior: mEsp.anterior, novo: mEsp.novo });
  }
  
  const mJud = obterMudancaCampo(solic, 'judicializado');
  if (mJud) {
    mudancas.push({ campo: 'Judicialização', anterior: mJud.anterior, novo: mJud.novo });
  }
  
  const mSwalis = obterMudancaCampo(solic, 'swalis');
  if (mSwalis) {
    mudancas.push({ campo: 'Swalis (Priorização)', anterior: mSwalis.anterior, novo: mSwalis.novo });
  }
  
  const mMed = obterMudancaCampo(solic, 'medico_responsavel');
  if (mMed) {
    mudancas.push({ campo: 'Médico Responsável', anterior: mMed.anterior, novo: mMed.novo });
  }

  const mCat = obterMudancaCampo(solic, 'categorizacao');
  if (mCat) {
    mudancas.push({ campo: 'Categorização Profissional', anterior: mCat.anterior, novo: mCat.novo });
  }
  
  return mudancas;
};

// Sincronização da barra de rolagem horizontal superior
const topScrollRef = ref<HTMLElement | null>(null);
const tableContainerRef = ref<HTMLElement | null>(null);
const tableRef = ref<HTMLElement | null>(null);
const larguraTabela = ref(0);
const temOverflowHorizontal = ref(false);

let isSyncingScroll = false;

const onTopScroll = () => {
  if (isSyncingScroll) return;
  isSyncingScroll = true;
  if (tableContainerRef.value && topScrollRef.value) {
    tableContainerRef.value.scrollLeft = topScrollRef.value.scrollLeft;
  }
  requestAnimationFrame(() => { isSyncingScroll = false; });
};

const onBottomScroll = () => {
  if (isSyncingScroll) return;
  isSyncingScroll = true;
  if (topScrollRef.value && tableContainerRef.value) {
    topScrollRef.value.scrollLeft = tableContainerRef.value.scrollLeft;
  }
  requestAnimationFrame(() => { isSyncingScroll = false; });
};

const atualizarDimensoesTabela = () => {
  if (tableRef.value && tableContainerRef.value) {
    const scrollW = tableRef.value.scrollWidth;
    const clientW = tableContainerRef.value.clientWidth;
    larguraTabela.value = scrollW;
    temOverflowHorizontal.value = scrollW > clientW + 10;
  }
};

watch([solicitacoesFiltradas, abaAcompanhamentoAtiva, subAbaAcompanhamento], () => {
  setTimeout(atualizarDimensoesTabela, 100);
});

onMounted(() => {
  perfisStore.fetchPerfis();
  carregarSolicitacoes();
  carregarPacientesBase();
  carregarUsuariosLocais();
  carregarCategorizacoes();
  window.addEventListener('resize', atualizarDimensoesTabela);
  setTimeout(atualizarDimensoesTabela, 300);
});

onUnmounted(() => {
  window.removeEventListener('resize', atualizarDimensoesTabela);
});
</script>
