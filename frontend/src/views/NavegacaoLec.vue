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

        <!-- Botão Configurar Grades e Exames -->
        <button
          type="button"
          @click="abrirModalConfig"
          class="inline-flex items-center space-x-1.5 px-3 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs rounded-lg border border-indigo-200 transition cursor-pointer"
        >
          <span>⚙️</span>
          <span>Grades e Exames Monitorados</span>
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
              <span>Localizar Paciente na Jornada Cirúrgica (Busca Global nas 5 Tabelas)</span>
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
                  @click="irParaTabelaComProntuario(oc.abaId, pac.prontuario)"
                  class="px-2.5 py-1.5 rounded-lg border text-left transition cursor-pointer hover:shadow-xs text-xs flex flex-col"
                  :class="oc.badgeClass"
                  title="Clique para abrir esta tabela filtrada neste prontuário"
                >
                  <span class="font-bold flex items-center space-x-1">
                    <span>{{ oc.tabelaTitulo }}</span>
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

    <!-- Abas das 5 Tabelas (Estágios da Jornada Cirúrgica) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
      <button
        v-for="aba in abasTabelas"
        :key="aba.id"
        type="button"
        @click="selecionarAbaTabela(aba.id)"
        class="p-3 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between"
        :class="abaAtiva === aba.id ? aba.activeClass : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-700'"
      >
        <div class="flex items-center justify-between w-full">
          <span class="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded" :class="abaAtiva === aba.id ? 'bg-white/20 text-white' : aba.pillClass">
            {{ aba.codigo }}
          </span>
          <span class="text-lg font-extrabold font-mono">
            {{ aba.total }}
          </span>
        </div>
        <div class="mt-2">
          <div class="text-xs font-bold leading-snug">{{ aba.titulo }}</div>
          <div class="text-[10px] mt-0.5" :class="abaAtiva === aba.id ? 'text-white/80' : 'text-gray-400'">
            {{ aba.subtitulo }}
          </div>
        </div>
      </button>
    </div>

    <!-- Filtros Modificáveis da Tabela Selecionada -->
    <Card>
      <div class="space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-2">
          <div>
            <h2 class="text-sm font-bold text-gray-800">
              {{ abaAtualInfo?.codigo }} — {{ abaAtualInfo?.titulo }}
            </h2>
            <p class="text-xs text-gray-500">
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

          <!-- 4. Filtro de Status (nas Tabelas 1, 2.1 e 3.1 onde há mais de um status possível) -->
          <div v-if="abaAtiva === 'T1' || abaAtiva === 'T2_1' || abaAtiva === 'T3_1'" class="form-group">
            <label class="form-label font-semibold text-xs">
              Status da {{ isAbaApa ? 'APA' : 'Consulta EPO' }}
            </label>
            <select v-model="filtroStatusConsulta" class="form-control text-xs py-1.5">
              <option value="">Todos os status desta tabela</option>
              <option v-if="abaAtiva === 'T1' || abaAtiva === 'T3_1'" value="Agendado">Agendado (Hoje / Futuro)</option>
              <option v-if="abaAtiva === 'T1' || abaAtiva === 'T3_1'" value="Agendado (Data Passada)">Agendado (Data Passada / Sem Desfecho)</option>
              <option v-if="abaAtiva === 'T2_1' || abaAtiva === 'T3_1'" value="Falta do paciente">Falta do paciente</option>
              <option v-if="abaAtiva === 'T2_1' || abaAtiva === 'T3_1'" value="Falta do profissional">Falta do profissional</option>
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

        <!-- Filtros Específicos da Tabela 2.2 (Exames Pré-Op e Consultas Pré-Op) -->
        <div v-if="abaAtiva === 'T2_2'" class="pt-2 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="form-group">
            <label class="form-label font-semibold text-xs">Filtrar por Grupo de Exame Solicitado</label>
            <select v-model="filtroGrupoExame22" class="form-control text-xs py-1.5">
              <option value="">Todos os grupos de exames</option>
              <option v-for="grp in gruposExamesAtivos" :key="grp.id" :value="grp.id">
                {{ grp.nome }}
              </option>
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
            <label class="form-label font-semibold text-xs">Consultas Pré-Op (RIS, PPC, RCI, OHR, PPO)</label>
            <select v-model="filtroConsultaPreop22" class="form-control text-xs py-1.5">
              <option value="">Todas</option>
              <option value="COM_CONSULTA">Com alguma consulta pré-op agendada/realizada</option>
              <option value="REALIZADA">Com consulta pré-op Realizada</option>
              <option value="AGENDADA">Com consulta pré-op Agendada (Hoje / Futuro)</option>
              <option value="AGENDADA_PASSADA">Com consulta pré-op Agendada em Data Passada (Sem Desfecho)</option>
              <option value="FALTOSA">Com consulta pré-op Faltosa</option>
              <option value="SEM_CONSULTA">Sem consulta pré-op registrada</option>
              <optgroup label="Por Grade Específica">
                <option v-for="gp in gradesPreopAtivas" :key="gp.sigla" :value="`SIGLA:${gp.sigla}`">
                  Grade {{ gp.sigla }} ({{ gp.nome }})
                </option>
              </optgroup>
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
      <div v-else class="overflow-x-auto border border-gray-100 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200 text-xs">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3.5 py-3 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">Prontuário</th>
              <th class="px-3.5 py-3 text-left font-bold text-gray-600 uppercase tracking-wider">Nome do Paciente</th>
              <th class="px-3.5 py-3 text-left font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">
                Grade {{ isAbaApa ? 'da APA' : 'da Consulta EPO' }}
              </th>
              <th class="px-3.5 py-3 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">
                Data da {{ isAbaApa ? 'APA' : 'Consulta EPO' }}
              </th>
              <th class="px-3.5 py-3 text-center font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap">
                Status da {{ isAbaApa ? 'APA' : 'Consulta EPO' }}
              </th>
              <template v-if="abaAtiva === 'T2_2'">
                <th class="px-3.5 py-3 text-left font-bold text-gray-600 uppercase tracking-wider min-w-[340px]">
                  Exames Pré-Operatórios Solicitados (Cards)
                </th>
                <th class="px-3.5 py-3 text-left font-bold text-gray-600 uppercase tracking-wider min-w-[260px]">
                  Consultas Pré-Operatórias (RIS / PPC / RCI / OHR / PPO)
                </th>
              </template>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="row in linhasPaginadas"
              :key="`${row.prontuario}-${row.grade_sigla}`"
              class="hover:bg-slate-50/80 transition"
            >
              <!-- Prontuário -->
              <td class="px-3.5 py-3 whitespace-nowrap align-top">
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
              <td class="px-3.5 py-3 align-top">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="font-bold text-gray-900">{{ row.nome_paciente }}</span>
                  <span
                    v-if="row.possui_nome_social"
                    class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-100 text-purple-800 border border-purple-200 uppercase"
                  >
                    Nome Social
                  </span>
                </div>
                <div v-if="row.dt_nascimento" class="text-[11px] text-gray-400 mt-0.5">
                  Nasc.: {{ formatarData(row.dt_nascimento) }}
                </div>
              </td>

              <!-- Grade da Consulta -->
              <td class="px-3.5 py-3 whitespace-nowrap align-top">
                <div class="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-800 font-bold">
                  <span>{{ row.grade_sigla }}</span>
                  <span v-if="row.grd_seq" class="text-[10px] font-mono text-slate-500">(Grade #{{ row.grd_seq }})</span>
                </div>
                <div class="text-[11px] text-gray-500 mt-0.5 max-w-[220px] truncate" :title="row.grade_nome">
                  {{ row.grade_nome }}
                </div>
              </td>

              <!-- Data da Consulta -->
              <td class="px-3.5 py-3 text-center whitespace-nowrap font-mono text-gray-800 font-semibold align-top">
                {{ formatarDataHora(row.data_consulta) }}
              </td>

              <!-- Status da Consulta -->
              <td class="px-3.5 py-3 text-center whitespace-nowrap align-top">
                <span :class="getStatusConsultaBadgeClass(row.status)" :title="row.status_detalhe">
                  {{ row.status_detalhe || row.status }}
                </span>
              </td>

              <!-- Colunas exclusivas da Tabela 2.2: Cards de Exames Pré-Op e Consultas Pré-Op -->
              <template v-if="abaAtiva === 'T2_2'">
                <!-- Cards de Exames Pré-Operatórios Solicitados -->
                <td class="px-3.5 py-3 align-top">
                  <div v-if="!row.exames_solicitados || row.exames_solicitados.length === 0" class="text-[11px] text-gray-400 italic">
                    Nenhum exame pré-op solicitado no período
                  </div>
                  <div v-else class="space-y-2">
                    <!-- Resumo de liberação dos exames -->
                    <div class="flex items-center justify-between">
                      <span
                        class="text-[10px] font-bold px-2 py-0.5 rounded-full border"
                        :class="contarExamesLiberados(row.exames_solicitados) === row.exames_solicitados.length
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : 'bg-amber-50 text-amber-800 border-amber-200'"
                      >
                        {{ contarExamesLiberados(row.exames_solicitados) }}/{{ row.exames_solicitados.length }} Liberado(s)
                      </span>
                      <button
                        v-if="row.exames_solicitados.length > 4"
                        type="button"
                        @click="toggleExpandirExames(row.prontuario)"
                        class="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer"
                      >
                        {{ examesExpandidos[row.prontuario] ? 'Recolher ▲' : `Ver todos (${row.exames_solicitados.length}) ▼` }}
                      </button>
                    </div>

                    <!-- Grid de Cards de Exames -->
                    <div class="flex flex-wrap gap-1.5">
                      <div
                        v-for="ex in obterExamesVisiveis(row)"
                        :key="ex.sigla"
                        class="p-2 rounded-lg border text-[11px] flex flex-col justify-between min-w-[155px] max-w-[230px] shadow-2xs"
                        :class="getCardExameClass(ex.cor)"
                        :title="`${ex.grupo_nome}: ${ex.nome} (${ex.sigla}) - Status: ${ex.status}`"
                      >
                        <div class="flex items-start justify-between gap-1.5">
                          <span class="font-bold leading-tight break-words">{{ ex.nome }}</span>
                          <span class="font-mono text-[9px] px-1 py-0.2 rounded bg-black/5 shrink-0">{{ ex.sigla }}</span>
                        </div>
                        <div class="flex items-center justify-between gap-2 mt-1.5 pt-1 border-t border-black/10 text-[10px]">
                          <span class="font-extrabold uppercase">{{ ex.status }}</span>
                          <span class="font-mono opacity-85">{{ formatarData(ex.data) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Cards de Consultas Pré-Operatórias Solicitadas -->
                <td class="px-3.5 py-3 align-top">
                  <div v-if="!row.consultas_preop || row.consultas_preop.length === 0" class="text-[11px] text-gray-400 italic">
                    Nenhuma consulta pré-op registrada
                  </div>
                  <div v-else class="flex flex-wrap gap-1.5">
                    <div
                      v-for="cp in row.consultas_preop"
                      :key="cp.sigla"
                      class="p-2 rounded-lg border text-[11px] flex flex-col justify-between min-w-[160px] max-w-[230px] shadow-2xs"
                      :class="getCardConsultaPreopClass(cp.status)"
                      :title="`${cp.sigla} - ${cp.nome}`"
                    >
                      <div class="flex items-center justify-between gap-1.5">
                        <span class="font-extrabold">{{ cp.sigla }}</span>
                        <span class="text-[10px] truncate opacity-85">{{ cp.nome }}</span>
                      </div>
                      <div class="flex items-center justify-between gap-2 mt-1.5 pt-1 border-t border-black/10 text-[10px]">
                        <span class="font-extrabold uppercase">{{ cp.status }}</span>
                        <span class="font-mono opacity-85">{{ formatarDataHora(cp.data) }}</span>
                      </div>
                    </div>
                  </div>
                </td>
              </template>
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
              ⚙️ Configurar Grades de Consultas e Exames do Circuito Cirúrgico
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              Visualize e edite as siglas de grades de consultas e os exames consultados no AGHU para cada etapa da navegação.
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

        <!-- Abas internas do Modal de Configuração -->
        <div class="flex border-b border-gray-200 bg-gray-50 p-1.5 rounded-lg gap-1 overflow-x-auto shrink-0">
          <button
            v-for="tab in abasModalConfig"
            :key="tab.id"
            type="button"
            @click="abaModalConfig = tab.id"
            class="px-3 py-2 text-xs font-bold rounded-md transition cursor-pointer whitespace-nowrap"
            :class="abaModalConfig === tab.id ? 'bg-indigo-600 text-white shadow-xs' : 'text-gray-600 hover:bg-gray-200'"
          >
            {{ tab.titulo }}
          </button>
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

const toast = useToast();

const loading = ref(false);
const atualizadoEm = ref('');
const janelaMeses = ref(12);

const config = ref<any>({
  janela_meses: 12,
  grades_epo: [],
  grades_preop: [],
  grades_apa: [],
  grupos_exames: []
});

const tabela1EpoAgendada = ref<any[]>([]);
const tabela21EpoFaltosa = ref<any[]>([]);
const tabela22EpoRealizada = ref<any[]>([]);
const tabela31ApaNaoRealizada = ref<any[]>([]);
const tabela32ApaRealizada = ref<any[]>([]);

// Aba ativa entre as 5 tabelas
const abaAtiva = ref<'T1' | 'T2_1' | 'T2_2' | 'T3_1' | 'T3_2'>('T1');

// Busca global por prontuário/nome em todas as 5 tabelas
const buscaGlobalProntuario = ref('');

// Filtros modificáveis da tabela ativa
const filtroProntuario = ref('');
const filtroDataDe = ref('');
const filtroDataAte = ref('');
const filtroStatusConsulta = ref('');
const gradesSelecionadasFiltro = ref<string[]>([]);

// Filtros adicionais exclusivos da Tabela 2.2
const filtroGrupoExame22 = ref('');
const filtroSituacaoExames22 = ref('');
const filtroConsultaPreop22 = ref('');

// Controle de expansão de cards de exames por prontuário
const examesExpandidos = ref<Record<string, boolean>>({});

// Paginação
const paginaAtual = ref(1);
const itensPorPagina = ref(50);

const isAbaApa = computed(() => abaAtiva.value === 'T3_1' || abaAtiva.value === 'T3_2');

const abasTabelas = computed(() => [
  {
    id: 'T1' as const,
    codigo: 'Tabela 1',
    titulo: 'Consulta EPO Agendada',
    subtitulo: 'Enfermagem Pré-Op · Agendado',
    regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade EPO) com status Agendado · Ordenação: da data mais antiga para a mais recente.',
    ordenacaoTexto: 'Data da consulta EPO (mais antiga ➔ mais recente)',
    total: tabela1EpoAgendada.value.length,
    activeClass: 'bg-blue-700 border-blue-700 text-white shadow-sm',
    pillClass: 'bg-blue-100 text-blue-800'
  },
  {
    id: 'T2_1' as const,
    codigo: 'Tabela 2.1',
    titulo: 'Consulta EPO Faltosa',
    subtitulo: 'Falta do paciente ou profissional',
    regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade EPO) com status Falta do paciente ou Falta do profissional · Ordenação: da data mais antiga para a mais recente.',
    ordenacaoTexto: 'Data da consulta EPO (mais antiga ➔ mais recente)',
    total: tabela21EpoFaltosa.value.length,
    activeClass: 'bg-rose-700 border-rose-700 text-white shadow-sm',
    pillClass: 'bg-rose-100 text-rose-800'
  },
  {
    id: 'T2_2' as const,
    codigo: 'Tabela 2.2',
    titulo: 'Consulta EPO Realizada + Exames/Pré-Op',
    subtitulo: 'Cards de Exames e Pareceres Pré-Op',
    regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade EPO) com status Realizado, exibindo os cards dos exames e consultas pré-operatórias solicitados.',
    ordenacaoTexto: 'Data da consulta EPO (mais antiga ➔ mais recente)',
    total: tabela22EpoRealizada.value.length,
    activeClass: 'bg-teal-700 border-teal-700 text-white shadow-sm',
    pillClass: 'bg-teal-100 text-teal-800'
  },
  {
    id: 'T3_1' as const,
    codigo: 'Tabela 3.1',
    titulo: 'APA Não Realizada',
    subtitulo: 'Agendado ou Faltoso (ANE / TAN)',
    regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade APA) com status Agendado, Falta do paciente ou Falta do profissional · Ordenação: da data mais antiga para a mais recente.',
    ordenacaoTexto: 'Data da APA (mais antiga ➔ mais recente)',
    total: tabela31ApaNaoRealizada.value.length,
    activeClass: 'bg-amber-600 border-amber-600 text-white shadow-sm',
    pillClass: 'bg-amber-100 text-amber-800'
  },
  {
    id: 'T3_2' as const,
    codigo: 'Tabela 3.2',
    titulo: 'APA Realizada',
    subtitulo: 'Avaliação Pré-Anestésica concluída',
    regraAutomatica: 'Filtro automático: consulta mais recente por (Prontuário + Grade APA) com status Realizado · Ordenação: da data mais recente para a mais antiga.',
    ordenacaoTexto: 'Data da APA (mais recente ➔ mais antiga)',
    total: tabela32ApaRealizada.value.length,
    activeClass: 'bg-emerald-700 border-emerald-700 text-white shadow-sm',
    pillClass: 'bg-emerald-100 text-emerald-800'
  }
]);

