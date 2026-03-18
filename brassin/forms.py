from django import forms
from .models import Profile, Fermenteur, Produit, Ingredient, Recette, Note, Brassin, BrassinEtapeChauffe, BrassinProduit, BrassinIngredient, RecetteIngredient, Achat, Vente
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import *
from django.utils.safestring import mark_safe

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class NoteForm(forms.ModelForm):
	class Meta:
		model = Note
		exclude = ['auteur','date']
		fields = '__all__'

class ProduitForm(forms.ModelForm):
    contenance = forms.DecimalField(required=True, widget= forms.TextInput(attrs={'placeholder':'L'}))
    prix = forms.DecimalField(required=False,widget= forms.TextInput(attrs={'placeholder':'€/L'}))
    class Meta:
        model = Produit
        fields = '__all__'

class FermenteurForm(forms.ModelForm):
    volume = forms.DecimalField(required=True, widget= forms.TextInput(attrs={'placeholder':'L'}))
    class Meta:
        model = Fermenteur
        fields = '__all__'

class BrassinForm(forms.ModelForm):
	volume_empatage = forms.DecimalField(required=False, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'L'}))
	volume_cuve_fermentation = forms.DecimalField(required=False, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'L'}))
	volume_mout = forms.DecimalField(required=False, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'L'}))
	volume_starter = forms.DecimalField(required=False, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'L'}))
	volume_rincage_dreches = forms.DecimalField(required=False, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'L'}))
	resucrage = forms.DecimalField(required=False, max_digits=2, min_value=0,widget= forms.TextInput(attrs={'placeholder':'g/L'}))

	class Meta:
		model = Brassin
		exclude = ['ingredient']
		attrs = {'class':'form-control'}
		widgets = {
			'date_brassin': DatePickerInput(format='%d/%m/%Y'),
			'date_mise_bouteille': DatePickerInput(format='%d/%m/%Y'),
			'temps_empatage': TimePickerInput(),
			'temps_fermentation': TimePickerInput(),
			'temps_ebullition': TimePickerInput(),}

class BrassinEtapeChauffeForm(forms.ModelForm):
    temperature = forms.DecimalField(required=False, max_digits=3, min_value=0,widget= forms.TextInput(attrs={'placeholder':'°C'}))

    class Meta:
        model = BrassinEtapeChauffe
        fields = '__all__'
        attrs = {'class':'form-control'}
        labels = {'numero': 'Etape n°','temps_etape': 'Durée'}
        widgets = {
            'brassin': forms.HiddenInput(),
            'temps_etape': TimePickerInput(),}

class BrassinIngredientForm(forms.ModelForm):
	quantite = forms.DecimalField(required=True, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'kg'}))

	class Meta:
		model = BrassinIngredient
		fields = '__all__'
		widgets = {
			'brassin': forms.HiddenInput(),
			'quantite': forms.TextInput(attrs={'placeholder': 'kg'}),
			'temps_infusion': TimePickerInput(),}

class BrassinProduitForm(forms.ModelForm):
	quantite = forms.DecimalField(required=True, max_digits=6, min_value=0)

	class Meta:
		model = BrassinProduit
		fields = '__all__'
		widgets = {
			'brassin': forms.HiddenInput(),}

class RecetteForm(forms.ModelForm):
	class Meta:
		model = Recette
		fields = '__all__'

class RecetteIngredientForm(forms.ModelForm):
	quantite = forms.DecimalField(required=True, max_digits=6, min_value=0)

	class Meta:
		model = RecetteIngredient
		fields = '__all__'
		widgets = {
			'recette': forms.HiddenInput(),
			'quantite': forms.TextInput(attrs={'placeholder': '%'}),
			'temps_infusion': TimePickerInput(),}

class IngredientForm(forms.ModelForm):
	prix_kg = forms.DecimalField(required=False, max_digits=6, min_value=0,widget= forms.TextInput(attrs={'placeholder':'€/kg'}))
	ebc_min = forms.DecimalField(required=False, max_digits=4, min_value=0)
	ebc_max = forms.DecimalField(required=False, max_digits=4, min_value=0)
	acide_alpha = forms.DecimalField(required=False, max_digits=3, min_value=0,widget= forms.TextInput(attrs={'placeholder':'%'}))
	attenuation_min = forms.DecimalField(required=False, max_digits=2, min_value=0,widget= forms.TextInput(attrs={'placeholder':'%'}))
	attenuation_max = forms.DecimalField(required=False, max_digits=3, min_value=0,widget= forms.TextInput(attrs={'placeholder':'%'}))

	class Meta:
		model = Ingredient
		fields = '__all__'

class AchatForm(forms.ModelForm):
	class Meta:
		model = Achat
		fields = '__all__'
		widgets = {
			'date_achat': DatePickerInput(format='%d/%m/%Y'),}

class VenteForm(forms.ModelForm):
    brassin_produit = forms.ModelChoiceField(queryset=BrassinProduit.objects.exclude(brassin__date_mise_bouteille__isnull=True))
    prix = forms.DecimalField(required=False,widget= forms.TextInput(attrs={'placeholder':'€'}))

    def clean_quantite(self):
        data = self.cleaned_data['quantite']
        bp_id = self['brassin_produit'].value()
        try:
            bp = BrassinProduit.objects.get(pk=bp_id)
        except BrassinProduit.DoesNotExist:
            raise ValidationError('Produit invalide.')
        total = bp.quantite
        ventes_sum = Vente.objects.filter(brassin_produit=bp_id).aggregate(Sum('quantite')).get('quantite__sum') or 0
        dispo = Decimal(total) - Decimal(ventes_sum)
        if data > dispo:
            raise ValidationError('Pas assez de produit disponible, reste ' + str(dispo))
        return data

    class Meta:
        model = Vente
        labels = {'brassin_produit': 'Produit'}
        exclude = ['vendeur']
        widgets = {
			'date_vente': DatePickerInput(format='%d/%m/%Y'),}

class StockUpdateForm(forms.ModelForm):

    class Meta:
        model = Achat
        fields = '__all__'
        labels = {'date_achat': 'Date mise à jour'}
        widgets = {
            'type_achat': forms.HiddenInput(),
            'ingredient': forms.HiddenInput(),
            'quantite': forms.HiddenInput(),
            'date_achat': DatePickerInput(format='%d/%m/%Y'),}