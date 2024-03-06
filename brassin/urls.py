from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('change_password/' , views.change_password, name='change_password'),
    path('', views.Home, name='home'),

    path('brassins/', views.BrassinsList, name="brassin_list"),
    path('brassins/<int:id>/', views.BrassinConsult, name='brassin_consult'),
    path('brassins/ajouter/', views.BrassinCreate.as_view(), name='brassin_create'),
    path('brassins/<int:pk>/editer/', views.BrassinUpdate.as_view(), name='brassin_update'),
    path('brassins/<int:pk>/supprimer/', views.BrassinDelete.as_view(), name='brassin_delete'),

    path('brassins/<int:id>/ajouter-ingredient/', views.BrassinIngredientAdd, name='brassin_ingredient_add'),
    path('brassins/<int:id>/auto-fill/', views.BrassinIngredientFill, name='brassin_ingredient_fill'),
    path('brassins/<int:b>/editer-ingredient/<int:pk>/', views.BrassinIngredientUpdate.as_view(), name='brassin_ingredient_update'),
    path('brassins/<int:b>/supprimer-ingredient/<int:pk>/', views.BrassinIngredientDelete.as_view(), name='brassin_ingredient_delete'),
    path('brassins/<int:id>/supprimer-ingredient-tous/', views.BrassinIngredientDeleteAll, name='brassin_ingredient_delete_all'),

    path('brassins/<int:id>/ajouter-produit/', views.BrassinProduitAdd, name='brassin_produit_add'),
    path('brassins/<int:b>/supprimer-produit/<int:pk>/', views.BrassinProduitDelete.as_view(), name='brassin_produit_delete'),

    path('brassins/<int:id>/ajouter-etape-chauffe/', views.BrassinEtapeChauffeAdd, name='brassin_etape_chauffe_add'),
    path('brassins/<int:b>/supprimer-etape-chauffe/<int:pk>/', views.BrassinEtapeChauffeDelete.as_view(), name='brassin_etape_chauffe_delete'),


    path('produits/ajouter/', views.ProduitCreate.as_view(), name='produit_create'),
    path('produits/<int:pk>/editer/', views.ProduitUpdate.as_view(), name='produit_update'),
    path('produits/<int:pk>/supprimer/', views.ProduitDelete, name='produit_delete'),

    path('fermenteurs/ajouter/', views.FermenteurCreate.as_view(), name='fermenteur_create'),
    path('fermenteurs/<int:pk>/editer/', views.FermenteurUpdate.as_view(), name='fermenteur_update'),
    path('fermenteurs/<int:pk>/supprimer/', views.FermenteurDelete.as_view(), name='fermenteur_delete'),

    path('notes/ajouter/', views.NoteCreate.as_view(), name='note_create'),
    path('notes/<int:pk>/editer/', views.NoteUpdate.as_view(), name='note_update'),
    path('notes/<int:pk>/supprimer/', views.NoteDelete.as_view(), name='note_delete'),

    path('recettes/', views.RecettesList.as_view(), name="recettes_list"),
    path('recettes/ajouter/', views.RecetteCreate.as_view(), name='recette_create'),
    path('recettes/<int:pk>/editer/', views.RecetteUpdate.as_view(), name='recette_update'),
    path('recettes/<int:pk>/supprimer/', views.RecetteDelete.as_view(), name='recette_delete'),

    path('recettes/<int:id>/', views.RecetteConsult, name='recette_consult'),
    path('recettes/<int:id>/ajouter-ingredient/', views.RecetteIngredientAdd, name='recette_ingredient_add'),
    path('recettes/<int:r>/editer-ingredient/<int:pk>/', views.RecetteIngredientUpdate.as_view(), name='recette_ingredient_update'),
    path('recettes/<int:r>/supprimer-ingredient/<int:pk>/', views.RecetteIngredientDelete.as_view(), name='recette_ingredient_delete'),


    path('ingredients/', views.IngredientsList.as_view(), name="ingredients_list"),
    path('ingredients/ajouter/', views.IngredientCreate.as_view(), name='ingredient_create'),
    path('ingredients/<int:pk>/editer/', views.IngredientUpdate.as_view(), name='ingredient_update'),
    path('ingredients/<int:pk>/supprimer/', views.IngredientDelete.as_view(), name='ingredient_delete'),
    path('ingredients/<int:id>/mise_a_jour_stock/', views.StockUpdate, name='ingredient_update_stock'),

    path('achats/', views.AchatsList.as_view(), name="achats_list"),
    path('achats/ajouter/', views.AchatCreate, name='achat_create'),
    path('achats/<int:pk>/editer/', views.AchatUpdate.as_view(), name='achat_update'),
    path('achats/<int:pk>/supprimer/', views.AchatDelete.as_view(), name='achat_delete'),

    path('ventes/', views.VentesList, name="ventes_list"),

    path('ventes/ajouter/', views.VenteCreate, name='vente_create'),
    path('ventes/ajouter/<int:bp>/', views.VenteCreate, name='vente_create'),
    path('ventes/<int:pk>/editer/', views.VenteUpdate.as_view(), name='vente_update'),
    path('ventes/<int:pk>/supprimer/', views.VenteDelete.as_view(), name='vente_delete'),
    path('ventes/<date_s>/<date_e>/', views.VentesList, name="ventes_list"),

    path('outils/<int:id>', views.Outils, name='outils'),
    path('outils/', views.Outils, name='outils'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
