from django.urls import path
from . import views

app_name = 'vente'

urlpatterns = [

    # ==========================================
    # ACCUEIL
    # ==========================================

    path(
        '',
        views.catalogue,
        name='accueil'
    ),

    # ==========================================
    # CATALOGUE
    # ==========================================

    path(
        'catalogue/',
        views.catalogue,
        name='catalogue'
    ),

    path(
        'produit/<int:produit_id>/',
        views.produit_detail,
        name='produit_detail'
    ),

    # ==========================================
    # PANIER
    # ==========================================

    path(
        'panier/',
        views.voir_panier,
        name='voir_panier'
    ),

    path(
        'panier/ajouter/<int:produit_id>/',
        views.ajouter_au_panier,
        name='ajouter_au_panier'
    ),

    path(
        'panier/retirer/<int:produit_id>/',
        views.retirer_du_panier,
        name='retirer_du_panier'
    ),

    path(
        'panier/vider/',
        views.vider_panier,
        name='vider_panier'
    ),

    # Création de la commande depuis le panier
    path(
        'panier/valider/',
        views.valider_commande,
        name='valider_commande'
    ),

    # ==========================================
    # CONNEXION
    # ==========================================

    path(
        'connexion/',
        views.Login_user,
        name='login_user'
    ),

    path(
        'inscription/',
        views.inscription,
        name='inscription'
    ),

    # ==========================================
    # COMMANDES
    # ==========================================

    path(
        'commande/<int:commande_id>/',
        views.detail_commande,
        name='detail_commande'
    ),

    path(
        'commande/<int:commande_id>/annuler/',
        views.annuler_commande,
        name='annuler_commande'
    ),

    # ⭐ NOUVELLE URL POUR VALIDER UNE COMMANDE
    path(
        'commande/<int:commande_id>/valider/',
        views.confirmer_commande,
        name='confirmer_commande'
    ),

    path(
        'mes-commandes/',
        views.mes_commandes,
        name='mes_commandes'
    ),

    # ==========================================
    # TABLEAU DE BORD
    # ==========================================

    path(
        'tableau_bord/',
        views.dashboard,
        name='dashboard'
    ),
    
    path(
    'tableau-de-bord/',
    views.dashboard,
    name='dashboard'
),

path(
    'tableau-de-bord/produit/ajouter/',
    views.ajouter_produit,
    name='ajouter_produit'
),

path(
    'tableau-de-bord/produit/<int:produit_id>/modifier/',
    views.modifier_produit,
    name='modifier_produit'
),

path(
    'tableau-de-bord/produit/<int:produit_id>/supprimer/',
    views.supprimer_produit,
    name='supprimer_produit'
),
]