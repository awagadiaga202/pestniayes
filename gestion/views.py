from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ClientForm, FournisseurForm, ProduitForm,CommandeForm, LigneCommandeFormSet,TransactionForm,CompteBancaireForm, ReceptionForm, DepotForm

from .forms import StockForm

from .models import Client, Fournisseur, Produit, LigneCommande, Commande, Vente,CompteBancaire,Transaction,Reception,Depot,Stock,BonCommande, LigneBonCommande
import io, json, uuid, base64, os
from django.db.models import Sum
from .forms import BordereauLivraisonForm
from decimal import Decimal
from .decorators import role_required
from django.urls import reverse

from django.forms import modelformset_factory
from .forms import CommandeForm, LigneCommandeForm
import openpyxl
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.db.models import Q
import openpyxl 
from datetime import datetime, timedelta
import uuid
from django.contrib.staticfiles import finders
import base64
import tempfile
from io import BytesIO
from django.conf import settings
from django.utils.timezone import localtime
from reportlab.lib.utils import ImageReader
from .forms import VenteForm
from django.utils.timezone import now
from django.template.loader import get_template
from xhtml2pdf import pisa
from .forms import VenteForm, LigneVenteForm
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import VenteForm, LigneVenteFormSet,LigneVente
from django.db import transaction
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.units import cm
from django.http import FileResponse
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from .forms import ProformaForm
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth import logout
from django.forms import inlineformset_factory

def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_clients')  # après enregistrement
    else:
        form = ClientForm()

    return render(request, 'gestion/ajouter_client.html', {
        'form': form,
        'titre': "Ajouter un client"
    })

def liste_clients(request):
    query = request.GET.get('q')
    if query:
        clients = Client.objects.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(telephone__icontains=query)
        )
    else:
        clients = Client.objects.all()
    
    return render(request, 'gestion/liste_clients.html', {'clients': clients, 'query': query})

def modifier_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('liste_clients')
    else:
        form = ClientForm(instance=client)
    return render(request, 'gestion/modifier_client.html', {'form': form, 'client': client})
  
def supprimer_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == "POST":
        client.delete()
        messages.success(request, "Client supprimé avec succès.")
        return redirect('liste_clients')
    
    return render(request, 'gestion/confirmer_suppression.html', {'client': client})

###export

def export_clients_excel(request):
    clients = Client.objects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clients"

    # En-têtes
    ws.append(['Nom', 'Prénom', 'Téléphone', 'Email', 'Adresse', 'N° Pièce'])

    for client in clients:
        ws.append([
            client.nom,
            client.prenom,
            client.telephone,
            client.email or '',
            client.adresse or '',
            client.numero_piece_identite
        ])

    # Sauvegarde dans un flux mémoire (BytesIO)
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=clients.xlsx'
    return response
##Exporte client PDF

def export_clients_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="clients.pdf"'

    # Crée le canvas PDF
    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # === 1. Ajouter le logo Prest-Niayes ===
    logo_path = os.path.join(settings.BASE_DIR, 'gestion', 'static', 'images', 'logo.jpg')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 80, width=100, preserveAspectRatio=True)

    # === 2. Titre du PDF ===
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, height - 60, "Liste des Clients - Prest-Niayes")

    # === 3. Préparer les données du tableau ===
    clients = Client.objects.all()
    data = [["Nom", "Prénom", "Téléphone", "Email","N° Pièce"]]
    for client in clients:
        data.append([
            client.nom,
            client.prenom,
            client.telephone,
            client.email, 
            client.numero_piece_identite or ""
        ])

    # === 4. Créer un tableau avec lignes ===
    table = Table(data, colWidths=[3 * cm, 3 * cm, 4 * cm, 5 * cm])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
    ])
    table.setStyle(style)

    # === 5. Positionner le tableau sur la page ===
    table.wrapOn(c, width, height)
    table.drawOn(c, 40, height - 130 - 20 * len(data))

    # Fin du document
    c.showPage()
    c.save()
    return response

# Fournisseur 

def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_fournisseurs')  # pour rester sur la page
    else:
        form = FournisseurForm()
    return render(request, 'gestion/ajouter_fournisseur.html', {'form': form})

def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'gestion/liste_fournisseurs.html', {'fournisseurs': fournisseurs})
# Modifier Ou Supprimer  un fournisseur 

# Modifier un fournisseur
def modifier_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'gestion/modifier_fournisseur.html', {'form': form})

# Supprimer un fournisseur
def supprimer_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        return redirect('liste_fournisseurs')
    return render(request, 'gestion/confirmer_suppression.html', {
        'objet': fournisseur,
        'retour_url': reverse('liste_fournisseurs')
    })
# Produit 
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
    else:
        form = ProduitForm()
    return render(request, 'gestion/ajouter_produit.html', {'form': form})
def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'gestion/liste_produits.html', {'produits': produits})
def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'gestion/modifier_produit.html', {'form': form, 'produit': produit})
def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('liste_produits')
    return render(request, 'gestion/confirmer_suppression.html', {
        'objet': produit,
        'retour_url': reverse('liste_produits')
    })

