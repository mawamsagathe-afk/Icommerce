from django.contrib import admin

from .models import (
    Client,
    Categorie,
    Commande,
    LieuLivraison,
    LigneCommande,
    ModePaiement,
    Paiement,
    Produit,
)


# -----------------------------
# CATÉGORIE
# -----------------------------
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)


# -----------------------------
# PRODUIT
# -----------------------------
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id','designation','categorie','stock','prix_achat','prix_vente',
                    'image','description',)
    list_filter = ('categorie',)
    search_fields = ('designation',)


# -----------------------------
# CLIENT
# -----------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'nom',
        'telephone',
    )

    search_fields = (
        'nom',
        'telephone',
        'user__username',
        'user__email',
    )

    list_per_page = 20


# -----------------------------
# LIEU DE LIVRAISON
# -----------------------------
@admin.register(LieuLivraison)
class LieuLivraisonAdmin(admin.ModelAdmin):
    list_display = ( 'id','ville','quartier','frais',)
    list_filter = ('ville',)
    search_fields = ('ville','quartier',)
    ordering = ('ville', 'quartier')


# -----------------------------
# LIGNE DE COMMANDE
# -----------------------------
@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('id','commande','produit','quantite','prix_unitaire',)
    list_filter = ('produit',)
    search_fields = ('commande__id','produit__designation',)
    
    
@admin.register(ModePaiement)
class ModePaiementAdmin(admin.ModelAdmin):
    list_display = ('nom',)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'commande',
        'mode',
        'montant',
        'statut',
        'date_paiement',
    )

    list_filter = (
        'statut',
        'mode',
    )

    search_fields = (
        'commande__id',
    )

# -----------------------------
# COMMANDE
# -----------------------------
@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id','client','lieu_livraison','date_commande','statut',)
    list_filter = ('statut','date_commande','lieu_livraison__ville')
    search_fields = ('client__user__username','client__user__email',)
    ordering = ('-date_commande',)
    readonly_fields = ('date_commande',)
    fieldsets = (
        (
            'Informations de la commande',
            {
                'fields': ('client','lieu_livraison','statut',)
            }
        ),
        (
            'Date',
            {
                'fields': (
                    'date_commande',
                )
            }
        ),
    )

