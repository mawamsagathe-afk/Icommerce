from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import connection, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required

from .forms import ProduitForm
from .models import (
    Produit,
    Categorie,
    Client,
    LieuLivraison,
    Commande,
    LigneCommande,
)

from .models import (
    Client,
    Commande,
    Notification,
)


# =========================================================
# OUTILS / PROTECTIONS
# =========================================================

def est_admin(user):
    """
    Vérifie si l'utilisateur est administrateur.
    Compatible avec staff et superuser.
    """
    return user.is_authenticated and (
        user.is_staff or user.is_superuser
    )


def envoyer_email_confirmation_commande(commande, message_admin=False):
    """
    Envoie un email au client après validation de sa commande.
    """

    email_client = commande.client.user.email

    if not email_client:
        return

    if message_admin:
        subject = (
            f"Commande N°{commande.id} validée - Icommerce"
        )

        message = (
            f"Bonjour {commande.client.nom},\n\n"
            f"Nous avons le plaisir de vous informer que "
            f"votre commande N°{commande.id} "
            f"a été validée par notre équipe.\n\n"
            f"Statut : Validée\n\n"
            f"Votre commande sera traitée dans les meilleurs délais.\n\n"
            f"Merci pour votre confiance.\n\n"
            f"L'équipe Icommerce"
        )

    else:
        subject = (
            f"Confirmation de votre commande N°{commande.id}"
        )

        message = (
            f"Bonjour {commande.client.nom},\n\n"
            f"Votre commande N°{commande.id} "
            f"a été confirmée avec succès.\n\n"
            f"Statut : Validée\n\n"
            f"Merci pour votre confiance.\n\n"
            f"L'équipe Icommerce"
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_client],
        fail_silently=False,
    )


def calculer_total_commande(commande):
    """
    Calcule le total des produits et les frais de livraison.
    """

    total_produits = Decimal("0.00")

    for ligne in commande.lignes.all():
        total_produits += (
            ligne.prix_unitaire * ligne.quantite
        )

    frais_livraison = Decimal("0.00")

    if commande.lieu_livraison:
        frais_livraison = commande.lieu_livraison.frais

    total_commande = (
        total_produits + frais_livraison
    )

    return (
        total_produits,
        frais_livraison,
        total_commande,
    )


# =========================================================
# CATALOGUE
# =========================================================

def catalogue(request):

    produits = Produit.objects.all()
    categories = Categorie.objects.all()

    # Recherche
    query = request.GET.get("q")

    if query:
        produits = produits.filter(
            designation__icontains=query
        )

    # Filtre par catégorie
    categorie_id = request.GET.get("categorie")

    if categorie_id:
        produits = produits.filter(
            categorie_id=categorie_id
        )

    context = {
        "produits": produits,
        "categories": categories,
    }

    return render(
        request,
        "vente/catalogue.html",
        context,
    )


# =========================================================
# DETAIL PRODUIT
# =========================================================

def produit_detail(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id,
    )

    return render(
        request,
        "vente/produit_detail.html",
        {
            "produit": produit,
        },
    )


# =========================================================
# PANIER
# =========================================================

@login_required
def voir_panier(request):

    panier = request.session.get("panier", {})

    produits = []
    total = Decimal("0.00")

    for produit_id, quantite in panier.items():

        produit = get_object_or_404(
            Produit,
            id=int(produit_id),
        )

        quantite = int(quantite)

        # Ignorer les quantités invalides
        if quantite <= 0:
            continue

        sous_total = (
            produit.prix_vente * quantite
        )

        produits.append({
            "produit": produit,
            "quantite": quantite,
            "sous_total": sous_total,
        })

        total += sous_total

    return render(
        request,
        "vente/panier.html",
        {
            "produits": produits,
            "total": total,
        },
    )


