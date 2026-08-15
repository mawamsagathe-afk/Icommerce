from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Sum

from .models import (
    Produit,
    Categorie,
    Client,
    LieuLivraison,
    Commande,
    LigneCommande,
)


# =========================================================
# CATALOGUE
# =========================================================

def catalogue(request):

    produits = Produit.objects.all()
    categories = Categorie.objects.all()

    # Recherche
    query = request.GET.get('q')

    if query:
        produits = produits.filter(
            designation__icontains=query
        )

    # Filtre par catégorie
    categorie_id = request.GET.get('categorie')

    if categorie_id:
        produits = produits.filter(
            categorie_id=categorie_id
        )

    context = {
        'produits': produits,
        'categories': categories,
    }

    return render(
        request,
        'vente/catalogue.html',
        context
    )


# =========================================================
# DETAIL PRODUIT
# =========================================================

def produit_detail(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id
    )

    return render(
        request,
        'vente/produit_detail.html',
        {
            'produit': produit
        }
    )


# =========================================================
# VOIR LE PANIER
# =========================================================

@login_required
def voir_panier(request):

    panier = request.session.get('panier', {})

    produits = []
    total = Decimal('0.00')

    for produit_id, quantite in panier.items():

        produit = get_object_or_404(
            Produit,
            id=int(produit_id)
        )

        quantite = int(quantite)

        sous_total = produit.prix_vente * quantite

        produits.append({
            'produit': produit,
            'quantite': quantite,
            'sous_total': sous_total,
        })

        total += sous_total

    return render(
        request,
        'vente/panier.html',
        {
            'produits': produits,
            'total': total,
        }
    )


# =========================================================
# AJOUTER AU PANIER
# =========================================================

@login_required
def ajouter_au_panier(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id
    )

    panier = request.session.get('panier', {})

    produit_id_str = str(produit_id)

    quantite_actuelle = int(
        panier.get(produit_id_str, 0)
    )

    nouvelle_quantite = quantite_actuelle + 1

    # Vérification du stock
    if nouvelle_quantite > produit.stock:

        messages.error(
            request,
            f"Stock insuffisant pour {produit.designation}. "
            f"Stock disponible : {produit.stock}."
        )

        return redirect('vente:catalogue')

    panier[produit_id_str] = nouvelle_quantite

    request.session['panier'] = panier
    request.session.modified = True

    messages.success(
        request,
        f"{produit.designation} a été ajouté au panier."
    )

    return redirect('vente:voir_panier')


# =========================================================
# RETIRER DU PANIER
# =========================================================

@login_required
def retirer_du_panier(request, produit_id):

    panier = request.session.get('panier', {})

    produit_id_str = str(produit_id)

    if produit_id_str in panier:

        del panier[produit_id_str]

        request.session['panier'] = panier
        request.session.modified = True

        messages.success(
            request,
            "Le produit a été retiré du panier."
        )

    return redirect('vente:voir_panier')


# =========================================================
# VIDER LE PANIER
# =========================================================

@login_required
def vider_panier(request):

    request.session['panier'] = {}
    request.session.modified = True

    messages.success(
        request,
        "Panier vidé."
    )

    return redirect('vente:voir_panier')


# =========================================================
# INSCRIPTION
# =========================================================

def inscription(request):

    if request.method == "POST":

        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        email = request.POST.get("email")
        telephone = request.POST.get("telephone")
        adresse = request.POST.get("adresse")
        password = request.POST.get("password")

        if User.objects.filter(
            username=email
        ).exists():

            messages.error(
                request,
                "Cette adresse email est déjà utilisée."
            )

            return render(
                request,
                "vente/inscription.html"
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=prenom,
            last_name=nom,
            password=password
        )

        Client.objects.create(
            user=user,
            telephone=telephone,
            adresse=adresse
        )

        login(
            request,
            user
        )

        return redirect(
            "vente:catalogue"
        )

    return render(
        request,
        "vente/inscription.html"
    )


# =========================================================
# CONNEXION
# =========================================================

def Login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                'vente:catalogue'
            )

        messages.error(
            request,
            "Nom d'utilisateur ou mot de passe incorrect."
        )

    return render(
        request,
        'vente/login.html'
    )


# =========================================================
# VALIDATION DE LA COMMANDE
# =========================================================

