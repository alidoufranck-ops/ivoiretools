from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm

def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Connecte l'utilisateur immédiatement
            # Redirige directement vers ta page d'accueil sécurisée (home) !
            return redirect('acceuil') 
    else:
        form = InscriptionForm()
    return render(request, 'inscription.html', {'form': form})

def connexion_view(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST.get('username')
        mot_de_passe = request.POST.get('password')
        
        user = authenticate(request, username=nom_utilisateur, password=mot_de_passe)
        
        if user is not None:
            login(request, user)
            return redirect('acceuil') # Redirige vers ta page d'accueil sécurisée (home)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            
    return render(request, 'connexion.html')

def deconnexion_view(request):
    logout(request)
    return redirect('connexion')