@login_required
def ajouter_au_panier(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id,
    )

    panier = request.session.get(
        "panier",
        {},
    )

    produit_id_str = str(produit_id)

    quantite_actuelle = int(
        panier.get(
            produit_id_str,
            0,
        )
    )

    nouvelle_quantite = (
        quantite_actuelle + 1
    )

    # Vérification du stock
    if nouvelle_quantite > produit.stock:

        messages.error(
            request,
            f"Stock insuffisant pour "
            f"{produit.designation}. "
            f"Stock disponible : {produit.stock}.",
        )

        return redirect(
            "vente:catalogue"
        )

    panier[produit_id_str] = (
        nouvelle_quantite
    )

    request.session["panier"] = panier
    request.session.modified = True

    messages.success(
        request,
        f"{produit.designation} a été ajouté au panier.",
    )

    return redirect(
        "vente:voir_panier"
    )


@login_required
def retirer_du_panier(request, produit_id):

    panier = request.session.get(
        "panier",
        {},
    )

    produit_id_str = str(produit_id)

    if produit_id_str in panier:

        del panier[produit_id_str]

        request.session["panier"] = panier
        request.session.modified = True

        messages.success(
            request,
            "Le produit a été retiré du panier.",
        )

    return redirect(
        "vente:voir_panier"
    )


@login_required
def vider_panier(request):

    request.session["panier"] = {}
    request.session.modified = True

    messages.success(
        request,
        "Panier vidé.",
    )

    return redirect(
        "vente:voir_panier"
    )


# =========================================================
# INSCRIPTION
# =========================================================

def inscription(request):

    if request.method == "POST":

        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        email = request.POST.get("email", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        password = request.POST.get("password", "")

        if not nom or not prenom or not email or not password:

            messages.error(
                request,
                "Veuillez remplir tous les champs obligatoires.",
            )

            return render(
                request,
                "vente/inscription.html",
            )

        # Vérifier si l'email existe déjà
        if User.objects.filter(
            username=email
        ).exists():

            messages.error(
                request,
                "Cette adresse email est déjà utilisée.",
            )

            return render(
                request,
                "vente/inscription.html",
            )

        # Créer le compte utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=prenom,
            last_name=nom,
            password=password,
        )

        # Créer le profil client
        Client.objects.create(
            user=user,
            nom=f"{prenom} {nom}",
            telephone=telephone,
        )

        # Connexion automatique
        login(
            request,
            user,
        )

        messages.success(
            request,
            "Votre compte client a été créé avec succès.",
        )

        return redirect(
            "vente:tableau_bord_client"
        )

    return render(
        request,
        "vente/inscription.html",
    )


# =========================================================
# CONNEXION
# =========================================================

