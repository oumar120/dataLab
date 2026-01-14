from rest_framework.serializers import ModelSerializer

from app.models import Donnee, Pays,Indicateur

class PaysSerializer(ModelSerializer):
    class Meta:
        model = Pays
        fields = ['nom', 'code_iso']

class IndicateurSerializer(ModelSerializer):
    class Meta:
        model = Indicateur
        fields = ['nom','id_indicateur', 'unite','levier']
class DataSerializer(ModelSerializer):
    pays = PaysSerializer(read_only=True)
    indicateur = IndicateurSerializer(read_only=True)
    class Meta:
        model = Donnee
        fields = '__all__'      