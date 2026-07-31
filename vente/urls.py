
from django.urls import path
from . import views

app_name = 'vente'

urlpatterns = [
    # Catalogue & Détails Produits
    path('', views.Login_user, name='Login_user'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('produit/<int:produit_id>/', views.produit_detail, name='produit_detail'),

    # Gestion du Panier
    path('panier/', views.voir_panier, name='voir_panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/retirer/<int:produit_id>/', views.retirer_du_panier, name='retirer_du_panier'),
    path('panier/valider/', views.valider_commande, name='valider_commande'),

    # Authentification & Inscription
    path('connexion/', views.Login_user, name='login_user'),
    path('inscription/', views.inscription, name='inscription'),
]