def Login_user(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(
                request,
                user,
            )

            # ADMIN
            if est_admin(user):

                return redirect(
                    "vente:tableau_bord_admin"
                )

            # CLIENT
            return redirect(
                "vente:tableau_bord_client"
            )

        messages.error(
            request,
            "Nom d'utilisateur ou mot de passe incorrect.",
        )

    return render(
        request,
        "vente/login.html",
    )


# =========================================================
# VALIDATION DE LA COMMANDE
# =========================================================

@login_required
def valider_commande(request):

    client = get_object_or_404(
        Client,
        user=request.user,
    )

    lieux = LieuLivraison.objects.all()

    villes = (
        LieuLivraison.objects
        .values_list(
            "ville",
            flat=True,
        )
        .distinct()
    )

    panier = request.session.get(
        "panier",
        {},
    )

    # Panier vide
    if not panier:

        messages.error(
            request,
            "Votre panier est vide.",
        )

        return redirect(
            "vente:voir_panier"
        )

    # Affichage de la page
    if request.method == "GET":

        return render(
            request,
            "vente/valider_commande.html",
            {
                "lieux": lieux,
                "villes": villes,
            },
        )

    # Récupérer le lieu de livraison
    lieu_id = request.POST.get(
        "lieu_livraison"
    )

    if not lieu_id:

        messages.error(
            request,
            "Veuillez choisir un lieu de livraison.",
        )

        return render(
            request,
            "vente/valider_commande.html",
            {
                "lieux": lieux,
                "villes": villes,
            },
        )

    lieu_livraison = get_object_or_404(
        LieuLivraison,
        id=lieu_id,
    )

    # =====================================================
    # TRANSACTION
    # =====================================================

    with transaction.atomic():

        produits_commande = []

        for produit_id, quantite in panier.items():

            produit_id = int(produit_id)
            quantite = int(quantite)

            if quantite <= 0:
                continue

            # Verrouillage du produit pendant la transaction
            produit = get_object_or_404(
                Produit.objects.select_for_update(),
                id=produit_id,
            )

            if produit.stock < quantite:

                messages.error(
                    request,
                    f"Stock insuffisant pour "
                    f"{produit.designation}. "
                    f"Stock disponible : {produit.stock}.",
                )

                return redirect(
                    "vente:voir_panier"
                )

            produits_commande.append(
                (
                    produit,
                    quantite,
                )
            )

        if not produits_commande:

            messages.error(
                request,
                "Votre panier est vide.",
            )

            return redirect(
                "vente:voir_panier"
            )

        # Créer la commande
        commande = Commande.objects.create(
            client=client,
            lieu_livraison=lieu_livraison,
            statut="E",
        )

        # Créer les lignes
        # et diminuer le stock
        for produit, quantite in produits_commande:

            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix_vente,
            )

            produit.stock -= quantite

            produit.save(
                update_fields=["stock"]
            )

    # Vider le panier
    request.session["panier"] = {}
    request.session.modified = True

    messages.success(
        request,
        f"Commande N°{commande.id} créée avec succès.",
    )

    return redirect(
        "vente:mes_commandes"
    )


# =========================================================
# CLIENT : CONFIRMER UNE COMMANDE
# =========================================================

@login_required
@transaction.atomic
def confirmer_commande(request, commande_id):

    client = get_object_or_404(
        Client,
        user=request.user,
    )

    commande = get_object_or_404(
        Commande,
        id=commande_id,
        client=client,
    )

    if request.method != "POST":

        return redirect(
            "vente:mes_commandes"
        )

    if commande.statut != "E":

        messages.warning(
            request,
            "Cette commande ne peut plus être validée.",
        )

        return redirect(
            "vente:mes_commandes"
        )

    commande.statut = "V"

    commande.save(
        update_fields=["statut"]
    )
    
    commande.statut = "V"
    commande.save(update_fields=["statut"])

    Notification.objects.create(
    titre=f"Commande N°{commande.id} validée",
    message=(
        f"Le client {client} vient de valider "
        f"la commande N°{commande.id}."
    ),
    type_notification="commande",
    commande=commande,
)

    envoyer_email_confirmation_commande(
        commande
    )

    messages.success(
        request,
        f"La commande N°{commande.id} "
        f"a été validée avec succès.",
    )

    return redirect(
        "vente:mes_commandes"
    )


# =========================================================
# CLIENT : ANNULER UNE COMMANDE
# =========================================================

@login_required
@transaction.atomic
def annuler_commande(request, commande_id):

    client = get_object_or_404(
        Client,
        user=request.user,
    )

    commande = get_object_or_404(
        Commande,
        id=commande_id,
        client=client,
    )

    if request.method != "POST":

        return redirect(
            "vente:detail_commande",
            commande_id=commande.id,
        )

    if commande.statut == "A":

        messages.warning(
            request,
            "Cette commande est déjà annulée.",
        )

        return redirect(
            "vente:detail_commande",
            commande_id=commande.id,
        )

    if commande.statut in ["V", "L"]:

        messages.error(
            request,
            "Cette commande ne peut plus être annulée.",
        )

        return redirect(
            "vente:detail_commande",
            commande_id=commande.id,
        )

    # Restituer le stock
    for ligne in commande.lignes.all():

        produit = (
            Produit.objects
            .select_for_update()
            .get(id=ligne.produit.id)
        )

        produit.stock += ligne.quantite

        produit.save(
            update_fields=["stock"]
        )

    commande.statut = "A"

    commande.save(
        update_fields=["statut"]
    )

    messages.success(
        request,
        "Commande annulée. "
        "Les produits ont été remis en stock.",
    )

    return redirect(
        "vente:detail_commande",
        commande_id=commande.id,
    )


