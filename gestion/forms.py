from django import forms
from .models import Client, Fournisseur,Produit,Commande, LigneCommande, Vente, Stock,CompteBancaire, Transaction, BordereauLivraison,Depot
from django.contrib.auth.forms import AuthenticationForm
from .models import Reception


from django.forms import inlineformset_factory
from django.utils import timezone
from django.forms import modelformset_factory
from .models import LigneVente

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'numero_piece_identite': forms.TextInput(attrs={'class': 'form-control'}),
        }
# Fournisseur 

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Adresse',
                'rows': 3  # 👈 On réduit ici la hauteur
            }),
            'entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entreprise'}),
        }
#Produit 
class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'variete', 'description', 'prix_unitaire', 'unite_stock', 'fournisseur']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }
#Commande 

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client', 'remise', 'avance']



class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite', 'unite']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'unite': forms.Select(attrs={'class': 'form-control'}),
        }

LigneCommandeFormSet = inlineformset_factory(
    Commande, LigneCommande, form=LigneCommandeForm,
    extra=1, can_delete=True
)
###############################################################
class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = [
            'client', 'type_vente','date_vente',  'mode_paiement', 'commentaire', 'vendeur'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'type_vente': forms.Select(attrs={'class': 'form-select'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vendeur': forms.Select(attrs={'class': 'form-select'}),
        }


class LigneVenteForm(forms.ModelForm):
    class Meta:
        model = LigneVente
        fields = ['produit', 'depot', 'quantite', 'remise']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select produit-select'}),
            'depot': forms.Select(attrs={'class': 'form-select depot-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': 1}),
            'remise': forms.NumberInput(attrs={'class': 'form-control remise-input', 'min': 0}),
        }


LigneVenteFormSet = inlineformset_factory(
    parent_model=Vente,
    model=LigneVente,
    form=LigneVenteForm,
    extra=1,
    can_delete=True
)

class LigneProformaForm(forms.Form):
    produit = forms.CharField(label='Produit', max_length=100)
    quantite = forms.IntegerField(label='Quantité', min_value=1)
    prix_unitaire = forms.DecimalField(label='Prix unitaire', max_digits=10, decimal_places=2)
    remise = forms.DecimalField(label='Remise (%)', max_digits=5, decimal_places=2, required=False, initial=0)

class ProformaForm(forms.Form):
    client_nom = forms.CharField(label="Nom du client", max_length=100, required=False)
    client_entreprise = forms.CharField(label="Entreprise", max_length=100, required=False)
    client_adresse = forms.CharField(label="Adresse", widget=forms.Textarea, required=False)
    lignes = forms.CharField(widget=forms.HiddenInput(), required=False)  # JSON ou liste encodée
#CompteBancaire

class CompteBancaireForm(forms.ModelForm):
    class Meta:
        model = CompteBancaire
        fields = '__all__'
        widgets = {
            'nom_banque': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_compte': forms.TextInput(attrs={'class': 'form-control'}),
            'solde': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TransactionForm(forms.ModelForm):
    date_transaction = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Date et heure de la transaction"
    )

    class Meta:
        model = Transaction
        fields = '__all__'

class BordereauLivraisonForm(forms.Form):
    client = forms.CharField(label="Nom du client", max_length=100)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    destination = forms.CharField(max_length=200)
    numero_vehicule = forms.CharField(max_length=50)
    nature_produit = forms.CharField(max_length=100)
    quantite = forms.DecimalField(max_digits=10, decimal_places=2)
    poids = forms.DecimalField(max_digits=10, decimal_places=2)
#Connexion

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
 #Depot 
 # forms.py


class DepotForm(forms.ModelForm):
    class Meta:
        model = Depot
        fields = ['nom', 'adresse']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }
#Reception

class ReceptionForm(forms.ModelForm):
    class Meta:
        model = Reception
        fields = ['produit', 'depot', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={'step': '0.01'}),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['produit', 'depot', 'quantite']
