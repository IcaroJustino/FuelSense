import { Component, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartConfiguration, ChartData, ChartType, ChartDataset } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { ChartInputData } from '../../interfaces/auth.interfaces';

@Component({
  selector: 'app-line-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './line-chart.component.html',
  styles: [],
})
export class LineChartComponent implements OnChanges {
  @Input() data!: ChartInputData;
  @Input() title: string = '';
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  public lineChartType: ChartType = 'line';

  public lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 0,
        right: 20,
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        align: 'center',
        labels: {
          usePointStyle: true,
          boxWidth: 8,
        },
      },
      tooltip: {
        callbacks: {
          label: ({ dataset, parsed }) => {
            const value = parsed.y != null ? parsed.y.toFixed(2).replace('.', ',') : '0,00';
            return `${dataset.label}: R$ ${value}`;
          },
        },
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: '#ccc',
        borderWidth: 1,
        titleColor: '#000',
        bodyColor: '#000',
      },
    },
    scales: {
      x: {
        grid: {
          display: true,
          drawOnChartArea: true,
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          color: '#000',
        },
      },
      y: {
        min: 0,
        title: {
          display: false,
        },
        grid: {
          display: true,
          drawOnChartArea: true,
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          color: '#000',
          callback: (value) => {
            return `R$ ${parseFloat(value.toString()).toFixed(2).replace('.', ',')}`;
          },
        },
      },
    },
  };

  public lineChartData: ChartData<'line'> = {
    labels: [],
    datasets: [],
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] && this.data) {
      this.updateChartData();
    }
  }

  private updateChartData(): void {
    if (!this.data?.series || !this.data.categories) {
      return;
    }

    this.lineChartData.labels = this.data.categories;

    this.lineChartData.datasets = this.data.series.map((dataset) => ({
      ...dataset,
      type: 'line',
      fill: false,
      borderWidth: 2,
      pointRadius: 4,
      pointBorderWidth: 1,
      pointBackgroundColor: dataset.borderColor,
      pointBorderColor: '#FFF',
      tension: 0,
    })) as ChartDataset<'line'>[];

    this.chart?.update();
  }
}