# =========================================================
# DETAIL COMMANDE
# =========================================================

@login_required
def detail_commande(request, commande_id):

    client = get_object_or_404(
        Client,
        user=request.user,
    )

    commande = get_object_or_404(
        Commande.objects.select_related(
            "lieu_livraison",
        ).prefetch_related(
            "lignes__produit",
        ),
        id=commande_id,
        client=client,
    )

    total_produits, frais_livraison, total_commande = (
        calculer_total_commande(commande)
    )

    return render(
        request,
        "vente/detail_commande.html",
        {
            "commande": commande,
            "total_produits": total_produits,
            "frais_livraison": frais_livraison,
            "total_commande": total_commande,
        },
    )


# =========================================================
# MES COMMANDES
# =========================================================

@login_required
def mes_commandes(request):

    client = get_object_or_404(
        Client,
        user=request.user,
    )

    commandes = (
        Commande.objects
        .filter(client=client)
        .select_related(
            "lieu_livraison",
        )
        .prefetch_related(
            "lignes__produit",
        )
        .order_by(
            "-date_commande"
        )
    )

    commandes_data = []

    for commande in commandes:

        (
            total_produits,
            frais_livraison,
            total_commande,
        ) = calculer_total_commande(commande)

        commandes_data.append({
            "commande": commande,
            "total_produits": total_produits,
            "frais_livraison": frais_livraison,
            "total_commande": total_commande,
        })

    return render(
        request,
        "vente/mes_commandes.html",
        {
            "commandes_data": commandes_data,
        },
    )


# =========================================================
# TABLEAU DE BORD CLIENT
# =========================================================

@login_required
def tableau_bord_client(request):

    if est_admin(request.user):

        return redirect(
            "vente:tableau_bord_admin"
        )

    return render(
        request,
        "vente/tableau_bord_client.html",
    )


# =========================================================
# TABLEAU DE BORD ADMIN
# =========================================================

