import os
import django
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()
from app.models import Theme, Indicateur, Pays, Donnee

from django.db.models import Count, Q, F, FloatField, ExpressionWrapper
from app.services.indice import main 

pays = ['SN']
indicateur = ["Accès à l'électricité", "Accès à l'internet", "Dépense publique consacrée à l'éducation"]
start_year = 2010
end_year = 2015
year = 2020

w = {
    "Accès à l'électricité": 25,
    "Accès à l'internet": 25,
    "Dépense publique consacrée à l'éducation": 25,
    "PIB par habitant": 25
}
re = main(pays, indicateur, 'analyse', start_year=start_year, end_year=end_year, weight=w)
print(re)

# Annoter chaque pays avec :
# - total_donnees : nombre total de lignes associées
# - donnees_non_nulles : nombre de valeurs non nulles
# - taux_completude : ratio entre les deux
#Indicateur.objects.get(pk=5).delete()
'''pays_avec_taux = (
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
Pays.objects.exclude(id__in=id_a_garder).delete()'''

'''for pays in pays_avec_taux:
    print(f"{pays.nom} ({pays.code_iso}) - Taux de complétude: {pays.taux_completude:.2%} ({pays.donnees_non_nulles}/{pays.total_donnees})")'''


'''for pays in Pays.objects.all():
    print(pays)
    for indicateur in Indicateur.objects.filter(donnees__pays=pays).distinct():
        print(f"  {indicateur.nom}")
        donnees = Donnee.objects.filter(pays=pays, indicateur=indicateur).order_by('annee')
        for donnee in donnees:
            print(f"    {donnee.annee}: {donnee.valeur}")
    print("---------------------------------")'''