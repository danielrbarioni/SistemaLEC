<template>
  <div class="space-y-5">
    <!-- Cabeçalho Principal e Controles Globais -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
      <div>
        <div class="flex items-center space-x-2.5 flex-wrap">
          <h1 class="text-xl font-bold text-gray-800">Navegação da Jornada Cirúrgica</h1>
          <span class="px-2.5 py-0.5 bg-teal-100 text-teal-800 text-xs font-bold rounded-full border border-teal-200">
            Leitura Direta AGHU
          </span>
          <span v-if="atualizadoEm" class="text-xs text-gray-500 font-mono">
            Atualizado em: {{ atualizadoEm }}
          </span>
        </div>
        <p class="text-xs text-gray-500 mt-1">
          Acompanhamento dos pacientes nos estágios pré-operatórios (Consultas EPO, Exames/Pareceres Pré-Op e Avaliação Pré-Anestésica — APA) a partir das grades e exames do AGHU.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Recorte Temporal -->
        <div class="flex items-center space-x-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5">
          <span class="text-xs font-semibold text-slate-600">Janela AGHU:</span>
          <select
            v-model.number="janelaMeses"
            @change="carregarPaineis(true)"
            class="text-xs font-bold text-slate-800 bg-transparent border-none focus:ring-0 cursor-pointer"
          >
            <option :value="3">Últimos 3 meses</option>
            <option :value="6">Últimos 6 meses</option>
            <option :value="12">Últimos 12 meses</option>
            <option :value="18">Últimos 18 meses</option>
            <option :value="24">Últimos 24 meses</option>
          </select>
        </div>

        <!-- Botão Configurar Consultas e Exames Monitorados -->
        <button
          type="button"
          @click="abrirModalConfig"
          class="inline-flex items-center space-x-1.5 px-3 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs rounded-lg border border-indigo-200 transition cursor-pointer"
        >
          <span>⚙️</span>
          <span>Consultas e Exames monitorados</span>
        </button>

        <!-- Botão Atualizar do AGHU -->
        <button
          type="button"
          @click="carregarPaineis(true)"
          :disabled="loading"
          class="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white font-semibold text-xs rounded-lg shadow-xs transition cursor-pointer"
        >
          <span>{{ loading ? '⏳' : '🔄' }}</span>
          <span>{{ loading ? 'Consultando AGHU...' : 'Atualizar do AGHU' }}</span>
        </button>
      </div>
    </div>

    <!-- Busca Global de Paciente em Todos os Estágios da Jornada Cirúrgica -->
    <Card>
      <div class="space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 class="text-sm font-bold text-gray-800 flex items-center space-x-1.5">
              <span>🔎</span>
              <span>Localizar Paciente na Jornada Cirúrgica (Busca Global nas 6 Tabelas)</span>
            </h2>
            <p class="text-xs text-gray-500">
              Digite o número do prontuário ou nome para verificar se e em qual(is) estágio(s) da navegação o paciente se encontra.
            </p>
          </div>
          <button
            v-if="buscaGlobalProntuario"
            type="button"
            @click="buscaGlobalProntuario = ''"
            class="text-xs text-indigo-600 hover:text-indigo-800 font-semibold self-end sm:self-auto cursor-pointer"
          >
            ✕ Limpar busca global
          </button>
        </div>

        <div class="relative">
          <input
            v-model="buscaGlobalProntuario"
            type="text"
            placeholder="Digite o nº do prontuário (ex.: 22103329) ou nome do paciente..."
            class="form-control text-sm pr-10"
          />
        </div>

        <!-- Resultados da Busca Global -->
        <div v-if="buscaGlobalProntuario.trim().length >= 2" class="pt-2">
          <div v-if="resultadosBuscaGlobal.length === 0" class="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
            Nenhum paciente encontrado com <strong>"{{ buscaGlobalProntuario }}"</strong> nas tabelas da jornada cirúrgica dentro da janela dos últimos {{ janelaMeses }} meses.
          </div>
          <div v-else class="space-y-2.5 max-h-72 overflow-y-auto pr-1">
            <div
              v-for="pac in resultadosBuscaGlobal"
              :key="pac.prontuario"
              class="p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div>
                <div class="flex items-center space-x-2 flex-wrap">
                  <span class="font-mono font-bold text-indigo-900 bg-indigo-100 px-2 py-0.5 rounded text-xs">
                    #{{ pac.prontuario }}
                  </span>
                  <span class="font-bold text-gray-900 text-sm">{{ pac.nome_paciente }}</span>
                  <span
                    v-if="pac.possui_nome_social"
                    class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200 uppercase"
                  >
                    Nome Social
                  </span>
                  <span v-if="pac.dt_nascimento" class="text-xs text-gray-500">
                    (Nasc.: {{ formatarData(pac.dt_nascimento) }})
                  </span>
                </div>
                <div class="text-[11px] text-gray-500 mt-0.5">
                  Presente em <strong>{{ pac.ocorrencias.length }}</strong> registro(s) nos painéis da jornada:
                </div>
              </div>

              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="(oc, idx) in pac.ocorrencias"
                  :key="idx"
                  type="button"
                  @click="irParaTabelaComProntuario(oc.abaId, pac.prontuario, oc.subtabela, oc.substatusAcao)"
                  class="px-2.5 py-1.5 rounded-lg border text-left transition cursor-pointer hover:shadow-xs text-xs flex flex-col"
                  :class="oc.badgeClass"
                  title="Clique para abrir esta tabela filtrada neste prontuário"
                >
                  <span class="font-bold flex items-center space-x-1 flex-wrap">
                    <span>{{ oc.tabelaTitulo }}</span>
                    <span v-if="oc.subtabela && oc.subtabela !== 'PRINCIPAL'" class="px-1.5 py-0.2 rounded bg-black/10 text-[10px]">
                      Subtabela: {{ oc.subtabelaLabel }}
                      <template v-if="oc.substatusLabel"> · {{ oc.substatusLabel }}</template>
                    </span>
                    <span>↗</span>
                  </span>
                  <span class="text-[11px] opacity-90">
                    Grade {{ oc.grade_sigla }} · {{ formatarDataHora(oc.data_consulta) }} · {{ oc.status }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>

    <!-- Seleção das 6 Tabelas em 2 Fileiras Agrupadas nos 4 Estágios da Jornada Cirúrgica -->
    <div class="space-y-3.5">
      <!-- Fileira 1: Estágio 1 (Tabelas 1.1 e 1.2) + Estágio 2 (Tabela 2) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3.5">
        <!-- ESTÁGIO 1 (2 colunas: Tabelas 1.1 e 1.2) -->
        <div
          class="lg:col-span-2 rounded-2xl border-2 p-3 transition flex flex-col justify-between"
          :class="abaAtiva === 'T1_1' || abaAtiva === 'T1_2'
            ? 'bg-indigo-50/70 border-indigo-400 shadow-xs'
            : 'bg-indigo-50/25 border-indigo-200/80'"
        >
          <div class="flex items-center justify-between gap-2 mb-2.5 px-0.5">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider bg-indigo-600 text-white shadow-2xs">
                Estágio 1
              </span>
              <span class="text-xs font-bold text-indigo-950">
                Consulta de Enfermagem (EPO) — Agendada / Não Realizada
              </span>
            </div>
            <span class="text-[11px] font-bold text-indigo-700 font-mono bg-indigo-100/80 px-2 py-0.5 rounded-full border border-indigo-200">
              {{ tabela11EpoAgendada.length + tabela12EpoNaoRealizada.length }} pac.
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              v-for="aba in abasEstagio1"
              :key="aba.id"
              type="button"
              @click="selecionarAbaTabela(aba.id)"
              class="p-3.5 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between"
              :class="abaAtiva === aba.id ? aba.activeClass : aba.inactiveClass"
            >
              <div class="flex items-center justify-between w-full gap-1.5">
                <span
                  class="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded"
                  :class="abaAtiva === aba.id ? 'bg-white/20 text-white' : aba.pillClass"
                >
                  {{ aba.codigo }}
                </span>
                <div class="flex items-center space-x-1.5">
                  <span
                    v-if="aba.alertasPendentes > 0"
                    class="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-red-600 text-white shadow-xs"
                    :title="`${aba.alertasPendentes} alerta(s) de ação pendente na subtabela`"
                  >
                    {{ aba.alertasPendentes }}
                  </span>
                  <span class="text-lg font-extrabold font-mono" :title="aba.totalSubtabelas > 0 ? `${aba.totalPrincipal} na Lista Principal + ${aba.totalSubtabelas} em Subtabelas` : ''">
                    {{ aba.totalPrincipal }}
                  </span>
                </div>
              </div>
              <div class="mt-2.5">
                <div class="text-xs font-bold leading-snug">{{ aba.titulo }}</div>
                <div class="text-[10px] mt-0.5" :class="abaAtiva === aba.id ? 'text-white/85' : 'text-gray-500'">
                  {{ aba.subtitulo }}
                  <span v-if="aba.totalSubtabelas > 0" class="font-bold">
                    · ({{ aba.totalSubtabelas }} em subtabelas)
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- ESTÁGIO 2 (1 coluna: Tabela 2) -->
        <div
          class="lg:col-span-1 rounded-2xl border-2 p-3 transition flex flex-col justify-between"
          :class="abaAtiva === 'T2'
            ? 'bg-teal-50/70 border-teal-500 shadow-xs'
            : 'bg-teal-50/25 border-teal-200/80'"
        >
          <div class="flex items-center justify-between gap-2 mb-2.5 px-0.5">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider bg-teal-700 text-white shadow-2xs">
                Estágio 2
              </span>
              <span class="text-xs font-bold text-teal-950">
                Consulta EPO Realizada
              </span>
            </div>
            <span class="text-[11px] font-bold text-teal-800 font-mono bg-teal-100/80 px-2 py-0.5 rounded-full border border-teal-200">
              {{ tabela2EpoRealizada.length }} pac.
            </span>
          </div>

          <div class="grid grid-cols-1 gap-2.5 flex-1">
            <button
              v-for="aba in abasEstagio2"
              :key="aba.id"
              type="button"
              @click="selecionarAbaTabela(aba.id)"
              class="p-3.5 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between h-full"
              :class="abaAtiva === aba.id ? aba.activeClass : aba.inactiveClass"
            >
              <div class="flex items-center justify-between w-full gap-1.5">
                <span
                  class="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded"
                  :class="abaAtiva === aba.id ? 'bg-white/20 text-white' : aba.pillClass"
                >
                  {{ aba.codigo }}
                </span>
                <div class="flex items-center space-x-1.5">
                  <span
                    v-if="aba.alertasPendentes > 0"
                    class="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-red-600 text-white shadow-xs"
                    :title="`${aba.alertasPendentes} alerta(s) de ação pendente na subtabela`"
                  >
                    {{ aba.alertasPendentes }}
                  </span>
                  <span class="text-lg font-extrabold font-mono" :title="aba.totalSubtabelas > 0 ? `${aba.totalPrincipal} na Lista Principal + ${aba.totalSubtabelas} em Subtabelas` : ''">
                    {{ aba.totalPrincipal }}
                  </span>
                </div>
              </div>
              <div class="mt-2.5">
                <div class="text-xs font-bold leading-snug">{{ aba.titulo }}</div>
                <div class="text-[10px] mt-0.5" :class="abaAtiva === aba.id ? 'text-white/85' : 'text-gray-500'">
                  {{ aba.subtitulo }}
                  <span v-if="aba.totalSubtabelas > 0" class="font-bold">
                    · ({{ aba.totalSubtabelas }} em subtabelas)
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Fileira 2: Estágio 3 (Tabelas 3.1 e 3.2) + Estágio 4 (Tabela 4) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3.5">
        <!-- ESTÁGIO 3 (2 colunas: Tabelas 3.1 e 3.2) -->
        <div
          class="lg:col-span-2 rounded-2xl border-2 p-3 transition flex flex-col justify-between"
          :class="abaAtiva === 'T3_1' || abaAtiva === 'T3_2'
            ? 'bg-amber-50/70 border-amber-400 shadow-xs'
            : 'bg-amber-50/25 border-amber-200/80'"
        >
          <div class="flex items-center justify-between gap-2 mb-2.5 px-0.5">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider bg-amber-600 text-white shadow-2xs">
                Estágio 3
              </span>
              <span class="text-xs font-bold text-amber-950">
                Avaliação Pré-Anestésica (APA) — Agendada / Não Realizada
              </span>
            </div>
            <span class="text-[11px] font-bold text-amber-800 font-mono bg-amber-100/80 px-2 py-0.5 rounded-full border border-amber-200">
              {{ tabela31ApaAgendada.length + tabela32ApaNaoRealizada.length }} pac.
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              v-for="aba in abasEstagio3"
              :key="aba.id"
              type="button"
              @click="selecionarAbaTabela(aba.id)"
              class="p-3.5 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between"
              :class="abaAtiva === aba.id ? aba.activeClass : aba.inactiveClass"
            >
              <div class="flex items-center justify-between w-full gap-1.5">
                <span
                  class="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded"
                  :class="abaAtiva === aba.id ? 'bg-white/20 text-white' : aba.pillClass"
                >
                  {{ aba.codigo }}
                </span>
                <div class="flex items-center space-x-1.5">
                  <span
                    v-if="aba.alertasPendentes > 0"
                    class="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-red-600 text-white shadow-xs"
                    :title="`${aba.alertasPendentes} alerta(s) de ação pendente na subtabela`"
                  >
                    {{ aba.alertasPendentes }}
                  </span>
                  <span class="text-lg font-extrabold font-mono" :title="aba.totalSubtabelas > 0 ? `${aba.totalPrincipal} na Lista Principal + ${aba.totalSubtabelas} em Subtabelas` : ''">
                    {{ aba.totalPrincipal }}
                  </span>
                </div>
              </div>
              <div class="mt-2.5">
                <div class="text-xs font-bold leading-snug">{{ aba.titulo }}</div>
                <div class="text-[10px] mt-0.5" :class="abaAtiva === aba.id ? 'text-white/85' : 'text-gray-500'">
                  {{ aba.subtitulo }}
                  <span v-if="aba.totalSubtabelas > 0" class="font-bold">
                    · ({{ aba.totalSubtabelas }} em subtabelas)
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- ESTÁGIO 4 (1 coluna: Tabela 4) -->
        <div
          class="lg:col-span-1 rounded-2xl border-2 p-3 transition flex flex-col justify-between"
          :class="abaAtiva === 'T4'
            ? 'bg-emerald-50/70 border-emerald-500 shadow-xs'
            : 'bg-emerald-50/25 border-emerald-200/80'"
        >
          <div class="flex items-center justify-between gap-2 mb-2.5 px-0.5">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider bg-emerald-700 text-white shadow-2xs">
                Estágio 4
              </span>
              <span class="text-xs font-bold text-emerald-950">
                APA Realizada
              </span>
            </div>
            <span class="text-[11px] font-bold text-emerald-800 font-mono bg-emerald-100/80 px-2 py-0.5 rounded-full border border-emerald-200">
              {{ tabela4ApaRealizada.length }} pac.
            </span>
          </div>

          <div class="grid grid-cols-1 gap-2.5 flex-1">
            <button
              v-for="aba in abasEstagio4"
              :key="aba.id"
              type="button"
              @click="selecionarAbaTabela(aba.id)"
              class="p-3.5 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between h-full"
              :class="abaAtiva === aba.id ? aba.activeClass : aba.inactiveClass"
            >
              <div class="flex items-center justify-between w-full gap-1.5">
                <span
                  class="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded"
                  :class="abaAtiva === aba.id ? 'bg-white/20 text-white' : aba.pillClass"
                >
                  {{ aba.codigo }}
                </span>
                <div class="flex items-center space-x-1.5">
                  <span
                    v-if="aba.alertasPendentes > 0"
                    class="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-red-600 text-white shadow-xs"
                    :title="`${aba.alertasPendentes} alerta(s) de ação pendente na subtabela`"
                  >
                    {{ aba.alertasPendentes }}
                  </span>
                  <span class="text-lg font-extrabold font-mono" :title="aba.totalSubtabelas > 0 ? `${aba.totalPrincipal} na Lista Principal + ${aba.totalSubtabelas} em Subtabelas` : ''">
                    {{ aba.totalPrincipal }}
                  </span>
                </div>
              </div>
              <div class="mt-2.5">
                <div class="text-xs font-bold leading-snug">{{ aba.titulo }}</div>
                <div class="text-[10px] mt-0.5" :class="abaAtiva === aba.id ? 'text-white/85' : 'text-gray-500'">
                  {{ aba.subtitulo }}
                  <span v-if="aba.totalSubtabelas > 0" class="font-bold">
                    · ({{ aba.totalSubtabelas }} em subtabelas)
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Barra de Subtabelas (Lista Principal vs Subtabelas de Classificação) nas Tabelas 1.2, 2, 3.2 e 4 -->
    <div v-if="subtabelasAbaAtual.length > 0" class="bg-white p-3.5 rounded-xl border border-gray-200 shadow-xs space-y-2">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <span class="text-xs font-bold text-gray-700 uppercase tracking-wider">
          Visão dentro de {{ abaAtualInfo?.codigo }} ({{ abaAtualInfo?.titulo }}):
        </span>
        <span class="text-[11px] text-gray-500">
          Pacientes classificados saem da <strong>Lista Principal</strong> e ficam segregados na subtabela até novo evento no AGHU (ou desfazimento).
        </span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        <button
          v-for="sub in subtabelasAbaAtual"
          :key="sub.id"
          type="button"
          @click="selecionarSubtabela(sub.id)"
          class="p-3 rounded-xl border text-left transition cursor-pointer flex items-center justify-between gap-2"
          :class="subtabelaAtiva === sub.id
            ? 'bg-slate-900 border-slate-900 text-white shadow-xs'
            : 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-800'"
        >
          <div>
            <div class="text-xs font-bold flex items-center space-x-1.5">
              <span>{{ sub.icone }}</span>
              <span>{{ sub.titulo }}</span>
            </div>
            <div class="text-[10px] mt-0.5" :class="subtabelaAtiva === sub.id ? 'text-slate-300' : 'text-slate-500'">
              {{ sub.descricao }}
            </div>
          </div>

          <div class="flex items-center space-x-1.5 shrink-0">
            <!-- Número em vermelho de alertas de ação pendente (check ainda não dado) -->
            <span
              v-if="sub.alertasPendentes > 0"
              class="px-2 py-0.5 rounded-full text-xs font-extrabold bg-red-600 text-white shadow-xs"
              :title="`${sub.alertasPendentes} ação(ões) pendente(s) (check ainda não dado)`"
            >
              {{ sub.alertasPendentes }}
            </span>
            <span
              class="px-2.5 py-0.5 rounded-lg text-sm font-extrabold font-mono"
              :class="subtabelaAtiva === sub.id ? 'bg-white/15 text-white' : 'bg-white border border-slate-200 text-slate-800'"
            >
              {{ sub.total }}
            </span>
          </div>
        </button>
      </div>

      <!-- Subdivisão interna para Subtabelas com Ação (Ações Pendentes vs Ações Solicitadas) -->
      <div v-if="subtabelaPossuiSubdivisao" class="pt-2.5 mt-2 border-t border-slate-200 space-y-2">
        <div class="flex items-center justify-between flex-wrap gap-1">
          <span class="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
            Subdivisão da Subtabela "{{ subtabelaAtualInfo?.titulo?.replace('Subtabela: ', '') }}":
          </span>
          <span class="text-[11px] text-slate-500">
            Selecione entre as <strong>Ações Pendentes</strong> (que geram o alerta vermelho e podem ser canceladas) e as <strong>Ações Solicitadas</strong> (check dado, que podem ser desfeitas).
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <!-- Sub-aba 1: Ações Pendentes (Check ainda não dado) -->
          <button
            type="button"
            @click="selecionarSubstatusAcao('PENDENTES')"
            class="p-3 rounded-xl border-2 text-left transition cursor-pointer flex items-center justify-between gap-2"
            :class="substatusAcaoAtiva === 'PENDENTES'
              ? 'bg-red-700 border-red-700 text-white shadow-xs'
              : 'bg-red-50/50 border-red-200 hover:bg-red-100/60 text-red-950'"
          >
            <div>
              <div class="text-xs font-extrabold flex items-center space-x-1.5">
                <span>🔴</span>
                <span>1. Ações Pendentes (Check ainda não dado)</span>
              </div>
              <div class="text-[10px] mt-0.5" :class="substatusAcaoAtiva === 'PENDENTES' ? 'text-red-100' : 'text-red-800/80'">
                Geram o alerta em número vermelho · Podem receber o check ou ter a solicitação cancelada
              </div>
            </div>
            <span
              class="px-2.5 py-0.5 rounded-full text-sm font-extrabold font-mono shrink-0"
              :class="substatusAcaoAtiva === 'PENDENTES'
                ? 'bg-white text-red-700 shadow-2xs'
                : 'bg-red-600 text-white shadow-2xs'"
            >
              {{ contagemSubdivisaoAtual.pendentes }}
            </span>
          </button>

          <!-- Sub-aba 2: Ações Solicitadas (Check dado) -->
          <button
            type="button"
            @click="selecionarSubstatusAcao('SOLICITADAS')"
            class="p-3 rounded-xl border-2 text-left transition cursor-pointer flex items-center justify-between gap-2"
            :class="substatusAcaoAtiva === 'SOLICITADAS'
              ? 'bg-emerald-700 border-emerald-700 text-white shadow-xs'
              : 'bg-emerald-50/50 border-emerald-200 hover:bg-emerald-100/60 text-emerald-950'"
          >
            <div>
              <div class="text-xs font-extrabold flex items-center space-x-1.5">
                <span>✅</span>
                <span>2. Ações Solicitadas (Check dado)</span>
              </div>
              <div class="text-[10px] mt-0.5" :class="substatusAcaoAtiva === 'SOLICITADAS' ? 'text-emerald-100' : 'text-emerald-800/80'">
                Não geram mais alerta · Aguardam nova consulta/evento no AGHU para mudar de tabela · Podem ser desfeitas
              </div>
            </div>
            <span
              class="px-2.5 py-0.5 rounded-lg text-sm font-extrabold font-mono shrink-0"
              :class="substatusAcaoAtiva === 'SOLICITADAS'
                ? 'bg-white/20 text-white'
                : 'bg-white border border-emerald-300 text-emerald-900'"
            >
              {{ contagemSubdivisaoAtual.solicitadas }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros Modificáveis da Tabela Selecionada -->
    <Card>
      <div class="space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-2">
          <div>
            <div class="flex items-center space-x-2">
              <span
                v-if="abaAtualInfo?.estagioLabel"
                class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider"
                :class="abaAtualInfo.estagioBadgeClass"
              >
                {{ abaAtualInfo.estagioLabel }}
              </span>
              <h2 class="text-sm font-bold text-gray-800">
                {{ abaAtualInfo?.codigo }} — {{ abaAtualInfo?.titulo }}
              </h2>
            </div>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ abaAtualInfo?.regraAutomatica }}
            </p>
          </div>
          <button
            type="button"
            @click="limparFiltrosTabela"
            class="text-xs text-indigo-600 hover:text-indigo-800 font-semibold cursor-pointer"
          >
            🔄 Limpar filtros desta tabela
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <!-- 1. Buscar Prontuário ou Nome -->
          <div class="form-group">
            <label class="form-label font-semibold text-xs">Prontuário ou Nome do Paciente</label>
            <input
              v-model="filtroProntuario"
              type="text"
              placeholder="Filtrar por prontuário ou nome..."
              class="form-control text-xs py-1.5"
            />
          </div>

          <!-- 2. Filtro de Data - De -->
          <div class="form-group">
            <label class="form-label font-semibold text-xs">
              Data da {{ isAbaApa ? 'APA' : 'Consulta EPO' }} (De)
            </label>
            <input
              v-model="filtroDataDe"
              type="date"
              class="form-control text-xs py-1.5"
            />
          </div>

          <!-- 3. Filtro de Data - Até -->
          <div class="form-group">
            <label class="form-label font-semibold text-xs">
              Data da {{ isAbaApa ? 'APA' : 'Consulta EPO' }} (Até)
            </label>
            <input
              v-model="filtroDataAte"
              type="date"
              class="form-control text-xs py-1.5"
            />
          </div>

          <!-- 4. Filtro de Status (nas Tabelas 1.2, 2, 3.2 e 4) -->
          <div v-if="abaAtiva === 'T1_2' || abaAtiva === 'T2' || abaAtiva === 'T3_2' || abaAtiva === 'T4'" class="form-group">
            <label class="form-label font-semibold text-xs">
              Status da {{ isAbaApa ? 'APA' : 'Consulta EPO' }}
            </label>
            <select v-if="abaAtiva === 'T1_2' || abaAtiva === 'T3_2'" v-model="filtroStatusConsulta" class="form-control text-xs py-1.5">
              <option value="">Todos os status não realizados</option>
              <option value="Agendado (Data Passada)">Agendado (Data Passada / Sem Desfecho)</option>
              <option value="Falta do paciente">Falta do paciente</option>
              <option value="Falta do profissional">Falta do profissional</option>
            </select>
            <select v-else v-model="filtroStatusConsulta" class="form-control text-xs py-1.5">
              <option value="">Todos os status realizados</option>
              <option value="Realizado">Realizado (registrado no AGHU)</option>
              <option value="Realizado (sem registro no AGHU)">Realizado (sem registro no AGHU)</option>
            </select>
          </div>
        </div>

        <!-- Filtro de Grades (Seleção Múltipla por Pills dentre as grades do filtro automático) -->
        <div class="pt-1">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-semibold text-gray-700">
              Filtrar por Grade(s) {{ isAbaApa ? 'da APA' : 'de Enfermagem (EPO)' }}:
            </span>
            <button
              v-if="gradesSelecionadasFiltro.length > 0"
              type="button"
              @click="gradesSelecionadasFiltro = []"
              class="text-[11px] text-indigo-600 hover:underline cursor-pointer"
            >
              Marcar todas ({{ gradesDisponiveisAbaAtual.length }})
            </button>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="g in gradesDisponiveisAbaAtual"
              :key="g.sigla"
              type="button"
              @click="toggleGradeFiltro(g.sigla)"
              class="px-2.5 py-1 rounded-lg text-xs font-semibold border transition cursor-pointer flex items-center space-x-1.5"
              :class="gradesSelecionadasFiltro.length === 0 || gradesSelecionadasFiltro.includes(g.sigla)
                ? 'bg-indigo-600 text-white border-indigo-600 shadow-2xs'
                : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100'"
              :title="g.nome"
            >
              <span>{{ g.sigla }}</span>
              <span class="text-[10px] opacity-80 font-normal hidden sm:inline">({{ g.nome }})</span>
            </button>
          </div>
        </div>

        <!-- Filtros Específicos da Tabela 2 (Exames Pré-Op e Consultas Pré-Op) -->
        <div v-if="abaAtiva === 'T2'" class="pt-2 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <div class="form-group">
            <label class="form-label font-semibold text-xs">Filtrar por Grupo ou Exame Solicitado</label>
            <select v-model="filtroGrupoExame22" class="form-control text-xs py-1.5">
              <option value="">Todos os grupos e exames</option>
              <optgroup label="Por Grupo de Exames">
                <option v-for="grp in gruposExamesAtivos" :key="grp.id" :value="grp.id">
                  Grupo: {{ grp.nome }}
                </option>
              </optgroup>
              <optgroup v-if="examesMonitoradosAtivos.length > 0" label="Por Exame Específico Monitorado">
                <option v-for="ex in examesMonitoradosAtivos" :key="ex.sigla" :value="`EXAME:${ex.sigla}`">
                  {{ ex.sigla }} — {{ ex.descricao }} ({{ ex.grupoNome }})
                </option>
              </optgroup>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label font-semibold text-xs">Situação dos Exames Pré-Op</label>
            <select v-model="filtroSituacaoExames22" class="form-control text-xs py-1.5">
              <option value="">Qualquer situação</option>
              <option value="COM_EXAMES">Com pelo menos 1 exame solicitado</option>
              <option value="TODOS_LIBERADOS">Todos os exames solicitados Liberados</option>
              <option value="COM_PENDENTES">Com exame pendente / em execução</option>
              <option value="SEM_EXAMES">Sem exames pré-op solicitados</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label font-semibold text-xs">Situação das Consultas Pré-Op</label>
            <select v-model="filtroSituacaoConsultaPreop22" class="form-control text-xs py-1.5">
              <option value="">Todas as situações</option>
              <option value="COM_CONSULTA">Com alguma consulta pré-op agendada/realizada</option>
              <option value="REALIZADA">Com consulta pré-op Realizada</option>
              <option value="AGENDADA">Com consulta pré-op Agendada (Hoje / Futuro)</option>
              <option value="NAO_REALIZADA">Com consulta pré-op Não Realizada (Data Passada ou Faltosa)</option>
              <option value="AGENDADA_PASSADA">Com consulta pré-op Agendada em Data Passada (Sem Desfecho)</option>
              <option value="FALTOSA">Com consulta pré-op Faltosa (Paciente / Profissional)</option>
              <option value="SEM_CONSULTA">Sem consulta pré-op registrada</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label font-semibold text-xs">Grades de Consulta Pré-Op</label>
            <select v-model="filtroGradeConsultaPreop22" class="form-control text-xs py-1.5">
              <option value="">Todas as grades pré-op</option>
              <option v-for="gp in gradesPreopAtivas" :key="gp.sigla" :value="gp.sigla">
                {{ gp.sigla }} — {{ gp.nome }}
              </option>
            </select>
          </div>
        </div>

        <!-- Filtros Específicos da Tabela 4 (Consultas Solicitadas pela APA) -->
        <div v-if="abaAtiva === 'T4'" class="pt-2 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="form-group">
            <label class="form-label font-semibold text-xs">Situação das Consultas Solicitadas pela APA</label>
            <select v-model="filtroSituacaoConsultaPosApa4" class="form-control text-xs py-1.5">
              <option value="">Todas as situações</option>
              <option value="COM_CONSULTA">Com alguma consulta solicitada pela APA agendada/realizada</option>
              <option value="REALIZADA">Com consulta solicitada pela APA Realizada</option>
              <option value="AGENDADA">Com consulta solicitada pela APA Agendada (Hoje / Futuro)</option>
              <option value="NAO_REALIZADA">Com consulta solicitada pela APA Não Realizada (Data Passada ou Faltosa)</option>
              <option value="AGENDADA_PASSADA">Com consulta solicitada pela APA Agendada em Data Passada (Sem Desfecho)</option>
              <option value="FALTOSA">Com consulta solicitada pela APA Faltosa (Paciente / Profissional)</option>
              <option value="SEM_CONSULTA">Sem consulta solicitada pela APA registrada</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label font-semibold text-xs">Grades de Consultas Solicitadas pela APA</label>
            <select v-model="filtroGradeConsultaPosApa4" class="form-control text-xs py-1.5">
              <option value="">Todas as grades solicitadas pela APA</option>
              <option v-for="gpa in gradesPosApaAtivas" :key="gpa.sigla" :value="gpa.sigla">
                {{ gpa.sigla }} — {{ gpa.nome }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </Card>

    <!-- Tabela de Dados do Estágio Selecionado -->
    <Card>
      <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-gray-100">
        <div class="text-xs text-gray-600">
          Exibindo <strong class="text-gray-900">{{ linhasFiltradas.length }}</strong> registro(s)
          <span class="text-gray-400">· Ordenação: {{ abaAtualInfo?.ordenacaoTexto }}</span>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-12">
        <LoadingIndicator />
      </div>
      <div v-else-if="linhasFiltradas.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-sm font-semibold text-gray-700">Nenhum paciente encontrado nesta tabela com os filtros atuais.</p>
        <p class="text-xs text-gray-400 mt-1">Experimente ajustar os filtros acima ou ampliar a janela temporal do AGHU.</p>
      </div>
      <div v-else class="border border-gray-100 rounded-lg overflow-hidden">
        <table class="w-full table-auto divide-y divide-gray-200 text-xs">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-2.5 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider w-[86px]">
                Prontuário
              </th>
              <th class="px-2.5 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider w-[165px]">
                Nome do Paciente
              </th>
              <th class="px-2 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider leading-tight w-[122px]">
                Grade da<br />{{ isAbaApa ? 'APA' : 'Consulta EPO' }}
              </th>
              <th class="px-2 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider leading-tight w-[84px]">
                Data da<br />{{ isAbaApa ? 'APA' : 'Consulta EPO' }}
              </th>
              <th class="px-2 py-2.5 text-center font-bold text-gray-600 uppercase tracking-wider leading-tight w-[112px]">
                Status da<br />{{ isAbaApa ? 'APA' : 'Consulta EPO' }}
              </th>
              <template v-if="abaAtiva === 'T2'">
                <th class="px-2.5 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider">
                  Exames Pré-Operatórios Solicitados
                </th>
                <th class="px-2.5 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider w-[180px]">
                  Consultas Pré-Operatórias<br />
                  <span class="text-[10px] font-semibold text-gray-500">({{ siglasPreopTexto }})</span>
                </th>
              </template>
              <template v-if="abaAtiva === 'T4'">
                <th class="px-2.5 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider">
                  Consultas solicitadas pela APA ({{ siglasPosApaTexto }})
                </th>
              </template>
              <th
                v-if="abaPossuiClassificacoes"
                class="px-2.5 py-2.5 text-left font-bold text-gray-600 uppercase tracking-wider w-[185px]"
              >
                Classificação / Ação
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="row in linhasPaginadas"
              :key="`${row.prontuario}-${row.grade_sigla}`"
              class="hover:bg-slate-50/80 transition"
            >
              <!-- Prontuário -->
              <td class="px-2.5 py-2.5 whitespace-nowrap align-top">
                <button
                  type="button"
                  @click="buscaGlobalProntuario = row.prontuario"
                  class="font-mono font-bold text-indigo-700 hover:text-indigo-950 hover:underline cursor-pointer"
                  title="Clique para localizar este prontuário em todas as tabelas da jornada"
                >
                  #{{ row.prontuario }}
                </button>
              </td>

              <!-- Nome do Paciente -->
              <td class="px-2.5 py-2.5 align-top max-w-[180px]">
                <div class="flex items-center gap-1 flex-wrap">
                  <span class="font-bold text-gray-900 leading-snug break-words">{{ row.nome_paciente }}</span>
                  <span
                    v-if="row.possui_nome_social"
                    class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-100 text-purple-800 border border-purple-200 uppercase"
                  >
                    Nome Social
                  </span>
                </div>
                <div v-if="row.dt_nascimento" class="text-[10px] text-gray-400 mt-0.5">
                  Nasc.: {{ formatarData(row.dt_nascimento) }}
                </div>
              </td>

              <!-- Grade da Consulta (largura reduzida + nome completo abaixo do card) -->
              <td class="px-2 py-2.5 align-top w-[122px] max-w-[132px]">
                <div class="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-800 font-bold text-[11px]">
                  <span>{{ row.grade_sigla }}</span>
                  <span v-if="row.grd_seq" class="text-[9px] font-mono text-slate-500">(#{{ row.grd_seq }})</span>
                </div>
                <div class="text-[10px] text-gray-600 mt-1 font-medium leading-tight break-words">
                  {{ row.grade_nome }}
                </div>
              </td>

              <!-- Data da Consulta (largura reduzida com data e hora empilhadas) -->
              <td class="px-2 py-2.5 text-center font-mono text-gray-800 font-semibold align-top w-[84px]">
                <div class="text-[11px] leading-tight">{{ formatarData(row.data_consulta) }}</div>
                <div v-if="formatarHora(row.data_consulta)" class="text-[10px] text-gray-500 mt-0.5">
                  {{ formatarHora(row.data_consulta) }}
                </div>
              </td>

              <!-- Status da Consulta (largura reduzida com quebra de linha inteligente) -->
              <td class="px-2 py-2.5 text-center align-top w-[112px] max-w-[125px]">
                <div class="inline-flex flex-col items-center gap-1">
                  <span :class="getStatusConsultaBadgeClass(row.status)" class="whitespace-normal leading-tight text-center" :title="row.status_detalhe">
                    {{ row.status_detalhe || row.status }}
                  </span>
                  <!-- Caso promovido por 'Realizada (sem registro no AGHU)' de T1_2 -> T2 ou T3_2 -> T4 -->
                  <div
                    v-if="row.promovido_sem_registro && row.promocao_info"
                    class="p-1 rounded-md bg-amber-50 border border-amber-200 text-[9.5px] text-amber-900 flex flex-col items-center gap-1 whitespace-normal leading-tight"
                  >
                    <span>
                      Orig.: <strong>{{ row.status_original_aghu }}</strong>
                    </span>
                    <button
                      type="button"
                      @click="solicitarConfirmacaoDesfazer(row, row.promocao_info, true)"
                      :disabled="processandoClassificacao"
                      class="px-1.5 py-0.5 rounded bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 font-bold cursor-pointer transition text-[9.5px]"
                      title="Desfazer classificação 'Realizada (sem registro no AGHU)' e retornar paciente para a tabela anterior"
                    >
                      ↩ Desfazer
                    </button>
                  </div>
                </div>
              </td>

              <!-- Colunas exclusivas da Tabela 2: Cards de Exames Pré-Op e Consultas Pré-Op -->
              <template v-if="abaAtiva === 'T2'">
                <!-- Cards de Exames Pré-Operatórios Solicitados (Padrão: Ver todos) -->
                <td class="px-2.5 py-2.5 align-top">
                  <div v-if="!row.exames_solicitados || row.exames_solicitados.length === 0" class="text-[11px] text-gray-400 italic">
                    Nenhum exame pré-op solicitado no período
                  </div>
                  <div v-else class="space-y-1.5">
                    <!-- Resumo de liberação dos exames -->
                    <div class="flex items-center justify-between gap-2">
                      <span
                        class="text-[10px] font-bold px-2 py-0.5 rounded-full border"
                        :class="contarExamesLiberados(row.exames_solicitados) === row.exames_solicitados.length
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : 'bg-amber-50 text-amber-800 border-amber-200'"
                      >
                        {{ contarExamesLiberados(row.exames_solicitados) }}/{{ row.exames_solicitados.length }} Liberado(s)
                      </span>
                      <button
                        v-if="row.exames_solicitados.length > 6"
                        type="button"
                        @click="toggleRecolherExames(row.prontuario)"
                        class="text-[10px] font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer"
                      >
                        {{ examesRecolhidos[row.prontuario] ? `Ver todos (${row.exames_solicitados.length}) ▼` : 'Recolher ▲' }}
                      </button>
                    </div>

                    <!-- Grid Compacto de Cards de Exames (exibindo todos por padrão sem cortar informação) -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-1">
                      <div
                        v-for="ex in obterExamesVisiveis(row)"
                        :key="ex.sigla"
                        class="px-2 py-1 rounded-md border text-[10px] flex flex-col justify-between shadow-2xs"
                        :class="getCardExameClass(ex.cor)"
                        :title="`${ex.grupo_nome}: ${ex.nome} (${ex.sigla}) - Status: ${ex.status}`"
                      >
                        <div class="flex items-start justify-between gap-1">
                          <span class="font-bold leading-tight break-words">{{ ex.nome }}</span>
                          <span class="font-mono text-[9px] font-bold px-1 rounded bg-black/5 shrink-0">{{ ex.sigla }}</span>
                        </div>
                        <div class="flex items-center justify-between gap-1 mt-1 pt-0.5 border-t border-black/10 text-[9.5px]">
                          <span class="font-extrabold uppercase leading-none">{{ ex.status }}</span>
                          <span class="font-mono opacity-90 shrink-0 leading-none">{{ formatarData(ex.data) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Cards de Consultas Pré-Operatórias Solicitadas -->
                <td class="px-2.5 py-2.5 align-top w-[180px] max-w-[195px]">
                  <div v-if="!row.consultas_preop || row.consultas_preop.length === 0" class="text-[10.5px] text-gray-400 italic">
                    Nenhuma consulta pré-op registrada
                  </div>
                  <div v-else class="flex flex-col gap-1">
                    <div
                      v-for="cp in row.consultas_preop"
                      :key="cp.sigla"
                      class="px-2 py-1 rounded-md border text-[10px] flex flex-col justify-between shadow-2xs"
                      :class="getCardConsultaPreopClass(cp.status)"
                      :title="`${cp.sigla} - ${cp.nome}`"
                    >
                      <div>
                        <span class="font-extrabold">{{ cp.sigla }}</span>
                        <span class="text-[9.5px] leading-tight break-words opacity-90 ml-1">— {{ cp.nome }}</span>
                      </div>
                      <div class="flex items-center justify-between gap-1 mt-1 pt-0.5 border-t border-black/10 text-[9.5px]">
                        <span class="font-extrabold uppercase leading-none">{{ cp.status }}</span>
                        <span class="font-mono opacity-90 shrink-0 leading-none">{{ formatarDataHora(cp.data) }}</span>
                      </div>
                    </div>
                  </div>
                </td>
              </template>

              <!-- Coluna exclusiva da Tabela 4: Consultas solicitadas pela APA -->
              <template v-if="abaAtiva === 'T4'">
                <td class="px-2.5 py-2.5 align-top">
                  <div v-if="gradesPosApaAtivas.length === 0" class="text-[11px] text-gray-400 italic">
                    Nenhuma grade configurada em "Consultas e Exames monitorados" (Item 5)
                  </div>
                  <div v-else-if="!row.consultas_pos_apa || row.consultas_pos_apa.length === 0" class="text-[11px] text-gray-400 italic">
                    Nenhuma consulta solicitada pela APA registrada
                  </div>
                  <div v-else class="flex flex-wrap gap-1.5">
                    <div
                      v-for="cpa in row.consultas_pos_apa"
                      :key="cpa.sigla"
                      class="px-2 py-1.5 rounded-md border text-[10.5px] flex flex-col justify-between min-w-[155px] max-w-[220px] shadow-2xs"
                      :class="getCardConsultaPreopClass(cpa.status)"
                      :title="`${cpa.sigla} - ${cpa.nome}`"
                    >
                      <div>
                        <div class="font-extrabold">{{ cpa.sigla }}</div>
                        <div class="text-[10px] leading-snug break-words opacity-90 mt-0.5">{{ cpa.nome }}</div>
                      </div>
                      <div class="flex items-center justify-between gap-2 mt-1 pt-0.5 border-t border-black/10 text-[10px]">
                        <span class="font-extrabold uppercase">{{ cpa.status }}</span>
                        <span class="font-mono opacity-85">{{ formatarDataHora(cpa.data) }}</span>
                      </div>
                    </div>
                  </div>
                </td>
              </template>

              <!-- Coluna de Classificação / Ação nas Tabelas 1.2, 2, 3.2 e 4 -->
              <td v-if="abaPossuiClassificacoes" class="px-2.5 py-2.5 align-top w-[185px] max-w-[200px]">
                <!-- Se o paciente está na Lista Principal: exibe os botões de classificação disponíveis para esta tabela -->
                <div v-if="!row.classificacao_info" class="flex flex-col gap-1">
                  <button
                    v-for="opt in opcoesClassificacaoAbaAtual"
                    :key="opt.codigo"
                    type="button"
                    @click="solicitarConfirmacaoClassificar(row, opt)"
                    :disabled="processandoClassificacao"
                    class="px-2 py-1 rounded-md border text-left text-[10.5px] font-bold transition cursor-pointer flex items-center justify-between gap-1 leading-tight"
                    :class="opt.btnClass"
                    :title="opt.hint"
                  >
                    <span>{{ opt.icone }} {{ opt.label }}</span>
                    <span class="text-[10px] opacity-75 shrink-0">➔</span>
                  </button>
                </div>

                <!-- Se o paciente já está classificado (exibido na respectiva Subtabela): exibe o Card da Classificação com Check de Ação e Cancelar/Desfazer -->
                <div
                  v-else
                  class="p-2 rounded-xl border text-[11px] space-y-1.5 shadow-2xs"
                  :class="row.classificacao_info.requer_acao
                    ? (row.classificacao_info.acao_realizada ? 'bg-emerald-50/90 border-emerald-300 text-emerald-950' : 'bg-red-50/90 border-red-300 text-red-950')
                    : 'bg-slate-100 border-slate-300 text-slate-900'"
                >
                  <div class="flex items-start justify-between gap-1.5">
                    <div class="font-extrabold leading-tight">
                      {{ row.classificacao_info.label }}
                    </div>
                    <!-- Se requer_acao e check ainda não foi dado (Ações Pendentes): botão '✕ Cancelar' (cancela a solicitação e volta para Lista Principal) -->
                    <button
                      v-if="row.classificacao_info.requer_acao && !row.classificacao_info.acao_realizada"
                      type="button"
                      @click="solicitarConfirmacaoDesfazer(row, row.classificacao_info, false)"
                      :disabled="processandoClassificacao"
                      class="px-1.5 py-0.5 rounded bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 text-[9.5px] font-bold cursor-pointer shrink-0 transition"
                      title="Cancelar esta solicitação pendente e retornar o paciente para a Lista Principal"
                    >
                      ✕ Cancelar
                    </button>
                    <!-- Se ação já solicitada (check dado) ou ação direta (Sem seguimento cirúrgico): botão '↩ Desfazer' -->
                    <button
                      v-else
                      type="button"
                      @click="row.classificacao_info.requer_acao && row.classificacao_info.acao_realizada
                        ? solicitarConfirmacaoTicar(row, row.classificacao_info)
                        : solicitarConfirmacaoDesfazer(row, row.classificacao_info, false)"
                      :disabled="processandoClassificacao"
                      class="px-1.5 py-0.5 rounded bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 text-[9.5px] font-bold cursor-pointer shrink-0 transition"
                      :title="row.classificacao_info.requer_acao && row.classificacao_info.acao_realizada
                        ? 'Desfazer marcação de solicitada (retornar paciente para Ações Pendentes)'
                        : 'Desfazer esta classificação e retornar o paciente para a Lista Principal'"
                    >
                      ↩ Desfazer
                    </button>
                  </div>

                  <!-- Controle de Indicação de Cumprimento da Ação Pendente ('Solicitada') com Quadradinho Maior -->
                  <div v-if="row.classificacao_info.requer_acao" class="pt-1.5 border-t border-black/10">
                    <button
                      type="button"
                      @click="solicitarConfirmacaoTicar(row, row.classificacao_info)"
                      :disabled="processandoClassificacao"
                      class="w-full p-2 rounded-lg border text-left text-[11px] font-bold flex items-center space-x-2.5 cursor-pointer transition shadow-2xs"
                      :class="row.classificacao_info.acao_realizada
                        ? 'bg-emerald-600 text-white border-emerald-700 hover:bg-emerald-700'
                        : 'bg-white text-red-900 border-red-300 hover:bg-red-50'"
                    >
                      <!-- Quadradinho de Checkbox Ampliado (24x24px) -->
                      <span
                        class="w-6 h-6 rounded-md border-2 flex items-center justify-center shrink-0 transition"
                        :class="row.classificacao_info.acao_realizada
                          ? 'bg-white border-white text-emerald-700'
                          : 'bg-white border-red-500 text-transparent'"
                      >
                        <svg v-if="row.classificacao_info.acao_realizada" class="w-4 h-4 stroke-[3]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </span>
                      <span class="leading-tight">
                        {{ obterTextoStatusAcaoSubtabela(row.classificacao_info) }}
                      </span>
                    </button>
                    <div v-if="row.classificacao_info.acao_realizada && row.classificacao_info.data_acao" class="text-[9.5px] opacity-85 mt-1 leading-tight">
                      {{ obterPrefixoDataAcaoSubtabela(row.classificacao_info) }} em {{ formatarDataHora(row.classificacao_info.data_acao) }} ({{ row.classificacao_info.usuario_acao }})
                    </div>
                  </div>

                  <div class="text-[9.5px] opacity-75 pt-1 border-t border-black/10 leading-tight">
                    Classificado em {{ formatarDataHora(row.classificacao_info.data_classificacao) }} ({{ row.classificacao_info.usuario_classificacao }})
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginação -->
      <div v-if="linhasFiltradas.length > 0" class="mt-3 border border-gray-100 rounded-lg overflow-hidden">
        <Pagination
          :total-items="linhasFiltradas.length"
          v-model:current-page="paginaAtual"
          v-model:items-per-page="itensPorPagina"
          item-name="pacientes neste estágio"
        />
      </div>
    </Card>

    <!-- Modal de Configuração de Grades de Consultas e Exames do Circuito Cirúrgico (Busca no AGHU) -->
    <div v-if="modalConfigAberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full p-6 space-y-4 border border-gray-200 max-h-[90vh] flex flex-col">
        <div class="flex items-start justify-between border-b border-gray-150 pb-3">
          <div>
            <h3 class="text-lg font-bold text-gray-900">
              ⚙️ Consultas e Exames monitorados
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              Visualize e edite as siglas de grades de consultas e os exames consultados no AGHU para cada etapa da navegação. As alterações refletem automaticamente nas tabelas e nos filtros.
            </p>
          </div>
          <button
            type="button"
            @click="modalConfigAberto = false"
            class="text-gray-400 hover:text-gray-600 text-lg font-bold p-1 cursor-pointer"
          >
            ✕
          </button>
        </div>

        <!-- Abas internas do Modal de Configuração em 2 Fileiras de Retângulos (Sem Barra de Rolagem) -->
        <div class="bg-slate-50 p-2 rounded-xl border border-slate-200 shrink-0">
          <div class="grid grid-cols-1 sm:grid-cols-6 gap-2">
            <button
              v-for="(tab, tIdx) in abasModalConfig"
              :key="tab.id"
              type="button"
              @click="abaModalConfig = tab.id"
              class="p-2.5 rounded-lg border text-left transition cursor-pointer flex flex-col justify-between"
              :class="[
                tIdx < 3 ? 'sm:col-span-2' : 'sm:col-span-3',
                abaModalConfig === tab.id
                  ? 'bg-indigo-600 border-indigo-600 text-white shadow-xs'
                  : 'bg-white border-gray-200 hover:bg-indigo-50/50 text-gray-800'
              ]"
            >
              <div class="text-xs font-bold leading-snug">{{ tab.titulo }}</div>
              <div class="text-[10px] mt-0.5" :class="abaModalConfig === tab.id ? 'text-indigo-100' : 'text-gray-500'">
                {{ tab.subtitulo }}
              </div>
            </button>
          </div>
        </div>

        <!-- Corpo Scrollável do Modal -->
        <div class="overflow-y-auto flex-1 space-y-4 pr-1 text-xs">
          <!-- ABA 1, 2 ou 3: Grades de Consultas (EPO, Pré-Op ou APA) -->
          <div v-if="abaModalConfig !== 'EXAMES'" class="space-y-4">
            <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <label class="font-bold text-slate-800 block">
                Pesquisar Grade / Sigla de Especialidade no AGHU para adicionar:
              </label>
              <div class="flex space-x-2">
                <input
                  v-model="termoBuscaGradeAghu"
                  type="text"
                  placeholder="Digite a sigla (ex.: EPO, RIS, ANE, TAN) ou nome da especialidade no AGHU..."
                  class="form-control text-xs"
                  @keydown.enter.prevent="pesquisarGradesNoAghu"
                />
                <Button type="button" @click="pesquisarGradesNoAghu" :disabled="buscandoGradesAghu" variant="info">
                  {{ buscandoGradesAghu ? 'Buscando...' : 'Buscar no AGHU' }}
                </Button>
              </div>

              <!-- Resultados da busca no AGHU -->
              <div v-if="resultadosGradesAghu.length > 0" class="mt-2 max-h-44 overflow-y-auto border border-gray-200 rounded-lg bg-white divide-y divide-gray-100">
                <div
                  v-for="g in resultadosGradesAghu"
                  :key="g.sigla"
                  class="px-3 py-2 flex items-center justify-between hover:bg-indigo-50/50"
                >
                  <div>
                    <span class="font-mono font-bold text-indigo-900">{{ g.sigla }}</span>
                    <span class="text-gray-700 font-medium ml-2">{{ g.nome }}</span>
                    <span class="text-[10px] text-gray-400 ml-2">({{ g.grades_ativas }} grade(s) ativa(s) no AGHU)</span>
                  </div>
                  <button
                    type="button"
                    @click="adicionarGradeNaCategoriaAtual(g)"
                    class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded text-[11px] cursor-pointer"
                  >
                    + Adicionar
                  </button>
                </div>
              </div>
            </div>

            <!-- Lista de Grades Configuradas na Categoria Selecionada -->
            <div class="space-y-2">
              <h4 class="font-bold text-gray-800">
                Grades atualmente monitoradas nesta etapa ({{ listaGradesCategoriaModal.length }}):
              </h4>
              <div class="divide-y divide-gray-200 border border-gray-200 rounded-xl overflow-hidden bg-white">
                <div
                  v-for="(item, idx) in listaGradesCategoriaModal"
                  :key="item.sigla"
                  class="px-4 py-2.5 flex items-center justify-between"
                >
                  <label class="flex items-center space-x-3 cursor-pointer">
                    <input type="checkbox" v-model="item.ativo" class="h-4 w-4 text-indigo-600 rounded" />
                    <div>
                      <span class="font-mono font-bold text-gray-900 text-sm">{{ item.sigla }}</span>
                      <span class="text-gray-600 ml-2">{{ item.nome }}</span>
                    </div>
                  </label>
                  <button
                    type="button"
                    @click="removerGradeDaCategoriaAtual(idx)"
                    class="text-red-600 hover:text-red-800 font-semibold text-xs cursor-pointer"
                  >
                    Remover
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ABA 4: Grupos e Exames Pré-Operatórios -->
          <div v-else class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Coluna Esquerda: Lista dos 8 Grupos -->
              <div class="space-y-2 border-r border-gray-200 pr-3">
                <div class="font-bold text-gray-800">Grupos de Exames Pré-Op:</div>
                <div
                  v-for="(grp, gIdx) in configEdicao.grupos_exames"
                  :key="grp.id"
                  @click="grupoExameSelecionadoIdx = gIdx"
                  class="p-2.5 rounded-lg border cursor-pointer transition flex items-center justify-between"
                  :class="grupoExameSelecionadoIdx === gIdx ? 'bg-indigo-50 border-indigo-400 text-indigo-950 font-bold' : 'bg-white border-gray-200 hover:bg-gray-50'"
                >
                  <div class="flex items-center space-x-2">
                    <input type="checkbox" v-model="grp.ativo" @click.stop class="h-4 w-4 text-indigo-600 rounded" />
                    <span>{{ grp.nome }}</span>
                  </div>
                  <span class="text-[10px] font-mono bg-gray-100 px-1.5 py-0.5 rounded border border-gray-200">
                    {{ grp.incluir_padrao_texto ? `Auto (${grp.incluir_padrao_texto})` : `${(grp.exames || []).length} siglas` }}
                  </span>
                </div>
              </div>

              <!-- Coluna Direita: Exames do Grupo Selecionado e Busca no AGHU -->
              <div v-if="grupoExameAtualModal" class="md:col-span-2 space-y-3">
                <div class="flex items-center justify-between border-b border-gray-100 pb-2">
                  <div>
                    <h4 class="font-bold text-gray-900 text-sm">{{ grupoExameAtualModal.nome }}</h4>
                    <p v-if="grupoExameAtualModal.incluir_padrao_texto" class="text-[11px] text-emerald-700 font-semibold">
                      ✓ Inclui automaticamente todos os exames ativos do AGHU que contenham "{{ grupoExameAtualModal.incluir_padrao_texto }}" (ex.: todas as 205 Ressonâncias Magnéticas), além das siglas extras abaixo.
                    </p>
                  </div>
                </div>

                <!-- Busca de Exame no AGHU -->
                <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                  <label class="font-bold text-slate-800 block">
                    Pesquisar Exame no Catálogo do AGHU (`agh.ael_exames`) para adicionar a "{{ grupoExameAtualModal.nome }}":
                  </label>
                  <div class="flex space-x-2">
                    <input
                      v-model="termoBuscaExameAghu"
                      type="text"
                      placeholder="Digite a sigla (ex.: HOLT, ERGO, ETT, RXPAP) ou nome do exame..."
                      class="form-control text-xs"
                      @keydown.enter.prevent="pesquisarExamesNoAghu"
                    />
                    <Button type="button" @click="pesquisarExamesNoAghu" :disabled="buscandoExamesAghu" variant="info">
                      {{ buscandoExamesAghu ? 'Buscando...' : 'Buscar Exame' }}
                    </Button>
                  </div>

                  <div v-if="resultadosExamesAghu.length > 0" class="mt-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg bg-white divide-y divide-gray-100">
                    <div
                      v-for="ex in resultadosExamesAghu"
                      :key="ex.sigla"
                      class="px-3 py-1.5 flex items-center justify-between hover:bg-indigo-50/50"
                    >
                      <div>
                        <span class="font-mono font-bold text-indigo-900">{{ ex.sigla }}</span>
                        <span class="text-gray-700 ml-2">{{ ex.descricao }}</span>
                      </div>
                      <button
                        type="button"
                        @click="adicionarExameNoGrupoAtual(ex)"
                        class="px-2 py-0.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded text-[11px] cursor-pointer shrink-0"
                      >
                        + Incluir
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Siglas cadastradas no grupo -->
                <div class="space-y-1.5">
                  <div class="font-bold text-gray-700">
                    Siglas vinculadas ao grupo "{{ grupoExameAtualModal.nome }}" ({{ (grupoExameAtualModal.exames || []).length }}):
                  </div>
                  <div v-if="(!grupoExameAtualModal.exames || grupoExameAtualModal.exames.length === 0)" class="text-gray-400 italic">
                    {{ grupoExameAtualModal.incluir_padrao_texto ? `Monitorando automaticamente todas as siglas do AGHU com "${grupoExameAtualModal.incluir_padrao_texto}".` : 'Nenhuma sigla vinculada.' }}
                  </div>
                  <div v-else class="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto p-2 bg-gray-50 rounded-lg border border-gray-200">
                    <div
                      v-for="(exItem, eIdx) in grupoExameAtualModal.exames"
                      :key="exItem.sigla"
                      class="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-white rounded-md border border-gray-300 text-xs shadow-2xs"
                    >
                      <span class="font-mono font-bold text-indigo-900">{{ exItem.sigla }}</span>
                      <span class="text-gray-600 text-[11px]">{{ exItem.descricao }}</span>
                      <button
                        type="button"
                        @click="grupoExameAtualModal.exames.splice(eIdx, 1)"
                        class="text-red-500 hover:text-red-700 font-bold ml-1 cursor-pointer"
                        title="Remover sigla deste grupo"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Rodapé do Modal -->
        <div class="flex items-center justify-between pt-3 border-t border-gray-150 shrink-0">
          <span class="text-[11px] text-gray-500">
            As alterações ficam salvas no Comunicação Cirúrgica e atualizam imediatamente a leitura do AGHU.
          </span>
          <div class="flex space-x-2">
            <Button type="button" @click="modalConfigAberto = false" variant="secondary">
              Cancelar
            </Button>
            <Button type="button" @click="salvarConfiguracao" :disabled="salvandoConfig" variant="primary">
              {{ salvandoConfig ? 'Salvando...' : 'Salvar Configuração e Atualizar Painéis' }}
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação para Executar, Ticar ou Desfazer Classificação -->
    <div v-if="modalConfirmacao.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 border border-gray-200">
        <div class="flex items-start justify-between border-b border-gray-150 pb-3">
          <div>
            <span
              class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider"
              :class="modalConfirmacao.badgeClass"
            >
              {{ modalConfirmacao.tipoLabel }}
            </span>
            <h3 class="text-base font-bold text-gray-900 mt-1">
              {{ modalConfirmacao.titulo }}
            </h3>
          </div>
          <button
            type="button"
            @click="fecharModalConfirmacao"
            class="text-gray-400 hover:text-gray-600 text-lg font-bold p-1 cursor-pointer"
          >
            ✕
          </button>
        </div>

        <div class="space-y-3 text-xs text-gray-700">
          <!-- Resumo do Paciente e Consulta -->
          <div v-if="modalConfirmacao.row" class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div class="flex items-center space-x-1.5 flex-wrap">
              <span class="font-mono font-bold text-indigo-900 bg-indigo-100 px-1.5 py-0.5 rounded">
                #{{ modalConfirmacao.row.prontuario }}
              </span>
              <span class="font-bold text-gray-900">{{ modalConfirmacao.row.nome_paciente }}</span>
            </div>
            <div class="text-[11px] text-gray-600">
              Grade <strong>{{ modalConfirmacao.row.grade_sigla }}</strong> ({{ modalConfirmacao.row.grade_nome }}) ·
              Consulta em <strong>{{ formatarDataHora(modalConfirmacao.row.data_consulta) }}</strong>
            </div>
          </div>

          <p class="leading-relaxed text-gray-700 font-medium">
            {{ modalConfirmacao.mensagem }}
          </p>
        </div>

        <div class="flex justify-end space-x-2 pt-3 border-t border-gray-150">
          <Button type="button" @click="fecharModalConfirmacao" :disabled="processandoClassificacao" variant="secondary">
            Cancelar
          </Button>
          <Button
            type="button"
            @click="confirmarAcaoModal"
            :disabled="processandoClassificacao"
            :variant="modalConfirmacao.variantBtn"
          >
            {{ processandoClassificacao ? 'Processando...' : modalConfirmacao.textoBotaoConfirmar }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import Pagination from '../components/Pagination.vue';
import { usePerfisStore } from '../stores/perfis';

const toast = useToast();
const perfisStore = usePerfisStore();

const loading = ref(false);
const atualizadoEm = ref('');
const janelaMeses = ref(12);

const config = ref<any>({
  janela_meses: 12,
  grades_epo: [],
  grades_preop: [],
  grades_apa: [],
  grades_pos_apa: [],
  grupos_exames: []
});

type AbaTabelaId = 'T1_1' | 'T1_2' | 'T2' | 'T3_1' | 'T3_2' | 'T4';

const tabela11EpoAgendada = ref<any[]>([]);
const tabela12EpoNaoRealizada = ref<any[]>([]);
const tabela2EpoRealizada = ref<any[]>([]);
const tabela31ApaAgendada = ref<any[]>([]);
const tabela32ApaNaoRealizada = ref<any[]>([]);
const tabela4ApaRealizada = ref<any[]>([]);

// Aba ativa entre as 6 tabelas, Subtabela ativa e Subdivisão de Status da Ação (Pendentes vs Solicitadas)
const abaAtiva = ref<AbaTabelaId>('T1_1');
const subtabelaAtiva = ref<string>('PRINCIPAL');
const substatusAcaoAtiva = ref<'PENDENTES' | 'SOLICITADAS'>('PENDENTES');
const processandoClassificacao = ref(false);

// Busca global por prontuário/nome em todas as 6 tabelas
const buscaGlobalProntuario = ref('');

// Filtros modificáveis da tabela ativa
const filtroProntuario = ref('');
const filtroDataDe = ref('');
const filtroDataAte = ref('');
const filtroStatusConsulta = ref('');
const gradesSelecionadasFiltro = ref<string[]>([]);

// Filtros adicionais exclusivos da Tabela 2
const filtroGrupoExame22 = ref('');
const filtroSituacaoExames22 = ref('');
const filtroSituacaoConsultaPreop22 = ref('');
const filtroGradeConsultaPreop22 = ref('');

// Filtros adicionais exclusivos da Tabela 4 (Consultas Solicitadas pela APA)
const filtroSituacaoConsultaPosApa4 = ref('');
const filtroGradeConsultaPosApa4 = ref('');

// Controle de recolhimento de cards de exames por prontuário (Padrão: todos visíveis = false)
const examesRecolhidos = ref<Record<string, boolean>>({});

// Paginação
const paginaAtual = ref(1);
const itensPorPagina = ref(50);

const isAbaApa = computed(() => abaAtiva.value === 'T3_1' || abaAtiva.value === 'T3_2' || abaAtiva.value === 'T4');
const abaPossuiClassificacoes = computed(() => ['T1_2', 'T2', 'T3_2', 'T4'].includes(abaAtiva.value));

const contarResumoTabela = (lista: any[]) => {
  let totalPrincipal = 0;
  let totalSubtabelas = 0;
  let alertasPendentes = 0;
  for (const r of lista) {
    const sub = r.subtabela || 'PRINCIPAL';
    if (sub === 'PRINCIPAL') {
      totalPrincipal++;
    } else {
      totalSubtabelas++;
      if (r.classificacao_info?.requer_acao && !r.classificacao_info?.acao_realizada) {
        alertasPendentes++;
      }
    }
  }
  return { total: lista.length, totalPrincipal, totalSubtabelas, alertasPendentes };
};

const abasTabelas = computed(() => {
  const r11 = contarResumoTabela(tabela11EpoAgendada.value);
  const r12 = contarResumoTabela(tabela12EpoNaoRealizada.value);
  const r2 = contarResumoTabela(tabela2EpoRealizada.value);
  const r31 = contarResumoTabela(tabela31ApaAgendada.value);
  const r32 = contarResumoTabela(tabela32ApaNaoRealizada.value);
  const r4 = contarResumoTabela(tabela4ApaRealizada.value);

  return [
    {
      id: 'T1_1' as const,
      estagio: 1,
      estagioLabel: 'Estágio 1',
      estagioBadgeClass: 'bg-indigo-100 text-indigo-800 border border-indigo-200',
      codigo: 'Tabela 1.1',
      titulo: 'Consulta EPO agendada',
      subtitulo: 'Somente agendadas para hoje / data futura',
      regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade EPO) com status Agendado para hoje ou data futura · Ordenação: da data mais antiga para a mais recente.',
      ordenacaoTexto: 'Data da consulta EPO (mais antiga ➔ mais recente)',
      ...r11,
      activeClass: 'bg-indigo-700 border-indigo-700 text-white shadow-sm ring-2 ring-indigo-300',
      inactiveClass: 'bg-white border-indigo-200 border-l-4 border-l-indigo-500 hover:bg-indigo-50/40 text-gray-800',
      pillClass: 'bg-indigo-100 text-indigo-800'
    },
    {
      id: 'T1_2' as const,
      estagio: 1,
      estagioLabel: 'Estágio 1',
      estagioBadgeClass: 'bg-indigo-100 text-indigo-800 border border-indigo-200',
      codigo: 'Tabela 1.2',
      titulo: 'Consulta EPO não realizada',
      subtitulo: 'Faltas (paciente/profissional) e agendadas em data passada',
      regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade EPO) com status Falta do paciente, Falta do profissional ou Agendado em data passada (sem desfecho) · Ordenação: da data mais antiga para a mais recente.',
      ordenacaoTexto: 'Data da consulta EPO (mais antiga ➔ mais recente)',
      ...r12,
      activeClass: 'bg-rose-700 border-rose-700 text-white shadow-sm ring-2 ring-rose-300',
      inactiveClass: 'bg-white border-indigo-200 border-l-4 border-l-rose-500 hover:bg-rose-50/40 text-gray-800',
      pillClass: 'bg-rose-100 text-rose-800'
    },
    {
      id: 'T2' as const,
      estagio: 2,
      estagioLabel: 'Estágio 2',
      estagioBadgeClass: 'bg-teal-100 text-teal-800 border border-teal-200',
      codigo: 'Tabela 2',
      titulo: 'Consulta EPO realizada',
      subtitulo: 'Cards de Exames e Pareceres Pré-Op solicitados',
      regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade EPO) com status Realizado (ou enviada como Realizada sem registro no AGHU), exibindo os cards dos exames e consultas pré-operatórias solicitados · Ordenação: da data mais antiga para a mais recente.',
      ordenacaoTexto: 'Data da consulta EPO (mais antiga ➔ mais recente)',
      ...r2,
      activeClass: 'bg-teal-700 border-teal-700 text-white shadow-sm ring-2 ring-teal-300',
      inactiveClass: 'bg-white border-teal-200 border-l-4 border-l-teal-600 hover:bg-teal-50/40 text-gray-800',
      pillClass: 'bg-teal-100 text-teal-800'
    },
    {
      id: 'T3_1' as const,
      estagio: 3,
      estagioLabel: 'Estágio 3',
      estagioBadgeClass: 'bg-amber-100 text-amber-900 border border-amber-200',
      codigo: 'Tabela 3.1',
      titulo: 'APA agendada',
      subtitulo: `Somente agendadas para hoje / data futura (${siglasApaTexto.value})`,
      regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade APA) com status Agendado para hoje ou data futura · Ordenação: da data mais antiga para a mais recente.',
      ordenacaoTexto: 'Data da APA (mais antiga ➔ mais recente)',
      ...r31,
      activeClass: 'bg-amber-600 border-amber-600 text-white shadow-sm ring-2 ring-amber-300',
      inactiveClass: 'bg-white border-amber-200 border-l-4 border-l-amber-500 hover:bg-amber-50/40 text-gray-800',
      pillClass: 'bg-amber-100 text-amber-800'
    },
    {
      id: 'T3_2' as const,
      estagio: 3,
      estagioLabel: 'Estágio 3',
      estagioBadgeClass: 'bg-amber-100 text-amber-900 border border-amber-200',
      codigo: 'Tabela 3.2',
      titulo: 'APA não realizada',
      subtitulo: 'Faltas (paciente/profissional) e agendadas em data passada',
      regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade APA) com status Falta do paciente, Falta do profissional ou Agendado em data passada (sem desfecho) · Ordenação: da data mais antiga para a mais recente.',
      ordenacaoTexto: 'Data da APA (mais antiga ➔ mais recente)',
      ...r32,
      activeClass: 'bg-orange-700 border-orange-700 text-white shadow-sm ring-2 ring-orange-300',
      inactiveClass: 'bg-white border-amber-200 border-l-4 border-l-orange-600 hover:bg-orange-50/40 text-gray-800',
      pillClass: 'bg-orange-100 text-orange-800'
    },
    {
      id: 'T4' as const,
      estagio: 4,
      estagioLabel: 'Estágio 4',
      estagioBadgeClass: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
      codigo: 'Tabela 4',
      titulo: 'APA realizada',
      subtitulo: 'Avaliação Pré-Anestésica concluída',
      regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade APA) com status Realizado (ou enviada como Realizada sem registro no AGHU) · Ordenação: da data mais antiga para a mais recente.',
      ordenacaoTexto: 'Data da APA (mais antiga ➔ mais recente)',
      ...r4,
      activeClass: 'bg-emerald-700 border-emerald-700 text-white shadow-sm ring-2 ring-emerald-300',
      inactiveClass: 'bg-white border-emerald-200 border-l-4 border-l-emerald-600 hover:bg-emerald-50/40 text-gray-800',
      pillClass: 'bg-emerald-100 text-emerald-800'
    }
  ];
});

