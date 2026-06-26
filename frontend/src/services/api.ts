import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import router from '../router';

// Determina se estamos rodando na nuvem (GitHub Pages) ou localmente
const isGitHubPages = window.location.hostname.includes('github.io');

const api = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  }
});

// -----------------------------------------------------------------------------
// SIMULADOR DE MODO DEMONSTRAÇÃO (Para rodar no GitHub Pages sem backend ativo)
// -----------------------------------------------------------------------------
const mockPacientes: Record<string, { codigo: string; nome: string; cpf: string }> = {
  '123456': { codigo: '123456', nome: 'CARLA DIAS (DEMO)', cpf: '111.222.333-44' },
  '789012': { codigo: '789012', nome: 'MARCOS OLIVEIRA (DEMO)', cpf: '555.666.777-88' },
  '345678': { codigo: '345678', nome: 'JULIANA SOUZA (DEMO)', cpf: '999.888.777-66' },
};

// Pacientes para o módulo de Especialidades (rota /api/pacientes)
const mockPacientesEspecialidades = [
  // ── PLÁSTICA (10 pacientes fictícios) ───────────────────────────────────────
  { codigo: 'HC-1045231', nome: 'ANA BEATRIZ FERREIRA', procedimento: 'Reconstrução Mamária',   especialidade: 'Plástica', ultima_consulta_epo: '2024-03-10' },
  { codigo: 'HC-2078934', nome: 'CARLA MENDES SILVA',   procedimento: 'Mamoplastia',             especialidade: 'Plástica', ultima_consulta_epo: '2024-05-22' },
  { codigo: 'HC-3012847', nome: 'DANIELA ROCHA LIMA',   procedimento: 'Abdominoplastia',         especialidade: 'Plástica', ultima_consulta_epo: '2024-07-08' },
  { codigo: 'HC-4056182', nome: 'FERNANDA COSTA REIS',  procedimento: 'Rinoplastia',             especialidade: 'Plástica', ultima_consulta_epo: '2024-08-14' },
  { codigo: 'HC-5091376', nome: 'JÉSSICA ALVES MOURA',  procedimento: 'Blefaroplastia',          especialidade: 'Plástica', ultima_consulta_epo: '2024-09-03' },
  { codigo: 'HC-6034721', nome: 'LÚCIA BARROS SANTOS',  procedimento: 'Reconstrução Mamária',   especialidade: 'Plástica', ultima_consulta_epo: '2024-10-17' },
  { codigo: 'HC-7083914', nome: 'MÁRCIA TEIXEIRA NUNES',procedimento: 'Mamoplastia',             especialidade: 'Plástica', ultima_consulta_epo: '2024-11-05' },
  { codigo: 'HC-8027563', nome: 'PATRÍCIA GOMES ARAUJO',procedimento: 'Abdominoplastia',         especialidade: 'Plástica', ultima_consulta_epo: '2025-01-20' },
  { codigo: 'HC-9041298', nome: 'RENATA CARDOSO FREITAS',procedimento: 'Rinoplastia',            especialidade: 'Plástica', ultima_consulta_epo: '2025-03-11' },
  { codigo: 'HC-1162047', nome: 'SANDRA OLIVEIRA PINTO',procedimento: 'Blefaroplastia',          especialidade: 'Plástica', ultima_consulta_epo: '2025-05-28' },
  // ── OFTALMOLOGIA (exemplos) ─────────────────────────────────────────────────
  { codigo: 'HC-2205831', nome: 'ANTONIO JOSE CAVALCANTE', procedimento: 'Facoemulsificação (Catarata)', especialidade: 'Oftalmologia', ultima_consulta_epo: '2024-06-15' },
  { codigo: 'HC-3318742', nome: 'BENEDITA RAMOS CORREIA',  procedimento: 'Trabeculectomia (Glaucoma)',  especialidade: 'Oftalmologia', ultima_consulta_epo: '2024-11-30' },
  // ── UROLOGIA (exemplos) ─────────────────────────────────────────────────────
  { codigo: 'HC-4421653', nome: 'CARLOS HENRIQUE MELO',    procedimento: 'Prostatectomia Radical',       especialidade: 'Urologia',     ultima_consulta_epo: '2024-04-19' },
  { codigo: 'HC-5534564', nome: 'DIEGO FERREIRA SOUZA',    procedimento: 'Ressecção Transuretral de Próstata (RTUP)', especialidade: 'Urologia', ultima_consulta_epo: '2025-02-07' },
  // ── TORÁCICA (exemplos) ─────────────────────────────────────────────────────
  { codigo: 'HC-6647475', nome: 'ELIANA MOREIRA BASTOS',   procedimento: 'Lobectomia',                  especialidade: 'Torácica',     ultima_consulta_epo: '2024-08-25' },
  { codigo: 'HC-7750386', nome: 'FABIO AZEVEDO CUNHA',     procedimento: 'Ressecção de Nódulo Pulmonar', especialidade: 'Torácica',     ultima_consulta_epo: '2025-04-13' },
];

