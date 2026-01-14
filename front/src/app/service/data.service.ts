import { effect, inject, Injectable, signal } from '@angular/core';
import { environment } from '../environments/environment';
import { forkJoin, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Donnee, Indicateur, Pays } from '../model/data.model';

@Injectable({
  providedIn: 'root',
})
export class Data {
  private API_URL = environment.apiUrl;
  http = inject(HttpClient);
  selectedCountry = signal<Pays>(null as any);
  selectedIndicator = signal<Indicateur>(null as any);
  yearStartSelected = signal<number>(2010);
  yearEndSelected = signal<number>(2024);
  years = signal<number[]>([]);
  indicateurs = signal<Indicateur[]>([]);
  pays = signal<Pays[]>([]);
  mode = signal<string>('dashboard');
  selectedManyCountry = signal<string[]>([]);
  weightIndicator = signal<{[key: string]: number}>({
    "Accès à l'électricité": 25,
    "Accès à l'internet": 25,
    "Dépense publique consacrée à l'éducation": 25,
    "PIB par habitant": 25
  });
  indiceData = signal<any>({});
  constructor() {
     forkJoin({
    pays: this.getPays(),
    indicateurs: this.getIndicateurs()
  }).subscribe((result:any) => {
    this.pays.set(result.pays);
    this.indicateurs.set(result.indicateurs);
  })
    effect(() => {
    if (this.pays().length>0 && (!this.selectedCountry() || !this.selectedIndicator()) && this.mode() !== 'indice') {
      this.selectedCountry.set(this.pays()[0]);
      this.selectedIndicator.set(this.indicateurs()[0]);
      this.getDonneesParPaysEtIndicateur(this.selectedCountry()?.code_iso || '', this.selectedIndicator()?.id_indicateur || '').subscribe((donnees) => {
      this.years.set(donnees.map(d => d.annee));
      });
    }
    });
  }










  getPays(): Observable<Pays> {
    return this.http.get<Pays>(`${this.API_URL}/pays/`);
  }
  getIndicateurs(): Observable<Indicateur> {
    return this.http.get<Indicateur>(`${this.API_URL}/indicateurs/`);
  }
  getDonnees(): Observable<Donnee[]> {
    return this.http.get<Donnee[]>(`${this.API_URL}/donnees/`);
  }
  getDonneesParPays(code_iso: string): Observable<Donnee[]> {
    return this.http.get<Donnee[]>(`${this.API_URL}/donnees/pays/${code_iso}`);
  }
  getDonneesParIndicateur(id_indicateur: string): Observable<Donnee[]> {
    return this.http.get<Donnee[]>(`${this.API_URL}/donnees/indicateur/${id_indicateur}`);
  }
  getDonneesParPaysEtIndicateur(code_iso?: string, id_indicateur?: string, start_year?: number, end_year?: number): Observable<Donnee[]> {
    return this.http.get<Donnee[]>(`${this.API_URL}/donnees/?pays=${code_iso}&indicateur=${id_indicateur}&start_year=${start_year || ''}&end_year=${end_year || ''}`);
  }
  getSimulationNarration(pays: string, i_cible: string, scenario_pct: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/simulation/?pays=${pays}&i_cible=${i_cible}&scenario_pct=${scenario_pct}`);
  }
  getIndice(pays: string[], indicateur: string[], start_year?: number, end_year?: number, weight?: {[key: string]: number}): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/indice/`, {
      pays: pays,
      indicateur: indicateur,
      start_year: start_year,
      end_year: end_year,
      weight: weight
    });
  }
}