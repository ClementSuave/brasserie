from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from decimal import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum, Count, Max, ProtectedError, F
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin

from .models import Profile, Fermenteur, Produit, Ingredient, Recette, Note, Brassin, BrassinEtapeChauffe, BrassinProduit, BrassinIngredient, RecetteIngredient, Achat, Vente
from .forms import ConnexionForm, FermenteurForm, ProduitForm, IngredientForm, RecetteForm, NoteForm, BrassinForm, BrassinEtapeChauffeForm, BrassinProduitForm, BrassinIngredientForm, RecetteIngredientForm, AchatForm, VenteForm, StockUpdateForm

#-------------------------------------------------------------------------------------------------------------
# CONNEXION
#-------------------------------------------------------------------------------------------------------------
def connexion(request):
    error = False

    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                error = True
    else:
        form = ConnexionForm()

    return render(request, 'connexion.html', locals())

@login_required
def deconnexion(request):
    logout(request)
    return redirect('connexion')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Mot de passe mis à jour!','alert-success')
            return redirect('home')
        else:
            messages.error(request, 'Erreur.','alert-danger')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})




#-------------------------------------------------------------------------------------------------------------
# HOME
#-------------------------------------------------------------------------------------------------------------

@login_required
def Home(request):
    bs = Brassin.objects.all()
    total_brassins = Brassin.objects.all().count()
    ns = Note.objects.all()
    f = Fermenteur.objects.all()
    ps = Produit.objects.all()
    rs = Recette.objects.all()
    #brassin_in_tank = Brassin.objects.filter(date_mise_bouteille__isnull=True).annotate(max_date=Max('date_mise_bouteille')).filter(date_mise_bouteille=F('max_date'))
    #stock = BrassinProduit.objects.filter(brassin__archive=False).values('brassin__recette__nom','produit__type_produit','produit__contenance').annotate(stock_remaining=Sum('quantite')).order_by('brassin__recette__nom')
    stock = BrassinProduit.objects.filter(brassin__archive=False).order_by('brassin__recette__nom')
    return render(request, "brassin/home.html", {'brassins': bs,'notes':ns,'total': total_brassins,'stock':stock,'fermenteurs':f,'produits':ps,'stock':stock})

#-------------------------------------------------------------------------------------------------------------
# NOTE
#-------------------------------------------------------------------------------------------------------------