const abaAtualInfo = computed(() => abasTabelas.value.find(a => a.id === abaAtiva.value));

const gradesEpoAtivas = computed(() => (config.value.grades_epo || []).filter((g: any) => g.ativo !== false));
const gradesPreopAtivas = computed(() => (config.value.grades_preop || []).filter((g: any) => g.ativo !== false));
const gradesApaAtivas = computed(() => (config.value.grades_apa || []).filter((g: any) => g.ativo !== false));
const gruposExamesAtivos = computed(() => (config.value.grupos_exames || []).filter((g: any) => g.ativo !== false));

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

const selecionarAbaTabela = (id: 'T1' | 'T2_1' | 'T2_2' | 'T3_1' | 'T3_2') => {
  abaAtiva.value = id;
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
  filtroConsultaPreop22.value = '';
  paginaAtual.value = 1;
};

const irParaTabelaComProntuario = (id: 'T1' | 'T2_1' | 'T2_2' | 'T3_1' | 'T3_2', prontuario: string) => {
  limparFiltrosTabela();
  abaAtiva.value = id;
  filtroProntuario.value = prontuario;
};

// Busca Global em todas as 5 tabelas
const resultadosBuscaGlobal = computed(() => {
  const q = buscaGlobalProntuario.value.trim().toLowerCase();
  if (q.length < 2) return [];

  const mapPac = new Map<string, any>();
  const fontes = [
    { abaId: 'T1' as const, tabelaTitulo: 'Tabela 1 (EPO Agendada)', badgeClass: 'bg-blue-50 border-blue-200 text-blue-900', lista: tabela1EpoAgendada.value },
    { abaId: 'T2_1' as const, tabelaTitulo: 'Tabela 2.1 (EPO Faltosa)', badgeClass: 'bg-rose-50 border-rose-200 text-rose-900', lista: tabela21EpoFaltosa.value },
    { abaId: 'T2_2' as const, tabelaTitulo: 'Tabela 2.2 (EPO Realizada)', badgeClass: 'bg-teal-50 border-teal-200 text-teal-900', lista: tabela22EpoRealizada.value },
    { abaId: 'T3_1' as const, tabelaTitulo: 'Tabela 3.1 (APA Não Realizada)', badgeClass: 'bg-amber-50 border-amber-200 text-amber-900', lista: tabela31ApaNaoRealizada.value },
    { abaId: 'T3_2' as const, tabelaTitulo: 'Tabela 3.2 (APA Realizada)', badgeClass: 'bg-emerald-50 border-emerald-200 text-emerald-900', lista: tabela32ApaRealizada.value },
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
          status: row.status_detalhe || row.status
        });
      }
    }
  }

  return Array.from(mapPac.values()).slice(0, 30);
});

