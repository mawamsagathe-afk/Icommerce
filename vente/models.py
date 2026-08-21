from django.db import models
from django.contrib.auth.models import User


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE
    )
    designation = models.CharField(max_length=150)
    description = models.TextField()

    prix_achat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    prix_vente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to='produits/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.designation

from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client'
    )
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nom


class LieuLivraison(models.Model):
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255,blank=True)
    frais = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.ville} - {self.quartier}"


class Commande(models.Model):

    STATUT = [
        ('E', 'En attente'),
        ('V', 'Validée'),
        ('L', 'Livrée'),
        ('A', 'Annulée'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    lieu_livraison = models.ForeignKey(
        LieuLivraison,
        on_delete=models.CASCADE
    )

    date_commande = models.DateTimeField(
        auto_now_add=True
    )

    statut = models.CharField(
        max_length=1,
        choices=STATUT,
        default='E'
    )

    def __str__(self):
        return f"Commande N°{self.id}"


class LigneCommande(models.Model):

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )

    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE
    )

    quantite = models.PositiveIntegerField()

    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.produit} ({self.quantite})"


class ModePaiement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Paiement(models.Model):

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE
    )

    mode = models.ForeignKey(
        ModePaiement,
        on_delete=models.PROTECT
    )

    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    date_paiement = models.DateTimeField(
        auto_now_add=True
    )

    statut = models.CharField(
        max_length=20,
        default='En attente'
    )

    def __str__(self):
        return f"Paiement commande N°{self.commande.id}"
    
class Notification(models.Model):
    TYPE_CHOICES = [
        ("commande", "Commande"),
        ("client", "Client"),
        ("autre", "Autre"),
    ]

    titre = models.CharField(max_length=255)
    message = models.TextField()

    type_notification = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="commande"
    )

    commande = models.ForeignKey(
        "Commande",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    lu = models.BooleanField(default=False)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ["-date_creation"]
    