const abasEstagio1 = computed(() => abasTabelas.value.filter(a => a.estagio === 1));
const abasEstagio2 = computed(() => abasTabelas.value.filter(a => a.estagio === 2));
const abasEstagio3 = computed(() => abasTabelas.value.filter(a => a.estagio === 3));
const abasEstagio4 = computed(() => abasTabelas.value.filter(a => a.estagio === 4));

const abaAtualInfo = computed(() => abasTabelas.value.find(a => a.id === abaAtiva.value));

const gradesEpoAtivas = computed(() => (config.value.grades_epo || []).filter((g: any) => g.ativo !== false));
const gradesPreopAtivas = computed(() => (config.value.grades_preop || []).filter((g: any) => g.ativo !== false));
const gradesApaAtivas = computed(() => (config.value.grades_apa || []).filter((g: any) => g.ativo !== false));
const gradesPosApaAtivas = computed(() => (config.value.grades_pos_apa || []).filter((g: any) => g.ativo !== false));
const gruposExamesAtivos = computed(() => (config.value.grupos_exames || []).filter((g: any) => g.ativo !== false));

const siglasPreopTexto = computed(() => {
  const list = gradesPreopAtivas.value.map((g: any) => g.sigla);
  return list.length > 0 ? list.join(' / ') : 'Consultas Pré-Op';
});

