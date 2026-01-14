from django.shortcuts import render
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from app.models import Donnee, Indicateur, Pays
from app.serializer import DataSerializer, IndicateurSerializer, PaysSerializer
from app.services.simulation import simulation_insights
from app.services.narration import generate_narration
from app.services.indice import main


class DataViewSet(ReadOnlyModelViewSet):
    queryset = Donnee.objects.all()
    serializer_class = DataSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        pays = self.request.query_params.get('pays')
        indicateur = self.request.query_params.get('indicateur')
        start_year = self.request.query_params.get('start_year')
        end_year = self.request.query_params.get('end_year')
        if pays:
            queryset = queryset.filter(pays__code_iso=pays)
        if indicateur:
            queryset = queryset.filter(indicateur__id_indicateur=indicateur)
        if start_year and end_year:
            queryset = queryset.filter(annee__gte=start_year, annee__lte=end_year)
        return queryset
class PaysViewSet(ReadOnlyModelViewSet):
    queryset = Pays.objects.all()
    serializer_class = PaysSerializer
class IndicateurViewSet(ReadOnlyModelViewSet):
    queryset = Indicateur.objects.all()
    serializer_class = IndicateurSerializer

@api_view(['GET'])
def similation_and_narration(request):
    print(request.GET.get('pays'), request.GET.get('i_cible'), request.GET.get('scenario_pct'))
    simulation_result = simulation_insights(request.GET.get('pays'), request.GET.get('i_cible'), float(request.GET.get('scenario_pct')))
    narration = generate_narration(simulation_result)
    return Response({"narration": narration ,"simulation": simulation_result})

@api_view(['POST'])
def indice(request):
    data = request.data
    pays = data.get('pays', [])
    indicateur = data.get('indicateur', [])
    start_year = data.get('start_year')
    end_year = data.get('end_year')
    weight = data.get('weight', {})
    result = []
    if len(pays) == 1:
        mode = "analyse"
        if not start_year or not end_year:
            return Response({"error": "start_year et end_year sont requis pour l'analyse d'un seul pays."}, status=400)
        result = main(pays, indicateur, mode, start_year=start_year, end_year=end_year, weight=weight)
    elif len(pays) > 1:
        mode = "comparaison"
        if not start_year:
            return Response({"error": "year est requis pour la comparaison entre plusieurs pays."}, status=400)
        result = main(pays, indicateur, mode, year=start_year, weight=weight)
    else:
        return Response({"error": "Au moins un pays doit être spécifié."}, status=400)
    narration = generate_narration(result)
    return Response({"result": result, "narration": narration})
    