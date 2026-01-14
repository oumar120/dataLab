
from app.models import Donnee


def somme_indice(normalize_values, weights):
    if not normalize_values or not weights:
        return None
    indice = 0
    for key in normalize_values:
        if key in weights and normalize_values[key] is not None:
            indice += normalize_values[key] * weights[key]
    return indice

def calculer_indice(value,min_val,max_val,direction):
    if value is None or min_val is None or max_val is None :
        return None
    if min_val==max_val:
        return 0.5
    normalize_value = (value - min_val) / (max_val - min_val)
    if direction == 'negative':
        normalize_value = 1 - normalize_value
    return max(0, min(1, normalize_value))

def normalize_weigth(weigths:dict):
    total = sum(weigths.values())
    if total == 0:
        raise ValueError("Total ne doit pas être zéro.")
    normalized_weights = {k: v / total for k, v in weigths.items()}
    return normalized_weights


def load_data_from_ind_pays_year(pays, indicateur, year):
    qs = Donnee.objects.filter(pays__code_iso__in=pays, indicateur__nom__in=indicateur, annee=year).select_related('indicateur')
    data = {}
    for row in qs:
        if row.valeur is not None:
            data[row.indicateur.nom] = row.valeur
    return data

def calcul_min_max(pays,indicateur,start_year=None,end_year=None,year=None):
    if start_year is None or end_year is None:
        qs = Donnee.objects.filter(pays__code_iso__in=pays, indicateur__nom__in=indicateur, annee=year,valeur__isnull=False)
    else:
        qs = Donnee.objects.filter(pays__code_iso__in=pays, indicateur__nom__in=indicateur, annee__gte=start_year, annee__lte=end_year,valeur__isnull=False)
    min_max = {}
    for ind in indicateur:
        values = [row.valeur for row in qs if row.indicateur.nom == ind and row.valeur is not None]
        if values:
            min_max[ind] = {'min': min(values), 'max': max(values)}
        else:
            min_max[ind] = {'min': None, 'max': None} 
    return min_max

def main(pays:list,indicateur:list,mode,start_year=None,end_year=None,year=None,weight:dict={}):
    data = {}
    if mode=="analyse":
        min_max = calcul_min_max(pays,indicateur,start_year,end_year)
        for year in range(start_year,end_year+1):
            data[year] = load_data_from_ind_pays_year(pays,indicateur,year)
            normalize_weigths = normalize_weigth(weight)
            normalize_values = {}
            for ind in indicateur:
                min = min_max[ind]['min']
                max = min_max[ind]['max']
                direction = 'positive'  # Par défaut
                normalize_values[ind] = calculer_indice(data[year].get(ind),min,max,direction)
            indice = somme_indice(normalize_values,normalize_weigths)
            data[year]['indice'] = indice
        return {'pays': pays[0], 'data': data}
    elif mode=="comparaison":
        for p in pays:
            data[p] = load_data_from_ind_pays_year([p],indicateur,year)
            min_max = calcul_min_max(pays,indicateur,year=year)
            normalize_weigths = normalize_weigth(weight)
            print(data)
            normalize_values = {}
            for ind in indicateur:
                min = min_max[ind]['min']
                max = min_max[ind]['max']
                direction = 'positive'  # Par défaut
                normalize_values[ind] = calculer_indice(data[p].get(ind),min,max,direction)
            indice = somme_indice(normalize_values,normalize_weigths)
            data[p]['indice'] = indice
        return {'pays': pays, 'data': data}