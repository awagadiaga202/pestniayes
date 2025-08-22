from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
        path('', views.accueil, name='accueil'),
        path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
        path('clients/', views.liste_clients, name='liste_clients'),
        path('clients/modifier/<int:client_id>/', views.modifier_client, name='modifier_client'),
        path('clients/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
        path('clients/export/excel/', views.export_clients_excel, name='export_clients_excel'),
        path('clients/export/pdf/', views.export_clients_pdf, name='export_clients_pdf'),
#Fournisseur 
        path('fournisseurs/ajouter-fournisseur/', views.ajouter_fournisseur, name='ajouter_fournisseur'),
        path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
        path('fournisseurs/modifier/<int:id>/', views.modifier_fournisseur, name='modifier_fournisseur'),
        path('fournisseurs/supprimer/<int:id>/', views.supprimer_fournisseur, name='supprimer_fournisseur'),

#Produit 
        path('produits/', views.liste_produits, name='liste_produits'),
        path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
        path('produits/modifier/<int:pk>/', views.modifier_produit, name='modifier_produit'),
        path('produits/supprimer/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),
# Commande 
        path('commandes/', views.liste_commandes, name='liste_commandes'),
        path('commandes/supprimer/<int:commande_id>/', views.supprimer_commande, name='supprimer_commande'),
        path('rapport-journalier/', views.rapport_journalier, name='rapport_journalier'),
        path('commandes/exporter-pdf/', views.exporter_commandes_par_client_pdf, name='exporter_commandes_pdf'),
        path('exporter-commandes/', views.exporter_commandes_pdf, name='exportons_commandes_pdf'),

        path('commandes/ajouter/', views.ajouter_commande, name='ajouter_commande'),
        path('commandes/modifier/<int:commande_id>/', views.modifier_commande, name='modifier_commande'),
        path('commandes/prioritaires/pdf/', views.exporter_commandes_prioritaires_pdf, name='commandes_prioritaires_pdf'),
        path('commandes/<int:commande_id>/facture/', views.generer_facture_pdff, name='facture_commande'),
        path('commandes/variete/<str:variete_nom>/export/', views.exporter_commandes_par_variete, name='exporter_commandes_variete'),
         path('commande/<int:pk>/valider/', views.valider_commande, name='valider_commande'),




# Vente 
        path('ventes/ajouter/', views.ajouter_vente, name='ajouter_vente'),
        path('ventes/', views.liste_ventes, name='liste_ventes'),
        path('ventes/modifier/<int:pk>/', views.modifier_vente, name='modifier_vente'),
        path('ventes/supprimer/<int:pk>/', views.supprimer_vente, name='supprimer_vente'),

        path('ventes/rapport-journalier/', views.rapport_journalier, name='rapport_journalier'),
        path('facture/<int:vente_id>/', views.generer_facture_pdf, name='facture_pdf'),
        path("facture-proforma/", views.facture_proforma_view, name="facture_proforma"),
        path('ventes/<int:vente_id>/facture/', views.facture_vente, name='facture_vente'),
        path('ventes/<int:vente_id>/facture/pdf/', views. generer_facture_pdf, name='exporter_facture_pdf'),
         path('bordereaux/ajouter/', views.ajouter_bordereau, name='ajouter_bordereau'),
        path('bordereau-livraison/', views.bordereau_livraison_pdf, name='bordereau_livraison_pdf'),
        path('lettre-voiture/pdf/', views.lettre_voiture_pdf, name='lettre_voiture_pdf'),
         path('lettre-voiture/', views.lettre_voiture, name='lettre_voiture'),
         path('ventes/variete/<str:variete>/export/', views.exporter_ventes_variete_pdf, name='exporter_ventes_variete'),
         path("ventes/client/<str:client_nom>/export/", views.exporter_ventes_client_pdf, name="exporter_ventes_client_pdf"),



#bon
        path("bon-commande/", views.bon_commande_view, name="bon_commande"),
        path("bons_commande/", views.liste_bons_commande, name="liste_bons_commande"),

#Compte bancaire 
        path('comptes/', views.liste_comptes, name='liste_comptes'),
        path('comptes/ajouter/', views.ajouter_compte, name='ajouter_compte'),
        path('transactions/', views.liste_transactions, name='liste_transactions'),
        path('transactions/ajouter/', views.ajouter_transaction, name='ajouter_transaction'),
        path('comptes/modifier/<int:compte_id>/', views.modifier_compte, name='modifier_compte'),
        path('comptes/supprimer/<int:compte_id>/', views.supprimer_compte, name='supprimer_compte'),
#connexion

       


        path('login/', views.login_view, name='login'),
        path('dashboard-vendeur/', views.dashboard_vendeur, name='dashboard_vendeur'),
        # path('dashboard-comptable/', views.dashboard_comptable, name='dashboard_comptable'),



        path('logout/', views.logout_view, name='logout'),
        # tes autres routes ici
        #Depot
        path('depots/', views.liste_depots, name='liste_depots'),
        path('depots/ajouter/', views.ajouter_depot, name='ajouter_depot'),
        path('depots/modifier/<int:pk>/', views.modifier_depot, name='modifier_depot'),
        path('depots/supprimer/<int:pk>/', views.supprimer_depot, name='supprimer_depot'),


#Reception
        path('receptions/ajouter/', views.ajouter_reception, name='ajouter_reception'),
        path('receptions/', views.liste_receptions, name='liste_receptions'),
        path('receptions/<int:pk>/modifier/', views.modifier_reception, name='modifier_reception'),
        path('receptions/<int:pk>/supprimer/', views.supprimer_reception, name='supprimer_reception'),

#Stock
       path('stocks/', views.liste_stocks, name='liste_stocks'),
        path('stocks/ajouter/', views.ajouter_stock, name='ajouter_stock'),
        path('stocks/modifier/<int:pk>/', views.modifier_stock, name='ajouter_ou_modifier_stock'),
        path('stocks/supprimer/<int:pk>/', views.supprimer_stock, name='supprimer_stock'),



]
