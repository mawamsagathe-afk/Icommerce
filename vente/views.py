from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction

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

def voir_panier(request):

    panier = request.session.get(
        'panier',
        {}
    )

    total = 0

    for item_id, item in panier.items():

        prix = float(item['prix'])
        quantite = int(item['quantite'])

        item['total_produit'] = prix * quantite

        total += item['total_produit']

    return render(
        request,
        'vente/panier.html',
        {
            'panier': panier,
            'total': total,
        }
    )


# =========================================================
# AJOUTER AU PANIER
# =========================================================

def ajouter_au_panier(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id
    )

    # Vérifier le stock
    if produit.stock <= 0:

        messages.error(
            request,
            f"Désolé, {produit.designation} est en rupture de stock."
        )

        return redirect(
            'vente:catalogue'
        )

    panier = request.session.get(
        'panier',
        {}
    )

    produit_id_str = str(produit_id)

    # Produit déjà présent
    if produit_id_str in panier:

        if panier[produit_id_str]['quantite'] < produit.stock:

            panier[produit_id_str]['quantite'] += 1

            messages.success(
                request,
                f"Quantité augmentée pour {produit.designation}."
            )

        else:

            messages.warning(
                request,
                f"Stock maximum atteint pour {produit.designation}."
            )

    # Nouveau produit
    else:

        panier[produit_id_str] = {
            'nom': produit.designation,
            'prix': str(produit.prix_vente),
            'quantite': 1
        }

        messages.success(
            request,
            f"{produit.designation} a été ajouté au panier."
        )

    request.session['panier'] = panier
    request.session.modified = True

    # IMPORTANT :
    # utiliser voir_panier et non panier
    return redirect(
        'vente:voir_panier'
    )


# =========================================================
# RETIRER DU PANIER
# =========================================================

def retirer_du_panier(request, produit_id):

    panier = request.session.get(
        'panier',
        {}
    )

    produit_id_str = str(produit_id)

    if produit_id_str in panier:

        del panier[produit_id_str]

        request.session['panier'] = panier
        request.session.modified = True

        messages.info(
            request,
            "L'article a été retiré du panier."
        )

    return redirect(
        'vente:voir_panier'
    )


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

        # Vérifier si l'utilisateur existe
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

        # Créer User
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=prenom,
            last_name=nom,
            password=password
        )

        # Créer Client
        Client.objects.create(
            user=user,
            telephone=telephone,
            adresse=adresse
        )

        # Connexion automatique
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

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

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

    client, created = Client.objects.get_or_create(
        user=request.user
    )

    panier = request.session.get('panier', {})

    if not panier:
        messages.error(
            request,
            "Votre panier est vide."
        )
        return redirect('vente:voir_panier')

    lieux = LieuLivraison.objects.all()

    villes = (
        LieuLivraison.objects
        .values_list('ville', flat=True)
        .distinct()
    )

    if request.method == 'POST':

        lieu_id = request.POST.get('lieu_livraison')

        if not lieu_id:
            messages.error(
                request,
                "Veuillez choisir un quartier."
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

        commande = Commande.objects.create(
            client=client,
            lieu_livraison=lieu_livraison
        )

        for item_id, item in panier.items():

            produit = get_object_or_404(
                Produit,
                id=item_id
            )

            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=item['quantite'],
                prix_unitaire=item['prix']
            )

        request.session['panier'] = {}
        request.session.modified = True

        messages.success(
            request,
            f"Commande N°{commande.id} créée avec succès."
        )

        return redirect(
            'vente:detail_commande',
            commande_id=commande.id
        )

    return render(
        request,
        'vente/valider_commande.html',
        {
            'lieux': lieux,
            'villes': villes,
        }
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

    # Déjà annulée
    if commande.statut == 'A':

        messages.warning(
            request,
            "Cette commande est déjà annulée."
        )

        return redirect(
            'vente:detail_commande',
            commande_id=commande.id
        )

    # Déjà validée
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
  