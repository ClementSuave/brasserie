from django.contrib import admin

# Register your models here.
from .models import Profile, Fermenteur, Produit, Ingredient, Recette, Note, Brassin, BrassinEtapeChauffe, BrassinProduit, BrassinIngredient, RecetteIngredient, Achat, Vente

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Fermenteur)
class FermenteurAdmin(admin.ModelAdmin):
    pass

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    pass

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass

@admin.register(Brassin)
class BrassinAdmin(admin.ModelAdmin):
    pass

@admin.register(BrassinEtapeChauffe)
class BrassinEtapeChauffeAdmin(admin.ModelAdmin):
    pass

@admin.register(BrassinProduit)
class BrassinProduitAdmin(admin.ModelAdmin):
    pass

@admin.register(BrassinIngredient)
class BrassinIngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(RecetteIngredient)
class RecetteIngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    pass

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    pass