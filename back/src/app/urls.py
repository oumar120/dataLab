from django.db import router
from django.urls import path
from rest_framework.routers import DefaultRouter


from app.views import DataViewSet, IndicateurViewSet, PaysViewSet, indice, similation_and_narration

router = DefaultRouter()
router.register(r'donnees', DataViewSet)
router.register(r'pays', PaysViewSet)
router.register(r'indicateurs', IndicateurViewSet)

urlpatterns = [
    path('simulation/', similation_and_narration),
    path('indice/',  indice),
]

urlpatterns += router.urls
