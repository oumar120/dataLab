
export interface Pays{
    nom: string;
    code_iso: string;
}
export interface Indicateur{
    id_indicateur: string;
    nom: string;
    unite: string;
    levier: boolean;
}
export interface Donnee{
    pays: Pays;
    indicateur: Indicateur;
    annee: number;
    valeur: number;
}