const listaBaseAbaAtiva = computed(() => {
  switch (abaAtiva.value) {
    case 'T1':   return tabela1EpoAgendada.value;
    case 'T2_1': return tabela21EpoFaltosa.value;
    case 'T2_2': return tabela22EpoRealizada.value;
    case 'T3_1': return tabela31ApaNaoRealizada.value;
    case 'T3_2': return tabela32ApaRealizada.value;
    default:     return [];
  }
});

const linhasFiltradas = computed(() => {
  return listaBaseAbaAtiva.value.filter(row => {
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

    // 4. Status da Consulta (T2_1 e T3_1)
    if (filtroStatusConsulta.value) {
      if (row.status !== filtroStatusConsulta.value) return false;
    }

    // 5. Filtros exclusivos da Tabela 2.2
    if (abaAtiva.value === 'T2_2') {
      const exames: any[] = row.exames_solicitados || [];
      const preops: any[] = row.consultas_preop || [];

      if (filtroGrupoExame22.value) {
        if (!exames.some(e => e.grupo_id === filtroGrupoExame22.value)) return false;
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

      if (filtroConsultaPreop22.value) {
        const fc = filtroConsultaPreop22.value;
        if (fc === 'COM_CONSULTA' && preops.length === 0) return false;
        if (fc === 'SEM_CONSULTA' && preops.length > 0) return false;
        if (fc === 'REALIZADA' && !preops.some(p => p.status === 'Realizado')) return false;
        if (fc === 'AGENDADA' && !preops.some(p => p.status === 'Agendado')) return false;
        if (fc === 'AGENDADA_PASSADA' && !preops.some(p => p.status === 'Agendado (Data Passada)')) return false;
        if (fc === 'FALTOSA' && !preops.some(p => p.status.includes('Falta'))) return false;
        if (fc.startsWith('SIGLA:')) {
          const sigAlvo = fc.replace('SIGLA:', '');
          if (!preops.some(p => p.sigla === sigAlvo)) return false;
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
  filtroProntuario,
  filtroDataDe,
  filtroDataAte,
  filtroStatusConsulta,
  gradesSelecionadasFiltro,
  filtroGrupoExame22,
  filtroSituacaoExames22,
  filtroConsultaPreop22,
  itensPorPagina
], () => {
  paginaAtual.value = 1;
}, { deep: true });

const contarExamesLiberados = (exames: any[]) => {
  return (exames || []).filter(e => e.status_categoria === 'LIBERADO').length;
};

const toggleExpandirExames = (prontuario: string) => {
  examesExpandidos.value[prontuario] = !examesExpandidos.value[prontuario];
};

const obterExamesVisiveis = (row: any) => {
  const list = row.exames_solicitados || [];
  if (list.length <= 4 || examesExpandidos.value[row.prontuario]) {
    return list;
  }
  return list.slice(0, 4);
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
    tabela1EpoAgendada.value = data.tabela_1_epo_agendada || [];
    tabela21EpoFaltosa.value = data.tabela_2_1_epo_faltosa || [];
    tabela22EpoRealizada.value = data.tabela_2_2_epo_realizada || [];
    tabela31ApaNaoRealizada.value = data.tabela_3_1_apa_nao_realizada || [];
    tabela32ApaRealizada.value = data.tabela_3_2_apa_realizada || [];
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
const abaModalConfig = ref<'EPO' | 'PREOP' | 'APA' | 'EXAMES'>('EPO');
const abasModalConfig = [
  { id: 'EPO' as const, titulo: '1. Grades de Enfermagem (EPO)' },
  { id: 'PREOP' as const, titulo: '2. Grades de Consultas Pré-Op (RIS/PPC...)' },
  { id: 'APA' as const, titulo: '3. Grades da APA (Anestesia)' },
  { id: 'EXAMES' as const, titulo: '4. Grupos e Exames Pré-Operatórios' },
];

const configEdicao = ref<any>({
  janela_meses: 12,
  grades_epo: [],
  grades_preop: [],
  grades_apa: [],
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
  configEdicao.value = JSON.parse(JSON.stringify(config.value));
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
    modalConfigAberto.value = false;
    toast.success('Configuração de grades e exames atualizada com sucesso!');
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