const getLocalSolicitacoes = () => {
  const data = localStorage.getItem('demo_solicitacoes');
  if (!data) {
    const defaultData = [
      {
        id: 'a1b2c3d4',
        tipo: 'INSERIR',
        especialidade: 'Cirurgia Geral',
        procedimento: 'Colecistectomia',
        codigo_paciente: '123456',
        nome_paciente: 'CARLA DIAS (DEMO)',
        judicializado: 'Não',
        swallis: 'A2',
        medico_responsavel: 'Dra. Helena Souza',
        detalhes: 'Paciente com colelitíase sintomática recorrente.',
        status: 'PENDENTE',
        data_criacao: '2026-06-25 14:30:00'
      },
      {
        id: 'e5f6g7h8',
        tipo: 'STANDBY',
        especialidade: 'Ortopedia',
        procedimento: 'Artroplastia Total de Joelho',
        codigo_paciente: '789012',
        nome_paciente: 'MARCOS OLIVEIRA (DEMO)',
        judicializado: 'Sim',
        swallis: 'A1',
        medico_responsavel: 'Dr. Roberto Cruz',
        detalhes: 'Aguardando liberação cardiológica devido a arritmia recente.',
        tempo_standby: 30,
        status: 'APROVADO',
        data_criacao: '2026-06-25 15:45:00'
      }
    ];
    localStorage.setItem('demo_solicitacoes', JSON.stringify(defaultData));
    return defaultData;
  }
  return JSON.parse(data);
};

const setLocalSolicitacoes = (solics: any[]) => {
  localStorage.setItem('demo_solicitacoes', JSON.stringify(solics));
};

function strMatch(a: any, b: any) {
  return String(a).trim() === String(b).trim();
}

