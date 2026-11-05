<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 overflow-y-auto bg-slate-900/60 backdrop-blur-xs"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-6xl max-h-[92vh] flex flex-col overflow-hidden"
    >
      <!-- Cabeçalho do Modal -->
      <div class="px-6 py-4 bg-slate-900 text-white flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-indigo-500/20 border border-indigo-400/30 rounded-xl">
            <ArrowsRightLeftIcon class="h-6 w-6 text-indigo-300" />
          </div>
          <div>
            <h2 class="text-base sm:text-lg font-bold tracking-tight">
              Diagnóstico Comunicação Cirúrgica x Sistema LEC
            </h2>
            <p class="text-xs text-slate-300">
              Comparação de filas, diagnóstico automático de divergências e sincronização no Comunicação Cirúrgica
            </p>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <button
            v-if="modoTela !== 'HISTORICO'"
            type="button"
            @click="voltarParaHistorico"
            class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition cursor-pointer"
          >
            <ArrowLeftIcon class="h-4 w-4" />
            <span>Diagnósticos Realizados</span>
          </button>

          <button
            v-if="modoTela === 'DETALHES' && diagnosticoAtual"
            type="button"
            @click="exportarExcelDiagnostico(false)"
            class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <ArrowDownTrayIcon class="h-4 w-4" />
            <span>Exportar Diagnóstico (.xlsx)</span>
          </button>

          <button
            v-if="modoTela !== 'NOVO'"
            type="button"
            @click="abrirTelaNovoDiagnostico"
            class="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <PlusCircleIcon class="h-4 w-4" />
            <span>Novo Diagnóstico</span>
          </button>

          <button
            type="button"
            @click="fecharModal"
            class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
            title="Fechar"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Corpo Rolável -->
      <div class="p-6 overflow-y-auto flex-1 space-y-5 bg-slate-50/60">
        <!-- ===================================================== -->
        <!-- VISÃO 1: LISTA DE DIAGNÓSTICOS REALIZADOS (HISTÓRICO) -->
        <!-- ===================================================== -->
        <div v-if="modoTela === 'HISTORICO'" class="space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2 bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div>
              <h3 class="text-sm font-bold text-slate-800 flex items-center space-x-2">
                <ClockIcon class="h-5 w-5 text-indigo-600" />
                <span>Histórico de Diagnósticos Realizados (do mais recente para o mais antigo)</span>
              </h3>
              <p class="text-xs text-slate-500 mt-0.5">
                Selecione um diagnóstico já realizado para consultar as informações e pendências ou executar ações de sincronização no Comunicação Cirúrgica.
              </p>
            </div>
            <button
              type="button"
              @click="abrirTelaNovoDiagnostico"
              class="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition cursor-pointer"
            >
              <PlusCircleIcon class="h-4 w-4" />
              <span>+ Novo Diagnóstico</span>
            </button>
          </div>

          <div v-if="carregandoHistorico" class="py-12 text-center text-slate-500 text-sm">
            <span class="inline-block animate-spin h-6 w-6 border-2 border-indigo-600 border-t-transparent rounded-full mb-2"></span>
            <p>Carregando diagnósticos realizados...</p>
          </div>

          <div
            v-else-if="listaDiagnosticos.length === 0"
            class="bg-white rounded-xl border border-dashed border-slate-300 p-10 text-center space-y-3"
          >
            <DocumentMagnifyingGlassIcon class="h-12 w-12 text-slate-400 mx-auto" />
            <div class="space-y-1">
              <p class="text-sm font-bold text-slate-700">Nenhum diagnóstico realizado até o momento</p>
              <p class="text-xs text-slate-500 max-w-md mx-auto">
                Envie as planilhas exportadas do Sistema LEC (.xlsx ou arquivo .zip com várias especialidades) para comparar com o Comunicação Cirúrgica.
              </p>
            </div>
            <button
              type="button"
              @click="abrirTelaNovoDiagnostico"
              class="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm transition cursor-pointer"
            >
              <PlusCircleIcon class="h-4 w-4" />
              <span>Realizar Primeiro Diagnóstico</span>
            </button>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="diag in listaDiagnosticos"
              :key="diag.id"
              class="bg-white rounded-xl border border-slate-200 hover:border-indigo-300 p-4 shadow-2xs transition flex flex-col lg:flex-row lg:items-center justify-between gap-4"
            >
              <div class="space-y-1.5">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="text-xs font-mono font-bold px-2.5 py-0.5 rounded bg-indigo-50 text-indigo-800 border border-indigo-200">
                    {{ formatarDataHora(diag.data_criacao) }}
                  </span>
                  <span class="text-xs font-semibold text-slate-700">
                    Realizado por: <strong class="text-slate-900">{{ diag.usuario }}</strong>
                  </span>
                  <span class="text-[11px] font-mono text-slate-400">({{ diag.id }})</span>
                </div>

                <div class="flex flex-wrap items-center gap-2 pt-1">
                  <span class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    Sincronia Global: {{ diag.percentual_sincronia_global }}%
                  </span>
                  <span class="text-xs px-2.5 py-0.5 rounded-full font-medium bg-slate-100 text-slate-700 border border-slate-200">
                    Especialidades comparadas: {{ diag.especialidades_importadas_count }} / {{ diag.especialidades_cadastradas_cc_count }}
                  </span>
                  <span
                    v-if="diag.especialidades_sem_planilha_count > 0"
                    class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-amber-50 text-amber-800 border border-amber-200"
                  >
                    ⚠️ {{ diag.especialidades_sem_planilha_count }} especialidade(s) sem planilha
                  </span>
                  <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-rose-50 text-rose-800 border border-rose-200">
                    {{ diag.total_divergencias }} divergência(s)
                  </span>
                  <span
                    v-if="diag.total_sincronizados_no_cc > 0"
                    class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-teal-50 text-teal-800 border border-teal-200"
                  >
                    ✓ {{ diag.total_sincronizados_no_cc }} ação(ões) executada(s) no CC
                  </span>
                </div>
              </div>

              <div class="flex items-center space-x-2 shrink-0">
                <button
                  type="button"
                  @click="selecionarDiagnosticoExistente(diag.id)"
                  class="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition cursor-pointer"
                >
                  <span>Abrir Diagnóstico / Ações</span>
                  <ChevronRightIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ===================================================== -->
        <!-- VISÃO 2: NOVO DIAGNÓSTICO (UPLOAD FLEXÍVEL)           -->
        <!-- ===================================================== -->
        <div v-else-if="modoTela === 'NOVO'" class="space-y-5">
          <div class="bg-white border border-slate-200 rounded-xl p-5 space-y-3 shadow-2xs">
            <h3 class="text-sm font-bold text-slate-800 flex items-center space-x-2">
              <CloudArrowUpIcon class="h-5 w-5 text-indigo-600" />
              <span>Enviar Planilhas do Sistema LEC (.xlsx, .xls ou pacote .zip)</span>
            </h3>
            <p class="text-xs text-slate-600 leading-relaxed">
              Você pode enviar <strong>1 planilha</strong> (para diagnosticar uma única especialidade), selecionar <strong>várias planilhas Excel de uma vez</strong> ou enviar um <strong>arquivo .zip</strong> contendo todas as planilhas exportadas do Sistema LEC. O sistema reconhece automaticamente cada especialidade, ignora arquivos duplicados e informa quais especialidades tiveram planilha importada e quais ficaram de fora.
            </p>

            <label
              class="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl cursor-pointer transition-colors"
              :class="
                isDragging
                  ? 'border-indigo-600 bg-indigo-50/70'
                  : arquivosSelecionados.length > 0
                  ? 'border-emerald-500 bg-emerald-50/30'
                  : 'border-slate-300 bg-slate-50 hover:bg-slate-100'
              "
              @dragenter.prevent="isDragging = true"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
            >
              <div class="flex flex-col items-center justify-center pt-4 pb-5 text-center px-4 pointer-events-none">
                <CloudArrowUpIcon class="w-10 h-10 text-indigo-500 mb-2" />
                <p class="text-xs text-slate-700">
                  <span class="font-bold text-indigo-600">Clique para escolher os arquivos</span> ou arraste-os aqui
                </p>
                <p class="text-[11px] text-slate-500 mt-1">
                  Suporta múltiplos arquivos <strong>.xlsx</strong>, <strong>.xls</strong> ou pacote compactado <strong>.zip</strong>
                </p>
              </div>
              <input
                type="file"
                multiple
                accept=".xlsx,.xls,.zip"
                class="hidden"
                @change="handleFileSelect"
                :disabled="processandoNovo"
              />
            </label>

            <!-- Lista de Arquivos Selecionados -->
            <div v-if="arquivosSelecionados.length > 0" class="space-y-2 pt-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-slate-700">
                  {{ arquivosSelecionados.length }} arquivo(s) selecionado(s) para o diagnóstico:
                </span>
                <button
                  type="button"
                  @click="arquivosSelecionados = []"
                  class="text-xs text-rose-600 hover:underline font-semibold cursor-pointer"
                  :disabled="processandoNovo"
                >
                  Limpar todos
                </button>
              </div>
              <div class="max-h-36 overflow-y-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                <div
                  v-for="(arq, idx) in arquivosSelecionados"
                  :key="idx"
                  class="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs"
                >
                  <span class="truncate font-medium text-slate-700" :title="arq.name">{{ arq.name }}</span>
                  <button
                    type="button"
                    @click="removerArquivo(idx)"
                    class="text-slate-400 hover:text-rose-600 ml-2 cursor-pointer"
                    :disabled="processandoNovo"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>

            <div
              v-if="erroMensagem"
              class="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 font-medium flex items-start space-x-2"
            >
              <ExclamationTriangleIcon class="h-4 w-4 text-rose-500 shrink-0 mt-0.5" />
              <span>{{ erroMensagem }}</span>
            </div>

            <div class="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                @click="voltarParaHistorico"
                class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 text-xs font-semibold transition cursor-pointer"
                :disabled="processandoNovo"
              >
                Cancelar
              </button>
              <button
                type="button"
                @click="executarNovoDiagnostico"
                :disabled="arquivosSelecionados.length === 0 || processandoNovo"
                class="flex items-center space-x-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold shadow-sm transition cursor-pointer"
              >
                <span
                  v-if="processandoNovo"
                  class="inline-block animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"
                ></span>
                <span>{{ processandoNovo ? 'Processando e Comparando Bases...' : 'Executar Diagnóstico Agora' }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- ===================================================== -->
        <!-- VISÃO 3: DETALHES DO DIAGNÓSTICO E AÇÕES NO CC        -->
        <!-- ===================================================== -->
        <div v-else-if="modoTela === 'DETALHES' && diagnosticoAtual" class="space-y-5">
          <!-- Barra de Identificação do Diagnóstico -->
          <div class="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 shadow-2xs">
            <div class="flex flex-wrap items-center gap-2.5">
              <span class="text-xs font-mono font-bold px-2.5 py-1 rounded bg-indigo-50 text-indigo-800 border border-indigo-200">
                Diagnóstico de {{ formatarDataHora(diagnosticoAtual.data_criacao) }}
              </span>
              <span class="text-xs text-slate-600">
                Executado por <strong class="text-slate-900">{{ diagnosticoAtual.usuario }}</strong>
              </span>
              <span class="text-xs font-mono text-slate-400">({{ diagnosticoAtual.id }})</span>
            </div>

            <button
              type="button"
              @click="mostrarPainelCobertura = !mostrarPainelCobertura"
              class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1 cursor-pointer"
            >
              <span>{{ mostrarPainelCobertura ? 'Ocultar Cobertura de Especialidades' : 'Exibir Cobertura de Especialidades' }}</span>
              <ChevronUpIcon v-if="mostrarPainelCobertura" class="h-4 w-4" />
              <ChevronDownIcon v-else class="h-4 w-4" />
            </button>
          </div>

          <!-- 1. VERIFICAÇÃO PRELIMINAR DE COBERTURA DE ESPECIALIDADES -->
          <div
            v-if="mostrarPainelCobertura && diagnosticoAtual.cobertura_especialidades"
            class="bg-white border border-slate-200 rounded-xl p-4 space-y-3 shadow-2xs"
          >
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
              <CheckBadgeIcon class="h-4 w-4 text-indigo-600" />
              <span>1. Verificação Preliminar de Planilhas e Especialidades</span>
            </h4>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <!-- Especialidades do CC com planilha importada -->
              <div class="p-3 rounded-lg bg-emerald-50/70 border border-emerald-200 space-y-1.5">
                <div class="text-xs font-bold text-emerald-900 flex items-center justify-between">
                  <span>✅ Especialidades do CC com planilha importada</span>
                  <span class="px-2 py-0.5 rounded-full bg-emerald-200/70 text-emerald-950 font-mono text-[11px]">
                    {{ diagnosticoAtual.cobertura_especialidades.especialidades_importadas.length }} de {{ diagnosticoAtual.cobertura_especialidades.total_cadastradas_cc }}
                  </span>
                </div>
                <div class="flex flex-wrap gap-1 pt-0.5">
                  <span
                    v-for="item in diagnosticoAtual.cobertura_especialidades.especialidades_importadas"
                    :key="item.esp_key"
                    class="text-[11px] font-medium px-2 py-0.5 rounded bg-white text-emerald-800 border border-emerald-200"
                  >
                    {{ item.especialidade }} ({{ item.prontuarios_lec }})
                  </span>
                </div>
              </div>

              <!-- Especialidades do CC SEM planilha enviada (Alerta de esquecimento) -->
              <div
                class="p-3 rounded-lg border space-y-1.5"
                :class="
                  diagnosticoAtual.cobertura_especialidades.especialidades_sem_planilha.length > 0
                    ? 'bg-amber-50 border-amber-300'
                    : 'bg-slate-50 border-slate-200'
                "
              >
                <div class="text-xs font-bold flex items-center justify-between" :class="diagnosticoAtual.cobertura_especialidades.especialidades_sem_planilha.length > 0 ? 'text-amber-900' : 'text-slate-700'">
                  <span>⚠️ Especialidades do CC sem planilha enviada</span>
                  <span class="px-2 py-0.5 rounded-full font-mono text-[11px]" :class="diagnosticoAtual.cobertura_especialidades.especialidades_sem_planilha.length > 0 ? 'bg-amber-200 text-amber-950' : 'bg-slate-200 text-slate-700'">
                    {{ diagnosticoAtual.cobertura_especialidades.especialidades_sem_planilha.length }}
                  </span>
                </div>
                <p
                  v-if="diagnosticoAtual.cobertura_especialidades.especialidades_sem_planilha.length === 0"
                  class="text-xs text-emerald-700 font-medium"
                >
                  Todas as especialidades ativas do Comunicação Cirúrgica tiveram planilha enviada neste diagnóstico!
                </p>
                <div v-else class="space-y-1">
                  <p class="text-[11px] text-amber-800">
                    As especialidades abaixo não tiveram planilha anexada (não foram incluídas no cálculo de divergências para evitar falsos positivos):
                  </p>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="item in diagnosticoAtual.cobertura_especialidades.especialidades_sem_planilha"
                      :key="item.esp_key"
                      class="text-[11px] font-bold px-2 py-0.5 rounded bg-white text-amber-900 border border-amber-300"
                    >
                      {{ item.especialidade }} ({{ item.pacientes_ativos_cc }} no CC)
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Avisos de Arquivos Duplicados Consolidados e Especialidades Não Cadastradas no CC -->
            <div
              v-if="
                diagnosticoAtual.cobertura_especialidades.arquivos_duplicados.length > 0 ||
                diagnosticoAtual.cobertura_especialidades.especialidades_nao_cadastradas_no_cc.length > 0
              "
              class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1"
            >
              <div
                v-if="diagnosticoAtual.cobertura_especialidades.arquivos_duplicados.length > 0"
                class="p-2.5 rounded-lg bg-blue-50/70 border border-blue-200 text-xs text-blue-900 space-y-1"
              >
                <div class="font-bold">
                  🔁 {{ diagnosticoAtual.cobertura_especialidades.arquivos_duplicados.length }} arquivo(s) duplicado(s) consolidado(s) automaticamente:
                </div>
                <ul class="list-disc list-inside text-[11px] space-y-0.5">
                  <li v-for="(dup, i) in diagnosticoAtual.cobertura_especialidades.arquivos_duplicados" :key="i">
                    <strong>{{ dup.arquivo_ignorado }}</strong> ({{ dup.especialidade }}) consolidado em <strong>{{ dup.arquivo_mantido }}</strong>
                  </li>
                </ul>
              </div>

              <div
                v-if="diagnosticoAtual.cobertura_especialidades.especialidades_nao_cadastradas_no_cc.length > 0"
                class="p-2.5 rounded-lg bg-purple-50/70 border border-purple-200 text-xs text-purple-900 space-y-1"
              >
                <div class="font-bold">
                  ℹ️ Planilha(s) de especialidade ainda sem fila ativa no Comunicação Cirúrgica:
                </div>
                <ul class="list-disc list-inside text-[11px] space-y-0.5">
                  <li v-for="nc in diagnosticoAtual.cobertura_especialidades.especialidades_nao_cadastradas_no_cc" :key="nc.esp_key">
                    <strong>{{ nc.especialidade }}</strong> ({{ nc.prontuarios_lec }} pacientes na planilha {{ nc.arquivos.join(', ') }})
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 2. CARDS DE RESUMO GLOBAL -->
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs text-center">
              <span class="text-[11px] font-semibold text-slate-500 uppercase block">Sincronia Global</span>
              <span class="text-xl font-black text-emerald-600">{{ diagnosticoAtual.percentual_sincronia_global }}%</span>
            </div>
            <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs text-center">
              <span class="text-[11px] font-semibold text-slate-500 uppercase block">Em Ambos (Sincronizados)</span>
              <span class="text-xl font-black text-slate-800">{{ diagnosticoAtual.prontuarios_em_ambos }}</span>
            </div>
            <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs text-center">
              <span class="text-[11px] font-semibold text-slate-500 uppercase block">Prontuários no LEC</span>
              <span class="text-xl font-bold text-indigo-700">{{ diagnosticoAtual.prontuarios_unicos_lec }}</span>
            </div>
            <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs text-center">
              <span class="text-[11px] font-semibold text-slate-500 uppercase block">Prontuários no CC</span>
              <span class="text-xl font-bold text-indigo-700">{{ diagnosticoAtual.prontuarios_unicos_cc }}</span>
            </div>
            <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs text-center col-span-2 sm:col-span-1">
              <span class="text-[11px] font-semibold text-slate-500 uppercase block">Divergências / Sincronizadas</span>
              <span class="text-xl font-black text-rose-600">
                {{ diagnosticoAtual.total_divergencias }}
                <span class="text-xs font-bold text-teal-700">({{ diagnosticoAtual.total_sincronizados_no_cc }} sinc.)</span>
              </span>
            </div>
          </div>

          <!-- 3. NAVEGAÇÃO POR ABAS (VISUALIZAÇÃO COMPLETA NO PRÓPRIO COMUNICAÇÃO CIRÚRGICA) -->
          <div class="bg-white border border-slate-200 rounded-xl shadow-2xs overflow-hidden">
            <div class="border-b border-slate-200 bg-slate-100/70 px-3 pt-2 flex flex-wrap gap-1.5">
              <button
                v-for="tab in abasDiagnostico"
                :key="tab.id"
                type="button"
                @click="abaAtiva = tab.id"
                class="px-3 py-2 rounded-t-lg text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer border-t border-x"
                :class="
                  abaAtiva === tab.id
                    ? 'bg-white text-indigo-700 border-slate-200 -mb-px shadow-2xs'
                    : 'bg-transparent text-slate-600 border-transparent hover:bg-white/60'
                "
              >
                <span>{{ tab.icone }}</span>
                <span>{{ tab.titulo }}</span>
                <span
                  v-if="tab.contador !== undefined"
                  class="px-1.5 py-0.2 rounded-full text-[10px] font-mono"
                  :class="abaAtiva === tab.id ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-200 text-slate-700'"
                >
                  {{ tab.contador }}
                </span>
              </button>
            </div>

            <!-- CONTEÚDO DA ABA 1: TABELA COMPARATIVA POR ESPECIALIDADE -->
            <div v-if="abaAtiva === 'TABELA_ESPECIALIDADES'" class="p-4 overflow-x-auto">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="border-b border-slate-200 text-slate-600 bg-slate-50 uppercase text-[11px]">
                    <th class="py-2.5 px-3 font-bold">Especialidade</th>
                    <th class="py-2.5 px-3 font-bold text-center">Sistema LEC (Linhas / Pront.)</th>
                    <th class="py-2.5 px-3 font-bold text-center">Com. Cirúrgica (Linhas / Pront.)</th>
                    <th class="py-2.5 px-3 font-bold text-center">Em Ambos</th>
                    <th class="py-2.5 px-3 font-bold text-center">Só no Sistema LEC</th>
                    <th class="py-2.5 px-3 font-bold text-center">Só no Com. Cirúrgica</th>
                    <th class="py-2.5 px-3 font-bold text-center">Diverg. Info (Em Ambos)</th>
                    <th class="py-2.5 px-3 font-bold text-center">Sincronia</th>
                    <th class="py-2.5 px-3 font-bold text-right">Ação Rápida</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200">
                  <tr
                    v-for="row in diagnosticoAtual.tabela_especialidades"
                    :key="row.esp_key"
                    class="hover:bg-slate-50/80 transition"
                  >
                    <td class="py-2.5 px-3 font-bold text-slate-800">
                      {{ row.especialidade }}
                      <span
                        v-if="!row.cadastrada_no_cc"
                        class="ml-1.5 text-[10px] font-semibold px-1.5 py-0.5 rounded bg-purple-100 text-purple-800"
                      >
                        Sem fila no CC
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono text-slate-700">
                      {{ row.lec_linhas }} / <strong>{{ row.lec_prontuarios }}</strong>
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono text-slate-700">
                      {{ row.cc_linhas }} / <strong>{{ row.cc_prontuarios }}</strong>
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-700">
                      {{ row.em_ambos }}
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono">
                      <span
                        :class="row.so_no_lec > 0 ? 'px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-bold' : 'text-slate-400'"
                      >
                        {{ row.so_no_lec }}
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono">
                      <span
                        :class="row.so_no_cc > 0 ? 'px-2 py-0.5 rounded-full bg-rose-100 text-rose-900 font-bold' : 'text-slate-400'"
                      >
                        {{ row.so_no_cc }}
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono">
                      <span
                        :class="(row.divergencias_info || 0) > 0 ? 'px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-900 font-bold' : 'text-slate-400'"
                      >
                        {{ row.divergencias_info || 0 }}
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-center font-mono font-bold">
                      <span
                        :class="
                          !row.cadastrada_no_cc
                            ? 'text-slate-400'
                            : row.percentual_sincronia >= 99
                            ? 'text-emerald-700'
                            : row.percentual_sincronia >= 95
                            ? 'text-indigo-700'
                            : 'text-amber-700'
                        "
                      >
                        {{ row.cadastrada_no_cc ? `${row.percentual_sincronia}%` : '—' }}
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-right">
                      <button
                        v-if="row.cadastrada_no_cc && (row.so_no_lec > 0 || row.so_no_cc > 0 || (row.divergencias_info || 0) > 0)"
                        type="button"
                        @click="filtrarDivergenciasPorEspecialidade(row.especialidade)"
                        class="text-xs font-semibold text-indigo-600 hover:text-indigo-900 hover:underline cursor-pointer"
                      >
                        Ver divergências →
                      </button>
                      <span v-else-if="row.cadastrada_no_cc" class="text-[11px] text-emerald-600 font-semibold">
                        ✓ 100% Sincronizado
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- CONTEÚDO DAS ABAS DE DIVERGÊNCIAS E PENDÊNCIAS (VISUALIZAÇÃO EM TELA + AÇÕES NO CC) -->
            <div v-else class="p-4 space-y-4">
              <!-- Banner Explicativo da Categoria Selecionada + Ações em Lote -->
              <div class="p-3.5 rounded-xl border bg-slate-50 border-slate-200 flex flex-col lg:flex-row lg:items-center justify-between gap-3">
                <div class="space-y-1">
                  <div class="text-xs font-bold text-slate-800">
                    {{ infoCategoriaAtiva.titulo }}
                  </div>
                  <p class="text-xs text-slate-600">
                    {{ infoCategoriaAtiva.descricao }}
                  </p>
                </div>

                <div class="flex flex-wrap items-center gap-2 shrink-0">
                  <!-- Botão Exportar Aba Atual para Excel -->
                  <button
                    type="button"
                    @click="exportarExcelDiagnostico(true)"
                    class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 text-xs font-semibold transition cursor-pointer"
                  >
                    <ArrowDownTrayIcon class="h-4 w-4 text-emerald-600" />
                    <span>Exportar Lista Visível (.xlsx)</span>
                  </button>

                  <!-- Botão de Ação em Lote no Comunicação Cirúrgica (somente quando aplicável) -->
                  <button
                    v-if="infoCategoriaAtiva.acaoLote"
                    type="button"
                    @click="executarSincronizacaoEmLote(infoCategoriaAtiva.acaoLote.codigo)"
                    :disabled="itensSelecionados.length === 0 || sincronizando"
                    class="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg text-white text-xs font-bold shadow-xs transition cursor-pointer disabled:opacity-50"
                    :class="infoCategoriaAtiva.acaoLote.corClasse"
                  >
                    <span
                      v-if="sincronizando"
                      class="inline-block animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full"
                    ></span>
                    <span>
                      {{ infoCategoriaAtiva.acaoLote.label }} ({{ itensSelecionados.length }} selecionado{{ itensSelecionados.length === 1 ? '' : 's' }})
                    </span>
                  </button>
                </div>
              </div>

              <!-- Barra de Filtros da Tabela de Divergências -->
              <div
                class="grid grid-cols-1 gap-3"
                :class="
                  abaAtiva === 'DIVERGENCIA_DADOS_CADASTRAIS' || abaAtiva === 'TODAS'
                    ? 'sm:grid-cols-4'
                    : 'sm:grid-cols-3'
                "
              >
                <div>
                  <label class="block text-[11px] font-bold text-slate-600 mb-1">Buscar por Prontuário ou Paciente</label>
                  <input
                    v-model="buscaDivergencia"
                    type="text"
                    placeholder="Digite o prontuário ou nome..."
                    class="w-full text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-800"
                  />
                </div>

                <div>
                  <label class="block text-[11px] font-bold text-slate-600 mb-1">Filtrar por Especialidade</label>
                  <select
                    v-model="filtroEspDivergencia"
                    class="w-full text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-800"
                  >
                    <option value="">Todas as Especialidades</option>
                    <option v-for="esp in especialidadesComDivergencia" :key="esp" :value="esp">
                      {{ esp }}
                    </option>
                  </select>
                </div>

                <div v-if="abaAtiva === 'DIVERGENCIA_DADOS_CADASTRAIS' || abaAtiva === 'TODAS'">
                  <label class="block text-[11px] font-bold text-slate-600 mb-1">Informação Divergente</label>
                  <select
                    v-model="filtroCampoDivergente"
                    class="w-full text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-800"
                  >
                    <option value="">Todas as Informações</option>
                    <option value="swalis">Swalis (Priorização)</option>
                    <option value="medico_responsavel">Médico Responsável</option>
                    <option value="lateralidade">Lateralidade</option>
                    <option value="judicializado">Judicialização</option>
                  </select>
                </div>

                <div>
                  <label class="block text-[11px] font-bold text-slate-600 mb-1">Status de Sincronização no CC</label>
                  <select
                    v-model="filtroStatusSinc"
                    class="w-full text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-800"
                  >
                    <option value="TODOS">Todos ({{ divergenciasFiltradasSemStatus.length }})</option>
                    <option value="PENDENTES">Ainda não corrigidos/sincronizados no CC</option>
                    <option value="SINCRONIZADOS">Já corrigidos/sincronizados no CC</option>
                  </select>
                </div>
              </div>

              <!-- Tabela Interativa de Pacientes Divergentes -->
              <div v-if="divergenciasVisiveis.length === 0" class="py-8 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
                Nenhum registro encontrado para os filtros selecionados nesta categoria.
              </div>

              <div v-else class="overflow-x-auto border border-slate-200 rounded-xl">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-200 text-slate-600 text-[11px] uppercase">
                      <th v-if="infoCategoriaAtiva.acaoLote" class="py-2.5 px-3 w-8 text-center">
                        <input
                          type="checkbox"
                          :checked="todosVisiveisSelecionados"
                          @change="toggleSelecionarTodosVisiveis"
                          class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                        />
                      </th>
                      <th class="py-2.5 px-3 font-bold">Prontuário / Paciente</th>
                      <th class="py-2.5 px-3 font-bold">Especialidade</th>
                      <th class="py-2.5 px-3 font-bold">Procedimento</th>
                      <th class="py-2.5 px-3 font-bold">Comparativo (CC x Sistema LEC) / Diagnóstico</th>
                      <th class="py-2.5 px-3 font-bold text-right">Ação no CC / Status</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-200">
                    <tr
                      v-for="item in divergenciasVisiveis"
                      :key="item.item_id"
                      class="hover:bg-slate-50/90 transition"
                      :class="item.sincronizado_no_cc ? 'bg-emerald-50/30' : ''"
                    >
                      <td v-if="infoCategoriaAtiva.acaoLote" class="py-2.5 px-3 text-center">
                        <input
                          type="checkbox"
                          :disabled="item.sincronizado_no_cc"
                          :value="item.item_id"
                          v-model="itensSelecionados"
                          class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer disabled:opacity-40"
                        />
                      </td>
                      <td class="py-2.5 px-3">
                        <div class="font-mono font-bold text-indigo-700">{{ item.prontuario }}</div>
                        <div class="font-semibold text-slate-800">{{ item.nome_paciente }}</div>
                      </td>
                      <td class="py-2.5 px-3">
                        <span class="font-bold text-slate-800">{{ item.especialidade }}</span>
                        <div
                          v-if="item.especialidade_secundaria"
                          class="text-[11px] text-purple-700 font-semibold mt-0.5"
                        >
                          No CC: {{ item.especialidade_secundaria }}
                        </div>
                      </td>
                      <td class="py-2.5 px-3 max-w-xs">
                        <div class="text-slate-800 font-medium break-words">{{ item.procedimento }}</div>
                        <div class="text-[11px] text-slate-500 mt-0.5">
                          Médico: {{ item.medico_responsavel }} | Swalis: {{ item.swalis }} | Lat: {{ item.lateralidade || 'Indefinida' }} | Jud: {{ item.judicializado }}
                        </div>
                      </td>
                      <td class="py-2.5 px-3 max-w-md">
                        <!-- Exibe badges lado a lado quando houver campos_divergentes -->
                        <div v-if="item.campos_divergentes && item.campos_divergentes.length > 0" class="space-y-1.5">
                          <div
                            v-for="(cd, cIdx) in item.campos_divergentes"
                            :key="cIdx"
                            class="p-1.5 rounded-lg bg-amber-50/80 border border-amber-200 text-[11px]"
                          >
                            <div class="font-bold text-amber-950 mb-0.5">{{ cd.campo }}:</div>
                            <div class="flex flex-wrap items-center gap-1.5">
                              <span class="px-1.5 py-0.5 rounded bg-white text-slate-800 border border-slate-300 font-medium">
                                <strong>CC:</strong> {{ cd.valor_cc || '—' }}
                              </span>
                              <span class="text-slate-400 font-bold">×</span>
                              <span class="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-900 border border-indigo-200 font-semibold">
                                <strong>LEC:</strong> {{ cd.valor_lec || '—' }}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div v-else class="text-slate-700 leading-snug">{{ item.detalhes_status }}</div>
                      </td>
                      <td class="py-2.5 px-3 text-right whitespace-nowrap">
                        <div v-if="item.sincronizado_no_cc" class="inline-flex flex-col items-end">
                          <span class="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px] border border-emerald-300">
                            ✓ Atualizado no CC
                          </span>
                          <span class="text-[10px] text-slate-500 mt-0.5">
                            {{ formatarDataHora(item.data_sincronizacao || '') }} ({{ item.usuario_sincronizacao }})
                          </span>
                        </div>

                        <div v-else class="inline-flex items-center space-x-1.5">
                          <button
                            v-if="item.acao_sugerida_cc === 'INCLUIR_NO_CC'"
                            type="button"
                            @click="executarSincronizacaoIndividual(item, 'INCLUIR_NO_CC')"
                            :disabled="sincronizando"
                            class="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold shadow-2xs transition cursor-pointer"
                          >
                            + Incluir no CC
                          </button>

                          <button
                            v-else-if="item.acao_sugerida_cc === 'EXCLUIR_DO_CC' || item.acao_sugerida_cc === 'DAR_BAIXA_NO_CC'"
                            type="button"
                            @click="executarSincronizacaoIndividual(item, 'EXCLUIR_DO_CC')"
                            :disabled="sincronizando"
                            class="px-2.5 py-1 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-[11px] font-bold shadow-2xs transition cursor-pointer"
                          >
                            Excluir do CC
                          </button>

                          <button
                            v-else-if="item.acao_sugerida_cc === 'TRANSFERIR_ESPECIALIDADE_NO_CC'"
                            type="button"
                            @click="executarSincronizacaoIndividual(item, 'TRANSFERIR_ESPECIALIDADE_NO_CC')"
                            :disabled="sincronizando"
                            class="px-2.5 py-1 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-[11px] font-bold shadow-2xs transition cursor-pointer"
                          >
                            Transferir p/ {{ item.especialidade }} no CC
                          </button>

                          <button
                            v-else-if="item.acao_sugerida_cc === 'EDITAR_INFORMACOES_NO_CC'"
                            type="button"
                            @click="abrirModalEdicaoIndividual(item)"
                            :disabled="sincronizando"
                            class="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-[11px] font-bold shadow-2xs transition cursor-pointer"
                          >
                            Avaliar / Corrigir no CC
                          </button>

                          <span
                            v-else
                            class="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-900 border border-amber-200 text-[11px] font-semibold"
                            title="A exclusão já está aprovada no Comunicação Cirúrgica; a exclusão precisa ser efetivada no Sistema LEC."
                          >
                            Pendente de exclusão no Sistema LEC
                          </span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SUBMODAL DE AVALIAÇÃO INDIVIDUAL E CORREÇÃO MANUAL DE INFORMAÇÕES DIVERGENTES NO CC -->
      <div
        v-if="itemEmEdicao"
        class="fixed inset-0 z-60 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs"
      >
        <div class="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden">
          <div class="px-5 py-3.5 bg-slate-900 text-white flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold">
                Avaliação Individual e Correção Manual no Comunicação Cirúrgica
              </h3>
              <p class="text-[11px] text-slate-300 mt-0.5">
                Prontuário <strong>{{ itemEmEdicao.prontuario }}</strong> — {{ itemEmEdicao.nome_paciente }} ({{ itemEmEdicao.especialidade }})
              </p>
            </div>
            <button
              type="button"
              @click="fecharModalEdicaoIndividual"
              class="text-slate-400 hover:text-white cursor-pointer"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>

          <div class="p-5 space-y-4 text-xs">
            <div class="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <div class="font-bold text-slate-700">Procedimento:</div>
              <div class="text-slate-900 font-medium mt-0.5">{{ itemEmEdicao.procedimento }}</div>
            </div>

            <p class="text-slate-600 leading-relaxed">
              Avalie abaixo o que consta em cada sistema e ajuste manualmente os valores que devem vigorar no <strong>Comunicação Cirúrgica</strong>. A alteração será registrada no menu <strong>Histórico</strong> (origem <em>Pacientes</em>) como uma <strong>Edição do tipo Execução</strong> com o seu usuário.
            </p>

            <div class="border border-slate-200 rounded-xl overflow-hidden">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="bg-slate-100 border-b border-slate-200 text-slate-700 text-[11px] uppercase">
                    <th class="py-2 px-3 font-bold">Informação</th>
                    <th class="py-2 px-3 font-bold">No Com. Cirúrgica</th>
                    <th class="py-2 px-3 font-bold">No Sistema LEC</th>
                    <th class="py-2 px-3 font-bold">Valor Manual p/ Salvar no CC</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200">
                  <!-- 1. Swalis -->
                  <tr :class="isCampoDivergente(itemEmEdicao, 'swalis') ? 'bg-amber-50/60' : ''">
                    <td class="py-2.5 px-3 font-bold text-slate-800">
                      Swalis
                      <span
                        v-if="isCampoDivergente(itemEmEdicao, 'swalis')"
                        class="ml-1 px-1.5 py-0.2 rounded bg-amber-200 text-amber-950 text-[10px]"
                      >
                        Divergente
                      </span>
                    </td>
                    <td class="py-2.5 px-3 font-mono text-slate-700">
                      {{ itemEmEdicao.valores_atuais_cc?.swalis || itemEmEdicao.swalis || '—' }}
                    </td>
                    <td class="py-2.5 px-3">
                      <div class="flex items-center space-x-1.5">
                        <span class="font-mono font-bold text-indigo-800">
                          {{ itemEmEdicao.valores_atuais_lec?.swalis || '—' }}
                        </span>
                        <button
                          v-if="itemEmEdicao.valores_atuais_lec?.swalis"
                          type="button"
                          @click="formEdicaoIndividual.swalis = itemEmEdicao.valores_atuais_lec.swalis"
                          class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 hover:bg-indigo-200 text-indigo-800 font-semibold cursor-pointer"
                          title="Preencher com o valor do Sistema LEC"
                        >
                          Usar LEC
                        </button>
                      </div>
                    </td>
                    <td class="py-2.5 px-3">
                      <select
                        v-model="formEdicaoIndividual.swalis"
                        class="w-full border border-slate-300 rounded-lg px-2.5 py-1 bg-white text-slate-900 font-semibold"
                      >
                        <option value="A1">A1</option>
                        <option value="A2">A2</option>
                        <option value="B">B</option>
                        <option value="C">C</option>
                        <option value="D">D</option>
                        <option value="—">— (Não informado)</option>
                      </select>
                    </td>
                  </tr>

                  <!-- 2. Médico Responsável -->
                  <tr :class="isCampoDivergente(itemEmEdicao, 'medico_responsavel') ? 'bg-amber-50/60' : ''">
                    <td class="py-2.5 px-3 font-bold text-slate-800">
                      Médico Responsável
                      <span
                        v-if="isCampoDivergente(itemEmEdicao, 'medico_responsavel')"
                        class="ml-1 px-1.5 py-0.2 rounded bg-amber-200 text-amber-950 text-[10px]"
                      >
                        Divergente
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-slate-700">
                      {{ itemEmEdicao.valores_atuais_cc?.medico_responsavel || itemEmEdicao.medico_responsavel || 'Não informado' }}
                    </td>
                    <td class="py-2.5 px-3">
                      <div class="flex flex-wrap items-center gap-1.5">
                        <span class="font-bold text-indigo-800">
                          {{ itemEmEdicao.valores_atuais_lec?.medico_responsavel || 'Não informado' }}
                        </span>
                        <button
                          v-if="itemEmEdicao.valores_atuais_lec?.medico_responsavel"
                          type="button"
                          @click="formEdicaoIndividual.medico_responsavel = itemEmEdicao.valores_atuais_lec.medico_responsavel"
                          class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 hover:bg-indigo-200 text-indigo-800 font-semibold cursor-pointer"
                          title="Preencher com o médico do Sistema LEC"
                        >
                          Usar LEC
                        </button>
                      </div>
                    </td>
                    <td class="py-2.5 px-3">
                      <input
                        v-model="formEdicaoIndividual.medico_responsavel"
                        type="text"
                        class="w-full border border-slate-300 rounded-lg px-2.5 py-1 bg-white text-slate-900 font-semibold"
                        placeholder="Nome do médico responsável"
                      />
                    </td>
                  </tr>

                  <!-- 3. Lateralidade -->
                  <tr :class="isCampoDivergente(itemEmEdicao, 'lateralidade') ? 'bg-amber-50/60' : ''">
                    <td class="py-2.5 px-3 font-bold text-slate-800">
                      Lateralidade
                      <span
                        v-if="isCampoDivergente(itemEmEdicao, 'lateralidade')"
                        class="ml-1 px-1.5 py-0.2 rounded bg-amber-200 text-amber-950 text-[10px]"
                      >
                        Divergente
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-slate-700">
                      {{ itemEmEdicao.valores_atuais_cc?.lateralidade || itemEmEdicao.lateralidade || 'Indefinida' }}
                    </td>
                    <td class="py-2.5 px-3">
                      <div class="flex items-center space-x-1.5">
                        <span class="font-bold text-indigo-800">
                          {{ itemEmEdicao.valores_atuais_lec?.lateralidade || 'Indefinida' }}
                        </span>
                        <button
                          v-if="itemEmEdicao.valores_atuais_lec?.lateralidade"
                          type="button"
                          @click="formEdicaoIndividual.lateralidade = itemEmEdicao.valores_atuais_lec.lateralidade"
                          class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 hover:bg-indigo-200 text-indigo-800 font-semibold cursor-pointer"
                          title="Preencher com a lateralidade do Sistema LEC"
                        >
                          Usar LEC
                        </button>
                      </div>
                    </td>
                    <td class="py-2.5 px-3">
                      <select
                        v-model="formEdicaoIndividual.lateralidade"
                        class="w-full border border-slate-300 rounded-lg px-2.5 py-1 bg-white text-slate-900 font-semibold"
                      >
                        <option value="Indefinida">Indefinida</option>
                        <option value="Direita">Direita</option>
                        <option value="Esquerda">Esquerda</option>
                        <option value="Bilateral">Bilateral</option>
                      </select>
                    </td>
                  </tr>

                  <!-- 4. Judicialização -->
                  <tr :class="isCampoDivergente(itemEmEdicao, 'judicializado') ? 'bg-amber-50/60' : ''">
                    <td class="py-2.5 px-3 font-bold text-slate-800">
                      Judicialização
                      <span
                        v-if="isCampoDivergente(itemEmEdicao, 'judicializado')"
                        class="ml-1 px-1.5 py-0.2 rounded bg-amber-200 text-amber-950 text-[10px]"
                      >
                        Divergente
                      </span>
                    </td>
                    <td class="py-2.5 px-3 text-slate-700">
                      {{ itemEmEdicao.valores_atuais_cc?.judicializado || itemEmEdicao.judicializado || 'Não' }}
                    </td>
                    <td class="py-2.5 px-3">
                      <div class="flex items-center space-x-1.5">
                        <span class="font-bold text-indigo-800">
                          {{ itemEmEdicao.valores_atuais_lec?.judicializado || 'Não' }}
                        </span>
                        <button
                          v-if="itemEmEdicao.valores_atuais_lec?.judicializado"
                          type="button"
                          @click="formEdicaoIndividual.judicializado = itemEmEdicao.valores_atuais_lec.judicializado"
                          class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 hover:bg-indigo-200 text-indigo-800 font-semibold cursor-pointer"
                          title="Preencher com a judicialização do Sistema LEC"
                        >
                          Usar LEC
                        </button>
                      </div>
                    </td>
                    <td class="py-2.5 px-3">
                      <select
                        v-model="formEdicaoIndividual.judicializado"
                        class="w-full border border-slate-300 rounded-lg px-2.5 py-1 bg-white text-slate-900 font-semibold"
                      >
                        <option value="Não">Não</option>
                        <option value="Sim">Sim</option>
                      </select>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex items-center justify-between gap-2">
              <button
                type="button"
                @click="preencherTodosComValoresLec"
                class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer"
              >
                ↺ Preencher todos os campos com os valores do Sistema LEC
              </button>
            </div>

            <div>
              <label class="block text-[11px] font-bold text-slate-700 mb-1">
                Detalhamento / Observação para o Histórico (opcional)
              </label>
              <input
                v-model="formEdicaoIndividual.justificativa"
                type="text"
                placeholder="Ex.: Ajustado conforme conferência individual com o Sistema LEC..."
                class="w-full border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-800 text-xs"
              />
            </div>

            <div class="flex justify-end space-x-2 pt-2 border-t border-slate-200">
              <button
                type="button"
                @click="fecharModalEdicaoIndividual"
                class="px-4 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 text-xs font-semibold cursor-pointer"
                :disabled="sincronizando"
              >
                Cancelar
              </button>
              <button
                type="button"
                @click="confirmarEdicaoIndividual"
                :disabled="sincronizando"
                class="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs cursor-pointer disabled:opacity-50"
              >
                <span
                  v-if="sincronizando"
                  class="inline-block animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full"
                ></span>
                <span>Salvar Correção no CC e Registrar no Histórico</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Rodapé do Modal -->
      <div class="px-6 py-3 bg-white border-t border-slate-200 flex items-center justify-between shrink-0">
        <span class="text-[11px] text-slate-500">
          * Todas as ações de sincronização deste painel são aplicadas exclusivamente no banco de dados do <strong>Comunicação Cirúrgica</strong> e registradas no menu <strong>Histórico</strong> (origem <em>Pacientes</em>).
        </span>
        <button
          type="button"
          @click="fecharModal"
          class="px-4 py-1.5 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-bold transition cursor-pointer"
        >
          Fechar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useToast } from 'vue-toastification';
