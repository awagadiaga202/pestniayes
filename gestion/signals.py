from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import LigneVente, Stock

@receiver(pre_save, sender=LigneVente)
def ajuster_stock_vente(sender, instance, **kwargs):
    if instance.pk:
        ancienne_ligne = LigneVente.objects.get(pk=instance.pk)
        diff = instance.quantite - ancienne_ligne.quantite
    else:
        diff = instance.quantite

    stock = Stock.objects.get(produit=instance.produit, depot=instance.depot)

    if stock.quantite < diff:
        raise ValueError("Stock insuffisant dans le dépôt.")

    stock.quantite -= diff
    stock.save()

@receiver(post_delete, sender=LigneVente)
def restaurer_stock_vente(sender, instance, **kwargs):
    stock = Stock.objects.get(produit=instance.produit, depot=instance.depot)
    stock.quantite += instance.quantite
    stock.save()
