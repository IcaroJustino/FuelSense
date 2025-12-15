import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartOptions, ChartType } from 'chart.js';
import { PieChartInputData } from '../../interfaces/auth.interfaces';

@Component({
  selector: 'app-pie-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './pie-chart.component.html',
  styleUrls: [],
})
export class PieChartComponent implements OnInit, OnChanges {
  @Input({ required: true }) data!: PieChartInputData;
  @Input() height: number = 300;
  public pieChartType: 'pie' = 'pie';

  public pieChartData: { labels: string[]; datasets: any[] } = {
    labels: [],
    datasets: [],
  };

  public pieChartOptions: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: {
            size: 10,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            let label = context.label || '';

            if (label) {
              label += ': ';
            }

            if (context.parsed) {
              const total = context.dataset.data.reduce((a, b) => (a as number) + (b as number), 0);
              const currentValue = context.parsed;
              const percentage = ((currentValue / total) * 100).toFixed(2);
              const formattedVolume = currentValue.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              });

              return `${label} ${formattedVolume} L (${percentage}%)`;
            }
            return label;
          },
          afterLabel: () => {
            return '';
          },
        },
      },
    },
  };

  ngOnInit(): void {
    this.updateChartData();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] && this.data) {
      this.updateChartData();
    }
  }

  private updateChartData(): void {
    if (!this.data) return;

    this.pieChartData = {
      labels: this.data.labels,
      datasets: [
        {
          data: this.data.data,
          backgroundColor: this.data.backgroundColor,
          hoverBackgroundColor: this.data.backgroundColor.map((color) => color + 'b3'),
          borderWidth: 1,
        },
      ],
    };
  }
}