@staff_member_required
def tableau_bord_admin(request):

    # =====================================================
    # PRODUITS
    # =====================================================

    produits = Produit.objects.all()

    nombre_produits = produits.count()

    stock_total = sum(
        produit.stock
        for produit in produits
    )

    valeur_stock_achat = sum(
        (
            produit.prix_achat *
            produit.stock
        )
        for produit in produits
    )

    valeur_stock_vente = sum(
        (
            produit.prix_vente *
            produit.stock
        )
        for produit in produits
    )

    benefice_stock_total = (
        valeur_stock_vente -
        valeur_stock_achat
    )

    # =====================================================
    # CLIENTS
    # =====================================================

    nombre_clients = Client.objects.count()

    # =====================================================
    # COMMANDES
    # =====================================================

    commandes = Commande.objects.all()

    nombre_commandes = commandes.count()

    commandes_attente = commandes.filter(
        statut="E"
    ).count()

    commandes_validees = commandes.filter(
        statut="V"
    ).count()

    commandes_livrees = commandes.filter(
        statut="L"
    ).count()

    commandes_annulees = commandes.filter(
        statut="A"
    ).count()

    # =====================================================
    # CHIFFRE D'AFFAIRES
    # =====================================================

    chiffre_affaires = Decimal("0.00")

    commandes_valides = (
        commandes
        .filter(
            statut__in=["V", "L"]
        )
        .select_related(
            "lieu_livraison"
        )
        .prefetch_related(
            "lignes"
        )
    )

    for commande in commandes_valides:

        for ligne in commande.lignes.all():

            chiffre_affaires += (
                ligne.prix_unitaire *
                ligne.quantite
            )

        # Ajouter les frais de livraison
        if commande.lieu_livraison:

            chiffre_affaires += (
                commande.lieu_livraison.frais
            )

    # =====================================================
    # DONNÉES PRODUITS
    # =====================================================

    produits_data = []

    for produit in produits:

        benefice_unitaire = (
            produit.prix_vente -
            produit.prix_achat
        )

        valeur_vente = (
            produit.prix_vente *
            produit.stock
        )

        benefice_total = (
            benefice_unitaire *
            produit.stock
        )

        produits_data.append({
            "produit": produit,
            "benefice_unitaire": benefice_unitaire,
            "valeur_vente": valeur_vente,
            "benefice_total": benefice_total,
        })

    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {
        "nombre_produits": nombre_produits,
        "nombre_clients": nombre_clients,
        "nombre_commandes": nombre_commandes,
        "chiffre_affaires": chiffre_affaires,

        "commandes_attente": commandes_attente,
        "commandes_validees": commandes_validees,
        "commandes_livrees": commandes_livrees,
        "commandes_annulees": commandes_annulees,

        "stock_total": stock_total,

        "valeur_stock_achat": valeur_stock_achat,
        "valeur_stock_vente": valeur_stock_vente,
        "benefice_stock_total": benefice_stock_total,

        "produits_data": produits_data,
    }

    return render(
        request,
        "vente/tableau_bord_admin.html",
        context,
    )


# =========================================================
# ADMIN : PRODUITS
# =========================================================

@staff_member_required
def gestion_produits(request):

    produits = (
        Produit.objects
        .select_related("categorie")
        .all()
    )

    return render(
        request,
        "vente/gestion/produits.html",
        {
            "produits": produits,
        },
    )


@staff_member_required
def ajouter_produit(request):

    if request.method == "POST":

        form = ProduitForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            produit = form.save()

            messages.success(
                request,
                f"Le produit « {produit.designation} » "
                f"a été ajouté avec succès.",
            )

            return redirect(
                "vente:tableau_bord_admin"
            )

    else:

        form = ProduitForm()

    return render(
        request,
        "vente/Tableau-bord/ajouter_produit.html",
        {
            "form": form,
        },
    )


@staff_member_required
def modifier_produit(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id,
    )

    if request.method == "POST":

        form = ProduitForm(
            request.POST,
            request.FILES,
            instance=produit,
        )

        if form.is_valid():

            produit = form.save()

            messages.success(
                request,
                f"Le produit « {produit.designation} » "
                f"a été modifié avec succès.",
            )

            return redirect(
                "vente:tableau_bord_admin"
            )

    else:

        form = ProduitForm(
            instance=produit,
        )

    return render(
        request,
        "vente/Tableau-bord/modifier_produit.html",
        {
            "form": form,
            "produit": produit,
        },
    )


@staff_member_required
def supprimer_produit(request, produit_id):

    produit = get_object_or_404(
        Produit,
        id=produit_id,
    )

    if request.method == "POST":

        designation = produit.designation

        produit.delete()

        messages.success(
            request,
            f"Le produit « {designation} » "
            f"a été supprimé.",
        )

        return redirect(
            "vente:tableau_bord_admin"
        )

    return render(
        request,
        "vente/Tableau-bord/supprimer_produit.html",
        {
            "produit": produit,
        },
    )


# =========================================================
# ADMIN : CATÉGORIES
# =========================================================

@staff_member_required
def gestion_categories(request):

    categories = (
        Categorie.objects
        .all()
        .order_by("nom")
    )

    return render(
        request,
        "vente/gestion_categories.html",
        {
            "categories": categories,
        },
    )


