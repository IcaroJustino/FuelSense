import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

import {
  Observable,
  BehaviorSubject,
  combineLatest,
  map,
  debounceTime,
  distinctUntilChanged,
  startWith,
} from 'rxjs';

import {
  DashboardService,
  HistoricalRecord,
  FuelAveragePrice,
  TopConsumer,
  TotalRevenue,
  ConsumptionDistribution,
  RawPriceEvolutionData,
  DataStatus,
} from '../../services/dasbhoard.service';

import { LineChartComponent } from '../../components/linechart/line-chart.component';
import { PieChartComponent } from '../../components/piechart/pie-chart.component';
import { HistoricalTableComponent } from '../../components/table/historical-table.component';
import { ChartInputData, PieChartInputData } from '../../interfaces/auth.interfaces';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    LineChartComponent,
    PieChartComponent,
    HistoricalTableComponent,
    FormsModule,
  ],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {
  private dashboardService = inject(DashboardService);
  private authService = inject(AuthService);

  dataStatus: string = 'Carregando...';
  isStatusLoading: boolean = true;
  priceEvolutionData: ChartInputData | undefined;
  isLoading: boolean = true;
  consumptionData: PieChartInputData | undefined;
  isConsumptionLoading: boolean = true;
  isFuelAveragesLoading: boolean = true;
  fuelAverages: { [key: string]: string } = {
    Gasolina: '0.00',
    Etanol: '0.00',
    'Diesel S10': '0.00',
  };
  isTotalRevenueLoading: boolean = true;
  formattedTotalRevenue: string = '0.00';
  isTopConsumerLoading: boolean = true;
  topConsumer: TopConsumer = { tipo_veiculo: 'N/A', volume_total: '0.00' };
  formattedTopVolume: string = '0.00';
  fuelFilter: string = 'todos';
  stateFilter: string = 'todos';
  vehicleFilter: string = 'todos';
  currentPage: number = 1;
  pageSize: number = 10;
  totalPages: number = 10;
  private searchTermSubject = new BehaviorSubject<string>('');
  searchTerm: string = '';
  historicalRecords$!: Observable<HistoricalRecord[]>;
  isTableLoading: boolean = true;

  onLogout(): void {
    this.authService.logout();
  }

  ngOnInit(): void {
    this.loadAllDashboardData();
    this.setupHistoricalDataStream();
    this.loadDataStatus();
  }
  loadAllDashboardData(): void {
    this.loadHistoricalData();
    this.loadFuelAverages();
    this.loadTotalRevenue();
    this.loadTopConsumer();
    this.loadChartData();
    this.loadConsumptionData();
  }
  loadDataStatus(): void {
    this.isStatusLoading = true;
    this.dashboardService.getDataStatus().subscribe({
      next: (data: DataStatus) => {
        this.dataStatus = data.friendly_status;
        this.isStatusLoading = false;
      },
      error: () => {
        this.dataStatus = 'Erro ao carregar status';
        this.isStatusLoading = false;
      },
    });
  }
  loadFuelAverages(): void {
    this.isFuelAveragesLoading = true;
    this.dashboardService
      .getFuelAveragePrices(this.fuelFilter, this.stateFilter, this.vehicleFilter)
      .subscribe({
        next: (data: FuelAveragePrice[]) => {
          this.fuelAverages = data.reduce((acc, curr) => {
            acc[curr.tipo_combustivel] = curr.media_preco ? curr.media_preco.toFixed(2) : '0.00';
            return acc;
          }, this.fuelAverages);
          this.isFuelAveragesLoading = false;
        },
        error: () => (this.isFuelAveragesLoading = false),
      });
  }

  loadTotalRevenue(): void {
    this.isTotalRevenueLoading = true;
    this.dashboardService
      .getTotalRevenue(this.fuelFilter, this.stateFilter, this.vehicleFilter)
      .subscribe({
        next: (data: TotalRevenue) => {
          this.formattedTotalRevenue = parseFloat(data.receita_total).toFixed(2);
          this.isTotalRevenueLoading = false;
        },
        error: () => (this.isTotalRevenueLoading = false),
      });
  }

  loadTopConsumer(): void {
    this.isTopConsumerLoading = true;
    this.dashboardService
      .getTopConsumer(this.fuelFilter, this.stateFilter, this.vehicleFilter)
      .subscribe({
        next: (data: TopConsumer) => {
          this.topConsumer = data;
          this.formattedTopVolume = parseFloat(data.volume_total).toFixed(2);
          this.isTopConsumerLoading = false;
        },
        error: () => (this.isTopConsumerLoading = false),
      });
  }

  loadChartData(): void {
    this.isLoading = true;
    this.dashboardService
      .getPriceEvolution(this.fuelFilter, this.stateFilter, this.vehicleFilter)
      .subscribe({
        next: (data: RawPriceEvolutionData[]) => {
          if (!data || data.length === 0) {
            this.priceEvolutionData = { categories: [], series: [] };
            this.isLoading = false;
            return;
          }
          const dates = Array.from(new Set(data.map((item) => item.data_coleta))).sort();
          const fuelTypes = Array.from(new Set(data.map((item) => item.tipo_combustivel)));

          const priceMap = new Map<string, { [key: string]: number }>();
          data.forEach((item) => {
            if (!priceMap.has(item.data_coleta)) {
              priceMap.set(item.data_coleta, {});
            }
            priceMap.get(item.data_coleta)![item.tipo_combustivel] = item.preco_medio_arredondado;
          });

          const series = fuelTypes.map((fuelType) => {
            const prices: number[] = dates.map((date) => {
              return priceMap.get(date)?.[fuelType] || 0;
            });

            return {
              label: fuelType,
              data: prices,
            };
          });

          this.priceEvolutionData = {
            categories: dates,
            series: series,
          };
          this.isLoading = false;
        },
        error: () => {
          this.priceEvolutionData = { categories: [], series: [] };
          this.isLoading = false;
        },
      });
  }

  loadConsumptionData(): void {
    this.isConsumptionLoading = true;
    this.dashboardService
      .getConsumptionDistribution(this.fuelFilter, this.stateFilter, this.vehicleFilter)
      .subscribe({
        next: (data: ConsumptionDistribution) => {
          this.consumptionData = data;
          this.isConsumptionLoading = false;
        },
        error: () => (this.isConsumptionLoading = false),
      });
  }
  setupHistoricalDataStream(): void {
    this.historicalRecords$ = combineLatest([
      this.dashboardService.records$,
      this.searchTermSubject.pipe(
        debounceTime(300),
        distinctUntilChanged(),
        startWith(this.searchTerm)
      ),
    ]).pipe(
      map(([records, searchTerm]) => {
        const lowerSearch = searchTerm.toLowerCase().trim();
        if (!lowerSearch) {
          return [...records];
        }

        return records.filter(
          (record) =>
            (record.motorista_nome || '').toLowerCase().includes(lowerSearch) ||
            (record.posto_nome || '').toLowerCase().includes(lowerSearch) ||
            (record.veiculo_placa || '').toLowerCase().includes(lowerSearch) ||
            (record.motorista_cpf || '').includes(lowerSearch)
        );
      })
    );
  }

  loadHistoricalData(): void {
    this.isTableLoading = true;
    const skip = (this.currentPage - 1) * this.pageSize;
    const limit = this.pageSize;

    this.dashboardService
      .getHistoricalRecords(this.fuelFilter, this.stateFilter, this.vehicleFilter, skip, limit)
      .subscribe({
        next: () => {
          this.isTableLoading = false;
        },
        error: (err) => {
          console.error('Erro ao carregar histórico da API:', err);
          this.isTableLoading = false;
        },
      });
  }
  onFilterChange(): void {
    this.currentPage = 1;
    this.loadAllDashboardData();
    this.loadDataStatus();
  }
  onSearchChange(): void {
    this.searchTermSubject.next(this.searchTerm);
  }
  onPageChange(page: number): void {
    if (page < 1) return;
    this.currentPage = page;
    this.loadHistoricalData();
  }
}
