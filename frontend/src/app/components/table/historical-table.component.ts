import { Component, Input, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule, CurrencyPipe, DecimalPipe } from '@angular/common';
import { HistoricalRecord } from '../../services/dasbhoard.service';

@Component({
  selector: 'app-historical-table',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, DecimalPipe],
  templateUrl: './historical-table.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styles: [],
})
export class HistoricalTableComponent implements OnInit {
  @Input() records: HistoricalRecord[] = [];
  @Input() isLoading: boolean = false;

  public columnNames = [
    { key: 'data_coleta', label: 'Data', type: 'text' },
    { key: 'posto_nome', label: 'Posto/Cidade', type: 'text' },
    { key: 'motorista_nome', label: 'Motorista/CPF', type: 'text' },
    { key: 'veiculo_placa', label: 'Veículo/Placa', type: 'text' },
    { key: 'tipo_combustivel', label: 'Combustível', type: 'text' },
    { key: 'preco_venda', label: 'Preço (R$)', type: 'currency' },
    { key: 'volume_vendido', label: 'Volume (L)', type: 'decimal' },
    { key: 'total', label: 'Total', type: 'currency', class: 'font-bold' },
  ];

  ngOnInit(): void {}

  getFuelClass(fuel: string): string {
    switch (fuel.toLowerCase()) {
      case 'etanol':
        return 'bg-green-100 text-green-800';
      case 'diesel s10':
        return 'bg-blue-100 text-blue-800';
      case 'gasolina':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  calculateTotal(record: HistoricalRecord): number {
    return record.preco_venda * record.volume_vendido;
  }
}
