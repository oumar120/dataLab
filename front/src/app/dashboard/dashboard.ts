
import { DecimalPipe } from '@angular/common';
import { Component, computed, effect, inject, signal } from '@angular/core';
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
  ApexGrid
} from 'ng-apexcharts';
import { Data } from '../service/data.service';
import { Indicateur, Pays } from '../model/data.model';
import { forkJoin } from 'rxjs';

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
};
@Component({
  standalone: true,
  selector: 'app-dashboard',
  imports: [NgApexchartsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  public chartOptions!: Partial<ChartOptions>;
  data = inject(Data);
  selectedCountry = computed(() => this.data.selectedCountry());
  selectedIndicator = computed(() => this.data.selectedIndicator());
  yearStartSelected = computed(() => this.data.yearStartSelected());
  yearEndSelected = computed(() => this.data.yearEndSelected());

  constructor() {
      this.data.mode.set('dashboard');
      this.data.yearStartSelected.set(2010);
      this.data.yearEndSelected.set(2024);
      effect(() => {
        this.loadChart(this.selectedCountry()?.code_iso, this.selectedIndicator()?.id_indicateur ?? '' , this.yearStartSelected(), this.yearEndSelected());
    // On initialise le graphique ici
      });
    this.chartOptions = {
      chart: {
        type: 'line',
        height: 400,
        width: '100%',
        toolbar: {
          show: true,
        },
        foreColor: '#e5e7eb', // texte gris clair (Tailwind slate-200)
      },
      title: {
        text: '',
      },
      xaxis: {
        categories: [],
        axisBorder: {
          show: false,
        },
      },
      yaxis: {
        labels: {
          formatter: (val) => val.toLocaleString(), // 25 300 000 000
        },
      },
      dataLabels: {
        enabled: false,
      },
      stroke: {
        curve: 'smooth',
        width: 3,
      },
      tooltip: {
        theme: 'dark',
        y: {
          formatter: (val) => val.toLocaleString() ,
        },
      },
      grid: {
        borderColor: '#1f2937', // gris foncé (bg-slate-800)
      },
    };
  }
loadChart(c:string,i:string, start_year: number, end_year: number) {
    this.data.getDonneesParPaysEtIndicateur(c, i, start_year, end_year).subscribe((donnees) => {
      const categories = donnees.map(d => d.annee);
      const data = donnees.map(d => d.valeur);
      this.chartOptions = {
        ...this.chartOptions,
        series: [
          {
            name: 'Valeur',
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
            text: this.selectedIndicator()?.unite || "Millions d'habitants",
          },
        },
      };
    });
  }
}