# Commande 
def ajouter_commande(request):
    prefix = 'lignes'  # 👈 préfixe pour le formset

    if request.method == 'POST':
        form_commande = CommandeForm(request.POST)
        formset_lignes = LigneCommandeFormSet(request.POST, prefix=prefix)

        if form_commande.is_valid() and formset_lignes.is_valid():
            commande = form_commande.save()
            lignes = formset_lignes.save(commit=False)
            for ligne in lignes:
                ligne.commande = commande
                ligne.prix_unitaire = ligne.produit.prix_unitaire
                ligne.save()
            return redirect('liste_commandes')
    else:
        form_commande = CommandeForm()
        formset_lignes = LigneCommandeFormSet(queryset=LigneCommande.objects.none(), prefix=prefix)

    context = {
        'form_commande': form_commande,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all()
    }
    return render(request, 'gestion/ajouter_commande.html', context)

def liste_commandes(request):
    commandes = Commande.objects.prefetch_related('lignes__produit')

    return render(request, 'gestion/liste_commandes.html', {'commandes': commandes})

def modifier_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)

    if request.method == 'POST':
        form_commande = CommandeForm(request.POST, instance=commande)
        formset_lignes = LigneCommandeFormSet(request.POST, instance=commande)

        if form_commande.is_valid() and formset_lignes.is_valid():
            commande = form_commande.save()

            lignes = formset_lignes.save(commit=False)
            for ligne in lignes:
                # Affecter automatiquement le prix unitaire à partir du produit
                ligne.prix_unitaire = ligne.produit.prix_unitaire
                ligne.save()

            # Supprimer les lignes marquées pour suppression
            for ligne in formset_lignes.deleted_objects:
                ligne.delete()

            return redirect('liste_commandes')
    else:
        form_commande = CommandeForm(instance=commande)
        formset_lignes = LigneCommandeFormSet(instance=commande)

    context = {
        'form_commande': form_commande,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all()
    }
    return render(request, 'gestion/modifier_commande.html', context)

def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)

    if request.method == 'POST':
        commande.delete()
        return redirect('liste_commandes')

    return render(request, 'gestion/commande_confirmer_suppression.html', {
        'commande': commande
    })