import * as XLSX from 'xlsx';
import {
  ArrowsRightLeftIcon,
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  PlusCircleIcon,
  XMarkIcon,
  ClockIcon,
  DocumentMagnifyingGlassIcon,
  ChevronRightIcon,
  CloudArrowUpIcon,
  ExclamationTriangleIcon,
  CheckBadgeIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/outline';
import {
  listarDiagnosticosLec,
  obterDiagnosticoLec,
  criarDiagnosticoLec,
  sincronizarItensDiagnosticoLec,
  type DiagnosticoLecResumo,
  type DiagnosticoLecDetalhado,
  type ItemDivergenciaLec,
} from '../services/pacienteService';

const props = defineProps({
  show: { type: Boolean, default: false },
});

const emit = defineEmits(['close', 'sincronizado']);
const toast = useToast();

const modoTela = ref<'HISTORICO' | 'NOVO' | 'DETALHES'>('HISTORICO');
const carregandoHistorico = ref(false);
const listaDiagnosticos = ref<DiagnosticoLecResumo[]>([]);
const diagnosticoAtual = ref<DiagnosticoLecDetalhado | null>(null);

// Estado de Upload (Novo Diagnóstico)
const arquivosSelecionados = ref<File[]>([]);
const isDragging = ref(false);
const processandoNovo = ref(false);
const erroMensagem = ref('');

// Estado de Visualização do Diagnóstico
const mostrarPainelCobertura = ref(true);
const abaAtiva = ref<string>('TABELA_ESPECIALIDADES');
const buscaDivergencia = ref('');
const filtroEspDivergencia = ref('');
const filtroCampoDivergente = ref('');
const filtroStatusSinc = ref<'TODOS' | 'PENDENTES' | 'SINCRONIZADOS'>('TODOS');
const itensSelecionados = ref<string[]>([]);
const sincronizando = ref(false);

// Estado do Submodal de Avaliação Individual e Correção Manual (DIVERGENCIA_DADOS_CADASTRAIS)
const itemEmEdicao = ref<ItemDivergenciaLec | null>(null);
const formEdicaoIndividual = ref<{
  swalis: string;
  medico_responsavel: string;
  lateralidade: string;
  judicializado: string;
  justificativa: string;
}>({
  swalis: '—',
  medico_responsavel: 'Não informado',
  lateralidade: 'Indefinida',
  judicializado: 'Não',
  justificativa: '',
});

watch(
  () => props.show,
  (abriu) => {
    if (abriu) {
      modoTela.value = 'HISTORICO';
      carregarListaDiagnosticos();
    }
  }
);

watch([abaAtiva, filtroEspDivergencia, filtroCampoDivergente, filtroStatusSinc], () => {
  itensSelecionados.value = [];
});

async function carregarListaDiagnosticos() {
  carregandoHistorico.value = true;
  try {
    listaDiagnosticos.value = await listarDiagnosticosLec();
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Erro ao carregar histórico de diagnósticos.');
  } finally {
    carregandoHistorico.value = false;
  }
}

function abrirTelaNovoDiagnostico() {
  arquivosSelecionados.value = [];
  erroMensagem.value = '';
  modoTela.value = 'NOVO';
}

function voltarParaHistorico() {
  modoTela.value = 'HISTORICO';
  carregarListaDiagnosticos();
}

async function selecionarDiagnosticoExistente(id: string) {
  try {
    carregandoHistorico.value = true;
    diagnosticoAtual.value = await obterDiagnosticoLec(id);
    abaAtiva.value = 'TABELA_ESPECIALIDADES';
    filtroEspDivergencia.value = '';
    buscaDivergencia.value = '';
    itensSelecionados.value = [];
    modoTela.value = 'DETALHES';
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Erro ao abrir diagnóstico.');
  } finally {
    carregandoHistorico.value = false;
  }
}

function adicionarArquivosValidos(fileList: FileList | File[]) {
  erroMensagem.value = '';
  for (const f of Array.from(fileList)) {
    const lower = f.name.toLowerCase();
    if (!lower.endsWith('.xlsx') && !lower.endsWith('.xls') && !lower.endsWith('.zip')) {
      erroMensagem.value = `O arquivo "${f.name}" não é suportado. Selecione apenas arquivos .xlsx, .xls ou .zip.`;
      continue;
    }
    if (!arquivosSelecionados.value.some((x) => x.name === f.name && x.size === f.size)) {
      arquivosSelecionados.value.push(f);
    }
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false;
  if (e.dataTransfer?.files?.length) {
    adicionarArquivosValidos(e.dataTransfer.files);
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files?.length) {
    adicionarArquivosValidos(target.files);
    target.value = '';
  }
}

function removerArquivo(idx: number) {
  arquivosSelecionados.value.splice(idx, 1);
}

async function executarNovoDiagnostico() {
  if (arquivosSelecionados.value.length === 0) return;
  processandoNovo.value = true;
  erroMensagem.value = '';
  try {
    const novo = await criarDiagnosticoLec(arquivosSelecionados.value);
    diagnosticoAtual.value = novo;
    abaAtiva.value = 'TABELA_ESPECIALIDADES';
    mostrarPainelCobertura.value = true;
    modoTela.value = 'DETALHES';
    toast.success('Diagnóstico concluído e salvo no histórico!');
  } catch (err: any) {
    erroMensagem.value = err?.response?.data?.detail || 'Erro ao processar as planilhas do Sistema LEC.';
  } finally {
    processandoNovo.value = false;
  }
}

const abasDiagnostico = computed(() => {
  const c = diagnosticoAtual.value?.contagem_categorias || ({} as Record<string, number>);
  return [
    {
      id: 'TABELA_ESPECIALIDADES',
      icone: '📊',
      titulo: 'Resumo por Especialidade',
      contador: diagnosticoAtual.value?.tabela_especialidades?.length || 0,
    },
    {
      id: 'EXCLUSAO_APROVADA_CC_PENDENTE_LEC',
      icone: '🔴',
      titulo: 'Exclusões Aprovadas no CC Pendentes no LEC',
      contador: c.EXCLUSAO_APROVADA_CC_PENDENTE_LEC || 0,
    },
    {
      id: 'INCLUSAO_APROVADA_CC_PENDENTE_LEC',
      icone: '🟠',
      titulo: 'Inclusões Aprovadas no CC Pendentes no LEC',
      contador: c.INCLUSAO_APROVADA_CC_PENDENTE_LEC || 0,
    },
    {
      id: 'EM_OUTRA_ESPECIALIDADE_NO_CC',
      icone: '🟣',
      titulo: 'Em Outra Especialidade no CC',
      contador: c.EM_OUTRA_ESPECIALIDADE_NO_CC || 0,
    },
    {
      id: 'DIVERGENCIA_DADOS_CADASTRAIS',
      icone: '🟡',
      titulo: 'Divergência de Informações (Swalis, Médico, Lat., Jud.)',
      contador: c.DIVERGENCIA_DADOS_CADASTRAIS || 0,
    },
    {
      id: 'INSERIDO_DIRETO_NO_LEC',
      icone: '🔵',
      titulo: 'Inseridos Direto no LEC (Sem CC)',
      contador: c.INSERIDO_DIRETO_NO_LEC || 0,
    },
    {
      id: 'SAIU_DO_LEC_SEM_BAIXA_NO_CC',
      icone: '⚪',
      titulo: 'Saíram do LEC sem Exclusão no CC',
      contador: c.SAIU_DO_LEC_SEM_BAIXA_NO_CC || 0,
    },
    {
      id: 'TODAS',
      icone: '📋',
      titulo: 'Todas as Divergências',
      contador: diagnosticoAtual.value?.total_divergencias || 0,
    },
  ];
});

const infoCategoriaAtiva = computed(() => {
  switch (abaAtiva.value) {
    case 'EXCLUSAO_APROVADA_CC_PENDENTE_LEC':
      return {
        titulo: '🔴 Pacientes com Exclusão já Aprovada no Comunicação Cirúrgica, mas que continuam ativos no Sistema LEC',
        descricao:
          'A Gestão LEC já aprovou a solicitação de EXCLUIR destes pacientes no Comunicação Cirúrgica, porém eles continuam na planilha do Sistema LEC. Visualize abaixo ou exporte em Excel para efetivar a exclusão lá no Sistema LEC.',
        acaoLote: null,
      };
    case 'INCLUSAO_APROVADA_CC_PENDENTE_LEC':
      return {
        titulo: '🟠 Pacientes com Inclusão Aprovada no Comunicação Cirúrgica que não constam na planilha do Sistema LEC',
        descricao:
          'Pacientes cuja solicitação de INSERIR foi aprovada no Comunicação Cirúrgica, mas que ainda não foram lançados no Sistema LEC (ou tiveram erro de digitação de prontuário). Caso deseje excluir do CC, selecione e clique em Excluir do CC.',
        acaoLote: {
          codigo: 'EXCLUIR_DO_CC',
          label: 'Excluir do CC',
          corClasse: 'bg-rose-600 hover:bg-rose-700',
        },
      };
    case 'EM_OUTRA_ESPECIALIDADE_NO_CC':
      return {
        titulo: '🟣 Pacientes em Especialidades Diferentes entre o Sistema LEC e o Comunicação Cirúrgica',
        descricao:
          'Estes pacientes estão nos dois sistemas, porém cadastrados em especialidades distintas (ex.: solicitados em GERAL no Comunicação Cirúrgica e inseridos em BARIÁTRICA no Sistema LEC). Você pode transferir a especialidade deles no CC (registrada no Histórico como Edição de Execução).',
        acaoLote: {
          codigo: 'TRANSFERIR_ESPECIALIDADE_NO_CC',
          label: 'Transferir para Especialidade do LEC (no CC)',
          corClasse: 'bg-purple-600 hover:bg-purple-700',
        },
      };
    case 'DIVERGENCIA_DADOS_CADASTRAIS':
      return {
        titulo: '🟡 Pacientes na Mesma Especialidade, mas com Divergência de Informações (Swalis, Médico Responsável, Lateralidade ou Judicialização)',
        descricao:
          'Estes pacientes estão ativos em ambos os sistemas na mesma especialidade, porém há divergência entre o Comunicação Cirúrgica e o Sistema LEC nas informações de Swalis, Médico Responsável, Lateralidade ou Judicialização. Cada caso deve ser avaliado individualmente e corrigido manualmente pelo usuário Gestão LEC clicando em "Avaliar / Corrigir no CC".',
        acaoLote: null,
      };
    case 'INSERIDO_DIRETO_NO_LEC':
      return {
        titulo: '🔵 Pacientes Inseridos Diretamente no Sistema LEC (Sem Passagem pelo Comunicação Cirúrgica)',
        descricao:
          'Estes pacientes constam ativos na planilha do Sistema LEC, mas nunca tiveram solicitação aberta/aprovada no Comunicação Cirúrgica. Selecione-os para incluí-los automaticamente na fila ativa do Comunicação Cirúrgica.',
        acaoLote: {
          codigo: 'INCLUIR_NO_CC',
          label: '+ Incluir no Comunicação Cirúrgica',
          corClasse: 'bg-emerald-600 hover:bg-emerald-700',
        },
      };
    case 'SAIU_DO_LEC_SEM_BAIXA_NO_CC':
      return {
        titulo: '⚪ Pacientes que já saíram do Sistema LEC (Operados ou Excluídos no LEC) sem Exclusão no Comunicação Cirúrgica',
        descricao:
          'Estes pacientes vieram de importações anteriores (ou testes) e continuam ativos na aba Pacientes do Comunicação Cirúrgica, mas não estão mais na lista ativa do Sistema LEC. Selecione-os para excluí-los da fila ativa do CC.',
        acaoLote: {
          codigo: 'EXCLUIR_DO_CC',
          label: 'Excluir do Comunicação Cirúrgica',
          corClasse: 'bg-rose-600 hover:bg-rose-700',
        },
      };
    default:
      return {
        titulo: '📋 Visão Consolidada de Todas as Divergências Encontradas',
        descricao:
          'Visualize, pesquise e filtre todas as divergências entre o Comunicação Cirúrgica e o Sistema LEC diretamente na tela ou exporte para Excel.',
        acaoLote: null,
      };
  }
});

const especialidadesComDivergencia = computed(() => {
  if (!diagnosticoAtual.value) return [];
  const set = new Set<string>();
  for (const d of diagnosticoAtual.value.divergencias) {
    if (abaAtiva.value === 'TODAS' || d.categoria === abaAtiva.value) {
      set.add(d.especialidade);
    }
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

const divergenciasFiltradasSemStatus = computed(() => {
  if (!diagnosticoAtual.value) return [];
  const termo = buscaDivergencia.value.trim().toLowerCase();
  return diagnosticoAtual.value.divergencias.filter((d) => {
    if (abaAtiva.value !== 'TODAS' && d.categoria !== abaAtiva.value) return false;
    if (filtroEspDivergencia.value && d.especialidade !== filtroEspDivergencia.value) return false;
    if (
      filtroCampoDivergente.value &&
      (abaAtiva.value === 'DIVERGENCIA_DADOS_CADASTRAIS' || abaAtiva.value === 'TODAS')
    ) {
      const hasCampo = (d.campos_divergentes || []).some((cd) => cd.chave === filtroCampoDivergente.value);
      if (!hasCampo) return false;
    }
    if (termo) {
      const matchPront = String(d.prontuario).includes(termo);
      const matchNome = (d.nome_paciente || '').toLowerCase().includes(termo);
      const matchProc = (d.procedimento || '').toLowerCase().includes(termo);
      if (!matchPront && !matchNome && !matchProc) return false;
    }
    return true;
  });
});

const divergenciasVisiveis = computed(() => {
  return divergenciasFiltradasSemStatus.value.filter((d) => {
    if (filtroStatusSinc.value === 'PENDENTES') return !d.sincronizado_no_cc;
    if (filtroStatusSinc.value === 'SINCRONIZADOS') return d.sincronizado_no_cc;
    return true;
  });
});

const itensElegiveisVisiveis = computed(() =>
  divergenciasVisiveis.value.filter((d) => !d.sincronizado_no_cc && d.acao_sugerida_cc !== 'NENHUMA_ACAO_NO_CC')
);

const todosVisiveisSelecionados = computed(() => {
  if (itensElegiveisVisiveis.value.length === 0) return false;
  const selSet = new Set(itensSelecionados.value);
  return itensElegiveisVisiveis.value.every((d) => selSet.has(d.item_id));
});

function toggleSelecionarTodosVisiveis() {
  if (todosVisiveisSelecionados.value) {
    itensSelecionados.value = [];
  } else {
    itensSelecionados.value = itensElegiveisVisiveis.value.map((d) => d.item_id);
  }
}

function filtrarDivergenciasPorEspecialidade(especialidade: string) {
  filtroEspDivergencia.value = especialidade;
  abaAtiva.value = 'TODAS';
}

function isCampoDivergente(item: ItemDivergenciaLec, chave: string): boolean {
  return Boolean(item.campos_divergentes?.some((cd) => cd.chave === chave));
}

function abrirModalEdicaoIndividual(item: ItemDivergenciaLec) {
  itemEmEdicao.value = item;
  const cc = item.valores_atuais_cc;
  formEdicaoIndividual.value = {
    swalis: cc?.swalis || item.swalis || '—',
    medico_responsavel: cc?.medico_responsavel || item.medico_responsavel || 'Não informado',
    lateralidade: cc?.lateralidade || item.lateralidade || 'Indefinida',
    judicializado: cc?.judicializado || item.judicializado || 'Não',
    justificativa: '',
  };
}

function fecharModalEdicaoIndividual() {
  itemEmEdicao.value = null;
}

function preencherTodosComValoresLec() {
  if (!itemEmEdicao.value?.valores_atuais_lec) return;
  const lec = itemEmEdicao.value.valores_atuais_lec;
  formEdicaoIndividual.value.swalis = lec.swalis || formEdicaoIndividual.value.swalis;
  formEdicaoIndividual.value.medico_responsavel = lec.medico_responsavel || formEdicaoIndividual.value.medico_responsavel;
  formEdicaoIndividual.value.lateralidade = lec.lateralidade || formEdicaoIndividual.value.lateralidade;
  formEdicaoIndividual.value.judicializado = lec.judicializado || formEdicaoIndividual.value.judicializado;
}

async function confirmarEdicaoIndividual() {
  if (!diagnosticoAtual.value || !itemEmEdicao.value) return;
  sincronizando.value = true;
  try {
    const resp = await sincronizarItensDiagnosticoLec(
      diagnosticoAtual.value.id,
      [itemEmEdicao.value.item_id],
      'EDITAR_INFORMACOES_NO_CC',
      { ...formEdicaoIndividual.value }
    );
    diagnosticoAtual.value = resp.diagnostico;
    toast.success(
      `Informações do prontuário ${itemEmEdicao.value.prontuario} atualizadas no CC e registradas no Histórico!`
    );
    itemEmEdicao.value = null;
    emit('sincronizado');
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Erro ao salvar correção manual no Comunicação Cirúrgica.');
  } finally {
    sincronizando.value = false;
  }
}

async function executarSincronizacaoIndividual(item: ItemDivergenciaLec, acao: string) {
  if (!diagnosticoAtual.value) return;
  sincronizando.value = true;
  try {
    const resp = await sincronizarItensDiagnosticoLec(diagnosticoAtual.value.id, [item.item_id], acao);
    diagnosticoAtual.value = resp.diagnostico;
    itensSelecionados.value = itensSelecionados.value.filter((id) => id !== item.item_id);
    toast.success(`Prontuário ${item.prontuario} atualizado no CC e registrado no Histórico!`);
    emit('sincronizado');
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Erro ao sincronizar item no Comunicação Cirúrgica.');
  } finally {
    sincronizando.value = false;
  }
}

async function executarSincronizacaoEmLote(acao: string) {
  if (!diagnosticoAtual.value || itensSelecionados.value.length === 0) return;
  sincronizando.value = true;
  try {
    const resp = await sincronizarItensDiagnosticoLec(
      diagnosticoAtual.value.id,
      itensSelecionados.value,
      acao
    );
    diagnosticoAtual.value = resp.diagnostico;
    itensSelecionados.value = [];
    toast.success(
      `${resp.sincronizados_agora} paciente(s) atualizado(s) no CC e registrado(s) no Histórico!`
    );
    emit('sincronizado');
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Erro ao executar sincronização em lote.');
  } finally {
    sincronizando.value = false;
  }
}

function exportarExcelDiagnostico(apenasAbaVisivel: boolean) {
  if (!diagnosticoAtual.value) return;
  const wb = XLSX.utils.book_new();

  if (!apenasAbaVisivel) {
    const resumoRows = diagnosticoAtual.value.tabela_especialidades.map((r) => ({
      Especialidade: r.especialidade,
      'Ativa no CC': r.cadastrada_no_cc ? 'Sim' : 'Não',
      'Linhas Sistema LEC': r.lec_linhas,
      'Prontuários Sistema LEC': r.lec_prontuarios,
      'Linhas Com. Cirúrgica': r.cc_linhas,
      'Prontuários Com. Cirúrgica': r.cc_prontuarios,
      'Em Ambos': r.em_ambos,
      'Só no Sistema LEC': r.so_no_lec,
      'Só no Com. Cirúrgica': r.so_no_cc,
      'Divergências de Informação (Em Ambos)': r.divergencias_info || 0,
      'Sincronia (%)': r.cadastrada_no_cc ? `${r.percentual_sincronia}%` : '—',
    }));
    const wsResumo = XLSX.utils.json_to_sheet(resumoRows);
    XLSX.utils.book_append_sheet(wb, wsResumo, 'Resumo Especialidades');
  }

  const fonteDivergencias = apenasAbaVisivel
    ? divergenciasVisiveis.value
    : diagnosticoAtual.value.divergencias;

  const divRows = fonteDivergencias.map((d) => ({
    Categoria: d.categoria,
    Prontuário: d.prontuario,
    Paciente: d.nome_paciente,
    Especialidade: d.especialidade,
    'Outra Especialidade (CC)': d.especialidade_secundaria || '—',
    Procedimento: d.procedimento,
    'Médico Responsável': d.medico_responsavel,
    Swalis: d.swalis,
    Lateralidade: d.lateralidade || 'Indefinida',
    Judicializado: d.judicializado,
    'Data Referência': d.data_referencia,
    'Diagnóstico / Comparativo (CC x LEC)': d.detalhes_status,
    'Atualizado no CC': d.sincronizado_no_cc ? 'Sim' : 'Não',
    'Data Atualização CC': d.data_sincronizacao || '—',
    'Usuário Executor': d.usuario_sincronizacao || '—',
  }));

  const wsDiv = XLSX.utils.json_to_sheet(divRows);
  XLSX.utils.book_append_sheet(wb, wsDiv, apenasAbaVisivel ? 'Lista Filtrada' : 'Todas Divergencias');

  const sufixo = apenasAbaVisivel ? abaAtiva.value.toLowerCase() : diagnosticoAtual.value.id;
  XLSX.writeFile(wb, `diagnostico_cc_x_lec_${sufixo}.xlsx`);
}

function formatarDataHora(dt: string) {
  if (!dt || dt === '—') return '—';
  const parts = dt.split(' ');
  const d = parts[0].split('-');
  if (d.length === 3) {
    return `${d[2]}/${d[1]}/${d[0]}${parts[1] ? ' às ' + parts[1] : ''}`;
  }
  return dt;
}

function fecharModal() {
  emit('close');
}
</script>

