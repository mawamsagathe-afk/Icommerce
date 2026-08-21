from django.urls import path
from . import views

app_name = 'vente'


urlpatterns = [

    # =========================================================
    # ACCUEIL / CATALOGUE
    # =========================================================

    path(
        '',
        views.catalogue,
        name='accueil'
    ),

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


    # =========================================================
    # PANIER
    # =========================================================

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

    path(
        'panier/valider/',
        views.valider_commande,
        name='valider_commande'
    ),


    # =========================================================
    # CONNEXION / INSCRIPTION
    # =========================================================

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


    # =========================================================
    # COMMANDES
    # =========================================================

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


    # =========================================================
    # TABLEAU DE BORD CLIENT
    # =========================================================

    path(
        'tableau-bord/',
        views.tableau_bord_client,
        name='tableau_bord_client'
    ),


    # =========================================================
    # TABLEAU DE BORD ADMIN
    # =========================================================

    path(
        'tableaud-de-bord/admin/',
        views.tableau_bord_admin,
        name='tableau_bord_admin'
    ),


    # =========================================================
    # GESTION ADMIN
    # =========================================================

    path(
        'gestion/produits/',
        views.gestion_produits,
        name='gestion_produits'
    ),

    path(
        'gestion/categories/',
        views.gestion_categories,
        name='gestion_categories'
    ),

    path(
        'gestion/clients/',
        views.gestion_clients,
        name='gestion_clients'
    ),

    path(
        'gestion/commandes/',
        views.gestion_commandes,
        name='gestion_commandes'
    ),


    # =========================================================
    # GESTION DES PRODUITS - ADMIN
    # =========================================================

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
    
    path(
    'gestion/categories/',
    views.gestion_categories,
    name='gestion_categories'
),
    
    path(
    'gestion/categories/ajouter/',
    views.ajouter_categorie,
    name='ajouter_categorie'
),

path(
    'gestion/categories/modifier/<int:categorie_id>/',
    views.modifier_categorie,
    name='modifier_categorie'
),

path(
    'gestion/categories/supprimer/<int:categorie_id>/',
    views.supprimer_categorie,
    name='supprimer_categorie'
),


    path(
        'gestion/clients/ajouter/',
        views.ajouter_client,
        name='ajouter_client'
    ),

    path(
        'gestion/clients/supprimer/<int:client_id>/',
        views.supprimer_client,
        name='supprimer_client'
    ),
    
path(
    "gestion/produits/ajouter/",
    views.ajouter_produit,
    name="ajouter_produit"
),

path(
    "gestion/produits/modifier/<int:produit_id>/",
    views.modifier_produit,
    name="modifier_produit"
),

path(
    "gestion/produits/supprimer/<int:produit_id>/",
    views.supprimer_produit,
    name="supprimer_produit"
),
path(
    'gestion/produits/',
    views.gestion_produits,
    name='gestion_produits'
),

path(
    'gestion/commandes/<int:commande_id>/valider/',
    views.admin_valider_commande,
    name='admin_valider_commande'
),
path(
    'gestion/commandes/reinitialiser/',
    views.reinitialiser_commandes,
    name='reinitialiser_commandes'
),

path(
    "gestion/notifications/",
    views.notifications_admin,
    name="notifications_admin"
),

path(
    "gestion/clients/reinitialiser/",
    views.reinitialiser_clients,
    name="reinitialiser_clients"
),

]