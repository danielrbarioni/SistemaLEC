<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full border border-gray-100 overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-200">
      <div class="p-6 text-center space-y-4">
        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-50 text-red-500">
          <svg class="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900">Funcionalidade indisponível</h3>
        <p class="text-sm text-gray-600 leading-relaxed">
          Esta funcionalidade não está disponível no momento.
        </p>
      </div>
      <div class="bg-gray-50 px-6 py-4 flex justify-center space-x-3 border-t border-gray-100">
        <Button @click="irParaHome" variant="primary" class="w-full justify-center">
          Voltar para o Sistema LEC
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Button from '../components/Button.vue';

const router = useRouter();
const irParaHome = () => {
  router.push('/interacoes');
};
</script>
