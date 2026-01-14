import requests
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()
from datetime import datetime
from app.models import Theme, Indicateur, Pays, Donnee
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper
#import class User
from django.contrib.auth.models import User

CURRENT_YEAR = datetime.now().year - 1
START_YEAR = CURRENT_YEAR - 14
INDICATEURS = [
    {
        "code": "EG.ELC.ACCS.ZS",
        "nom": "Accès à l'électricité",
        "unite": "% de la population",
        "direction": "positive",
        "theme": "Infrastructures"
    },
    {
        "code": "IT.NET.USER.ZS",
        "nom": "Accès à l'internet",
        "unite": "% de la population",
        "direction": "positive",
        "theme": "Infrastructures"
    },
    {
        "code": "SE.XPD.TOTL.GD.ZS",
        "nom": "Dépense publique consacrée à l'éducation",
        "unite": "% PIB",
        "direction": "positive",
        "theme": "Éducation"
    },
    {
        "code": "SP.DYN.LE00.IN",
        "nom": "Espérance de vie à la naissance",
        "unite": "années",
        "direction": "positive",
        "theme": "Santé"
    },
    {
        "code": "SH.MLR.INCD.P3",
        "nom": "Indice du paludisme",
        "unite": "cas pour 1000 personnes",
        "direction": "negative",
        "theme": "Santé"
    },
    {
        "code": "SP.DYN.IMRT.IN",
        "nom": "Mortalité infantile",
        "unite": "pour 1000 naissances vivantes",
        "direction": "negative",
        "theme": "Santé"
    },
    {
        "code": "NY.GDP.PCAP.CD",
        "nom": "PIB par habitant",
        "unite": "USD",
        "direction": "positive",
        "theme": "Économie"
    },
    {
        "code": "SL.UEM.TOTL.ZS",
        "nom": "Taux de chômage total",
        "unite": "% de la population active",
        "direction": "negative",
        "theme": "Économie"
    },
    {
        "code": "SP.DYN.TFRT.IN",
        "nom": "Taux de fécondité",
        "unite": "enfants/femme",
        "direction": "negative",
        "theme": "Démographie"
    },
    {
        "code": "SP.POP.TOTL",
        "nom": "Population totale",
        "unite": "personnes",
        "direction": "positive",
        "theme": "Démographie"
    },
    {
        "code": "SH.XPD.CHEX.GD.ZS",
        "nom": "Dépenses de santé",
        "unite": "% PIB",
        "direction": "positive",
        "theme": "Santé"
    },
    {
        "code": "SE.PRM.ENRR",
        "nom": "Taux de scolarisation",
        "unite": "% de la population scolarisée",
        "direction": "positive",
        "theme": "Éducation"
    }
]

def import_themes():
    themes = {i["theme"] for i in INDICATEURS}
    for nom in themes:
        Theme.objects.get_or_create(nom=nom)
    print("----------Thèmes importés--------------")

def import_indicateurs():
    for i in INDICATEURS:
        theme = Theme.objects.get(nom=i["theme"])
        Indicateur.objects.get_or_create(
            id_indicateur=i["code"],
            defaults={
                "nom": i["nom"],
                "unite": i["unite"],
                "direction": i["direction"],
                "theme": theme,
                "levier": False
            }
        )
    print("✅ Indicateurs importés")

def import_donnees():
    BASE_URL = "http://api.worldbank.org/v2/country/{country}/indicator/{indicator}?date={START_YEAR}:{CURRENT_YEAR}&format=json"
    for indicateur in Indicateur.objects.all():
        print(f"Récupération des données pour l'indicateur {indicateur.nom}...")
        for pays in Pays.objects.all():
                url = BASE_URL.format(country=pays.code_iso, indicator=indicateur.id_indicateur, START_YEAR=START_YEAR, CURRENT_YEAR=CURRENT_YEAR)
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and isinstance(data[1], list):
                        for entry in data[1]:
                            annee = entry.get('date')
                            valeur = entry.get('value')
                            created = Donnee.objects.get_or_create(
                                indicateur=indicateur,
                                pays=pays,
                                annee=int(annee),
                                valeur=valeur
                                )
                            if created:
                                    print(f"  - Donnée ajoutée: {pays.code_iso} {annee} {valeur}")
                    else:
                        print(f"  - Pas de données pour {pays.code_iso}")
                else:
                    print(f"  - Erreur API pour {pays.code_iso}: {response.status_code}")

def importer_pays_africains():
    url = "https://api.worldbank.org/v2/country/?region=ssf&format=json"
    response = requests.get(url)

    if response.status_code != 200:
        print("Erreur lors de la récupération des pays :", response.status_code)
        return

    data = response.json()
    total = 0

    for country in data[1]:
        nom = country.get("name")
        code_iso = country.get("iso2Code")

        if nom and code_iso:
            # Vérifie s’il n’existe pas déjà
            obj, created = Pays.objects.get_or_create(
                code_iso=code_iso,
                defaults={"nom": nom}
            )
            if created:
                total += 1
                print(f"✅ {nom} ajouté ({code_iso})")
            else:
                print(f"⏩ {nom} déjà existant")

    print(f"\nImportation terminée : {total} nouveaux pays ajoutés.")


def cleaning_data():
    pays_avec_taux = (
    Pays.objects
    .annotate(
        total_donnees=Count('donnees'),
        donnees_non_nulles=Count('donnees', filter=Q(donnees__valeur__isnull=False))
    )
    .annotate(
        taux_completude=ExpressionWrapper(
            F('donnees_non_nulles') * 1.0 / F('total_donnees'),
            output_field=FloatField()
        )
    )
    .order_by('-taux_completude')[:20]  # Top 20
)

    id_a_garder = [pays.id for pays in pays_avec_taux]
    Pays.objects.exclude(id__in=id_a_garder).delete()

    for pays in pays_avec_taux:
        print(f"{pays.nom} ({pays.code_iso}) - Taux de complétude: {pays.taux_completude:.2%} ({pays.donnees_non_nulles}/{pays.total_donnees})")
        
if __name__ == "__main__":
    #import_themes()
    #import_indicateurs()
    #importer_pays_africains()
    #import_donnees()
    cleaning_data()
