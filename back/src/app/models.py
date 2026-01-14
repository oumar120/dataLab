from django.db import models

class Theme(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Indicateur(models.Model):
    id_indicateur = models.CharField(max_length=50, unique=True)  # ex: SP.POP.TOTL
    nom = models.CharField(max_length=150)
    unite = models.CharField(max_length=50, blank=True, null=True)  # ex: personnes, pourcentage
    levier = models.BooleanField(default=False)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="indicateurs")
    direction = models.CharField(max_length=10, choices=[('positive', 'positive'), ('negative', 'negative')], default='positive')

    def __str__(self):
        return f"{self.nom} ({self.unite})" if self.unite else self.nom


class Pays(models.Model):
    nom = models.CharField(max_length=100)
    code_iso = models.CharField(max_length=3, unique=True)  # ex: SEN, CIV, GHA

    def __str__(self):
        return self.nom


class Donnee(models.Model):
    indicateur = models.ForeignKey(Indicateur, on_delete=models.CASCADE, related_name="donnees")
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name="donnees")
    annee = models.PositiveIntegerField()
    valeur = models.FloatField(null=True)

    class Meta:
        unique_together = ("indicateur", "pays", "annee")  # éviter doublons

    def __str__(self):
        return f"{self.indicateur.nom} - {self.pays.nom} ({self.annee}): {self.valeur}"
