import { Indicateur } from './../model/data.model';

import { KeyValuePipe, NgFor, NgIf, SlicePipe } from '@angular/common';
import { Component, computed, effect, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Data } from '../service/data.service';

@Component({
  selector: 'app-header',
  imports: [FormsModule,FormsModule, NgFor, NgIf,KeyValuePipe],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header  {
data = inject(Data)
readonly pays = computed(() => this.data.pays());
readonly indicateurs = computed(() => {
  if(this.data.mode() === 'simulateur') {
    return this.data.indicateurs().filter(ind => ind.levier === true);
  }
  return this.data.indicateurs();
});
readonly years = computed(() => this.data.years());

constructor() {
    effect(() => {
      const Indicateur = this.indicateurs;
      const selected = this.data.selectedIndicator();
      if (selected && !Indicateur().some(ind => ind.id_indicateur === selected.id_indicateur)) {
        this.data.selectedIndicator.set(Indicateur()[0]);
      }
      if (this.data.mode() !== 'indice') {
        this.data.selectedCountry.set(this.pays()[0]);
      }
      if(this.data.selectedManyCountry().length>1) {
          this.data.yearEndSelected.set(null as any);
      } else {
        this.data.yearEndSelected.set(2024);
      }
    });
}
onToggle(indicatorName: string, event: any) {
  const value = event.target.value;
  this.data.weightIndicator.update((currentWeights) => {
    return {
      ...currentWeights,
      [indicatorName]: Number(value)
    };
  });
}

onCountryChange(selectedCodes: string[]) {
  this.data.selectedManyCountry.set(selectedCodes);
}
onCreate() {
  const indicateur_nom = Object.keys(this.data.weightIndicator());
  const indicateur_weight = this.data.weightIndicator();
  const year_start = Number(this.data.yearStartSelected());
  const year_end = Number(this.data.yearEndSelected());
  const countries = this.data.selectedManyCountry();
  if(year_end === null) {
    this.data.getIndice(countries, indicateur_nom, year_start, undefined, indicateur_weight).subscribe((res: any) => {
      this.data.indiceData.set(res);
    });
  } else {
    this.data.getIndice(countries, indicateur_nom, year_start, year_end, indicateur_weight).subscribe((res: any) => {
      this.data.indiceData.set(res);
    });
  }
}
}