const siglasApaTexto = computed(() => {
  const list = gradesApaAtivas.value.map((g: any) => g.sigla);
  return list.length > 0 ? list.join(' / ') : 'APA';
});

const siglasPosApaTexto = computed(() => {
  const list = gradesPosApaAtivas.value.map((g: any) => g.sigla);
  return list.length > 0 ? list.join(' / ') : 'A configurar';
});

// Definição das Subtabelas e Opções de Classificação por Tabela (1.2, 2, 3.2 e 4)
const subtabelasAbaAtual = computed(() => {
  const lista = listaBaseAbaAtiva.value;
  const countSub = (cod: string) => lista.filter(r => (r.subtabela || 'PRINCIPAL') === cod).length;
  const countAlertas = (cod: string) =>
    lista.filter(r => (r.subtabela || 'PRINCIPAL') === cod && r.classificacao_info?.requer_acao && !r.classificacao_info?.acao_realizada).length;

  if (abaAtiva.value === 'T1_2') {
    return [
      { id: 'PRINCIPAL', icone: '📋', titulo: 'Lista Principal (Tabela 1.2)', descricao: 'Pacientes aguardando análise / classificação', total: countSub('PRINCIPAL'), alertasPendentes: 0 },
      { id: 'REAGENDAR_EPO', icone: '📅', titulo: 'Subtabela: Reagendar consulta EPO', descricao: 'Solicitação de reagendamento de EPO', total: countSub('REAGENDAR_EPO'), alertasPendentes: countAlertas('REAGENDAR_EPO') },
      { id: 'SEM_SEGUIMENTO', icone: '🚫', titulo: 'Subtabela: Sem seguimento cirúrgico', descricao: 'Sem seguimento cirúrgico identificado', total: countSub('SEM_SEGUIMENTO'), alertasPendentes: 0 },
    ];
  }
  if (abaAtiva.value === 'T2') {
    return [
      { id: 'PRINCIPAL', icone: '📋', titulo: 'Lista Principal (Tabela 2)', descricao: 'Pacientes com EPO realizada aguardando liberação/ação', total: countSub('PRINCIPAL'), alertasPendentes: 0 },
      { id: 'AGENDAR_APA', icone: '📅', titulo: 'Subtabela: Agendar consulta APA', descricao: 'Solicitação de marcação da APA', total: countSub('AGENDAR_APA'), alertasPendentes: countAlertas('AGENDAR_APA') },
      { id: 'SEM_SEGUIMENTO', icone: '🚫', titulo: 'Subtabela: Sem seguimento cirúrgico', descricao: 'Sem seguimento cirúrgico identificado', total: countSub('SEM_SEGUIMENTO'), alertasPendentes: 0 },
    ];
  }
  if (abaAtiva.value === 'T3_2') {
    return [
      { id: 'PRINCIPAL', icone: '📋', titulo: 'Lista Principal (Tabela 3.2)', descricao: 'Pacientes aguardando análise / classificação', total: countSub('PRINCIPAL'), alertasPendentes: 0 },
      { id: 'REAGENDAR_APA', icone: '📅', titulo: 'Subtabela: Reagendar consulta APA', descricao: 'Solicitação de reagendamento de APA', total: countSub('REAGENDAR_APA'), alertasPendentes: countAlertas('REAGENDAR_APA') },
      { id: 'SEM_SEGUIMENTO', icone: '🚫', titulo: 'Subtabela: Sem seguimento cirúrgico', descricao: 'Sem seguimento cirúrgico identificado', total: countSub('SEM_SEGUIMENTO'), alertasPendentes: 0 },
    ];
  }
  if (abaAtiva.value === 'T4') {
    return [
      { id: 'PRINCIPAL', icone: '📋', titulo: 'Lista Principal (Tabela 4)', descricao: 'Pacientes com APA realizada aguardando ação', total: countSub('PRINCIPAL'), alertasPendentes: 0 },
      { id: 'PACIENTE_PRONTO_LEC', icone: '🏥', titulo: 'Subtabela: Paciente pronto no Sistema LEC', descricao: 'Sinalizar paciente pronto no Sistema LEC', total: countSub('PACIENTE_PRONTO_LEC'), alertasPendentes: countAlertas('PACIENTE_PRONTO_LEC') },
      { id: 'SEM_SEGUIMENTO', icone: '🚫', titulo: 'Subtabela: Sem seguimento cirúrgico', descricao: 'Sem seguimento cirúrgico identificado', total: countSub('SEM_SEGUIMENTO'), alertasPendentes: 0 },
    ];
  }
  return [];
});

