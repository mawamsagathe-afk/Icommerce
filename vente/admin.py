
from django.contrib import admin

from vente.models import  Categorie, Client, Commande, LieuLivraison, LigneCommande, Livraison, ModePaiement, Paiement, Produit

# Register your models here.

    
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display=('categorie','designation','prix_achat','prix_vente', 'stock', 'image', 'description')
    list_fields = ('categorie', 'Produit')
    list_filter=('categorie',)

class LigneCommandeInline(admin.TabularInline):
    """Permet d'ajouter/modifier des produits directement depuis la fiche Commande."""
    model = LigneCommande
    extra = 1  # Nombre de lignes vides affichées par défaut
    fields = ('produit', 'quantite', 'prix_unitaire')


# --- CONFIGURATIONS DES MODÈLES ---

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone')
    search_fields = ('nom', 'prenom', 'email', 'telephone')
    list_per_page = 20


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)

# @admin.register(Produit)
# class ProduitAdmin(admin.ModelAdmin):
#     list_display = ('designation', 'categorie', 'prix', 'stock')
#     list_filter = ('categorie',)
#     search_fields = ('designation',)
#     list_editable = ('prix', 'stock')  # Permet de modifier le prix et le stock directement depuis la liste
#     list_per_page = 20


@admin.register(LieuLivraison)
class LieuLivraisonAdmin(admin.ModelAdmin):
    list_display = ('ville', 'quartier', 'frais')
    list_filter = ('ville',)
    search_fields = ('ville', 'quartier')


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'lieu_livraison', 'date_commande', 'statut')
    list_filter = ('statut', 'date_commande', 'lieu_livraison__ville')
    search_fields = ('client__nom', 'client__prenom', 'id')
    date_hierarchy = 'date_commande'  # Ajoute une navigation temporelle en haut de page
    inlines = [LigneCommandeInline]  # Intègre la gestion des produits commandés


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire')
    list_filter = ('produit__categorie',)


@admin.register(ModePaiement)
class ModePaiementAdmin(admin.ModelAdmin):
    list_display = ('nom',)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('commande', 'mode_paiement', 'montant', 'date_paiement', 'etat')
    list_filter = ('etat', 'mode_paiement', 'date_paiement')
    search_fields = ('commande__id', 'commande__client__nom')


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('commande', 'date_livraison', 'etat')
    list_filter = ('etat', 'date_livraison')
    search_fields = ('commande__id',)
    
    