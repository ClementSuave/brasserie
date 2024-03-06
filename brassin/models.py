from django.db import models
from django.db.models import Sum
from decimal import *
from math import exp, expm1
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	brasserie = models.CharField(max_length=100)
	logo = models.ImageField(upload_to ='logos',blank=True,null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Fermenteur(models.Model):
    numero = models.CharField(blank=True,null=True,max_length=30)
    volume = models.DecimalField(max_digits=5, decimal_places=1)
    marque = models.CharField(null=True,blank=True,max_length=30)
    diametre = models.DecimalField(blank=True,null=True,max_digits=5, decimal_places=1)
    notes = models.TextField(blank=True,null=True)

    def __str__(self):
        if self.dispo:
            return "Cuve " + str(self.volume) + "L - (" + str(self.marque) + ")"
        else:
            return "Cuve " + str(self.volume) + "L - (" + str(self.marque) + ") /!\ PLEIN: " + str(self.filled_with)

    @property
    def filled_with(self):
        brassin_f = Brassin.objects.filter(fermenteur=self.id,date_mise_bouteille__isnull=True,archive=False).first()
        if brassin_f is None:
            return "Vide"
        else:
            return str(brassin_f)

    @property
    def dispo(self):
        if self.filled_with == "Vide":
            return True
        return False

class Produit(models.Model):
    PRODUIT_TYPE = [('Bouteille','Bouteille'),('Canette','Canette'),('Fut','Fut'),('Autre','Autre')]
    type_produit = models.CharField(null=True,max_length=30,choices=PRODUIT_TYPE,default='Bouteille')
    contenance = models.DecimalField(max_digits=6, decimal_places=2)
    prix = models.DecimalField(null=True, blank= True,max_digits=6,decimal_places=2)

    def __str__(self):
        return str(self.type_produit) + " (" + str(self.contenance) + " L)"

class Ingredient(models.Model):
	INGREDIENT_TYPE = [('Malt','Malt'),('Houblon','Houblon'),('Levure','Levure'),('Autre','Autre'),]
	type_ingredient = models.CharField(null=True,max_length=30,choices=INGREDIENT_TYPE,default='Autre')
	variete = models.CharField(max_length=30)
	prix_kg = models.DecimalField(null=True, max_digits=5, decimal_places=2)
	acide_alpha = models.DecimalField(blank=True,null=True, max_digits=3, decimal_places=1)
	ebc_min = models.DecimalField(blank=True,null=True, max_digits=4, decimal_places=0)
	ebc_max = models.DecimalField(blank=True,null=True, max_digits=4, decimal_places=0)
	attenuation_min = models.DecimalField(blank=True,null=True, max_digits=2, decimal_places=0)
	attenuation_max = models.DecimalField(blank=True,null=True, max_digits=2, decimal_places=0)
	description = models.TextField(blank=True,null=True)

	@property
	def stock(self):
		achat_sum = Achat.objects.filter(ingredient=self.id).aggregate(Sum('quantite')).get('quantite__sum',0.00) if Achat else 0.00
		brassin_sum = BrassinIngredient.objects.filter(ingredient=self.id).aggregate(Sum('quantite')).get('quantite__sum',0.00) if BrassinIngredient else 0.00
		if not achat_sum:
			return brassin_sum
		if not brassin_sum:
			return achat_sum
		return achat_sum - brassin_sum

	@property
	def stock_last_update(self):
	    last_update = Achat.objects.filter(ingredient=self.id,type_achat='MAJ').last()
	    if last_update is None:
	        return 'pas de mise à jour de stock'
	    else:
	        return last_update.date_achat

	@property
	def unite(self):
	    if self.type_ingredient=="Malt":
	        return "%"
	    else:
	        return "g/L"

	@property
	def ebc(self):
	    if not self.ebc_min and not self.ebc_max:
	        return 0
	    elif not self.ebc_min or not self.ebc_max:
	        return
	    else:
	        return (self.ebc_min + self.ebc_max)/2

	@property
	def attenuation(self):
		if not self.attenuation_min or not self.attenuation_max:
			return
		return (self.attenuation_min + self.attenuation_max)/2

	@property
	def propriete(self):
		if self.type_ingredient=="Malt":
			return str((self.ebc_min+self.ebc_max)/2)
		if self.type_ingredient=="Houblon":
			return str(self.acide_alpha) + " %"
		if self.type_ingredient=="Levure":
			return str(self.attenuation_min) + " - " + str(self.attenuation_max) + " %"
		else:
			return ""

	class Meta:
		verbose_name = "Ingredient"
		ordering = ['type_ingredient']

	def __str__(self):
		return self.type_ingredient + " - " + self.variete

class Recette(models.Model):
	nom = models.CharField(max_length=30)
	type_biere = models.CharField(blank=True,null=True,max_length=30)
	densite_desire = models.DecimalField(blank=True,null=True, max_digits=4, decimal_places=3)
	taux_empatage =  models.DecimalField(max_digits=4, decimal_places=3,default=0.3)
	resucrage = models.DecimalField(blank=True,null=True, max_digits=3, decimal_places=1,default=7)
	notes = models.TextField(blank=True,null=True)
	etiquette = models.ImageField(upload_to = 'recettes',blank=True,null=True)

	@property
	def nombre_brassin(self):
		return Brassin.objects.filter(recette=self.id).count()

	class Meta:
		verbose_name = "Recette"
		ordering = ['id']

	def __str__(self):
		return self.nom

class Note(models.Model):
    date = models.DateField(null=True)
    titre = models.CharField(null=True, blank= True,max_length=30)
    texte = models.TextField(blank=False,null=False)
    auteur = models.CharField(null=True, blank= True,max_length=30)

    class Meta:
        verbose_name = "Notes"
        ordering = ['-date']

class Brassin(models.Model):
	date_brassin = models.DateField(null=True)
	numero = models.CharField(blank=True,null=True,max_length=30)
	date_mise_bouteille = models.DateField(blank=True,null=True)
	densite_avant_ebullition = models.DecimalField(blank=True,null=True, max_digits=4, decimal_places=3)
	densite_initiale = models.DecimalField(blank=True,null=True, max_digits=4, decimal_places=3)
	densite_finale = models.DecimalField(blank=True,null=True, max_digits=4, decimal_places=3)
	volume_empatage = models.DecimalField(blank=True,null=True, max_digits=5, decimal_places=1)
	volume_rincage_dreches = models.DecimalField(blank=True,null=True, max_digits=5, decimal_places=1)
	volume_mout = models.DecimalField(blank=True,null=True, max_digits=5, decimal_places=1)
	volume_cuve_fermentation = models.DecimalField(blank=True,null=True, max_digits=5, decimal_places=1)
	volume_starter = models.DecimalField(blank=True,null=True, max_digits=5, decimal_places=1,default=0)
	temps_empatage = models.TimeField(blank=True,null=True,default="01:15:00")
	temps_ebullition = models.TimeField(blank=True,null=True,default="01:30:00")
	temps_fermentation = models.TimeField(blank=True,null=True)
	notes = models.TextField(blank=True,null=True)
	resucrage = models.DecimalField(blank=True,null=True, max_digits=2, decimal_places=1)

	ingredient = models.ManyToManyField(Ingredient, through='BrassinIngredient',null=True,blank=True)
	recette = models.ForeignKey(Recette, on_delete=models.SET_NULL, null=True,blank=True)
	fermenteur = models.ForeignKey(Fermenteur, on_delete=models.SET_NULL, null=True,blank=True)

	archive = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Brassin"
		ordering = ['-date_brassin']

	def __str__(self):
	    if not self.recette:
	        return str(self.numero) + ": Sans recette (" + str(self.date_brassin) + ")"
	    return str(self.numero) + ": " + str(self.recette.nom) + " (" + str(self.date_brassin) + ")"

	@property
	def densite_initialeP(self):
		if not self.densite_initiale:
			return
		return ((Decimal(258.6)*(self.densite_initiale-1))/(Decimal(0.88)*self.densite_initiale+Decimal(0.12)));


	@property
	def densite_finaleP(self):
		if not self.densite_finale:
			return
		return ((Decimal(258.6)*(self.densite_finale-1))/(Decimal(0.88)*self.densite_finale+Decimal(0.12)));


	@property
	def densite_avant_ebullitionP(self):
		if not self.densite_avant_ebullition:
			return
		return ((Decimal(258.6)*(self.densite_avant_ebullition-1))/(Decimal(0.88)*self.densite_avant_ebullition+Decimal(0.12)));

	@property
	def malt_kg_total(self):
		return BrassinIngredient.objects.filter(brassin=self.id).filter(ingredient__type_ingredient="Malt").aggregate(Sum('quantite')).get('quantite__sum',0.00) if BrassinIngredient else 0

	@property
	def cout_brassin(self):
		ings_achetes=BrassinIngredient.objects.filter(brassin=self.id).filter(achete=True)
		cout_brassin=0
		if ings_achetes.exists():
			for ing in ings_achetes:
			    cout_brassin += ing.ingredient.prix_kg*ing.quantite
		if not self.volume_cuve_fermentation:
			return
		return cout_brassin/self.volume_cuve_fermentation

	@property
	def attenuation(self):
		if not self.densite_initiale or not self.densite_finale:
			return
		return (self.densite_initiale-self.densite_finale)/(self.densite_initiale-1)*100

	@property
	def rendement(self):
		if not self.volume_mout or not self.densite_initiale or not self.densite_finale or not self.malt_kg_total:
			return
		return (self.volume_mout*self.densite_initiale)*(259-259/self.densite_initiale)/self.malt_kg_total

	@property
	def calories(self):
		if not self.densite_initiale or not self.densite_finale:
			return
		return (Decimal(9862.42)*self.densite_finale*(Decimal(0.1808)*self.densite_initiale+Decimal(0.8192)*self.densite_finale-Decimal(1.0004))) + (Decimal(5300.9)*self.densite_finale*(self.densite_initiale-self.densite_finale)/(Decimal(1.775)-self.densite_initiale))

	@property
	def taux_alcool(self):
		if not self.densite_initiale or not self.densite_finale:
			return
		return (self.densite_initiale-self.densite_finale)*Decimal(133.333)

	@property
	def IBU(self):
		Houblons_brassin=BrassinIngredient.objects.filter(brassin=self).filter(ingredient__type_ingredient="Houblon")
		IBU=0
		utilisation=0
		cdensite=0
		if Houblons_brassin.exists() and self.densite_initiale and self.volume_mout:
			for houblon in Houblons_brassin:
				t=str(houblon.temps_infusion).split(':')
				t_min= int(t[0])*60+int(t[1])*1 +int(t[2])/60
				if t_min:
				    utilisation=Decimal(1.65)*Decimal(0.000125)**(self.densite_initiale-Decimal(1.00))*(Decimal(1.0)-Decimal(exp(Decimal(-0.04)*Decimal(t_min))))/Decimal(4.15)
				else:
				    utilisation= 0
				if self.densite_initiale>1.05:
					cdensite= 1+(self.densite_initiale-Decimal(1.05))/Decimal(0.2)
				else: cdensite=1
				IBU += houblon.quantite*1000*utilisation*houblon.ingredient.acide_alpha*10/(Decimal(self.volume_mout)*cdensite)
		return IBU

	@property
	def EBC(self):
		Malts_brassin = BrassinIngredient.objects.filter(brassin=self.id).filter(ingredient__type_ingredient="Malt")
		MCU =0
		if Malts_brassin.exists() and self.volume_mout and self.volume_mout != 0:
			    for malt in Malts_brassin:
				    MCU += Decimal(4.23)*malt.quantite*malt.ingredient.ebc/self.volume_mout
		return Decimal(2.939)*MCU**Decimal(0.6859)

class BrassinEtapeChauffe(models.Model):
    numero = models.PositiveIntegerField(default=1)
    temps_etape = models.TimeField(default="00:00:00")
    temperature = models.DecimalField(max_digits=3, decimal_places=1)
    brassin = models.ForeignKey(Brassin, on_delete=models.CASCADE)

class BrassinProduit(models.Model):
	brassin = models.ForeignKey(Brassin, on_delete=models.CASCADE)
	produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
	quantite = models.PositiveIntegerField()

	class Meta:
	    verbose_name = "Produits disponibles"
	    ordering = ['-brassin__date_brassin']

	def __str__(self):
	    return "Brassin n°" + str(self.brassin) + " ----------------------- " + str(self.produit) + " ----------------------- (reste " + str(self.restant) + ")"

	@property
	def vendu(self):
		vendu = Vente.objects.filter(brassin_produit=self.id).aggregate(Sum('quantite')).get('quantite__sum',0.00)
		if vendu is None:
		    return 0.00
		else:
		    return vendu

	@property
	def restant(self):
	    restant = Decimal(self.quantite) - Decimal(self.vendu)
	    return restant

class BrassinIngredient(models.Model):
	brassin = models.ForeignKey(Brassin, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	quantite = models.DecimalField(null=True,max_digits=8,decimal_places=4)
	temps_infusion = models.TimeField(blank=True,null=True,default="01:30:00")
	achete = models.BooleanField(default=True)

class RecetteIngredient(models.Model):
	recette = models.ForeignKey(Recette, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	quantite = models.DecimalField(null=True,max_digits=8,decimal_places=4)
	temps_infusion = models.TimeField(blank=True,null=True,default="01:30:00")


class Achat(models.Model):
    ACHAT_TYPE = [('Fonctionnement','Fonctionnement'),('MAJ','MAJ'),]
    type_achat = models.CharField(null=True,max_length=30,choices=ACHAT_TYPE,default='Fonctionnement')
    date_achat = models.DateField(null=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL,null=True,blank=True)
    quantite = models.DecimalField(null=True,max_digits=6,decimal_places=3)

    class Meta:
        verbose_name = "Achat"
        ordering = ['date_achat']

    @property
    def prix(self):
        if self.type_achat == 'MAJ':
            return 0
        else:
            ing = self.ingredient
            if ing.prix_kg:
                return ing.prix_kg*self.quantite
            else:
                return 0

    @property
    def total(self):
        total = 0
        achats = Achat.objects.all()
        for a in achats:
            ing = a.ingredient
            total += ing.prix_kg*a.quantite
        return total

class Vente(models.Model):
	date_vente = models.DateField(default=datetime.now,null=True)
	brassin_produit = models.ForeignKey(BrassinProduit, on_delete=models.CASCADE)
	quantite = models.PositiveIntegerField()
	client = models.CharField(null=True, blank= True,max_length=30)
	vendeur = models.CharField(null=True, blank= True,max_length=30)
	prix = models.DecimalField(max_digits=6,decimal_places=2)
	virement = models.BooleanField(default=False)
	notes = models.TextField(blank=True,null=True)

	class Meta:
		verbose_name = "Vente"
		ordering = ['date_vente']
