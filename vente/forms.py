from django import forms
from .models import Produit


class ProduitForm(forms.ModelForm):

    class Meta:
        model = Produit

        fields = [
            'categorie',
            'designation',
            'description',
            'prix_achat',
            'prix_vente',
            'stock',
            'image',
        ]