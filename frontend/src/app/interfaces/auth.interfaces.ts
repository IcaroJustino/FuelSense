import { ChartDataset } from 'chart.js';

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  email: string;
  senha: string;
}

export interface UserInfo {
  id: number;
  nome: string;
  email: string;
  cpf: string;
  coreid: string;
}

export interface ChartInputData {
  categories: string[];
  series: ChartDataset<'line'>[];
}
export interface PieChartInputData {
  labels: string[];
  data: number[];
  backgroundColor: string[];
}

export interface Toast {
  message: string;
  type: 'success' | 'error';
}

export interface HistoricalRecord {
  posto_identificador: string;
  posto_nome: string;
  cidade: string;
  estado: string;
  data_coleta: string;
  tipo_combustivel: string;
  preco_venda: number;
  volume_vendido: number;
  motorista_nome: string;
  motorista_cpf: string;
  veiculo_placa: string;
  tipo_veiculo: string;
  id: number;
}

export interface TotalRevenue {
  receita_total: string;
}

export interface DataStatus {
  last_update_timestamp: number;
  last_update_datetime: string;
  time_since_last_update_seconds: number;
  friendly_status: string; // O campo que você quer exibir
}

export interface FuelAveragePrice {
  tipo_combustivel: 'Gasolina' | 'Etanol' | 'Diesel S10';
  media_preco: number;
}

export interface RawPriceEvolutionData {
  data_coleta: string;
  tipo_combustivel: string;
  preco_medio_arredondado: number;
}

export interface DashboardEvolutionResponse {
  categories: string[];
  series: { name: string; data: number[] }[];
}

export interface VolumePorVeiculoResponse {
  tipo_veiculo: string;
  volume_total: number;
}

export interface ConsumptionDistribution {
  labels: string[];
  data: number[];
  backgroundColor: string[];
}

export interface TopConsumer {
  tipo_veiculo: string;
  volume_total: string;
}
