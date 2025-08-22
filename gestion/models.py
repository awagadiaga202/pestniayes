from django.db import models
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser,Group,Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
# Classe Utilisateur
class Utilisateur(AbstractUser):
    ROLES = [
        ('admin', 'Administrateur'),
        ('vendeur', 'Vendeur'),
        ('comptable', 'Comptable'),
    ]
    role = models.CharField(max_length=20, choices=ROLES)

    groups = models.ManyToManyField(
        Group,
        related_name='utilisateurs_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='utilisateurs_permissions',
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# 2. Client
class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True)
    numero_piece_identite = models.CharField(max_length=50, verbose_name="Numéro de pièce d'identité")
    def __str__(self):
        return f"{self.prenom} {self.nom}"

# 3. Fournisseur

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    entreprise = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.entreprise

# 4. Produit

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    variete = models.CharField(max_length=100)  # Choix dynamiques via JS
    description = models.TextField(blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    UNITE_CHOIX = [
        ('tonne', 'Tonne'),
        ('sac', 'Sac'),
    ]

    unite_stock = models.CharField(max_length=10, choices=UNITE_CHOIX)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} - {self.variete}"
     # ✅ Stock total calculé dynamiquement
    def stock_total(self):
        return sum(stock.quantite for stock in self.stock_set.all())
#
#Depot 
class Depot(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField(blank=True)

    def __str__(self):
        return self.nom
#Stock
class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('produit', 'depot')
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"


    def __str__(self):
        return f"{self.produit.nom} - {self.depot.nom} : {self.quantite}"
#Reception 
class Reception(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    date_reception = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        stock, _ = Stock.objects.get_or_create(produit=self.produit, depot=self.depot)
        stock.quantite += self.quantite
        stock.save()
# 5. Commande
class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    est_validee = models.BooleanField(default=False)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.nom}"

    def total_sans_remise(self):
        return sum(ligne.quantite * ligne.prix_unitaire for ligne in self.lignes.all())

    def total(self):
        return self.total_sans_remise() - self.remise

    def reste_a_payer(self):
        return self.total() - self.avance

class LigneCommande(models.Model):
    UNITE_CHOICES = [
        ('sac', 'Sac'),
        ('tonne', 'Tonne'),
    ]

    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    unite = models.CharField(max_length=20, choices=UNITE_CHOICES)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.quantite} {self.unite} de {self.produit.nom}"
# 6. Vente

class Vente(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    date_vente = models.DateTimeField(default=timezone.now)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    


    commentaire = models.TextField(blank=True, null=True)
    
    VENTE_TYPE = [
        ('directe', 'Vente directe'),
        ('commande', 'Vente sur commande'),
    ]
    type_vente = models.CharField(max_length=20, choices=VENTE_TYPE, default='directe')

    mode_paiement = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('transfert', 'Transfert'),
        ('chèque', 'Chèque')
    ])
    
    vendeur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Vente #{self.id} - {self.client.nom}"
  

class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name="lignes")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    @property
    def montant_total(self):
            remise = self.remise or 0
            total = (self.produit.prix_unitaire * self.quantite) - remise
            return max(total, 0)


# 7. Paiement
class Paiement(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('transfert', 'Transfert'), ('chèque', 'Chèque')])
    

# 8. CompteBancaire
class CompteBancaire(models.Model):
    nom_banque = models.CharField(max_length=100)
    numero_compte = models.CharField(max_length=50)
    solde = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nom_banque} - {self.numero_compte}"

# 9. Transaction
class Transaction(models.Model):
    compte = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    TYPE_CHOICES = [('entrée', 'Entrée'), ('sortie', 'Sortie')]
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    date_transaction = models.DateTimeField()


    def __str__(self):
        return f"{self.type_transaction} - {self.montant} F"
    def save(self, *args, **kwargs):
        if self.pk is None:  # Nouvelle transaction uniquement
            if self.type_transaction == 'entrée':
                self.compte.solde += self.montant
            elif self.type_transaction == 'sortie':
                if self.compte.solde >= self.montant:
                    self.compte.solde -= self.montant
                else:
                    raise ValueError("Fonds insuffisants pour effectuer la sortie.")
            self.compte.save()
        super().save(*args, **kwargs)

# models.py
class BordereauLivraison(models.Model):
    client = models.CharField(max_length=100)

    date = models.DateField()
    destination = models.CharField(max_length=200)
    numero_vehicule = models.CharField(max_length=50)
    nature_produit = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    poids = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bordereau {self.id} - {self.date} - {self.destination}"

#Bon de commande 

class BonCommande(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    date_commande = models.DateField()  # <- ici
    date_livraison = models.DateField()
    fournisseur_nom = models.CharField(max_length=100)
    fournisseur_entreprise = models.CharField(max_length=100)
    fournisseur_adresse = models.TextField()
    numero_vehicule = models.CharField(max_length=50, blank=True, null=True)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.numero


class LigneBonCommande(models.Model):
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.CharField(max_length=100)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    montant = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.produit} - {self.quantite} x {self.prix_unitaire}"



