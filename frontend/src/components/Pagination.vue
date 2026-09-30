<template>
  <div v-if="totalItems > 0" class="flex flex-col sm:flex-row items-center justify-between gap-4 py-3 px-4 bg-white border-t border-gray-200 text-xs text-gray-700 select-none">
    <!-- Informação de Contagem -->
    <div class="flex items-center space-x-2">
      <span>
        Exibindo
        <strong class="font-bold text-gray-900">{{ itemInicialFormatado }}</strong>
        a
        <strong class="font-bold text-gray-900">{{ itemFinalFormatado }}</strong>
        de
        <strong class="font-bold text-gray-900">{{ totalItemsFormatado }}</strong>
        {{ itemName }}
      </span>

      <!-- Seletor de Itens por Página -->
      <div v-if="showItemsPerPage" class="flex items-center space-x-1.5 ml-4 pl-4 border-l border-gray-200">
        <label for="itensPorPaginaSelect" class="text-gray-500 text-[11px]">Por página:</label>
        <select
          id="itensPorPaginaSelect"
          :value="itemsPerPage"
          @change="onItemsPerPageChange(($event.target as HTMLSelectElement).value)"
          class="text-xs bg-gray-50 border border-gray-200 rounded px-2 py-1 font-semibold text-gray-700 cursor-pointer focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option :value="25">25</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
          <option :value="200">200</option>
        </select>
      </div>
    </div>

    <!-- Controles de Navegação -->
    <div v-if="totalPages > 1" class="flex items-center space-x-1">
      <!-- Primeira Página -->
      <button
        type="button"
        @click="mudarPagina(1)"
        :disabled="currentPage === 1"
        class="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent transition cursor-pointer text-gray-600"
        title="Primeira Página"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>

      <!-- Página Anterior -->
      <button
        type="button"
        @click="mudarPagina(currentPage - 1)"
        :disabled="currentPage === 1"
        class="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent transition cursor-pointer font-medium text-gray-700"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="hidden sm:inline">Anterior</span>
      </button>

      <!-- Botões Numéricos das Páginas -->
      <div class="flex items-center space-x-1">
        <template v-for="(p, idx) in paginasVisiveis" :key="idx">
          <span v-if="p === '...'" class="px-2 py-1 text-gray-400 font-mono">...</span>
          <button
            v-else
            type="button"
            @click="mudarPagina(p as number)"
            :class="[
              'min-w-[32px] h-8 px-2 rounded-lg font-bold transition cursor-pointer text-xs flex items-center justify-center',
              currentPage === p
                ? 'bg-indigo-600 text-white shadow-sm border border-indigo-600'
                : 'border border-gray-200 text-gray-700 hover:bg-gray-100'
            ]"
          >
            {{ p }}
          </button>
        </template>
      </div>

      <!-- Próxima Página -->
      <button
        type="button"
        @click="mudarPagina(currentPage + 1)"
        :disabled="currentPage >= totalPages"
        class="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent transition cursor-pointer font-medium text-gray-700"
      >
        <span class="hidden sm:inline">Próxima</span>
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <!-- Última Página -->
      <button
        type="button"
        @click="mudarPagina(totalPages)"
        :disabled="currentPage >= totalPages"
        class="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent transition cursor-pointer text-gray-600"
        title="Última Página"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    totalItems: number;
    itemsPerPage?: number;
    currentPage: number;
    itemName?: string;
    showItemsPerPage?: boolean;
  }>(),
  {
    itemsPerPage: 50,
    itemName: 'registros',
    showItemsPerPage: true,
  }
);

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void;
  (e: 'update:itemsPerPage', count: number): void;
}>();

const totalPages = computed(() => {
  if (props.totalItems <= 0) return 1;
  return Math.ceil(props.totalItems / props.itemsPerPage);
});

const itemInicial = computed(() => {
  if (props.totalItems === 0) return 0;
  return (props.currentPage - 1) * props.itemsPerPage + 1;
});

const itemFinal = computed(() => {
  return Math.min(props.currentPage * props.itemsPerPage, props.totalItems);
});

const itemInicialFormatado = computed(() => itemInicial.value.toLocaleString('pt-BR'));
const itemFinalFormatado = computed(() => itemFinal.value.toLocaleString('pt-BR'));
const totalItemsFormatado = computed(() => props.totalItems.toLocaleString('pt-BR'));

const mudarPagina = (page: number) => {
  if (page < 1 || page > totalPages.value || page === props.currentPage) return;
  emit('update:currentPage', page);
};

const onItemsPerPageChange = (valStr: string) => {
  const val = parseInt(valStr, 10);
  if (!isNaN(val) && val > 0) {
    emit('update:itemsPerPage', val);
    emit('update:currentPage', 1);
  }
};

const paginasVisiveis = computed<(number | string)[]>(() => {
  const total = totalPages.value;
  const current = props.currentPage;

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | string)[] = [];

  if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i);
    pages.push('...');
    pages.push(total);
  } else if (current >= total - 3) {
    pages.push(1);
    pages.push('...');
    for (let i = total - 4; i <= total; i++) pages.push(i);
  } else {
    pages.push(1);
    pages.push('...');
    pages.push(current - 1);
    pages.push(current);
    pages.push(current + 1);
    pages.push('...');
    pages.push(total);
  }

  return pages;
});
</script>
