from django.contrib import admin

# Register your models here.

from .models import (
    Client, Fournisseur, Produit, Vente,
    CompteBancaire, Transaction, Utilisateur,
    Commande, Paiement, LigneCommande,Transaction
)

admin.site.register(Client)
admin.site.register(Fournisseur)
admin.site.register(Produit)
admin.site.register(Vente)
admin.site.register(CompteBancaire)
admin.site.register(Transaction)
admin.site.register(Utilisateur)
admin.site.register(Commande)
admin.site.register(Paiement)
admin.site.register(LigneCommande)