// Se estiver no GitHub Pages, intercepta tudo pelo adapter do Axios
if (isGitHubPages) {
  api.defaults.adapter = async (config: any): Promise<any> => {
    const url = config.url || '';
    const method = (config.method || 'get').toLowerCase();
    
    // Converte os dados se vierem em URLSearchParams ou JSON string
    let data: any = null;
    if (config.data) {
      if (typeof config.data === 'string') {
        try {
          if (config.data.startsWith('username=')) {
            const params = new URLSearchParams(config.data);
            data = Object.fromEntries(params.entries());
          } else {
            data = JSON.parse(config.data);
          }
        } catch (e) {
          data = config.data;
        }
      } else {
        data = config.data;
      }
    }

    console.log(`[MOCK API ADAPTER] Interceptado: ${method.toUpperCase()} ${url}`, data);

    // Latência simulada
    await new Promise(resolve => setTimeout(resolve, 300));

    // Rota: POST /api/login ou qualquer link de login
    if (url.includes('/api/login')) {
      if (data?.username === 'admin' && data?.password === 'admin') {
        return {
          data: {
            access_token: 'mock-jwt-token-for-demo',
            token_type: 'bearer'
          },
          status: 200,
          statusText: 'OK',
          headers: {},
          config
        };
      }
      return Promise.reject({
        response: {
          status: 401,
          data: { detail: 'Usuário ou senha incorretos' }
        }
      });
    }

    // Rota: POST /api/token/refresh
    if (url.includes('/api/token/refresh')) {
      return {
        data: { access_token: 'mock-jwt-token-for-demo' },
        status: 200,
        headers: {},
        config
      };
    }

    // Rota: GET /api/users/me
    if (url.includes('/api/users/me')) {
      return {
        data: { username: 'admin', groups: ['GLO-SEC-HCPE-SETISD'] }, // Permite acesso admin e total
        status: 200,
        headers: {},
        config
      };
    }

    // Rota: POST /api/logout
    if (url.includes('/api/logout')) {
      return { data: { success: true }, status: 200, headers: {}, config };
    }

    // Rota: GET /api/pacientes  (lista para o módulo Especialidades)
    if (url.match(/\/api\/pacientes$/) && method === 'get') {
      return { data: mockPacientesEspecialidades, status: 200, headers: {}, config };
    }

    // Rota: GET /api/pacientes/{codigo}
    if (url.includes('/api/pacientes/')) {
      const parts = url.split('/');
      const codigo = parts[parts.length - 1];
      const paciente = mockPacientes[codigo];
      if (paciente) {
        return { data: paciente, status: 200, headers: {}, config };
      }
      return Promise.reject({
        response: {
          status: 404,
          data: { detail: 'Paciente não localizado' }
        }
      });
    }

    // Rota: GET /api/solicitacoes/paciente/{codigo}
    if (url.includes('/api/solicitacoes/paciente/')) {
      const parts = url.split('/');
      const codigo = parts[parts.length - 1];
      const solics = getLocalSolicitacoes();
      const solic = solics.find((s: any) => strMatch(s.codigo_paciente, codigo));
      if (solic) {
        return { data: solic, status: 200, headers: {}, config };
      }
      return Promise.reject({
        response: {
          status: 404,
          data: { detail: 'Nenhuma solicitação encontrada' }
        }
      });
    }

    // Rota: GET /api/solicitacoes
    if (url.includes('/api/solicitacoes') && method === 'get') {
      return { data: getLocalSolicitacoes(), status: 200, headers: {}, config };
    }

    // Rota: POST /api/solicitacoes
    if (url.includes('/api/solicitacoes') && method === 'post') {
      const solics = getLocalSolicitacoes();
      const nova = {
        ...data,
        id: Math.random().toString(36).substring(2, 10),
        status: 'PENDENTE',
        data_criacao: new Date().toISOString().replace('T', ' ').substring(0, 19)
      };
      solics.push(nova);
      setLocalSolicitacoes(solics);
      return { data: nova, status: 200, headers: {}, config };
    }

    // Rota: PUT /api/solicitacoes/{id}/status
    if (url.includes('/api/solicitacoes/') && url.includes('/status') && method === 'put') {
      const parts = url.split('/');
      const id = parts[parts.length - 2];
      const solics = getLocalSolicitacoes();
      const index = solics.findIndex((s: any) => s.id === id);
      if (index !== -1) {
        solics[index].status = data.status;
        setLocalSolicitacoes(solics);
        return { data: solics[index], status: 200, headers: {}, config };
      }
      return Promise.reject({
        response: {
          status: 404,
          data: { detail: 'Solicitação não encontrada' }
        }
      });
    }

    return { data: {}, status: 200, headers: {}, config };
  };
}

// Interceptor original para anexar token (caso não esteja no Github Pages)
api.interceptors.request.use(config => {
  const authStore = useAuthStore();
  const token = authStore.accessToken;
  
  if (token && !isGitHubPages) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor de token expirado (caso não esteja no Github Pages)
api.interceptors.response.use(
  response => response,
  async error => {
    if (isGitHubPages) return Promise.reject(error);
    
    const originalRequest = error.config;
    const authStore = useAuthStore();

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        console.log('Access token expired. Attempting to refresh...');
        const { data } = await axios.post('/api/token/refresh');
        authStore.setToken(data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        processQueue(null, data.access_token);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        console.error('Unable to refresh token. Logging out.', refreshError);
        authStore.logout(router);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export default api;