@staff_member_required
def ajouter_categorie(request):

    if request.method != "POST":

        return redirect(
            "vente:gestion_categories"
        )

    nom = request.POST.get(
        "nom",
        "",
    ).strip()

    if not nom:

        messages.error(
            request,
            "Veuillez saisir le nom de la catégorie.",
        )

        return redirect(
            "vente:gestion_categories"
        )

    if Categorie.objects.filter(
        nom__iexact=nom
    ).exists():

        messages.error(
            request,
            "Cette catégorie existe déjà.",
        )

        return redirect(
            "vente:gestion_categories"
        )

    Categorie.objects.create(
        nom=nom
    )

    messages.success(
        request,
        f"La catégorie « {nom} » "
        f"a été ajoutée avec succès.",
    )

    return redirect(
        "vente:gestion_categories"
    )


@staff_member_required
def modifier_categorie(request, categorie_id):

    categorie = get_object_or_404(
        Categorie,
        id=categorie_id,
    )

    if request.method == "POST":

        nom = request.POST.get(
            "nom",
            "",
        ).strip()

        if not nom:

            messages.error(
                request,
                "Veuillez saisir le nom de la catégorie.",
            )

            return redirect(
                "vente:modifier_categorie",
                categorie_id=categorie.id,
            )

        existe_deja = (
            Categorie.objects
            .filter(
                nom__iexact=nom
            )
            .exclude(
                id=categorie.id
            )
            .exists()
        )

        if existe_deja:

            messages.error(
                request,
                "Une autre catégorie porte déjà ce nom.",
            )

            return redirect(
                "vente:modifier_categorie",
                categorie_id=categorie.id,
            )

        categorie.nom = nom

        categorie.save(
            update_fields=["nom"]
        )

        messages.success(
            request,
            "La catégorie a été modifiée avec succès.",
        )

        return redirect(
            "vente:gestion_categories"
        )

    return render(
        request,
        "vente/modifier_categorie.html",
        {
            "categorie": categorie,
        },
    )


@staff_member_required
def supprimer_categorie(request, categorie_id):

    categorie = get_object_or_404(
        Categorie,
        id=categorie_id,
    )

    if request.method == "POST":

        nom = categorie.nom

        categorie.delete()

        messages.success(
            request,
            f"La catégorie « {nom} » "
            f"a été supprimée.",
        )

        return redirect(
            "vente:gestion_categories"
        )

    return render(
        request,
        "vente/supprimer_categorie.html",
        {
            "categorie": categorie,
        },
    )


# =========================================================
# ADMIN : CLIENTS
# =========================================================

@staff_member_required
def gestion_clients(request):

    clients = (
        Client.objects
        .select_related("user")
        .order_by("nom")
    )

    return render(
        request,
        "vente/gestion_clients.html",
        {
            "clients": clients,
        },
    )


@staff_member_required
def ajouter_client(request):

    if request.method == "POST":

        nom = request.POST.get(
            "nom",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        telephone = request.POST.get(
            "telephone",
            "",
        ).strip()

        mot_de_passe = request.POST.get(
            "mot_de_passe",
            "",
        )

        if not nom or not email or not mot_de_passe:

            messages.error(
                request,
                "Veuillez remplir tous les champs obligatoires.",
            )

            return render(
                request,
                "vente/ajouter_client.html",
            )

        # Vérifier email
        if User.objects.filter(
            username=email
        ).exists():

            messages.error(
                request,
                "Un utilisateur avec cette adresse email existe déjà.",
            )

            return render(
                request,
                "vente/ajouter_client.html",
            )

        # Créer utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=mot_de_passe,
        )

        # Créer client
        Client.objects.create(
            user=user,
            nom=nom,
            telephone=telephone,
        )

        messages.success(
            request,
            "Le client a été ajouté avec succès.",
        )

        return redirect(
            "vente:gestion_clients"
        )

    return render(
        request,
        "vente/ajouter_client.html",
    )


