import { JsonPipe, NgFor, NgIf } from '@angular/common';
import { Component, effect, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Data } from '../service/data.service';
import {
  NgApexchartsModule,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexStroke,
  ApexTitleSubtitle,
  ApexYAxis,
  ApexTooltip,
  ApexGrid,
  ApexPlotOptions,
  ApexFill
} from 'ng-apexcharts';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
  dataLabels: ApexDataLabels;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  tooltip: ApexTooltip;
  grid: ApexGrid;
  plotOptions: ApexPlotOptions;
  fill: ApexFill;
};
@Component({
  standalone: true,
  selector: 'app-indice',
  imports: [FormsModule,NgFor,NgIf,JsonPipe,NgApexchartsModule],
  templateUrl: './indice.html',
  styleUrl: './indice.scss',
})
export class Indice {
  public chartOptions!: Partial<ChartOptions>;
  data = inject(Data);
  indiceData = signal<any>({});
constructor() {
this.data.mode.set('indice');
effect(() => {
  this.indiceData.set(this.data.indiceData());
  if(this.indiceData() && Object.keys(this.indiceData()).length>0) {
    this.loadChart(this.indiceData().result);
  }
})
this.chartOptions = {
      chart: {
        type: 'bar',
        height: 400,
        width: '100%',
        toolbar: {
          show: true,
          
        },
        foreColor: '#e5e7eb', // texte gris clair (Tailwind slate-200)
      },
      plotOptions: {
        bar: {
          dataLabels: {
            position: 'top',
          },
        },
      },
      title: {
        text: '',
      },
      xaxis: {
        categories: [],
        axisBorder: {
          show: false,
        },
        axisTicks: {
          show: false,
        },
        tooltip: {
          enabled: true,
        },
      },
      yaxis: {
        labels: {
          formatter: (val) => (val ?? 0).toLocaleString(), // 25 300 000 000
        },
      },
      dataLabels: {
        enabled: false,
        formatter: (val) => (val ?? 0).toLocaleString(),
        offsetY: -10,
      },
      stroke: {
        curve: 'smooth',
        width: 3,
      },
      tooltip: {
        enabled: true,
        shared: false,
        intersect: true,
        theme: 'dark',
        y: {
          formatter: (val) => (val ?? 0).toLocaleString(),
        },
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'light',
          type: 'vertical',
          shadeIntensity: 0.25,
          inverseColors: true,
          opacityFrom: 0.85,
          opacityTo: 0.85,
          stops: [50, 0, 100],
        },
      },
      grid: {
        borderColor: '#1f2937', // gris foncé (bg-slate-800)
      },
    };
}
loadChart(indiceData: any) {
      const categories = Object.keys(indiceData.data);
      const data = categories.map((cat) => Number(indiceData.data[cat].indice));
      console.log(data);
      this.chartOptions = {
        ...this.chartOptions,
        series: [
          {
            name: 'Indice Composite',
            data: data,
          },
        ],
        xaxis: {
          ...this.chartOptions.xaxis,
          categories: categories,
        },
        yaxis: {
          ...this.chartOptions.yaxis,
          title: {
            text: "Valeur de l'indice",
          },
        },
      };
  }
}