const opcoesClassificacaoAbaAtual = computed(() => {
  if (abaAtiva.value === 'T1_2') {
    return [
      { codigo: 'REAGENDAR_EPO', icone: '📅', label: 'Reagendar consulta EPO', hint: 'Segrega para subtabela da 1.2 e gera alerta vermelho até ser marcada como solicitada', btnClass: 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-300' },
      { codigo: 'SEM_SEGUIMENTO', icone: '🚫', label: 'Sem seguimento cirúrgico', hint: 'Segrega para subtabela Sem seguimento cirúrgico da 1.2', btnClass: 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300' },
      { codigo: 'REALIZADA_SEM_REGISTRO_AGHU', icone: '✅', label: 'Realizada (sem registro no AGHU)', hint: 'Envia para a Lista Principal da Tabela 2 com status equivalente a Realizada', btnClass: 'bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border-emerald-300' },
    ];
  }
  if (abaAtiva.value === 'T2') {
    return [
      { codigo: 'AGENDAR_APA', icone: '📅', label: 'Agendar consulta APA', hint: 'Segrega para subtabela da 2 e gera alerta vermelho até ser marcada como solicitada', btnClass: 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-300' },
      { codigo: 'SEM_SEGUIMENTO', icone: '🚫', label: 'Sem seguimento cirúrgico', hint: 'Segrega para subtabela Sem seguimento cirúrgico da 2', btnClass: 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300' },
    ];
  }
  if (abaAtiva.value === 'T3_2') {
    return [
      { codigo: 'REAGENDAR_APA', icone: '📅', label: 'Reagendar consulta APA', hint: 'Segrega para subtabela da 3.2 e gera alerta vermelho até ser marcada como solicitada', btnClass: 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-300' },
      { codigo: 'SEM_SEGUIMENTO', icone: '🚫', label: 'Sem seguimento cirúrgico', hint: 'Segrega para subtabela Sem seguimento cirúrgico da 3.2', btnClass: 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300' },
      { codigo: 'REALIZADA_SEM_REGISTRO_AGHU', icone: '✅', label: 'Realizada (sem registro no AGHU)', hint: 'Envia para a Lista Principal da Tabela 4 com status equivalente a Realizada', btnClass: 'bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border-emerald-300' },
    ];
  }
  if (abaAtiva.value === 'T4') {
    return [
      { codigo: 'PACIENTE_PRONTO_LEC', icone: '🏥', label: 'Paciente pronto no Sistema LEC', hint: 'Segrega para subtabela da 4 e gera alerta vermelho até ser marcada como concluída', btnClass: 'bg-indigo-50 hover:bg-indigo-100 text-indigo-900 border-indigo-300' },
      { codigo: 'SEM_SEGUIMENTO', icone: '🚫', label: 'Sem seguimento cirúrgico', hint: 'Segrega para subtabela Sem seguimento cirúrgico da 4', btnClass: 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300' },
    ];
  }
  return [];
});

const isAcaoAgendamentoConsulta = (clsInfo: any) => {
  return ['REAGENDAR_EPO', 'AGENDAR_APA', 'REAGENDAR_APA'].includes(clsInfo?.classificacao);
};

const obterTextoStatusAcaoSubtabela = (clsInfo: any) => {
  const isAgend = isAcaoAgendamentoConsulta(clsInfo);
  if (clsInfo?.acao_realizada) {
    return isAgend ? 'Solicitada' : 'Concluída no Sistema LEC';
  }
  return isAgend ? 'Ação pendente — Marcar como solicitada' : 'Ação pendente — Marcar como concluída';
};

const obterPrefixoDataAcaoSubtabela = (clsInfo: any) => {
  return isAcaoAgendamentoConsulta(clsInfo) ? 'Solicitada' : 'Concluída';
};

const selecionarSubtabela = (subId: string) => {
  subtabelaAtiva.value = subId;
  substatusAcaoAtiva.value = 'PENDENTES';
  paginaAtual.value = 1;
};

const selecionarSubstatusAcao = (statusAcao: 'PENDENTES' | 'SOLICITADAS') => {
  substatusAcaoAtiva.value = statusAcao;
  paginaAtual.value = 1;
};

const subtabelaPossuiSubdivisao = computed(() => {
  return ['REAGENDAR_EPO', 'AGENDAR_APA', 'REAGENDAR_APA', 'PACIENTE_PRONTO_LEC'].includes(subtabelaAtiva.value);
});

const subtabelaAtualInfo = computed(() => {
  return subtabelasAbaAtual.value.find(s => s.id === subtabelaAtiva.value) || null;
});

const contagemSubdivisaoAtual = computed(() => {
  if (!subtabelaPossuiSubdivisao.value) return { pendentes: 0, solicitadas: 0 };
  const rowsSub = listaBaseAbaAtiva.value.filter(r => (r.subtabela || 'PRINCIPAL') === subtabelaAtiva.value);
  let pendentes = 0;
  let solicitadas = 0;
  for (const r of rowsSub) {
    if (r.classificacao_info?.acao_realizada) {
      solicitadas++;
    } else {
      pendentes++;
    }
  }
  return { pendentes, solicitadas };
});

// Modal de Confirmação para Executar, Ticar ou Desfazer Classificação
const modalConfirmacao = ref<{
  aberto: boolean;
  acaoTipo: 'CLASSIFICAR' | 'TICAR' | 'DESFAZER';
  tipoLabel: string;
  badgeClass: string;
  titulo: string;
  mensagem: string;
  textoBotaoConfirmar: string;
  variantBtn: 'primary' | 'danger' | 'success' | 'warning';
  row: any;
  codigoClassificacao?: string;
  clsInfo?: any;
}>({
  aberto: false,
  acaoTipo: 'CLASSIFICAR',
  tipoLabel: '',
  badgeClass: '',
  titulo: '',
  mensagem: '',
  textoBotaoConfirmar: 'Confirmar',
  variantBtn: 'primary',
  row: null,
});

const solicitarConfirmacaoClassificar = (row: any, opt: any) => {
  const isPromocao = opt.codigo === 'REALIZADA_SEM_REGISTRO_AGHU';
  const isComAlerta = ['REAGENDAR_EPO', 'AGENDAR_APA', 'REAGENDAR_APA', 'PACIENTE_PRONTO_LEC'].includes(opt.codigo);
  const isAgend = ['REAGENDAR_EPO', 'AGENDAR_APA', 'REAGENDAR_APA'].includes(opt.codigo);
  const destinoTexto = isPromocao
    ? (abaAtiva.value === 'T1_2' ? 'enviado para a Lista Principal da Tabela 2 (Consulta EPO realizada)' : 'enviado para a Lista Principal da Tabela 4 (APA realizada)')
    : `movido para a subtabela "${opt.label}" dentro de ${abaAtualInfo.value?.codigo}`;

  modalConfirmacao.value = {
    aberto: true,
    acaoTipo: 'CLASSIFICAR',
    tipoLabel: isComAlerta ? 'Solicitação com Alerta' : 'Execução de Classificação',
    badgeClass: isComAlerta ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-indigo-100 text-indigo-800 border border-indigo-200',
    titulo: `Confirmar classificação: ${opt.label}`,
    mensagem: `Confirma aplicar a classificação "${opt.label}" para este paciente? Ele será ${destinoTexto}${
      isComAlerta
        ? (isAgend ? ' e gerará um alerta de ação pendente até ser marcada como solicitada.' : ' e gerará um alerta de ação pendente.')
        : '.'
    }`,
    textoBotaoConfirmar: 'Confirmar Classificação',
    variantBtn: 'primary',
    row,
    codigoClassificacao: opt.codigo,
  };
};

const solicitarConfirmacaoTicar = (row: any, clsInfo: any) => {
  const vaiMarcar = !clsInfo.acao_realizada;
  const isAgend = isAcaoAgendamentoConsulta(clsInfo);
  const termo = isAgend ? 'solicitada' : 'solicitada / concluída';

  modalConfirmacao.value = {
    aberto: true,
    acaoTipo: 'TICAR',
    tipoLabel: vaiMarcar ? 'Resposta / Cumprimento de Pendência' : 'Desfazer Ação Solicitada',
    badgeClass: vaiMarcar ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-rose-100 text-rose-800 border border-rose-200',
    titulo: vaiMarcar ? `Marcar "${clsInfo.label}" como ${termo}` : `Desfazer marcação de "${clsInfo.label}"`,
    mensagem: vaiMarcar
      ? (isAgend
          ? `Confirma que a marcação de "${clsInfo.label}" foi solicitada? O alerta vermelho será baixado e o paciente passará para a aba "2. Ações Solicitadas (Check dado)" até que a nova consulta seja agendada no AGHU.`
          : `Confirma que a ação "${clsInfo.label}" foi realizada? O alerta vermelho será baixado e o paciente passará para a aba "2. Ações Solicitadas (Check dado)".`)
      : `Confirma desfazer a marcação de "${clsInfo.label}"? O paciente retornará para a aba "1. Ações Pendentes (Check ainda não dado)" e voltará a gerar alerta vermelho.`,
    textoBotaoConfirmar: vaiMarcar ? 'Confirmar como Solicitada' : 'Sim, Desfazer e Voltar para Pendentes',
    variantBtn: vaiMarcar ? 'success' : 'danger',
    row,
    clsInfo,
  };
};

const solicitarConfirmacaoDesfazer = (row: any, clsInfo: any, isPromocao = false) => {
  const isCancelamentoSolicitacaoPendente = Boolean(clsInfo?.requer_acao && !clsInfo?.acao_realizada);
  modalConfirmacao.value = {
    aberto: true,
    acaoTipo: 'DESFAZER',
    tipoLabel: isCancelamentoSolicitacaoPendente ? 'Cancelamento de Solicitação' : 'Desfazer Classificação',
    badgeClass: 'bg-rose-100 text-rose-800 border border-rose-200',
    titulo: isCancelamentoSolicitacaoPendente ? `Cancelar solicitação: "${clsInfo.label}"` : `Desfazer "${clsInfo.label}"`,
    mensagem: isPromocao
      ? `Confirma desfazer a classificação "${clsInfo.label}"? O paciente retornará imediatamente para a Lista Principal da tabela de consulta não realizada com seu status original do AGHU.`
      : (isCancelamentoSolicitacaoPendente
          ? `Confirma cancelar a solicitação pendente "${clsInfo.label}"? O alerta vermelho será removido e o paciente retornará imediatamente para a Lista Principal.`
          : `Confirma desfazer a classificação "${clsInfo.label}"? O paciente sairá desta subtabela e retornará imediatamente para a Lista Principal.`),
    textoBotaoConfirmar: isCancelamentoSolicitacaoPendente ? 'Sim, Cancelar Solicitação' : 'Sim, Desfazer Classificação',
    variantBtn: 'danger',
    row,
    clsInfo,
  };
};

const fecharModalConfirmacao = () => {
  modalConfirmacao.value.aberto = false;
};

const confirmarAcaoModal = async () => {
  const m = modalConfirmacao.value;
  if (!m.aberto) return;
  if (m.acaoTipo === 'CLASSIFICAR' && m.row && m.codigoClassificacao) {
    await aplicarClassificacao(m.row, m.codigoClassificacao);
  } else if (m.acaoTipo === 'TICAR' && m.row && m.clsInfo) {
    await alternarTicarAcao(m.row, m.clsInfo);
  } else if (m.acaoTipo === 'DESFAZER' && m.row && m.clsInfo) {
    await desfazerClassificacao(m.row, m.clsInfo.id);
  }
  fecharModalConfirmacao();
};

const obterNomePerfilAtivo = () => {
  return perfisStore.perfilAtivo?.nome || perfisStore.perfilAtivo?.id || 'ADMIN';
};

const aplicarClassificacao = async (row: any, codigoClassificacao: string) => {
  processandoClassificacao.value = true;
  try {
    await api.post('/api/navegacao/classificar', {
      pac_codigo: row.pac_codigo,
      prontuario: row.prontuario,
      nome_paciente: row.nome_paciente,
      tabela_origem: abaAtiva.value,
      numero_consulta_ref: row.numero_consulta,
      data_consulta_ref: row.data_consulta,
      grade_sigla_ref: row.grade_sigla,
      grade_nome_ref: row.grade_nome,
      status_consulta_ref: row.status_original_aghu || row.status,
      classificacao: codigoClassificacao,
      perfil_executor: obterNomePerfilAtivo()
    });
    toast.success(`Classificação aplicada ao prontuário #${row.prontuario}!`);
    await carregarPaineis(true);
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao aplicar classificação.');
  } finally {
    processandoClassificacao.value = false;
  }
};

const alternarTicarAcao = async (row: any, clsInfo: any) => {
  processandoClassificacao.value = true;
  try {
    const novoValor = !clsInfo.acao_realizada;
    await api.post('/api/navegacao/classificacao/ticar', {
      id: clsInfo.id,
      acao_realizada: novoValor,
      nome_paciente: row?.nome_paciente,
      perfil_executor: obterNomePerfilAtivo()
    });
    const termoToast = isAcaoAgendamentoConsulta(clsInfo) ? 'solicitada' : 'concluída';
    toast.success(novoValor ? `Marcada como ${termoToast}!` : 'Marcação desfeita.');
    await carregarPaineis(true);
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao atualizar status da ação.');
  } finally {
    processandoClassificacao.value = false;
  }
};

const desfazerClassificacao = async (row: any, classificacaoId: string) => {
  processandoClassificacao.value = true;
  try {
    await api.delete(`/api/navegacao/classificacao/${encodeURIComponent(classificacaoId)}`, {
      params: {
        perfil_executor: obterNomePerfilAtivo(),
        nome_paciente: row?.nome_paciente
      }
    });
    toast.info('Classificação desfeita. Paciente retornado ao status anterior.');
    await carregarPaineis(true);
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao desfazer classificação.');
  } finally {
    processandoClassificacao.value = false;
  }
};

const examesMonitoradosAtivos = computed(() => {
  const out: Array<{ sigla: string; descricao: string; grupoId: string; grupoNome: string }> = [];
  const seen = new Set<string>();
  for (const grp of gruposExamesAtivos.value) {
    for (const ex of (grp.exames || [])) {
      const s = String(ex.sigla || '').trim().toUpperCase();
      if (s && !seen.has(s)) {
        seen.add(s);
        out.push({
          sigla: s,
          descricao: ex.descricao || s,
          grupoId: grp.id,
          grupoNome: grp.nome
        });
      }
    }
  }
  return out;
});

const gradesDisponiveisAbaAtual = computed(() => {
  return isAbaApa.value ? gradesApaAtivas.value : gradesEpoAtivas.value;
});

const toggleGradeFiltro = (sigla: string) => {
  const idx = gradesSelecionadasFiltro.value.indexOf(sigla);
  if (idx === -1) {
    gradesSelecionadasFiltro.value.push(sigla);
  } else {
    gradesSelecionadasFiltro.value.splice(idx, 1);
  }
};

const selecionarAbaTabela = (id: AbaTabelaId) => {
  abaAtiva.value = id;
  subtabelaAtiva.value = 'PRINCIPAL';
  substatusAcaoAtiva.value = 'PENDENTES';
  gradesSelecionadasFiltro.value = [];
  filtroStatusConsulta.value = '';
  paginaAtual.value = 1;
};

const limparFiltrosTabela = () => {
  filtroProntuario.value = '';
  filtroDataDe.value = '';
  filtroDataAte.value = '';
  filtroStatusConsulta.value = '';
  gradesSelecionadasFiltro.value = [];
  filtroGrupoExame22.value = '';
  filtroSituacaoExames22.value = '';
  filtroSituacaoConsultaPreop22.value = '';
  filtroGradeConsultaPreop22.value = '';
  filtroSituacaoConsultaPosApa4.value = '';
  filtroGradeConsultaPosApa4.value = '';
  paginaAtual.value = 1;
};

const irParaTabelaComProntuario = (id: AbaTabelaId, prontuario: string, subtabela = 'PRINCIPAL', substatusAcao: 'PENDENTES' | 'SOLICITADAS' = 'PENDENTES') => {
  limparFiltrosTabela();
  abaAtiva.value = id;
  subtabelaAtiva.value = subtabela || 'PRINCIPAL';
  substatusAcaoAtiva.value = substatusAcao || 'PENDENTES';
  filtroProntuario.value = prontuario;
};

// Busca Global em todas as 6 tabelas
const resultadosBuscaGlobal = computed(() => {
  const q = buscaGlobalProntuario.value.trim().toLowerCase();
  if (q.length < 2) return [];

  const mapPac = new Map<string, any>();
  const fontes = [
    { abaId: 'T1_1' as const, tabelaTitulo: 'Tabela 1.1 (Consulta EPO agendada)', badgeClass: 'bg-indigo-50 border-indigo-200 text-indigo-900', lista: tabela11EpoAgendada.value },
    { abaId: 'T1_2' as const, tabelaTitulo: 'Tabela 1.2 (Consulta EPO não realizada)', badgeClass: 'bg-rose-50 border-rose-200 text-rose-900', lista: tabela12EpoNaoRealizada.value },
    { abaId: 'T2' as const, tabelaTitulo: 'Tabela 2 (Consulta EPO realizada)', badgeClass: 'bg-teal-50 border-teal-200 text-teal-900', lista: tabela2EpoRealizada.value },
    { abaId: 'T3_1' as const, tabelaTitulo: 'Tabela 3.1 (APA agendada)', badgeClass: 'bg-amber-50 border-amber-200 text-amber-900', lista: tabela31ApaAgendada.value },
    { abaId: 'T3_2' as const, tabelaTitulo: 'Tabela 3.2 (APA não realizada)', badgeClass: 'bg-orange-50 border-orange-200 text-orange-900', lista: tabela32ApaNaoRealizada.value },
    { abaId: 'T4' as const, tabelaTitulo: 'Tabela 4 (APA realizada)', badgeClass: 'bg-emerald-50 border-emerald-200 text-emerald-900', lista: tabela4ApaRealizada.value },
  ];

  for (const f of fontes) {
    for (const row of f.lista) {
      if (String(row.prontuario).toLowerCase().includes(q) || (row.nome_paciente || '').toLowerCase().includes(q)) {
        let entry = mapPac.get(row.prontuario);
        if (!entry) {
          entry = {
            prontuario: row.prontuario,
            nome_paciente: row.nome_paciente,
            possui_nome_social: row.possui_nome_social,
            dt_nascimento: row.dt_nascimento,
            ocorrencias: []
          };
          mapPac.set(row.prontuario, entry);
        }
        entry.ocorrencias.push({
          abaId: f.abaId,
          tabelaTitulo: f.tabelaTitulo,
          badgeClass: f.badgeClass,
          grade_sigla: row.grade_sigla,
          data_consulta: row.data_consulta,
          status: row.status_detalhe || row.status,
          subtabela: row.subtabela || 'PRINCIPAL',
          subtabelaLabel: row.classificacao_info?.label || '',
          substatusAcao: row.classificacao_info?.acao_realizada ? ('SOLICITADAS' as const) : ('PENDENTES' as const),
          substatusLabel: row.classificacao_info?.requer_acao
            ? (row.classificacao_info?.acao_realizada ? 'Ação Solicitada' : 'Ação Pendente')
            : ''
        });
      }
    }
  }

  return Array.from(mapPac.values()).slice(0, 30);
});

const listaBaseAbaAtiva = computed(() => {
  switch (abaAtiva.value) {
    case 'T1_1': return tabela11EpoAgendada.value;
    case 'T1_2': return tabela12EpoNaoRealizada.value;
    case 'T2':   return tabela2EpoRealizada.value;
    case 'T3_1': return tabela31ApaAgendada.value;
    case 'T3_2': return tabela32ApaNaoRealizada.value;
    case 'T4':   return tabela4ApaRealizada.value;
    default:     return [];
  }
});

const linhasFiltradas = computed(() => {
  return listaBaseAbaAtiva.value.filter(row => {
    // 0. Filtro de Lista Principal vs Subtabela nas Tabelas 1.2, 2, 3.2 e 4
    if (abaPossuiClassificacoes.value) {
      const subRow = row.subtabela || 'PRINCIPAL';
      if (subRow !== subtabelaAtiva.value) return false;
      // 0.1. Subdivisão dentro das subtabelas que possuem ação (Ações Pendentes vs Ações Solicitadas)
      if (subtabelaPossuiSubdivisao.value) {
        const isSolicitada = Boolean(row.classificacao_info?.acao_realizada);
        if (substatusAcaoAtiva.value === 'PENDENTES' && isSolicitada) return false;
        if (substatusAcaoAtiva.value === 'SOLICITADAS' && !isSolicitada) return false;
      }
    }

    // 1. Prontuário ou Nome
    if (filtroProntuario.value.trim()) {
      const q = filtroProntuario.value.trim().toLowerCase();
      const matchCod = String(row.prontuario).toLowerCase().includes(q);
      const matchNome = (row.nome_paciente || '').toLowerCase().includes(q);
      if (!matchCod && !matchNome) return false;
    }

    // 2. Grade(s) selecionada(s)
    if (gradesSelecionadasFiltro.value.length > 0) {
      if (!gradesSelecionadasFiltro.value.includes(row.grade_sigla)) return false;
    }

    // 3. Intervalo de Data da Consulta
    if (filtroDataDe.value || filtroDataAte.value) {
      const dtOnly = (row.data_consulta || '').split(' ')[0];
      if (!dtOnly) return false;
      if (filtroDataDe.value && dtOnly < filtroDataDe.value) return false;
      if (filtroDataAte.value && dtOnly > filtroDataAte.value) return false;
    }

    // 4. Status da Consulta (T1_2, T2, T3_2 e T4)
    if (filtroStatusConsulta.value) {
      if (abaAtiva.value === 'T2' || abaAtiva.value === 'T4') {
        if (filtroStatusConsulta.value === 'Realizado (sem registro no AGHU)') {
          if (!row.promovido_sem_registro) return false;
        } else if (filtroStatusConsulta.value === 'Realizado') {
          if (row.promovido_sem_registro) return false;
        }
      } else {
        if (row.status !== filtroStatusConsulta.value) return false;
      }
    }

    // 5. Filtros exclusivos da Tabela 2
    if (abaAtiva.value === 'T2') {
      const exames: any[] = row.exames_solicitados || [];
      const preops: any[] = row.consultas_preop || [];

      if (filtroGrupoExame22.value) {
        if (filtroGrupoExame22.value.startsWith('EXAME:')) {
          const siglaExAlvo = filtroGrupoExame22.value.replace('EXAME:', '');
          if (!exames.some(e => e.sigla === siglaExAlvo)) return false;
        } else {
          if (!exames.some(e => e.grupo_id === filtroGrupoExame22.value)) return false;
        }
      }

      if (filtroSituacaoExames22.value) {
        if (filtroSituacaoExames22.value === 'COM_EXAMES' && exames.length === 0) return false;
        if (filtroSituacaoExames22.value === 'SEM_EXAMES' && exames.length > 0) return false;
        if (filtroSituacaoExames22.value === 'TODOS_LIBERADOS') {
          if (exames.length === 0 || !exames.every(e => e.status_categoria === 'LIBERADO')) return false;
        }
        if (filtroSituacaoExames22.value === 'COM_PENDENTES') {
          if (!exames.some(e => e.status_categoria !== 'LIBERADO')) return false;
        }
      }

      if (filtroGradeConsultaPreop22.value || filtroSituacaoConsultaPreop22.value) {
        const sigAlvo = filtroGradeConsultaPreop22.value;
        const sitAlvo = filtroSituacaoConsultaPreop22.value;
        const preopsAlvo = sigAlvo ? preops.filter(p => p.sigla === sigAlvo) : preops;

        if (sigAlvo && !sitAlvo) {
          if (preopsAlvo.length === 0) return false;
        }

        if (sitAlvo) {
          if (sitAlvo === 'COM_CONSULTA' && preopsAlvo.length === 0) return false;
          if (sitAlvo === 'SEM_CONSULTA' && preopsAlvo.length > 0) return false;
          if (sitAlvo === 'REALIZADA' && !preopsAlvo.some(p => p.status === 'Realizado')) return false;
          if (sitAlvo === 'AGENDADA' && !preopsAlvo.some(p => p.status === 'Agendado')) return false;
          if (sitAlvo === 'NAO_REALIZADA' && !preopsAlvo.some(p => p.status === 'Agendado (Data Passada)' || p.status.includes('Falta'))) return false;
          if (sitAlvo === 'AGENDADA_PASSADA' && !preopsAlvo.some(p => p.status === 'Agendado (Data Passada)')) return false;
          if (sitAlvo === 'FALTOSA' && !preopsAlvo.some(p => p.status.includes('Falta'))) return false;
        }
      }
    }

    // 6. Filtros exclusivos da Tabela 4 (Consultas Solicitadas pela APA)
    if (abaAtiva.value === 'T4') {
      const posApas: any[] = row.consultas_pos_apa || [];
      if (filtroGradeConsultaPosApa4.value || filtroSituacaoConsultaPosApa4.value) {
        const sigAlvo4 = filtroGradeConsultaPosApa4.value;
        const sitAlvo4 = filtroSituacaoConsultaPosApa4.value;
        const posApasAlvo = sigAlvo4 ? posApas.filter(p => p.sigla === sigAlvo4) : posApas;

        if (sigAlvo4 && !sitAlvo4) {
          if (posApasAlvo.length === 0) return false;
        }

        if (sitAlvo4) {
          if (sitAlvo4 === 'COM_CONSULTA' && posApasAlvo.length === 0) return false;
          if (sitAlvo4 === 'SEM_CONSULTA' && posApasAlvo.length > 0) return false;
          if (sitAlvo4 === 'REALIZADA' && !posApasAlvo.some(p => p.status === 'Realizado')) return false;
          if (sitAlvo4 === 'AGENDADA' && !posApasAlvo.some(p => p.status === 'Agendado')) return false;
          if (sitAlvo4 === 'NAO_REALIZADA' && !posApasAlvo.some(p => p.status === 'Agendado (Data Passada)' || p.status.includes('Falta'))) return false;
          if (sitAlvo4 === 'AGENDADA_PASSADA' && !posApasAlvo.some(p => p.status === 'Agendado (Data Passada)')) return false;
          if (sitAlvo4 === 'FALTOSA' && !posApasAlvo.some(p => p.status.includes('Falta'))) return false;
        }
      }
    }

    return true;
  });
});

const linhasPaginadas = computed(() => {
  const inicio = (paginaAtual.value - 1) * itensPorPagina.value;
  return linhasFiltradas.value.slice(inicio, inicio + itensPorPagina.value);
});

watch([
  subtabelaAtiva,
  substatusAcaoAtiva,
  filtroProntuario,
  filtroDataDe,
  filtroDataAte,
  filtroStatusConsulta,
  gradesSelecionadasFiltro,
  filtroGrupoExame22,
  filtroSituacaoExames22,
  filtroSituacaoConsultaPreop22,
  filtroGradeConsultaPreop22,
  filtroSituacaoConsultaPosApa4,
  filtroGradeConsultaPosApa4,
  itensPorPagina
], () => {
  paginaAtual.value = 1;
}, { deep: true });

const contarExamesLiberados = (exames: any[]) => {
  return (exames || []).filter(e => e.status_categoria === 'LIBERADO').length;
};

const toggleRecolherExames = (prontuario: string) => {
  examesRecolhidos.value[prontuario] = !examesRecolhidos.value[prontuario];
};

const obterExamesVisiveis = (row: any) => {
  const list = row.exames_solicitados || [];
  if (examesRecolhidos.value[row.prontuario] && list.length > 6) {
    return list.slice(0, 6);
  }
  return list;
};

const getStatusConsultaBadgeClass = (status: string) => {
  switch (status) {
    case 'Realizado':
      return 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200';
    case 'Agendado':
      return 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200';
    case 'Agendado (Data Passada)':
      return 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-100 text-purple-900 border border-purple-300';
    case 'Falta do paciente':
      return 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200';
    case 'Falta do profissional':
      return 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-orange-100 text-orange-800 border border-orange-200';
    default:
      return 'px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-gray-100 text-gray-800';
  }
};

const getCardExameClass = (cor: string) => {
  switch (cor) {
    case 'verde':
      return 'bg-emerald-50/90 border-emerald-200 text-emerald-950';
    case 'azul':
      return 'bg-blue-50/90 border-blue-200 text-blue-950';
    case 'amarelo':
      return 'bg-amber-50/90 border-amber-200 text-amber-950';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
};

const getCardConsultaPreopClass = (status: string) => {
  switch (status) {
    case 'Realizado':
      return 'bg-emerald-50/90 border-emerald-200 text-emerald-950';
    case 'Agendado':
      return 'bg-blue-50/90 border-blue-200 text-blue-950';
    case 'Agendado (Data Passada)':
      return 'bg-purple-50/90 border-purple-300 text-purple-950';
    case 'Falta do paciente':
    case 'Falta do profissional':
      return 'bg-rose-50/90 border-rose-200 text-rose-950';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
};

const formatarData = (dataStr?: string) => {
  if (!dataStr) return '—';
  const s = String(dataStr).trim().split(' ')[0].split('T')[0];
  const parts = s.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dataStr;
};

const formatarHora = (dataStr?: string) => {
  if (!dataStr) return '';
  const parts = String(dataStr).trim().replace('T', ' ').split(' ');
  return parts[1] ? parts[1].substring(0, 5) : '';
};

const formatarDataHora = (dataStr?: string) => {
  if (!dataStr) return '—';
  const parts = String(dataStr).trim().replace('T', ' ').split(' ');
  const d = formatarData(parts[0]);
  const h = parts[1] ? parts[1].substring(0, 5) : '';
  return h ? `${d} ${h}` : d;
};

const carregarPaineis = async (forceRefresh = false) => {
  loading.value = true;
  try {
    const { data } = await api.get('/api/navegacao/paineis', {
      params: {
        janela_meses: janelaMeses.value,
        refresh: forceRefresh
      }
    });
    atualizadoEm.value = data.atualizado_em || '';
    if (data.config) {
      config.value = data.config;
    }
    tabela11EpoAgendada.value = data.tabela_1_1_epo_agendada || [];
    tabela12EpoNaoRealizada.value = data.tabela_1_2_epo_nao_realizada || [];
    tabela2EpoRealizada.value = data.tabela_2_epo_realizada || [];
    tabela31ApaAgendada.value = data.tabela_3_1_apa_agendada || [];
    tabela32ApaNaoRealizada.value = data.tabela_3_2_apa_nao_realizada || [];
    tabela4ApaRealizada.value = data.tabela_4_apa_realizada || [];
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao carregar painéis da Navegação do AGHU.');
  } finally {
    loading.value = false;
  }
};

// =========================================================================
// Modal de Configuração de Grades e Exames (com Busca no AGHU)
// =========================================================================
const modalConfigAberto = ref(false);
const salvandoConfig = ref(false);
const abaModalConfig = ref<'EPO' | 'PREOP' | 'APA' | 'POS_APA' | 'EXAMES'>('EPO');
const abasModalConfig = [
  { id: 'EPO' as const, titulo: '1. Grades de Enfermagem (EPO)', subtitulo: 'Consultas EPO (Estágios 1 e 2)' },
  { id: 'EXAMES' as const, titulo: '2. Grupos e Exames Pré-Operatórios', subtitulo: 'Exames monitorados na Tabela 2' },
  { id: 'PREOP' as const, titulo: '3. Grades de Consultas Pré-Op (RIS/PPC...)', subtitulo: 'Pareceres monitorados na Tabela 2' },
  { id: 'APA' as const, titulo: '4. Grades da APA (Anestesia)', subtitulo: 'Consultas APA (Estágios 3 e 4)' },
  { id: 'POS_APA' as const, titulo: '5. Grades de Consultas Solicitadas pela APA', subtitulo: 'Consultas monitoradas na Tabela 4' },
];

const configEdicao = ref<any>({
  janela_meses: 12,
  grades_epo: [],
  grades_preop: [],
  grades_apa: [],
  grades_pos_apa: [],
  grupos_exames: []
});

const termoBuscaGradeAghu = ref('');
const buscandoGradesAghu = ref(false);
const resultadosGradesAghu = ref<any[]>([]);

const grupoExameSelecionadoIdx = ref(0);
const termoBuscaExameAghu = ref('');
const buscandoExamesAghu = ref(false);
const resultadosExamesAghu = ref<any[]>([]);

const abrirModalConfig = () => {
  const clone = JSON.parse(JSON.stringify(config.value));
  if (!clone.grades_pos_apa) clone.grades_pos_apa = [];
  configEdicao.value = clone;
  termoBuscaGradeAghu.value = '';
  resultadosGradesAghu.value = [];
  termoBuscaExameAghu.value = '';
  resultadosExamesAghu.value = [];
  grupoExameSelecionadoIdx.value = 0;
  modalConfigAberto.value = true;
};

const listaGradesCategoriaModal = computed(() => {
  if (abaModalConfig.value === 'EPO') return configEdicao.value.grades_epo || [];
  if (abaModalConfig.value === 'PREOP') return configEdicao.value.grades_preop || [];
  if (abaModalConfig.value === 'APA') return configEdicao.value.grades_apa || [];
  if (abaModalConfig.value === 'POS_APA') return configEdicao.value.grades_pos_apa || [];
  return [];
});

const grupoExameAtualModal = computed(() => {
  const list = configEdicao.value.grupos_exames || [];
  return list[grupoExameSelecionadoIdx.value] || list[0] || null;
});

const pesquisarGradesNoAghu = async () => {
  buscandoGradesAghu.value = true;
  try {
    const { data } = await api.get('/api/navegacao/aghu/grades', {
      params: { q: termoBuscaGradeAghu.value }
    });
    resultadosGradesAghu.value = data || [];
  } catch {
    toast.error('Erro ao pesquisar grades no AGHU.');
  } finally {
    buscandoGradesAghu.value = false;
  }
};

const adicionarGradeNaCategoriaAtual = (gradeAghu: any) => {
  const lista = listaGradesCategoriaModal.value;
  if (lista.some((g: any) => g.sigla === gradeAghu.sigla)) {
    toast.info(`A sigla ${gradeAghu.sigla} já está na lista desta etapa.`);
    return;
  }
  lista.push({
    sigla: gradeAghu.sigla,
    nome: gradeAghu.nome,
    ativo: true
  });
  toast.success(`Grade ${gradeAghu.sigla} adicionada!`);
};

const removerGradeDaCategoriaAtual = (idx: number) => {
  listaGradesCategoriaModal.value.splice(idx, 1);
};

const pesquisarExamesNoAghu = async () => {
  buscandoExamesAghu.value = true;
  try {
    const { data } = await api.get('/api/navegacao/aghu/exames', {
      params: { q: termoBuscaExameAghu.value }
    });
    resultadosExamesAghu.value = data || [];
  } catch {
    toast.error('Erro ao pesquisar exames no AGHU.');
  } finally {
    buscandoExamesAghu.value = false;
  }
};

const adicionarExameNoGrupoAtual = (exAghu: any) => {
  const grp = grupoExameAtualModal.value;
  if (!grp) return;
  if (!grp.exames) grp.exames = [];
  if (grp.exames.some((e: any) => e.sigla === exAghu.sigla)) {
    toast.info(`O exame ${exAghu.sigla} já está vinculado ao grupo "${grp.nome}".`);
    return;
  }
  grp.exames.push({
    sigla: exAghu.sigla,
    descricao: exAghu.descricao
  });
  toast.success(`Exame ${exAghu.sigla} adicionado ao grupo "${grp.nome}"!`);
};

const salvarConfiguracao = async () => {
  salvandoConfig.value = true;
  try {
    configEdicao.value.janela_meses = janelaMeses.value;
    const { data } = await api.put('/api/navegacao/config', configEdicao.value);
    config.value = data;
    // Higieniza filtros selecionados caso alguma grade ou exame/grupo tenha sido removido ou desativado
    const siglasDisponiveisAba = new Set(gradesDisponiveisAbaAtual.value.map((g: any) => g.sigla));
    gradesSelecionadasFiltro.value = gradesSelecionadasFiltro.value.filter(s => siglasDisponiveisAba.has(s));
    if (filtroGradeConsultaPreop22.value && !gradesPreopAtivas.value.some((g: any) => g.sigla === filtroGradeConsultaPreop22.value)) {
      filtroGradeConsultaPreop22.value = '';
    }
    if (filtroGradeConsultaPosApa4.value && !gradesPosApaAtivas.value.some((g: any) => g.sigla === filtroGradeConsultaPosApa4.value)) {
      filtroGradeConsultaPosApa4.value = '';
    }
    if (filtroGrupoExame22.value) {
      if (filtroGrupoExame22.value.startsWith('EXAME:')) {
        const sigEx = filtroGrupoExame22.value.replace('EXAME:', '');
        if (!examesMonitoradosAtivos.value.some(e => e.sigla === sigEx)) {
          filtroGrupoExame22.value = '';
        }
      } else if (!gruposExamesAtivos.value.some((grp: any) => grp.id === filtroGrupoExame22.value)) {
        filtroGrupoExame22.value = '';
      }
    }
    modalConfigAberto.value = false;
    toast.success('Configuração de consultas e exames atualizada com sucesso!');
    await carregarPaineis(true);
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao salvar configuração.');
  } finally {
    salvandoConfig.value = false;
  }
};

onMounted(() => {
  carregarPaineis(false);
});
</script>
