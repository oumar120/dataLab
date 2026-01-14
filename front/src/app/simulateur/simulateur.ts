import { Component, computed, effect, inject, OnInit, signal } from '@angular/core';
import { DecimalPipe, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Data } from '../service/data.service';
import { Indicateur, Pays } from '../model/data.model';
import { forkJoin, generate } from 'rxjs';
import { jsPDFAPI,jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

@Component({
  standalone: true,
  selector: 'app-simulateur',
  imports: [DecimalPipe,FormsModule,NgFor,NgIf],
  templateUrl: './simulateur.html',
  styleUrl: './simulateur.scss',
})
export class Simulateur  {
  
  selectedIndicator = computed(() => this.data.selectedIndicator());
  selectedCountry = computed(() => this.data.selectedCountry());
  data = inject(Data)
  SNData = signal<any>({});
  
  ProjectionValue = signal(0);
  projection1Year = signal(1.1);
  projection3Year = signal(1.3);
  projection5Year = signal(1.5);

  constructor() {
    this.data.mode.set('simulateur');
  }

runPrt() {
  const baseValue = this.ProjectionValue()/100;
  this.projection1Year.set(baseValue * 1);
  this.projection3Year.set(1 + baseValue * 3);
  this.projection5Year.set(1 + baseValue * 5);
  this.data.getSimulationNarration(
    this.selectedCountry()?.code_iso || '',
    this.selectedIndicator()?.nom || '',
    this.ProjectionValue()
  ).subscribe((res:any) => {
    this.SNData.set(res);
    console.log(this.SNData());
  });
}
generatePDF() {
  const doc = new jsPDF();

  let y = 10; // position verticale

  // ----- TITRE -----
  doc.setFontSize(16);
  doc.text('Rapport de simulation socio-économique', 10, y);
  y += 10;

  // ----- META -----
  doc.setFontSize(11);
  doc.text(`Pays : ${this.SNData().simulation.country}`, 10, y); y += 6;
  doc.text(`Indicateur cible : ${this.SNData().simulation.indicator_cible}`, 10, y); y += 6;
  doc.text(`Scénario appliqué : ${this.SNData().simulation.scenario_pct}%`, 10, y); y += 10;

  // ----- PROJECTION DIRECTE -----
  doc.setFontSize(13);
  doc.text('Projection directe', 10, y);
  y += 8;

  doc.setFontSize(11);
  doc.text(`Valeur actuelle : ${this.SNData().simulation.direct_projection.current_value}`, 10, y); y += 6;
  doc.text(`Croissance dernière année : ${this.SNData().simulation.direct_projection.last_year_growth.toFixed(2)}%`, 10, y); y += 6;
  doc.text(`Projection à 1 an : ${this.SNData().simulation.direct_projection.projected_1y}`, 10, y); y += 6;
  doc.text(`Projection à 3 ans : ${this.SNData().simulation.direct_projection.projected_3y}`, 10, y); y += 6;
  doc.text(`Projection à 5 ans : ${this.SNData().simulation.direct_projection.projected_5y}`, 10, y); y += 10;
  // ----- NARRATION IA -----
  doc.setFontSize(13);
  doc.text('Analyse interprétée par l’IA', 10, y);
  y += 8;

  doc.setFontSize(12);
  const narrationLines = doc.splitTextToSize(this.SNData().narration, 180);
  doc.text(narrationLines, 10, y);

  // ----- TABLEAU DES INDICATEURS IMPACTÉS -----
doc.addPage();

doc.setFontSize(14);
doc.text('Indicateurs indirectement impactés', 10, 10);

// Préparation des colonnes
const head = [[
  'Indicateur',
  'Corrélation',
  'Impact (%)',
  'Valeur actuelle',
  'Proj. 1 an',
  'Proj. 3 ans',
  'Proj. 5 ans'
]];

// Préparation des lignes
const body = this.SNData().simulation.indirect_projections.map((ind: any) => [
  ind.name,
  ind.correlation.toFixed(2),
  ind.impact_pct.toFixed(2),
  ind.current_value.toFixed(2),
  ind.projected_1_year.toFixed(2),
  ind.projected_3_years.toFixed(2),
  ind.projected_5_years.toFixed(2),
]);

autoTable(doc, {
  head,
  body,
  startY: 20,
  styles: {
    fontSize: 12,
    cellPadding: 2
  },
  headStyles: {
    fillColor: [30, 64, 175], // bleu sobre
    textColor: 255
  },
  alternateRowStyles: {
    fillColor: [245, 247, 250]
  }
});


  // ----- SAVE -----
  doc.save('rapport_simulation.pdf');
}
}