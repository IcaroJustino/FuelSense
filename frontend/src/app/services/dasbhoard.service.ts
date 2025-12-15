import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, catchError, of, map } from 'rxjs';
import {
  ConsumptionDistribution,
  DataStatus,
  FuelAveragePrice,
  HistoricalRecord,
  RawPriceEvolutionData,
  TopConsumer,
  TotalRevenue,
  VolumePorVeiculoResponse,
} from '../interfaces/auth.interfaces';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private http = inject(HttpClient);
  private recordsSubject = new BehaviorSubject<HistoricalRecord[]>([]);
  public records$: Observable<HistoricalRecord[]> = this.recordsSubject.asObservable();

  constructor() {}

  getDataStatus(): Observable<DataStatus> {
    const url = `${this.apiUrl}/status-dados`;
    return this.http.get<DataStatus>(url);
  }

  private buildFilterParams(fuel: string, state: string, vehicle: string): HttpParams {
    let params = new HttpParams();

    if (fuel !== 'todos') params = params.set('tipo_combustivel', fuel);
    if (state !== 'todos') params = params.set('estado', state);
    if (vehicle !== 'todos') params = params.set('tipo_veiculo', vehicle);

    return params;
  }

  private formatData(data: HistoricalRecord[]): HistoricalRecord[] {
    return data.map((record) => ({
      ...record,
      preco_venda: parseFloat(record.preco_venda.toString()),
      volume_vendido: parseFloat(record.volume_vendido.toString()),
    }));
  }

  public getHistoricalRecords(
    fuel: string,
    state: string,
    vehicle: string,
    skip: number,
    limit: number
  ): Observable<HistoricalRecord[]> {
    let params = this.buildFilterParams(fuel, state, vehicle)
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    const endpoint = '/coletas/coletas';

    return this.http.get<HistoricalRecord[]>(`${this.apiUrl}${endpoint}`, { params }).pipe(
      map(this.formatData),
      tap((records) => this.recordsSubject.next(records)),
      catchError((err: HttpErrorResponse) => {
        console.error('Erro ao carregar histórico da API:', err);
        return of([]);
      })
    );
  }

  public getFuelAveragePrices(
    fuel: string,
    state: string,
    vehicle: string
  ): Observable<FuelAveragePrice[]> {
    const params = this.buildFilterParams(fuel, state, vehicle);
    const endpoint = '/dashboard/media-preco-combustivel';

    return this.http.get<FuelAveragePrice[]>(`${this.apiUrl}${endpoint}`, { params }).pipe(
      catchError((err: HttpErrorResponse) => {
        console.error('Erro ao carregar médias de preço:', err);
        return of([]);
      })
    );
  }
  public getPriceEvolution(
    fuel: string,
    state: string,
    vehicle: string
  ): Observable<RawPriceEvolutionData[]> {
    const endpoint = '/dashboard/historico-preco-combustivel';
    const params = this.buildFilterParams(fuel, state, vehicle);

    return this.http.get<RawPriceEvolutionData[]>(`${this.apiUrl}${endpoint}`, { params }).pipe(
      tap(() => console.log('Dados de Evolução Histórica (API) carregados.')),
      catchError((err: HttpErrorResponse) => {
        console.error('Erro ao carregar evolução de preço:', err);
        return of([]);
      })
    );
  }

  public getConsumptionDistribution(
    fuel: string,
    state: string,
    vehicle: string
  ): Observable<ConsumptionDistribution> {
    const endpoint = '/dashboard/volume-por-veiculo';
    const params = this.buildFilterParams(fuel, state, vehicle);

    const backgroundColors = [
      '#4f46e5',
      '#059669',
      '#f59e0b',
      '#ef4444',
      '#10b981',
      '#3b82f6',
      '#6366f1',
    ];

    return this.http.get<VolumePorVeiculoResponse[]>(`${this.apiUrl}${endpoint}`, { params }).pipe(
      map((data: VolumePorVeiculoResponse[]) => {
        const labels = data.map((item) => item.tipo_veiculo);
        const volumes = data.map((item) => parseFloat(item.volume_total.toString()));

        return {
          labels: labels,
          data: volumes,
          backgroundColor: labels.map(
            (_, index) => backgroundColors[index % backgroundColors.length]
          ),
        } as ConsumptionDistribution;
      }),
      catchError((err: HttpErrorResponse) => {
        console.error('Erro ao carregar Distribuição de Consumo da API:', err);
        return of({ labels: [], data: [], backgroundColor: [] });
      })
    );
  }

  public getTopConsumer(fuel: string, state: string, vehicle: string): Observable<TopConsumer> {
    const endpoint = '/dashboard/maior-consumidor';
    const params = this.buildFilterParams(fuel, state, vehicle);

    return this.http.get<TopConsumer>(`${this.apiUrl}${endpoint}`, { params }).pipe(
      catchError((err: HttpErrorResponse) => {
        console.error('Erro ao carregar maior consumidor:', err);
        return of({ tipo_veiculo: 'N/A', volume_total: '0.00' });
      })
    );
  }

  public getTotalRevenue(fuel: string, state: string, vehicle: string): Observable<TotalRevenue> {
    const endpoint = '/dashboard/receita-total-estimada';
    const params = this.buildFilterParams(fuel, state, vehicle);

    return this.http.get<TotalRevenue>(`${this.apiUrl}${endpoint}`, { params }).pipe(
      catchError((err: HttpErrorResponse) => {
        console.error('Erro ao carregar receita total:', err);
        return of({ receita_total: '0.00' });
      })
    );
  }
}
export type {
  ConsumptionDistribution,
  HistoricalRecord,
  FuelAveragePrice,
  TopConsumer,
  TotalRevenue,
  RawPriceEvolutionData,
  DataStatus,
};