@login_required
@transaction.atomic
def valider_commande(request):

    # Récupérer le client connecté
    client = get_object_or_404(
        Client,
        user=request.user
    )

    # Récupérer les lieux
    lieux = LieuLivraison.objects.all()

    villes = (
        LieuLivraison.objects
        .values_list('ville', flat=True)
        .distinct()
    )

    # Récupérer le panier
    panier = request.session.get(
        'panier',
        {}
    )

    # Vérifier panier vide
    if not panier:

        messages.error(
            request,
            "Votre panier est vide."
        )

        return redirect(
            'vente:voir_panier'
        )

    # =====================================================
    # AFFICHER LA PAGE
    # =====================================================

    if request.method == 'GET':

        return render(
            request,
            'vente/valider_commande.html',
            {
                'lieux': lieux,
                'villes': villes,
            }
        )

    # =====================================================
    # RÉCUPÉRER LE LIEU
    # =====================================================

    lieu_id = request.POST.get(
        'lieu_livraison'
    )

    if not lieu_id:

        messages.error(
            request,
            "Veuillez choisir un lieu de livraison."
        )

        return render(
            request,
            'vente/valider_commande.html',
            {
                'lieux': lieux,
                'villes': villes,
            }
        )

    lieu_livraison = get_object_or_404(
        LieuLivraison,
        id=lieu_id
    )

    # =====================================================
    # VÉRIFIER LE STOCK
    # =====================================================

    produits_commande = []

    for produit_id, quantite in panier.items():

        produit_id = int(produit_id)
        quantite = int(quantite)

        if quantite <= 0:
            continue

        produit = get_object_or_404(
            Produit,
            id=produit_id
        )

        if produit.stock < quantite:

            messages.error(
                request,
                f"Stock insuffisant pour "
                f"{produit.designation}. "
                f"Stock disponible : {produit.stock}."
            )

            return redirect(
                'vente:voir_panier'
            )

        produits_commande.append(
            (produit, quantite)
        )

    # =====================================================
    # VÉRIFIER PANIER
    # =====================================================

    if not produits_commande:

        messages.error(
            request,
            "Votre panier est vide."
        )

        return redirect(
            'vente:voir_panier'
        )

    # =====================================================
    # CRÉER LA COMMANDE
    # =====================================================

    commande = Commande.objects.create(
        client=client,
        lieu_livraison=lieu_livraison,
        statut='E'
    )

    # =====================================================
    # CRÉER LES LIGNES + DIMINUER STOCK
    # =====================================================

    for produit, quantite in produits_commande:

        LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            quantite=quantite,
            prix_unitaire=produit.prix_vente
        )

        produit.stock -= quantite

        produit.save(
            update_fields=['stock']
        )

    # =====================================================
    # VIDER LE PANIER
    # =====================================================

    request.session['panier'] = {}
    request.session.modified = True

    # =====================================================
    # MESSAGE
    # =====================================================

    messages.success(
        request,
        f"Commande N°{commande.id} créée avec succès."
    )

    return redirect(
        'vente:mes_commandes'
    )


# =========================================================
# ANNULER UNE COMMANDE
# =========================================================

@login_required
@transaction.atomic
def annuler_commande(request, commande_id):

    client = get_object_or_404(
        Client,
        user=request.user
    )

    commande = get_object_or_404(
        Commande,
        id=commande_id,
        client=client
    )

    if commande.statut == 'A':

        messages.warning(
            request,
            "Cette commande est déjà annulée."
        )

        return redirect(
            'vente:detail_commande',
            commande_id=commande.id
        )

    if commande.statut == 'V':

        messages.error(
            request,
            "Cette commande ne peut plus être annulée."
        )

        return redirect(
            'vente:detail_commande',
            commande_id=commande.id
        )

    # Restituer le stock
    for ligne in commande.lignes.all():

        produit = Produit.objects.select_for_update().get(
            id=ligne.produit.id
        )

        produit.stock += ligne.quantite

        produit.save(
            update_fields=['stock']
        )

    commande.statut = 'A'

    commande.save(
        update_fields=['statut']
    )

    messages.success(
        request,
        "Commande annulée. Les produits ont été remis en stock."
    )

    return redirect(
        'vente:detail_commande',
        commande_id=commande.id
    )


# =========================================================
# DETAIL COMMANDE
# =========================================================

@login_required
def detail_commande(request, commande_id):

    client = get_object_or_404(
        Client,
        user=request.user
    )

    commande = get_object_or_404(
        Commande,
        id=commande_id,
        client=client
    )

    return render(
        request,
        'vente/detail_commande.html',
        {
            'commande': commande
        }
    )


# =========================================================
# MES COMMANDES
# =========================================================

@login_required
def mes_commandes(request):

    client = get_object_or_404(
        Client,
        user=request.user
    )

    commandes = (
        Commande.objects
        .filter(client=client)
        .select_related('lieu_livraison')
        .prefetch_related('lignes__produit')
        .order_by('-date_commande')
    )

    commandes_data = []

    for commande in commandes:

        total_produits = Decimal('0.00')

        for ligne in commande.lignes.all():

            total_produits += (
                ligne.prix_unitaire * ligne.quantite
            )

        frais_livraison = commande.lieu_livraison.frais

        total_commande = (
            total_produits + frais_livraison
        )

        commandes_data.append({
            'commande': commande,
            'total_produits': total_produits,
            'frais_livraison': frais_livraison,
            'total_commande': total_commande,
        })

    return render(
        request,
        'vente/mes_commandes.html',
        {
            'commandes_data': commandes_data,
        }
    )


# =========================================================
# TABLEAU DE BORD ADMIN
# =========================================================

@staff_member_required
def dashboard(request):

    nombre_produits = Produit.objects.count()

    nombre_clients = Client.objects.count()

    nombre_commandes = Commande.objects.count()

    commandes_attente = Commande.objects.filter(
        statut='E'
    ).count()

    commandes_validees = Commande.objects.filter(
        statut='V'
    ).count()

    commandes_livrees = Commande.objects.filter(
        statut='L'
    ).count()

    commandes_annulees = Commande.objects.filter(
        statut='A'
    ).count()

    stock_total = Produit.objects.aggregate(
        total=Sum('stock')
    )['total'] or 0

    chiffre_affaires = Decimal('0.00')

    lignes = LigneCommande.objects.filter(
        commande__statut__in=['V', 'L']
    )

    for ligne in lignes:

        chiffre_affaires += (
            ligne.quantite * ligne.prix_unitaire
        )

    context = {
        'nombre_produits': nombre_produits,
        'nombre_clients': nombre_clients,
        'nombre_commandes': nombre_commandes,
        'commandes_attente': commandes_attente,
        'commandes_validees': commandes_validees,
        'commandes_livrees': commandes_livrees,
        'commandes_annulees': commandes_annulees,
        'stock_total': stock_total,
        'chiffre_affaires': chiffre_affaires,
    }

    return render(
        request,
        'vente/Tableau-bord/tableau_bord.html',
        context
    )