@staff_member_required
def supprimer_client(request, client_id):

    client = get_object_or_404(
        Client,
        id=client_id,
    )

    if request.method == "POST":

        user = client.user

        client.delete()

        # Supprimer également le compte utilisateur
        if user:
            user.delete()

        messages.success(
            request,
            "Le client a été supprimé avec succès.",
        )

        return redirect(
            "vente:gestion_clients"
        )

    return render(
        request,
        "vente/confirmer_suppression_client.html",
        {
            "client": client,
        },
    )


# =========================================================
# ADMIN : COMMANDES
# =========================================================

@staff_member_required
def gestion_commandes(request):

    commandes = (
        Commande.objects
        .select_related(
            "client",
            "client__user",
            "lieu_livraison",
        )
        .prefetch_related(
            "lignes__produit",
        )
        .order_by(
            "-date_commande"
        )
    )

    return render(
        request,
        "vente/gestion_commandes.html",
        {
            "commandes": commandes,
        },
    )


# =========================================================
# ADMIN : VALIDER UNE COMMANDE
# =========================================================

@staff_member_required
@transaction.atomic
def admin_valider_commande(request, commande_id):

    commande = get_object_or_404(
        Commande.objects.select_related(
            "client__user"
        ),
        id=commande_id,
    )

    if request.method != "POST":

        return redirect(
            "vente:gestion_commandes"
        )

    if commande.statut != "E":

        messages.warning(
            request,
            f"La commande N°{commande.id} "
            f"ne peut plus être validée.",
        )

        return redirect(
            "vente:gestion_commandes"
        )

    commande.statut = "V"

    commande.save(
        update_fields=["statut"]
    )

    envoyer_email_confirmation_commande(
        commande,
        message_admin=True,
    )

    messages.success(
        request,
        f"La commande N°{commande.id} "
        f"a été validée et le client a été notifié par email.",
    )

    return redirect(
        "vente:gestion_commandes"
    )


# =========================================================
# ADMIN : RÉINITIALISER LES COMMANDES
# =========================================================

@staff_member_required
@transaction.atomic
def reinitialiser_commandes(request):

    if request.method != "POST":

        return redirect(
            "vente:gestion_commandes"
        )

    # Supprimer les lignes
    LigneCommande.objects.all().delete()

    # Supprimer les commandes
    Commande.objects.all().delete()

    # Réinitialiser le compteur uniquement avec SQLite
    if connection.vendor == "sqlite":

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM sqlite_sequence
                WHERE name = 'vente_commande'
                """
            )

    messages.success(
        request,
        "Toutes les commandes ont été supprimées. "
        "Le compteur des commandes a été réinitialisé à 1.",
    )

    return redirect(
        "vente:gestion_commandes"
    )
    
@staff_member_required
def notifications_admin(request):

    notifications = Notification.objects.all()

    return render(
        request,
        "vente/notifications_admin.html",
        {
            "notifications": notifications,
        }
    )
    
@staff_member_required
@transaction.atomic
def supprimer_client(request, client_id):

    if request.method != "POST":
        return redirect("vente:gestion_clients")

    client = get_object_or_404(Client, id=client_id)

    nom_client = client.nom
    email_client = client.user.email

    # Supprime Client + User + Commandes liées
    # grâce aux on_delete=models.CASCADE
    client.delete()

    messages.success(
        request,
        f"Le client {nom_client} ({email_client}) a été supprimé avec son compte."
    )

    return redirect("vente:gestion_clients")

@staff_member_required
@transaction.atomic
def reinitialiser_clients(request):

    if request.method != "POST":
        return redirect("vente:gestion_clients")

    nombre_clients = Client.objects.count()

    Client.objects.all().delete()

    messages.success(
        request,
        f"{nombre_clients} client(s) ont été supprimé(s) avec leur compte."
    )

    return redirect("vente:gestion_clients")