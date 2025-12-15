// src/app/chart-config.ts
import { Chart, registerables, CategoryScale } from 'chart.js';

/**
 * Funções para registro do Chart.js
 */

export function registerChartJS() {
  // 1. Método Simples (Recomendado): Registra todos os componentes padrão
  // Chart.register(...registerables);

  // 2. Método Otimizado: Registra APENAS os componentes necessários para um gráfico de LINHA
  // Isso é útil para reduzir o tamanho final do bundle (tree-shaking), mas exige que você liste tudo.
  // Neste caso, a escala 'category' é crítica.

  Chart.register(
    ...registerables.filter(
      (registerable) => !('id' in registerable) || registerable.id !== 'category' // Remove o default para garantir que CategoryScale seja o primeiro
    ),
    CategoryScale
  );

  // Se o método 1 não funcionou, vamos garantir que o CategoryScale seja registrado
  // Chart.register(CategoryScale);
}
