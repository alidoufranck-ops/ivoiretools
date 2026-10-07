from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class InscriptionForm(UserCreationForm):
    # On s'assure que le champ email est requis pour la création de compte
    email = forms.EmailField(required=True, label="Adresse email")

    class Meta:
        model = User
        fields = ['username', 'email'] # Les champs qui seront visibles dans le formulaire
