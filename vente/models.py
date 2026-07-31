from django.db import models

# Create your models here.


class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    designation = models.CharField(max_length=150)
    description = models.TextField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)

    def __str__(self):
        return self.designation


class LieuLivraison(models.Model):
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    frais = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.ville} - {self.quartier}"


class Commande(models.Model):
    STATUT = [
        ('E', 'En attente'),
        ('V', 'Validée'),
        ('L', 'Livrée'),
        ('A', 'Annulée'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    lieu_livraison = models.ForeignKey(LieuLivraison, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=1, choices=STATUT, default='E')

    def __str__(self):
        return f"Commande N°{self.id}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produit} ({self.quantite})"


class ModePaiement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Paiement(models.Model):
    ETAT = [
        ('A', 'En attente'),
        ('P', 'Payé'),
        ('R', 'Refusé'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    mode_paiement = models.ForeignKey(ModePaiement, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=1, choices=ETAT, default='A')

    def __str__(self):
        return f"Paiement {self.commande.id}"


class Livraison(models.Model):
    ETAT = [
        ('P', 'Préparation'),
        ('T', 'En transport'),
        ('L', 'Livrée'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    date_livraison = models.DateField()
    etat = models.CharField(max_length=1, choices=ETAT, default='P')

    def __str__(self):
        return f"Livraison {self.commande.id}"   
    
    