class NoteCreate(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Note
    template_name = 'brassin/note_create_form.html'
    form_class = NoteForm
    success_url =  reverse_lazy('home')
    permission_required = 'note.add_choice'
    success_message = 'Note ajoutée.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

    def form_valid(self, form):
        n = form.save(commit=False)
        n.auteur = self.request.user.username
        n.date = datetime.now()
        n.save()
        return super().form_valid(form)

class NoteUpdate(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Note
    id = Note.id
    template_name = 'brassin/note_update_form.html'
    form_class = NoteForm
    success_url =  reverse_lazy('home')
    permission_required = 'note.change_choice'
    success_message = 'Note mise à jour.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

class NoteDelete(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Note
    template_name = 'brassin/note_delete_form.html'
    success_url = reverse_lazy('home')
    permission_required = 'note.delete_choice'
    success_message = 'Note supprimée.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

#-------------------------------------------------------------------------------------------------------------
# PRODUIT
#-------------------------------------------------------------------------------------------------------------

class ProduitCreate(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Produit
    template_name = 'brassin/produit_create_form.html'
    form_class = ProduitForm
    success_url =  reverse_lazy('home')
    permission_required = 'produit.add_choice'
    success_message = 'Produit ajouté.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

class ProduitUpdate(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Produit
    id = Produit.id
    template_name = 'brassin/produit_update_form.html'
    form_class = ProduitForm
    success_url =  reverse_lazy('home')
    permission_required = 'produit.change_choice'
    success_message = 'Produit mis à jour.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')


@login_required
@permission_required('produit.delete_choice', raise_exception=True)
def ProduitDelete(request, pk):

    p = get_object_or_404(Produit, pk=pk)

    if request.method == 'POST':
        try:
            p.delete()
            messages.success(request, 'Produit supprimé','alert-success')
        except ProtectedError:
            messages.error(request, 'Le produit ne peut pas être supprimé car il est utilisé.','alert-danger')

        return redirect('home')

    return render(request, 'brassin/produit_delete_form.html', {'produit':p})

#-------------------------------------------------------------------------------------------------------------
# FERMENTEUR
#-------------------------------------------------------------------------------------------------------------

class FermenteurCreate(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Fermenteur
    template_name = 'brassin/fermenteur_create_form.html'
    form_class = FermenteurForm
    success_url =  reverse_lazy('home')
    permission_required = 'fermenteur.add_choice'
    success_message = 'Fermenteur ajouté.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

class FermenteurUpdate(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Fermenteur
    id = Fermenteur.id
    template_name = 'brassin/fermenteur_update_form.html'
    form_class = FermenteurForm
    success_url =  reverse_lazy('home')
    permission_required = 'fermenteur.change_choice'
    success_message = 'Fermenteur mis à jour.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

class FermenteurDelete(SuccessMessageMixin,PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Fermenteur
    template_name = 'brassin/fermenteur_delete_form.html'
    success_url = reverse_lazy('home')
    permission_required = 'fermenteur.delete_choice'
    success_message = 'Fermenteur supprimé.'
    def get_success_message(self, cleaned_data):
        return messages.success(self.request,self.success_message, extra_tags = 'alert-success')

#-------------------------------------------------------------------------------------------------------------
# BRASSIN
#-------------------------------------------------------------------------------------------------------------

@login_required
def BrassinsList(request):
    bs = Brassin.objects.all()

    return render(request, "brassin/brassin_list.html", {'brassins': bs})

class BrassinCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Brassin
    template_name = 'brassin/brassin_create_form.html'
    form_class = BrassinForm
    permission_required = 'brassin.add_choice'
    success_url =  reverse_lazy('brassin_list')

class BrassinUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Brassin
    id = Brassin.id
    template_name = 'brassin/brassin_update_form.html'
    form_class = BrassinForm
    permission_required = 'brassin.change_choice'
    success_url = "/brasserie/brassins/{id}/"

class BrassinDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Brassin
    template_name = 'brassin/brassin_delete_form.html'
    permission_required = 'brassin.delete_choice'
    success_url = reverse_lazy('brassin_list')

@login_required
def BrassinConsult(request, id):
    b = get_object_or_404(Brassin, id=id)
    bi = BrassinIngredient.objects.all().filter(brassin=b).order_by('ingredient__type_ingredient')
    p = BrassinProduit.objects.all().filter(brassin=b)
    c = BrassinEtapeChauffe.objects.all().filter(brassin=b).order_by('numero')

    try:
        r = Recette.objects.get(id=b.recette_id)
    except Recette.DoesNotExist:
        r = None
    return render(request, 'brassin/brassin_consulter.html', {'brassin': b,'brassin_ingredient':bi,'recette':r,'brassin_produit':p,'etape_chauffe':c})

#-------------------------------------------------------------------------------------------------------------
# BRASSIN ETAPE
#-------------------------------------------------------------------------------------------------------------

@login_required
@permission_required('brassin_etape_chauffe.add_choice', raise_exception=True)
def BrassinEtapeChauffeAdd(request,id):
    b = Brassin.objects.get(pk=id)
    c = BrassinEtapeChauffe.objects.all().filter(brassin=b).order_by('numero')
    if request.method == 'POST':
        form = BrassinEtapeChauffeForm(request.POST)
        form.fields["brassin"].initial = id
        if form.is_valid():
            data = form.cleaned_data
            message = "Etape " + str(data["numero"]) + ": " + str(data["temperature"]) + " °C pendant " + str(data["temps_etape"]) + " h."
            form.save()
            messages.success(request, message)
    else:
        form = BrassinEtapeChauffeForm()
        form.fields["brassin"].initial = id
    return render(request, 'brassin/brassin_etape_chauffe_add_form.html', {'form': form,'b':b,'etape_chauffe':c})

class BrassinEtapeChauffeDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = BrassinEtapeChauffe
    brassin_id = BrassinEtapeChauffe.brassin
    template_name = 'brassin/brassin_etape_chauffe_delete_form.html'
    permission_required = 'brassin_etape_chauffe.delete_choice'
    success_url = "/brasserie/brassins/{brassin_id}/"

#-------------------------------------------------------------------------------------------------------------
# BRASSIN INGREDIENT
#-------------------------------------------------------------------------------------------------------------

@login_required
@permission_required('brassin_ingredient.add_choice', raise_exception=True)
def BrassinIngredientFill(request,id):
    b = Brassin.objects.get(pk=id)
    b_vol = b.volume_empatage
    if b_vol:
        pass
    else:
        b_vol = 0
    ings_recette = RecetteIngredient.objects.all().filter(recette=b.recette)
    try:
        r = Recette.objects.get(id=b.recette_id)
        for i in ings_recette:
            BrassinIngredient.objects.create(brassin = b, ingredient = i.ingredient, quantite = i.quantite*b_vol/100*r.taux_empatage, temps_infusion = i.temps_infusion , achete = True)
        bi = BrassinIngredient.objects.all().filter(brassin=b)
        p = BrassinProduit.objects.all().filter(brassin=b)
        c = BrassinEtapeChauffe.objects.all().filter(brassin=b).order_by('numero')
    except Recette.DoesNotExist:
        r = None
    return render(request, 'brassin/brassin_consulter.html', {'brassin': b,'brassin_ingredient':bi,'recette':r,'brassin_produit':p,'etape_chauffe':c})

@login_required
@permission_required('brassin_ingredient.add_choice', raise_exception=True)
def BrassinIngredientAdd(request,id):
    b = Brassin.objects.get(pk=id)
    bi = BrassinIngredient.objects.all().filter(brassin=b)
    if request.method == 'POST':
        form = BrassinIngredientForm(request.POST)
        form.fields["brassin"].initial = id
        form.fields["achete"].initial = True

        if form.is_valid():
            data = form.cleaned_data
            if "Levure" in str(data["ingredient"]):
                message = "Paquets de " + str(data["ingredient"]) + " ajouté: "  + str(data["quantite"])
            else:
                message = str(data["quantite"]) + " kg de " + str(data["ingredient"]) + " ont étés ajoutés."
            form.save()
            messages.success(request, message)
    else:
        form = BrassinIngredientForm()
        form.fields["brassin"].initial = id
        form.fields["achete"].initial = True
    return render(request, 'brassin/brassin_ingredient_add_form.html', {'form': form,'b':b,'brassin_ingredient':bi})

class BrassinIngredientUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = BrassinIngredient
    id = BrassinIngredient.id
    brassin_id = BrassinIngredient.brassin
    template_name = 'brassin/brassin_ingredient_update_form.html'
    form_class = BrassinIngredientForm
    permission_required = 'brassin_ingredient.update_choice'
    success_url = "/brasserie/brassins/{brassin_id}/"

class BrassinIngredientDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = BrassinIngredient
    brassin_id = BrassinIngredient.brassin
    template_name = 'brassin/brassin_ingredient_delete_form.html'
    permission_required = 'brassin_ingredient.delete_choice'
    success_url = "/brasserie/brassins/{brassin_id}/"

@login_required
@permission_required('brassin_ingredient.delete_choice', raise_exception=True)
def BrassinIngredientDeleteAll(request,id):
    b = Brassin.objects.get(pk=id)
    bi = BrassinIngredient.objects.all().filter(brassin=b)
    for i in bi:
        i.delete()
    try:
        r = Recette.objects.get(id=b.recette_id)
    except Recette.DoesNotExist:
        r = None
    p = BrassinProduit.objects.all().filter(brassin=b)
    c = BrassinEtapeChauffe.objects.all().filter(brassin=b).order_by('numero')

    return render(request, 'brassin/brassin_consulter.html', {'brassin': b,'brassin_ingredient':bi,'recette':r,'brassin_produit':p,'etape_chauffe':c})


#-------------------------------------------------------------------------------------------------------------
# BRASSIN PRODUIT
#-------------------------------------------------------------------------------------------------------------

@login_required
@permission_required('brassin_ingredient.add_choice', raise_exception=True)
def BrassinProduitAdd(request,id):
    b = Brassin.objects.get(pk=id)
    p = BrassinProduit.objects.all().filter(brassin=b)
    if request.method == 'POST':
        form= BrassinProduitForm(request.POST)
        form.fields["brassin"].initial = id

        if form.is_valid():
            data = form.cleaned_data
            message = str(data["quantite"]) + " "  + str(data["produit"])
            form.save()
            messages.success(request, message)
    else:
        form = BrassinProduitForm()
        form.fields["brassin"].initial = id
    return render(request, 'brassin/brassin_produit_add_form.html', {'form': form,'b':b,'brassin_produit':p})

class BrassinProduitDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = BrassinProduit
    brassin_id = BrassinProduit.brassin
    template_name = 'brassin/brassin_produit_delete_form.html'
    permission_required = 'brassin_produit.delete_choice'
    success_url = "/brasserie/brassins/{brassin_id}/"



#-------------------------------------------------------------------------------------------------------------
# RECETTE
#-------------------------------------------------------------------------------------------------------------

class RecettesList(LoginRequiredMixin,ListView):
    model = Recette
    context_object_name = "recettes"
    template_name = "brassin/recettes_list.html"

class RecetteCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Recette
    template_name = 'brassin/recette_create_form.html'
    form_class = RecetteForm
    permission_required = 'recette.add_choice'
    success_url =  reverse_lazy('recettes_list')

class RecetteUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Recette
    id = Recette.id
    template_name = 'brassin/recette_update_form.html'
    form_class = RecetteForm
    permission_required = 'recette.change_choice'
    success_url = "/brasserie/recettes/{id}/"

class RecetteDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Recette
    template_name = 'brassin/recette_delete_form.html'
    permission_required = 'recette.delete_choice'
    success_url = reverse_lazy('recettes_list')

@login_required
def RecetteConsult(request, id):
    r = get_object_or_404(Recette, id=id)
    ri = RecetteIngredient.objects.all().filter(recette=r)
    dataset_chart_recette = Brassin.objects.all().filter(recette=r).exclude(densite_initiale__isnull=True).exclude(densite_finale__isnull=True).values('id','date_brassin', 'densite_initiale','densite_finale').order_by('date_brassin')
    return render(request, 'brassin/recette_consulter.html', {'recette': r,'recette_ingredient':ri,'dataset_chart_recette':dataset_chart_recette})

#-------------------------------------------------------------------------------------------------------------
# RECETTE INGREDIENT
#-------------------------------------------------------------------------------------------------------------
@login_required
@permission_required('recette_ingredient.add_choice', raise_exception=True)
def RecetteIngredientAdd(request,id):

    if request.method == 'POST':
        form = RecetteIngredientForm(request.POST)
        form.fields["recette"].initial = id

        if form.is_valid():
            data = form.cleaned_data
            if "Levure" in str(data["ingredient"]):
                message = str(data["ingredient"]) + " ajouté."
            elif "Malt" in str(data["ingredient"]):
                message = str(data["quantite"])+ " % masse totale de " + str(data["ingredient"]) + " ajouté."
            else:
                message = str(data["quantite"]) + " g/l de " + str(data["ingredient"]) + " ont étés ajoutés."
            form.save()
            messages.success(request, message)
    else:
        form = RecetteIngredientForm()
        form.fields["recette"].initial = id
    return render(request, 'brassin/recette_ingredient_add_form.html', {'form': form})

class RecetteIngredientUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = RecetteIngredient
    id = RecetteIngredient.id
    recette_id = RecetteIngredient.recette
    template_name = 'brassin/recette_ingredient_update_form.html'
    form_class = RecetteIngredientForm
    permission_required = 'recette_ingredient.update_choice'
    success_url = "/brasserie/recettes/{recette_id}/"

class RecetteIngredientDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = RecetteIngredient
    recette_id = RecetteIngredient.recette
    template_name = 'brassin/recette_ingredient_delete_form.html'
    permission_required = 'recette_ingredient.delete_choice'
    success_url = "/brasserie/recettes/{recette_id}"

#-------------------------------------------------------------------------------------------------------------
# INGREDIENTS
#-------------------------------------------------------------------------------------------------------------

@login_required
@permission_required('achat.add_choice', raise_exception=True)
def StockUpdate(request,id):
    i = get_object_or_404(Ingredient, id=id)

    a_update = Achat.objects.all().filter(type_achat='MAJ',ingredient=i)
    if a_update:
        for MAJ in a_update:
            MAJ.delete()

    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        form.fields["type_achat"].initial = 'MAJ'
        form.fields["ingredient"].initial = id

        if form.is_valid():
            data = form.cleaned_data
            message = "Le stock de " + str(data["ingredient"]) + " a été mis à jour."
            form.save()
            messages.success(request, message)
    else:
        form = StockUpdateForm()
        form.fields["type_achat"].initial = 'MAJ'
        form.fields["ingredient"].initial = id
        message = "Requete invalide."
    return render(request, 'brassin/stock_update_form.html', {'form': form,'i':i})

class IngredientsList(LoginRequiredMixin,ListView):
    model = Ingredient
    template_name = "brassin/ingredients_list.html"

    def get_context_data(self, **kwargs):
        context = super(IngredientsList, self).get_context_data(**kwargs)
        context['malt'] = Ingredient.objects.filter(type_ingredient="Malt")
        context['houblon'] = Ingredient.objects.filter(type_ingredient="Houblon")
        context['levure'] = Ingredient.objects.filter(type_ingredient="Levure")
        context['autre'] = Ingredient.objects.filter(type_ingredient="Autre")
        return context

class IngredientCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Ingredient
    template_name = 'brassin/ingredient_create_form.html'
    form_class = IngredientForm
    permission_required = 'ingredient.add_choice'
    success_url =  reverse_lazy('ingredients_list')

class IngredientUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Ingredient
    template_name = 'brassin/ingredient_update_form.html'
    form_class = IngredientForm
    permission_required = 'ingredient.change_choice'
    success_url =  reverse_lazy('ingredients_list')


class IngredientDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Ingredient
    template_name = 'brassin/ingredient_delete_form.html'
    form_class = IngredientForm
    permission_required = 'ingredient.delete_choice'
    success_url =  reverse_lazy('ingredients_list')

#-------------------------------------------------------------------------------------------------------------
# ACHATS
#-------------------------------------------------------------------------------------------------------------

class AchatsList(LoginRequiredMixin,ListView):
    model = Achat
    context_object_name = "achats"
    template_name = "brassin/achats_list.html"
    ordering = ['-date_achat']

    def get_context_data(self, **kwargs):
        context = super(AchatsList, self).get_context_data(**kwargs)
        achats = Achat.objects.all()
        context['achat'] = achats
        context['fonctionnement'] = Achat.objects.filter(type_achat="Fonctionnement").order_by('-date_achat')
        prix_achat = 0
        for a in achats:
            if a.ingredient.prix_kg:
                prix_achat += a.ingredient.prix_kg*a.quantite
        context['total_achats'] = prix_achat
        return context

@login_required
@permission_required('achat.add_choice', raise_exception=True)
def AchatCreate(request):
    l = Achat.objects.filter(type_achat="Fonctionnement").order_by('-date_achat')[:3]

    if request.method == 'POST':
        form = AchatForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            message = str(data["quantite"]) + " de " + str(data["ingredient"]) + " ajoutés."
            form.save()
            messages.success(request, message)
    else:
        form = AchatForm()
    return render(request, 'brassin/achat_create_form.html', {'form': form,'last_three':l})


class AchatUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Achat
    template_name = 'brassin/achat_update_form.html'
    form_class = AchatForm
    permission_required = 'achat.change_choice'
    success_url = reverse_lazy('achats_list')

class AchatDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Achat
    template_name = 'brassin/achat_delete_form.html'
    permission_required = 'achat.delete_choice'
    success_url = reverse_lazy('achats_list')

#-------------------------------------------------------------------------------------------------------------
# VENTES
#-------------------------------------------------------------------------------------------------------------

@login_required
def VentesList(request, date_s=datetime.now().replace(year = datetime.now().year - 1),date_e=datetime.now()):

    if request.method == 'POST':
        date_s = request.POST['date_s']
        date_e = request.POST['date_e']
    else:
        date_s=datetime.now().replace(year = datetime.now().year - 1)
        date_e=datetime.now()

    v = Vente.objects.filter(date_vente__range = [date_s,date_e])
    vm = Vente.objects.filter(date_vente__range = [date_s,date_e]).annotate(month=TruncMonth('date_vente')).values('month').annotate(tot_by_month=Sum('prix')).order_by()
    t = Vente.objects.all().filter(date_vente__range = [date_s,date_e]).aggregate(sum_all=Sum('prix')).get('sum_all')

    return render(request, "brassin/ventes_list.html", {'ventes': v, 'ventes_by_month':vm, 'total_recettes':t,'date_s':date_s})

@login_required
@permission_required('vente.add_choice', raise_exception=True)
def VenteCreate(request, bp=None, r=None):
    l = Vente.objects.all().order_by('-date_vente')[:3]

    if request.method == 'POST':
        form = VenteForm(request.POST)
        form.fields["brassin_produit"].initial = bp

        if form.is_valid():
            data = form.cleaned_data
            message = str(data["quantite"]) + " de " + str(data["brassin_produit"]) + " ajoutés."
            form.save()
            messages.success(request, message)
    else:
        form = VenteForm()
        form.fields["brassin_produit"].initial = bp
    return render(request, 'brassin/vente_create_form.html', {'form': form,'last_three':l})

class VenteUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Vente
    template_name = 'brassin/vente_update_form.html'
    form_class = VenteForm
    permission_required = 'vente.change_choice'
    success_url = reverse_lazy('ventes_list')

class VenteDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Vente
    template_name = 'brassin/vente_delete_form.html'
    permission_required = 'vente.delete_choice'
    success_url = reverse_lazy('ventes_list')


#-------------------------------------------------------------------------------------------------------------
# OUTILS
#-------------------------------------------------------------------------------------------------------------

@login_required
def Outils(request,id=0):
    f = Fermenteur.objects.all()
    if id != 0:
        b = Brassin.objects.get(id=id)
    else:
        b = Brassin.objects.latest('id')
    try:
        r = Recette.objects.get(id=b.recette_id)
    except Recette.DoesNotExist:
        r = Recette.objects.get(id=1)
    return render(request, "brassin/outils.html", {'brassin_x': b,'recette':r,'fermenteur':f})