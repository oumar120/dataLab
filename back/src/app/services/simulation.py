from pandas import DataFrame

from app.models import Donnee


def loadDataFromContry(country: str) -> DataFrame:
    queryset = Donnee.objects.filter(pays__code_iso=country)
    rows = queryset.values('annee', 'indicateur__nom', 'valeur')
    df = DataFrame.from_records(rows)
    if df.empty:
        return []
    df = df.pivot(index='annee', columns='indicateur__nom', values='valeur')
    df = df.sort_index()
    return df

def correlationMatrix(data: DataFrame) -> DataFrame:
    if data.empty:
        return DataFrame()
    corr_matrix = data.corr()
    return corr_matrix

def getImpactedIndicator(corr_matrix: DataFrame, indicateur_target:str,seuil:float):
    if indicateur_target not in corr_matrix.columns:
        return []
    impacted = [ind for ind, corr in corr_matrix[indicateur_target].items() if abs(corr) >= seuil and ind != indicateur_target]
    return sorted(impacted[:4])

def projectionImpact(df, corr_matrix, indicateur_target, scenarioPct, impactedIndicators):
    projections = []

    for indicator in impactedIndicators:
        # 1) Dernière valeur NON NULLE pour CET indicateur impacté
        series = df[indicator].dropna()
        if len(series) == 0:
            # aucune donnée → pas de projection possible
            projections[indicator] = {
                "correlation": float(corr_matrix.at[indicator, indicateur_target]),
                "impact_pct": None,
                "current_value": None,
                "projected_value_next_year": None,
            }
            continue

        current_value = series.iloc[-1]

        # 2) Corrélation entre indicateur cible et indicateur impacté
        corr_value = corr_matrix.at[indicator, indicateur_target]

        # 3) Impact en %
        impact_pct = scenarioPct * corr_value

        # 4) Projection pluriannuelle (1,3,5 ans)
        proj_1y = current_value * (1 + impact_pct / 100)
        proj_3y = current_value * (1 + impact_pct / 100 * 3)
        proj_5y = current_value * (1 + impact_pct / 100 * 5)

        projections.append({
            "name": indicator,
            "correlation": float(corr_value),
            "impact_pct": float(impact_pct),
            "current_value": float(current_value),
            'projected_1_year': float(proj_1y),
            'projected_3_years': float(proj_3y),
            'projected_5_years': float(proj_5y),
        })

    return projections


def simulation_insights(pays: str,indicateur_cible: str,scenario_pct: float):
    """
    Fonction clef appelée par la vue Django.
    
    Retourne un dictionnaire contenant :
    - données directes (croissance réelle, projection)
    - indicateurs impactés (choix user ou auto)
    - projections indirectes
    """

    df = loadDataFromContry(pays)

    if df.empty:
        return {"error": "Aucune donnée disponible pour ce pays."}

    if indicateur_cible not in df.columns:
        return {"error": f"L'indicateur {indicateur_cible} n'existe pas pour {pays}"}

    # MATRICE DE CORRÉLATION
    corr_matrix = correlationMatrix(df)

    # SÉLECTION DES INDICATEURS IMPACTÉS
    '''if user_impacted_indicators:  # si l'utilisateur a choisi
        impacted = user_impacted_indicators
    else:  # sinon automatique'''
    impacted = getImpactedIndicator(corr_matrix, indicateur_cible, seuil=0.6)

    # PROJECTIONS INDIRECTES
    indirect_projections = projectionImpact(
        df, corr_matrix, indicateur_cible, scenario_pct, impacted
    )

    # CROISSANCE DIRECTE
    serie = df[indicateur_cible].dropna()
    if len(serie) < 2:
        return {"error": f"Pas assez de données pour calculer la croissance de {indicateur_cible}."}
    last_value = serie.iloc[-1]
    prev_value = serie.iloc[-2]

    real_growth_last_year = (
        (last_value - prev_value) / prev_value * 100
        if prev_value != 0 else 0
    )

    direct_projection = {
        "current_value": float(last_value),
        "last_year_growth": float(real_growth_last_year),
        "scenario_pct": scenario_pct,
        "projected_1y": float(last_value * (1 + scenario_pct / 100)),
        "projected_3y": float(last_value * (1 + scenario_pct / 100 * 3)),
        "projected_5y": float(last_value * (1 + scenario_pct / 100 * 5)),
    }

    # STRUCTURE FINALE POUR L’IA
    return {
        "country": pays,
        "indicator_cible": indicateur_cible,
        "scenario_pct": scenario_pct,
        "direct_projection": direct_projection,
        "impacted_indicators": impacted,
        "indirect_projections": indirect_projections,
    }
   