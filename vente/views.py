from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produit, Categorie, Client


def catalogue(request):
    """
    Affiche la liste des produits avec recherche (q) et filtrage par catégorie.
    """
    produits = Produit.objects.all()
    categories = Categorie.objects.all()

    # Recherche par désignation (nom du produit dans votre modèle)
    query = request.GET.get('q')
    if query:
        produits = produits.filter(designation__icontains=query)

    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)

    context = {
        'produits': produits,
        'categories': categories,
    }
    return render(request, 'vente/catalogue.html', context)


def produit_detail(request, produit_id):
    """
    Affiche la fiche détaillée d'un produit.
    """
    produit = get_object_or_404(Produit, id=produit_id)
    context = {
        'produit': produit
    }
    return render(request, 'vente/produit_detail.html', context)


def voir_panier(request):
    """
    Affiche le contenu du panier stocké en session et calcule le total.
    """
    panier = request.session.get('panier', {})
    total = 0

    # Calcul du total pour chaque ligne et du total général
    for item_id, item in panier.items():
        item['total_produit'] = float(item['prix']) * item['quantite']
        total += item['total_produit']

    context = {
        'panier': panier,
        'total': total,
    }
    return render(request, 'vente/panier.html', context)


def ajouter_au_panier(request, produit_id):
    """
    Ajoute un produit au panier en session.
    """
    produit = get_object_or_404(Produit, id=produit_id)

    if produit.stock <= 0:
        messages.error(request, f"Désolé, {produit.designation} est en rupture de stock.")
        return redirect('vente:catalogue')

    panier = request.session.get('panier', {})
    produit_id_str = str(produit_id)

    if produit_id_str in panier:
        if panier[produit_id_str]['quantite'] < produit.stock:
            panier[produit_id_str]['quantite'] += 1
            messages.success(request, f"Quantité augmentée pour {produit.designation}.")
        else:
            messages.warning(request, f"Stock maximum atteint pour {produit.designation}.")
    else:
        panier[produit_id_str] = {
            'nom': produit.designation,
            'prix': str(produit.prix),
            'quantite': 1
        }
        messages.success(request, f"{produit.designation} a été ajouté au panier.")

    request.session['panier'] = panier
    request.session.modified = True
    return redirect('vente:voir_panier')


def retirer_du_panier(request, produit_id):
    """
    Supprime un produit du panier en session.
    """
    panier = request.session.get('panier', {})
    produit_id_str = str(produit_id)

    if produit_id_str in panier:
        del panier[produit_id_str]
        request.session['panier'] = panier
        request.session.modified = True
        messages.info(request, "L'article a été retiré du panier.")

    return redirect('vente:voir_panier')


def inscription(request):
    """
    Enregistre un nouveau client dans la base de données.
    """
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')

        # Vérification si l'email existe déjà
        if Client.objects.filter(email=email).exists():
            messages.error(request, "Un compte existe déjà avec cette adresse email.")
            return render(request, 'vente/inscription.html')

        # Création du client
        Client.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            adresse=adresse
        )
        messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
        return redirect('vente:Login_user')

    return render(request, 'vente/inscription.html')


def Login_user(request):
    """
    Page de connexion (à personnaliser selon votre système d'auth).
    """
    return render(request, 'login.html')


def valider_commande(request):
    """
    Vue temporaire pour la validation de commande.
    """
    messages.info(request, "La gestion des commandes est en cours de finalisation.")
    return redirect('vente:voir_panier')