############################################################################################################
def exporter_commandes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_commandes.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontSize = 9

    # ======== En-tête encadré avec logo et infos =========
    logo_path = os.path.join(settings.BASE_DIR, "gestion", "static", "images", "logo_prestniayes.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=4*cm, height=4*cm)
    else:
        logo = Paragraph("", normal_style)

    entete_html = """
    <para align=left>
    <b>République du Sénégal</b><br/>
    <b>Entreprise Prest-Niayes</b><br/>
    Localisation : Notto Gouye Diama, Sénégal<br/>
    RC: SN THS 2018 A 3014 - NINEA: 006906400<br/>
    Téléphone : +221 77 477 17 07 | +221 77 996 96 56 | +221 76 016 91 94<br/>
    Email : mbayeb2@live.fr<br/>
    N° Compte LBA : SN04804001 000110340201 48<br/>
    N° Compte ECOBANK : 101390048001
    </para>
    """
    entete_paragraph = Paragraph(entete_html, normal_style)

    entete_table = Table([[logo, entete_paragraph]], colWidths=[4.5*cm, 11.5*cm])
    entete_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(entete_table)
    elements.append(Spacer(1, 20))

    # ======== Titre ========
    title = Paragraph("Liste des Commandes", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # ======== Tableau des commandes =========
    data = [['#', 'Client', 'Produits', 'Téléphone','Avance (F CFA)']]
    commandes = Commande.objects.all()

    for commande in commandes:
        produits_text = ""
        for ligne in commande.lignes.all():
            produits_text += f"- {ligne.quantite} {ligne.unite} de {ligne.produit.variete}<br/>"

        row = [
            str(commande.id),
            f"{commande.client.prenom} {commande.client.nom} ",

            Paragraph(produits_text, normal_style),
            f"{commande.client.telephone}  ",

            f"{commande.avance}"

        ]
        data.append(row)

    table = Table(data, colWidths=[30, 100, 260, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)

    return response
def exporter_commandes_prioritaires_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="commandes_prioritaires.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontSize = 9

    # --- En-tête professionnel (tu peux reprendre celui que tu as déjà)
    entete_html = """
    <para align=center>
    <b>République du Sénégal</b><br/>
    <b>Entreprise Prest-Niayes</b><br/>
    Localisation : Notto Gouye Diama, Sénégal<br/>
    RC: SN THS 2018 A 3014 - NINEA: 006906400<br/>
    Téléphone : +221 77 477 17 07 | +221 77 996 96 56 | +221 76 016 91 94<br/>
    Email : mbayeb2@live.fr<br/>
    N° Compte LBA : SN04804001 000110340201 48<br/>
    N° Compte ECOBANK : 101390048001
    </para>
    """
    entete_paragraph = Paragraph(entete_html, normal)
    entete_table = Table([[entete_paragraph]], colWidths=[500])
    entete_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(entete_table)
    elements.append(Spacer(1, 20))

    title = Paragraph("Commandes Prioritaires (Avance > 0)", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # --- Commandes filtrées
    commandes = Commande.objects.filter(avance__gt=0)

    data = [['#', 'Client', 'Produits', 'Avance (F CFA)','Téléphone']]
    for commande in commandes:
        produits_text = ""
        for ligne in commande.lignes.all():
            produits_text += f"- {ligne.quantite} {ligne.unite} de {ligne.produit.variete}<br/>"

        row = [
            str(commande.id),
            f"{commande.client.prenom} {commande.client.nom}",
            Paragraph(produits_text, normal),
            f"{commande.avance}",
             f"{commande.client.telephone}"

        ]
        data.append(row)

    table = Table(data, colWidths=[30, 100, 260, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(table)
    doc.build(elements)
    return response
#
def generer_facture_pdff(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_commande_{commande.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontSize = 9

    # --- En-tête entreprise ---
    entete_html = """
    <para align=center>
    <b>République du Sénégal</b><br/>
    <b>Entreprise Prest-Niayes</b><br/>
    Localisation : Notto Gouye Diama, Sénégal<br/>
    RC: SN THS 2018 A 3014 - NINEA: 006906400<br/>
    Téléphone : +221 77 477 17 07 | +221 77 996 96 56 | +221 76 016 91 94<br/>
    Email : mbayeb2@live.fr<br/>
    N° Compte LBA : SN04804001 000110340201 48<br/>
    N° Compte ECOBANK : 101390048001
    </para>
    """
    elements.append(Table([[Paragraph(entete_html, normal)]], colWidths=[500],
        style=[('BOX', (0,0), (-1,-1), 1, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER')]
    ))
    elements.append(Spacer(1, 12))

    # --- Infos facture ---
    client = commande.client
    info_html = f"""
    <b>Facture Commande N° {commande.id}</b><br/>
    Date : {commande.date_commande.strftime('%d/%m/%Y')}<br/>
    Client : {client.prenom} {client.nom}<br/>
    Téléphone : {client.telephone}<br/>
    """
    elements.append(Paragraph(info_html, normal))
    elements.append(Spacer(1, 12))

    # --- Tableau des produits commandés ---
    data = [['Produit', 'Quantité', 'Unité']]
    total = 0
    for ligne in commande.lignes.all():
        montant = ligne.quantite * ligne.prix_unitaire
        total += montant
        data.append([
            ligne.produit.variete,
            ligne.quantite,
            ligne.unite,
            #f"{ligne.prix_unitaire} F",
           # f"{montant} F"
        ])

    table = Table(data, colWidths=[160, 60, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # --- Résumé financier ---
    avance = commande.avance or 0
    resume_html = f"""
    <b>Avance : {avance} F</b><br/>
    """
    elements.append(Paragraph(resume_html, normal))
    elements.append(Spacer(1, 20))

    # --- Footer ---
    footer = Paragraph("<i>Merci pour votre confiance !</i>", styles['Italic'])
    elements.append(footer)

    doc.build(elements)
    return response

# views.pyfrom django.http import FileResponse

def exporter_commandes_par_client_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontSize = 9

   

    logo_path = os.path.join(settings.BASE_DIR, "gestion", "static", "images", "logo_prestniayes.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=4*cm, height=4*cm)
    else:
        logo = Paragraph("", normal_style)

    entete_html = """
    <para align=left>
    <b>République du Sénégal</b><br/>
    <b>Entreprise Prest-Niayes</b><br/>
    Localisation : Notto Gouye Diama, Sénégal<br/>
    RC: SN THS 2018 A 3014 - NINEA: 006906400<br/>
    Téléphone : +221 77 477 17 07 | +221 77 996 96 56 | +221 76 016 91 94<br/>
    Email : mbayeb2@live.fr<br/>
    N° Compte LBA : SN04804001 000110340201 48<br/>
    N° Compte ECOBANK : 101390048001
    </para>
    """
    entete_paragraph = Paragraph(entete_html, normal_style)

    entete_table = Table([[logo, entete_paragraph]], colWidths=[4.5*cm, 11.5*cm])
    entete_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(entete_table)
    elements.append(Spacer(1, 20))
    title = Paragraph("Liste des commandes par Client", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.5 * cm))

    grouped = {}
    for commande in Commande.objects.prefetch_related('lignes', 'client', 'lignes__produit'):
        client = commande.client
        grouped.setdefault(client, []).append(commande)

    for client, commandes in grouped.items():
        elements.append(Paragraph(f"<b>Client :</b> {client.prenom} {client.nom} {client.telephone}", styles['Heading3']))
        for commande in commandes:
            data = [["Produit", "Quantité", "Unité", "Prix unitaire", "Montant total"]]
            for ligne in commande.lignes.all():
                montant = ligne.quantite * ligne.prix_unitaire
                data.append([
                    str(ligne.produit),
                    str(ligne.quantite),
                    ligne.unite,
                    f"{ligne.prix_unitaire:.0f} F",
                    f"{montant:.0f} F"
                ])
            table = Table(data, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ]))
            elements.append(table)

            # Infos supplémentaires
            #elements.append(Paragraph(f"<b>Remise :</b> {commande.remise:.0f} F", styles['Normal']))
            elements.append(Paragraph(f"<b>Avance :</b> {commande.avance:.0f} F", styles['Normal']))
            elements.append(Paragraph(f"<b>Total :</b> {commande.total():.0f} F", styles['Normal']))
            elements.append(Paragraph(f"<b>Reste à payer :</b> {commande.reste_a_payer():.0f} F", styles['Normal']))
            elements.append(Spacer(1, 0.6 * cm))

        elements.append(Spacer(1, 1 * cm))

    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="commandes_par_client.pdf")
#######################################################################################################
def exporter_commandes_par_variete(request, variete_nom):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="commandes_{variete_nom}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontSize = 9

    title = Paragraph(f"Commandes pour la variété : <b>{variete_nom}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [['#', 'Client', 'Produits', 'Avance (F)', 'Téléphone']]

    commandes = Commande.objects.all()

    total_avance = 0
    total_quantite = 0
    ligne_index = 1

    for commande in commandes:
        lignes_variete = commande.lignes.filter(produit__variete__iexact=variete_nom)
        if lignes_variete.exists():
            produits_text = ""
            for ligne in lignes_variete:
                produits_text += f"- {ligne.quantite} {ligne.unite} de {ligne.produit.variete}<br/>"
                total_quantite += ligne.quantite

            total_avance += commande.avance or 0

            data.append([
                str(ligne_index),
                f"{commande.client.prenom} {commande.client.nom}",
                Paragraph(produits_text, normal),
                f"{commande.avance:,}",
                f"{commande.client.telephone}"
            ])
            ligne_index += 1

    # Ligne vide
    data.append(["", "", "", "", ""])

    # Ligne de total
    data.append([
        "", "TOTAL",
        f"{total_quantite} Sacs",  
        f"{total_avance:,} F",
        ""
    ])

    table = Table(data, colWidths=[30, 100, 180, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (-3,-1), (-2,-1), 'Helvetica-Bold'),  # Totaux en gras
    ]))

    elements.append(table)
    doc.build(elements)

    return response

#Ventre

def ajouter_vente(request):
    if request.method == 'POST':
        vente_form = VenteForm(request.POST)
        vente_temp = Vente()
        formset = LigneVenteFormSet(request.POST, instance=vente_temp)

        if vente_form.is_valid():
            vente = vente_form.save(commit=False)
            formset = LigneVenteFormSet(request.POST, instance=vente)

            if formset.is_valid():
                montant_total = 0
                vente.save()  # On sauvegarde la vente avant les lignes

                for form in formset:
                    ligne = form.save(commit=False)
                    ligne.vente = vente

                    # Calcul du montant ligne
                    prix_unitaire = ligne.produit.prix_unitaire
                    total_ligne = prix_unitaire * ligne.quantite - ligne.remise
                    montant_total += max(total_ligne, 0)

                    # Mise à jour stock
                    try:
                        stock = Stock.objects.get(produit=ligne.produit, depot=ligne.depot)
                        if stock.quantite < ligne.quantite:
                            messages.error(request,
                                f"Stock insuffisant pour {ligne.produit.nom} dans le dépôt {ligne.depot.nom}.")
                            # On annule la transaction en affichant la page avec erreurs
                            return render(request, 'gestion/liste_vente.html', {
                                'vente_form': vente_form,
                                'formset': formset,
                                'produits': Produit.objects.all(),
                            })
                        stock.quantite -= ligne.quantite
                        stock.save()
                    except Stock.DoesNotExist:
                        messages.error(request,
                            f"Le produit {ligne.produit.nom} n'existe pas dans le dépôt {ligne.depot.nom}.")
                        return render(request, 'gestion/ajouter_vente.html', {
                            'vente_form': vente_form,
                            'formset': formset,
                            'produits': Produit.objects.all(),
                        })

                    ligne.save()

                # Mise à jour montant total
                vente.montant_total = montant_total
                vente.save()

                messages.success(request, "Vente enregistrée avec succès.")
                return redirect('liste_ventes')

            else:
                messages.error(request, "Veuillez corriger les erreurs dans les lignes de vente.")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire de vente.")

    else:
        vente_form = VenteForm()
        formset = LigneVenteFormSet(instance=Vente())

    return render(request, 'gestion/ajouter_vente.html', {
        'vente_form': vente_form,
        'formset': formset,
        'produits': Produit.objects.all(),
    })


#Modifier vente

def modifier_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)

    if request.method == 'POST':
        vente_form = VenteForm(request.POST, instance=vente)
        formset = LigneVenteFormSet(request.POST, instance=vente)

        if vente_form.is_valid() and formset.is_valid():
            vente = vente_form.save(commit=False)
            lignes = formset.save(commit=False)

            montant_total = 0

            # Supprimer les lignes marquées à supprimer par le formset
            for ligne in formset.deleted_objects:
                ligne.delete()

            # Sauvegarder les lignes et calculer le montant total
            for ligne in lignes:
                ligne.vente = vente
                prix_unitaire = ligne.produit.prix_unitaire
                total_ligne = prix_unitaire * ligne.quantite - ligne.remise
                montant_total += max(total_ligne, 0)
                ligne.save()

            vente.montant_total = montant_total
            vente.save()

            messages.success(request, "Vente modifiée avec succès.")
            return redirect('liste_ventes')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire ou les lignes.")
    else:
        vente_form = VenteForm(instance=vente)
        formset = LigneVenteFormSet(instance=vente)

    return render(request, 'gestion/modifier_vente.html', {
        'vente_form': vente_form,
        'formset': formset,
        'produits': Produit.objects.all(),
        'vente': vente,
    })


#Supprimer une vente 

def supprimer_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    if request.method == 'POST':
        vente.delete()
        messages.success(request, "La vente a bien été supprimée.")
        return redirect('liste_ventes')
    return render(request, 'gestion/confirmer_suppression.html', {
        'objet': vente,
        'retour_url': reverse('liste_ventes'),
        'type_objet': 'vente',
    })

# Formset lié à la vente

def facture_vente(request, vente_id):
    vente = get_object_or_404(Vente, pk=vente_id)
    lignes = vente.lignes.all()
    html = render_to_string('gestion/facture.html', {
        'vente': vente,
        'lignes': lignes
    })
    return HttpResponse(html)
##############################

def exporter_ventes_variete_pdf(request, variete):
    response = HttpResponse(content_type='application/pdf')
    filename = f"liste_ventes_variete_{variete}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontSize = 9

    title = Paragraph(f"Liste des ventes pour la variété : <b>{variete}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # En-tête du tableau
    data = [['#', 'Client', 'Produits', 'Date', 'Total (F)']]

    ventes = Vente.objects.filter(lignes__produit__variete=variete).distinct()

    total_quantite = 0
    total_montant = 0
    ligne_index = 1

    for vente in ventes:
        produits_text = ""
        vente_quantite = 0
        for ligne in vente.lignes.all():
            if ligne.produit.variete.strip().lower() == variete.strip().lower():
                produits_text += f"- {ligne.quantite} sacs de {ligne.produit.variete}<br/>"
                total_quantite += ligne.quantite
                vente_quantite += ligne.quantite
        total_montant += vente.montant_total

        data.append([
            str(ligne_index),
            f"{vente.client.prenom} {vente.client.nom}",
            Paragraph(produits_text, normal),
            vente.date_vente.strftime('%d/%m/%Y') if vente.date_vente else '',
            f"{vente.montant_total:,.0f}"
        ])
        ligne_index += 1

    # Ligne vide
    data.append(["", "", "", "", ""])

    # Ligne de total
    data.append([
        "", "TOTAL",
        f"{total_quantite} sacs",
        "", f"{total_montant:,.0f} F"
    ])

    table = Table(data, colWidths=[30, 100, 200, 70, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),  # total en gras
    ]))

    elements.append(table)
    doc.build(elements)
    return response


def liste_ventes(request):
    client_nom = request.GET.get('client')
    ventes = Vente.objects.all().select_related('client', 'vendeur').prefetch_related('lignes__produit')

    if client_nom:
        ventes = ventes.filter(client__nom__icontains=client_nom)

    return render(request, 'gestion/liste_ventes.html', {
        'ventes': ventes,
        'client_nom': client_nom,
    })
#####

def exporter_ventes_client_pdf(request, client_nom): 
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ventes_{client_nom}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    normal = styles['Normal']

    title = Paragraph(f"Liste des ventes pour le client : <b>{client_nom}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # En-tête du tableau
    data = [['#', 'Date', 'Produits', 'Montant total (F)']]
    
    ventes = Vente.objects.filter(client__nom__iexact=client_nom)

    total_quantite = 0
    total_montant = 0

    for i, vente in enumerate(ventes, start=1):
        produits_text = ""
        for ligne in vente.lignes.all():
            produits_text += f"- {ligne.quantite} sacs de {ligne.produit.variete} <br/>"
            total_quantite += ligne.quantite
        total_montant += vente.montant_total

        data.append([
            str(i),
            vente.date_vente.strftime("%d/%m/%Y") if vente.date_vente else "",
            Paragraph(produits_text, normal),
            f"{vente.montant_total:,.0f}"
        ])

    # Ligne de séparation vide
    data.append(["", "", "", ""])
    
    # Ligne du total général
    data.append([
        "",  # vide
        "TOTAL",
        f"{total_quantite} sacs",
        f"{total_montant:,.0f} F"
    ])

    table = Table(data, colWidths=[30, 80, 180, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.green),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),  # total en gras
    ]))
    
    elements.append(table)
    doc.build(elements)
    return response

# facture

def rapport_journalier(request):
    aujourd_hui = now().date()
    ventes_du_jour = Vente.objects.filter(date_vente__date=aujourd_hui)

    total_journalier = sum(vente.montant_total for vente in ventes_du_jour)

    context = {
        'ventes': ventes_du_jour,
        'total_journalier': total_journalier,
        'date': aujourd_hui,
    }
    return render(request, 'gestion/rapport_journalier.html', context)




def generer_facture_pdf(request, vente_id):
    vente = get_object_or_404(Vente, id=vente_id)
    template_path = 'gestion/facture_pdf.html'

    # ✅ Trouver le chemin absolu du logo
    logo_path = finders.find('images/awa.jpg')
    logo_base64 = ""

    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode()

    context = {
        'vente': vente,
        'logo_base64': logo_base64,
    }

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{vente.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF')

    return response

def facture_proforma_view(request):
    if request.method == "POST":
        client_nom = request.POST.get("client_nom")
        client_entreprise = request.POST.get("client_entreprise")
        client_adresse = request.POST.get("client_adresse")
        lignes_json = request.POST.get("lignes")

        try:
            lignes = json.loads(lignes_json)
        except json.JSONDecodeError:
            lignes = []

        # Calculer montant par ligne et total
        total = 0
        for ligne in lignes:
            prix_unitaire = float(ligne.get("prix_unitaire", 0))
            quantite = int(ligne.get("quantite", 0))
            remise = float(ligne.get("remise", 0))
            montant = prix_unitaire * quantite * (1 - remise / 100)
            ligne["montant"] = round(montant, 2)
            total += montant
        total = round(total, 2)

        # Générer un numéro de facture unique (exemple simple)
        numero_facture = f"PF-{uuid.uuid4().hex[:6].upper()}"

        # Dates
        date_facture = datetime.today().strftime("%d/%m/%Y")
        date_validite = (datetime.today() + timedelta(days=10)).strftime("%d/%m/%Y")

        # Chemin absolu logo (à adapter selon ta config)

        logo_path = finders.find("images/awa.jpg")

        
        # Charger logo en base64
        logo_base64 = ""
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode()
        # Chemin du cachet/signature
        cachet_path = finders.find("images/cachet.jpeg")
        cachet_signature_base64 = ""
        if cachet_path and os.path.exists(cachet_path):
            with open(cachet_path, "rb") as image_file:
                cachet_signature_base64 = base64.b64encode(image_file.read()).decode()

        context = {
            "client_nom": client_nom,
            "client_entreprise": client_entreprise,
            "client_adresse": client_adresse,
            "lignes": lignes,
            "total": total,
            "numero_facture": numero_facture,
            "date_facture": date_facture,
            "date_validite": date_validite,
            "logo_base64": logo_base64,
            "cachet_signature_base64": cachet_signature_base64,
        }

        template = get_template("gestion/facture_proforma_pdf.html")
        html = template.render(context)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="facture_proforma.pdf"'

        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
        if pisa_status.err:
            return HttpResponse("Une erreur est survenue lors de la génération du PDF.", status=500)

        return response

    # En GET, afficher le formulaire de saisie
    return render(request, "gestion/facture_proforma_form.html")
#Bon Commande 
def bon_commande_view(request):
    if request.method == "POST":
        fournisseur_nom = request.POST.get("fournisseur_nom")
        fournisseur_entreprise = request.POST.get("fournisseur_entreprise")
        fournisseur_adresse = request.POST.get("fournisseur_adresse")
        numero_vehicule = request.POST.get("numero_vehicule")
        lignes_json = request.POST.get("lignes")

        try:
            lignes = json.loads(lignes_json)
        except json.JSONDecodeError:
            lignes = []

        total = 0
        for ligne in lignes:
            prix_unitaire = float(ligne.get("prix_unitaire", 0))
            quantite = int(ligne.get("quantite", 0))
            montant = prix_unitaire * quantite
            ligne["montant"] = round(montant, 2)
            total += montant
        total = round(total, 2)

        numero_bc = f"BC-{uuid.uuid4().hex[:6].upper()}"
        date_commande_str = request.POST.get("date_commande")
        try:
            date_commande = datetime.strptime(date_commande_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            date_commande = datetime.today().date()

        # ✅ toujours défini après avoir obtenu une date valide
        date_livraison = date_commande + timedelta(days=7)


        # Sauvegarde en base
        bon = BonCommande.objects.create(
            numero=numero_bc,
            date_commande=date_commande,
            date_livraison=date_livraison,
            fournisseur_nom=fournisseur_nom,
            fournisseur_entreprise=fournisseur_entreprise,
            fournisseur_adresse=fournisseur_adresse,
            numero_vehicule=numero_vehicule,
            montant_total=total
        )

        for ligne in lignes:
            LigneBonCommande.objects.create(
                bon_commande=bon,
                produit=ligne["produit"],
                quantite=int(ligne["quantite"]),
                prix_unitaire=float(ligne["prix_unitaire"]),
                montant=float(ligne["montant"])
            )

        # Génération PDF
        logo_base64 = ""
        cachet_signature_base64 = ""

        logo_path = finders.find("images/awa.jpg")
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img:
                logo_base64 = base64.b64encode(img.read()).decode()

        cachet_path = finders.find("images/cachet_signature.png")
        if cachet_path and os.path.exists(cachet_path):
            with open(cachet_path, "rb") as image_file:
                cachet_signature_base64 = base64.b64encode(image_file.read()).decode()

        context = {
            "fournisseur_nom": fournisseur_nom,
            "fournisseur_entreprise": fournisseur_entreprise,
            "fournisseur_adresse": fournisseur_adresse,
            "numero_vehicule": numero_vehicule,
            "lignes": lignes,
            "total": total,
            "numero_bc": numero_bc,
            "date_commande": date_commande.strftime("%d/%m/%Y"),
            "date_livraison": date_livraison.strftime("%d/%m/%Y"),
            "logo_base64": logo_base64,
            "cachet_signature_base64": cachet_signature_base64,
        }

        template = get_template("gestion/bon_commande_pdf.html")
        html = template.render(context)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{numero_bc}.pdf"'
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
        if pisa_status.err:
            return HttpResponse("Erreur lors de la génération du PDF.", status=500)

        return response

    return render(request, "gestion/bon_commande_form.html")
def liste_bons_commande(request):
    bons = BonCommande.objects.all().order_by('-date_commande')
    return render(request, "gestion/liste_bons_commande.html", {"bons": bons})

####################################################################################################
def accueil(request):
    return render(request, 'gestion/home.html')

def ajouter_compte(request):
    if request.method == 'POST':
        form = CompteBancaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_comptes')
    else:
        form = CompteBancaireForm()
    return render(request, 'gestion/ajouter_compte.html', {'form': form})

def liste_comptes(request):
    comptes = CompteBancaire.objects.all()
    return render(request, 'gestion/liste_comptes.html', {'comptes': comptes})


def ajouter_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_transactions')
    else:
        form = TransactionForm()
    return render(request, 'gestion/ajouter_transaction.html', {'form': form})
def liste_transactions(request):
    comptes = CompteBancaire.objects.all()
    transactions = Transaction.objects.all().select_related('compte')

    # Récupération des filtres
    compte_id = request.GET.get('compte')
    type_transaction = request.GET.get('type')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    # Application des filtres
    if compte_id:
        transactions = transactions.filter(compte__id=compte_id)
    if type_transaction:
        transactions = transactions.filter(type_transaction=type_transaction)
    if date_debut:
        transactions = transactions.filter(date_transaction__date__gte=parse_date(date_debut))
    if date_fin:
        transactions = transactions.filter(date_transaction__date__lte=parse_date(date_fin))

    transactions = transactions.order_by('-date_transaction')
    # Totaux

    total_entrees = transactions.filter(type_transaction='entrée').aggregate(total=Sum('montant'))['total'] or 0
    total_sorties = transactions.filter(type_transaction='sortie').aggregate(total=Sum('montant'))['total'] or 0

    solde_net = total_entrees - total_sorties


    context = {
    'transactions': transactions,
    'comptes': comptes,
    'compte_id': compte_id,
    'type_transaction': type_transaction,
    'date_debut': date_debut,
    'date_fin': date_fin,
    'total_entrees': total_entrees,
    'total_sorties': total_sorties,
    'solde_net': solde_net,
    }

    return render(request, 'gestion/liste_transactions.html', context)
def modifier_compte(request, compte_id):
    compte = get_object_or_404(CompteBancaire, id=compte_id)
    if request.method == 'POST':
        form = CompteBancaireForm(request.POST, instance=compte)
        if form.is_valid():
            form.save()
            return redirect('liste_comptes')
    else:
        form = CompteBancaireForm(instance=compte)
    return render(request, 'gestion/modifier_compte.html', {'form': form, 'compte': compte})

def supprimer_compte(request, compte_id):
    compte = get_object_or_404(CompteBancaire, id=compte_id)
    if request.method == 'POST':
        compte.delete()
        return redirect('liste_comptes')
    return render(request, 'gestion/supprimer_compte.html', {'compte': compte})

# bordeau
def ajouter_bordereau(request):
    if request.method == 'POST':
        form = BordereauLivraisonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Conversion des types non sérialisables
            session_data = {
                'client': data['client'],
                'date': data['date'].strftime('%Y-%m-%d'),
                'destination': data['destination'],
                'numero_vehicule': data['numero_vehicule'],
                'nature_produit': data['nature_produit'],
                'quantite': float(data['quantite']) if isinstance(data['quantite'], Decimal) else data['quantite'],
                'poids': float(data['poids']) if isinstance(data['poids'], Decimal) else data['poids'],
            }

            request.session['bordereau'] = session_data
            return redirect('bordereau_livraison_pdf')
    else:
        form = BordereauLivraisonForm()

    return render(request, 'gestion/ajouter_bordereau.html', {'form': form})


def bordereau_livraison_pdf(request):
    data = request.session.get('bordereau')
    if not data:
        return HttpResponse("Aucune donnée de bordereau disponible", status=400)

    numero_bordereau = f"BL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    logo_path = finders.find("images/awa.jpg")
    logo_base64 = ""
    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as img:
            logo_base64 = base64.b64encode(img.read()).decode()

    context = {
        "client": data['client'],
        "date": datetime.strptime(data['date'], "%Y-%m-%d").strftime("%d/%m/%Y"),
        "destination": data['destination'],
        "numero_vehicule": data['numero_vehicule'],
        "nature_produit": data['nature_produit'],
        "quantite": data['quantite'],
        "poids": data['poids'],
        "numero_bordereau": numero_bordereau,
        "logo_base64": logo_base64,
    }

    template = get_template("gestion/bordereau_livraison_pdf.html")
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bordereau_{numero_bordereau}.pdf"'
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)
    return response
#connexion 
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == 'vendeur':
                return redirect('dashboard_vendeur')
            elif user.role == 'comptable':
                return redirect('dashboard_comptable')
            elif user.role == 'admin':
                return redirect('accueil')  # ou dashboard_admin si tu veux

        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "registration/login.html")


@login_required
@role_required('vendeur')
def dashboard_vendeur(request):
    ventes = Vente.objects.all().order_by('-date_vente')[:5]  # Récupère les 5 dernières ventes
    produits = Produit.objects.all()

    return render(request, 'gestion/dashboard_vendeur.html', {
        'ventes': ventes,
        'produits': produits,
    })
def logout_view(request):
    logout(request)
    return redirect('login')


def lettre_voiture_pdf(request):
    
    logo_path = finders.find("images/awa.jpg")
    logo_base64 = ""
    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as img:
            logo_base64 = base64.b64encode(img.read()).decode()

    if request.method == "POST":
        context = {
            "nature": request.POST.get("nature"),
            "origine": request.POST.get("origine"),
            "poids_expediteur": request.POST.get("poids_expediteur"),
            "transporteur": request.POST.get("transporteur"),
            "chauffeur": request.POST.get("chauffeur"),
            "numero_camion": request.POST.get("numero_camion"),
            "date_expedition": request.POST.get("date_expedition"),
            "logo_base64": logo_base64,
        }

        # Charger le template HTML
        template = get_template("gestion/lettre_voiture_pdf.html")
        html = template.render(context)

        # Générer le PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=lettre_voiture.pdf"
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)

        if pisa_status.err:
            return HttpResponse("Erreur lors de la génération du PDF", status=500)

        return response
    else:
        # Si GET, afficher le formulaire
        return render(request, "gestion/lettre_voiture.html")
    
  
def lettre_voiture(request):
    if request.method == "POST":
        context = {
            "nature": request.POST.get("nature"),
            "origine": request.POST.get("origine"),
            "poids_expediteur": request.POST.get("poids_expediteur"),
            "transporteur": request.POST.get("transporteur"),
            "chauffeur": request.POST.get("chauffeur"),
            "numero_camion": request.POST.get("numero_camion"),
            "date_expedition": request.POST.get("date_expedition"),
        }

        # Rendu HTML -> PDF
        template = get_template("gestion/lettre_voiture_pdf.html")
        html = template.render(context)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=lettre_voiture.pdf"
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
        if pisa_status.err:
            return HttpResponse("Erreur de génération PDF", status=500)

        return response

    return render(request, "gestion/lettre_de_voiture.html")


def ajouter_depot(request):
    if request.method == 'POST':
        form = DepotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_depots')
    else:
        form = DepotForm()
    return render(request, 'gestion/ajouter_depot.html', {'form': form})

def liste_depots(request):
    depots = Depot.objects.all()
    return render(request, 'gestion/liste_depots.html', {'depots': depots})

def modifier_depot(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    if request.method == 'POST':
        form = DepotForm(request.POST, instance=depot)
        if form.is_valid():
            form.save()
            return redirect('liste_depots')
    else:
        form = DepotForm(instance=depot)
    return render(request, 'gestion/modifier_depot.html', {'form': form, 'depot': depot})

def supprimer_depot(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    if request.method == 'POST':
        depot.delete()
        return redirect('liste_depots')
    return render(request, 'gestion/confirmer_suppression.html', {
        'objet': depot,
        'retour_url': reverse('liste_depots')
    })
#Reception

def ajouter_reception(request):
    if request.method == 'POST':
        form = ReceptionForm(request.POST)
        if form.is_valid():
            form.save()  # Le stock est mis à jour automatiquement
            return redirect('liste_receptions')  
    else:
        form = ReceptionForm()
    return render(request, 'gestion/ajouter_reception.html', {'form': form})

def liste_receptions(request):
    produit_id = request.GET.get('produit')
    depot_id = request.GET.get('depot')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    receptions = Reception.objects.select_related('produit', 'depot').all()

    # Filtres
    if produit_id:
        receptions = receptions.filter(produit__id=produit_id)
    if depot_id:
        receptions = receptions.filter(depot__id=depot_id)
    if date_debut:
        receptions = receptions.filter(date_reception__date__gte=date_debut)
    if date_fin:
        receptions = receptions.filter(date_reception__date__lte=date_fin)

    receptions = receptions.order_by('-date_reception')

    context = {
        'receptions': receptions,
        'produits': Produit.objects.all(),
        'depots': Depot.objects.all(),
        'produit_filtre': produit_id,
        'depot_filtre': depot_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    return render(request, 'gestion/liste_receptions.html', context)

def modifier_reception(request, pk):
    reception = get_object_or_404(Reception, pk=pk)
    ancienne_quantite = reception.quantite  # Pour recalcul du stock

    if request.method == 'POST':
        form = ReceptionForm(request.POST, instance=reception)
        if form.is_valid():
            reception = form.save(commit=False)

            # Retirer l’ancienne quantité du stock
            ancien_stock = Stock.objects.get(produit=reception.produit, depot=reception.depot)
            ancien_stock.quantite -= ancienne_quantite
            ancien_stock.save()

            # Ajouter la nouvelle quantité
            reception.save()  # va déclencher .save() et re-ajouter la quantité
            return redirect('liste_receptions')
    else:
        form = ReceptionForm(instance=reception)

    return render(request, 'gestion/modifier_reception.html', {
        'form': form,
        'reception': reception
    })
def supprimer_reception(request, pk):
    reception = get_object_or_404(Reception, pk=pk)

    if request.method == 'POST':
        # Retirer du stock avant suppression
        stock = Stock.objects.get(produit=reception.produit, depot=reception.depot)
        stock.quantite -= reception.quantite
        stock.save()

        reception.delete()
        return redirect('liste_receptions')

    return render(request, 'gestion/confirmer_suppression.html', {
        'objet': reception,
        'retour_url': reverse('liste_receptions')
    })
#Stock
def ajouter_ou_modifier_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            produit = form.cleaned_data['produit']
            depot = form.cleaned_data['depot']
            quantite = form.cleaned_data['quantite']

            stock, created = Stock.objects.get_or_create(produit=produit, depot=depot, defaults={'quantite': 0})
            stock.quantite += quantite
            stock.save()

            if created:
                messages.success(request, f"Stock créé: {produit.nom} dans {depot.nom} = {stock.quantite}")
            else:
                messages.success(request, f"Stock mis à jour: {produit.nom} dans {depot.nom} = {stock.quantite}")
            return redirect('liste_stocks')  # à adapter selon ta route
    else:
        form = StockForm()

    return render(request, 'gestion/ajouter_ou_modifier_stock.html', {'form': form})

def ajouter_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock enregistré avec succès.")
            return redirect('liste_stocks')  # ou une autre page
    else:
        form = StockForm()
    return render(request, 'gestion/ajouter_stock.html', {'form': form})

def liste_stocks(request):
    stocks = Stock.objects.select_related('produit', 'depot').all().order_by('depot__nom', 'produit__nom')
    return render(request, 'gestion/liste_stocks.html', {'stocks': stocks})

def modifier_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock modifié avec succès.")
            return redirect('liste_stocks')
    else:
        form = StockForm(instance=stock)
    return render(request, 'gestion/modifier_stock.html', {'form': form})

def supprimer_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, "Stock supprimé avec succès.")
        return redirect('liste_stocks')
    return render(request, 'gestion/confirmer_suppression.html', {'objet': stock, 'retour_url': 'liste_stocks'})