import os
os.environ["DISABLE_NUMBA"] = "1"
os.environ["NUMBA_NUM_THREADS"] = "1"
from django.shortcuts import render  # Afficher une page HTML

from django.core.files.base import ContentFile  # Créer un fichier à partir de données en mémoire

from .models import table  # Importer notre modèle


from django.contrib.auth.decorators import login_required

import requests  # Télécharger une image à partir d'une URL
# Create your views here.
def acceuil (request):
    return render  (request, 'home.html')

from django.shortcuts import render
from django.core.files.base import ContentFile



@login_required

@login_required
def emove(request):

    # 1. Récupérer uniquement les images de l'utilisateur connecté
    images_liste = table.objects.filter(
        utilisateur=request.user
    ).order_by("-id")

    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        photo_url = request.POST.get("photo_url", "").strip()
        photo_fichier = request.FILES.get("photo")

        # 2. Vérification des entrées
        if photo_url:
            try:
                response = requests.get(
                    photo_url,
                    timeout=15
                )
                response.raise_for_status()

                # Vérifier que l'URL renvoie bien une image
                content_type = response.headers.get(
                    "Content-Type", ""
                )

                if not content_type.startswith("image/"):
                    raise ValueError(
                        "L'URL fournie ne renvoie pas une image."
                    )

                input_bytes = response.content

            except Exception as e:
                return render(
                    request,
                    "rmbg.html",
                    {
                        "erreur": (
                            f"Impossible de récupérer l'image : {e}"
                        ),
                        "images": images_liste
                    }
                )

        elif photo_fichier:
            # L'utilisateur a envoyé une image depuis son appareil
            input_bytes = photo_fichier.read()

        else:
            return render(
                request,
                "rmbg.html",
                {
                    "erreur": "Veuillez fournir une image.",
                    "images": images_liste
                }
            )

        # 3. Suppression de l'arrière-plan
        try:
            import rembg
            output_bytes = rembg.remove(input_bytes)

        except Exception as e:
            return render(
                request,
                "rmbg.html",
                {
                    "erreur": (
                        f"Erreur lors de la suppression du fond : {e}"
                    ),
                    "images": images_liste
                }
            )

        # 4. Création de l'image associée à l'utilisateur connecté
        nouvelle_image = table(
            nom=nom,
            utilisateur=request.user
        )

        nom_fichier = f"{nom or 'image'}_no_bg.png"

        nouvelle_image.photo_modifier.save(
            nom_fichier,
            ContentFile(output_bytes),
            save=False
        )

        nouvelle_image.save()

        # 5. Actualiser l'historique de cet utilisateur
        images_liste = table.objects.filter(
            utilisateur=request.user
        ).order_by("-id")

        return render(
            request,
            "rmbg.html",
            {
                "image": nouvelle_image,
                "images": images_liste
            }
        )

    # GET : afficher simplement la page
    return render(
        request,
        "rmbg.html",
        {"images": images_liste}
    )

@login_required
def code (requests):
    return render (requests , 'qr.html')
@login_required
def son (request):
    return render (request, 'vocal.html')


@login_required
def convertisseur(request):
    return render(request, 'convertisseur.html')
"""
Vues Django pour l'outil de transcription vocale.

Point important par rapport à ton script de départ :
------------------------------------------------------
Ton code utilisait `sr.Microphone()`, qui capture le micro de la machine
qui EXÉCUTE le script Python (donc ton serveur, pas l'ordinateur du visiteur).
Sur un site web, c'est le NAVIGATEUR du visiteur qui doit enregistrer le son
(via l'API MediaRecorder, déjà branchée dans le template transcription-vocale.html),
puis l'envoyer au serveur sous forme de fichier.

Côté Django, on remplace donc `sr.Microphone()` par `sr.AudioFile(...)`,
qui lit un fichier audio au lieu d'écouter un micro physique.

Le navigateur enregistre généralement en .webm/.ogg : on le convertit en
.wav (mono, 16 kHz) avec pydub, car SpeechRecognition ne sait lire
nativement que du WAV / AIFF / FLAC.

Dépendances à installer :
    pip install SpeechRecognition pydub
Et pydub a besoin de ffmpeg installé sur le système (apt install ffmpeg
sur Linux, ou via https://ffmpeg.org sur Windows/Mac).
"""

import os
import tempfile

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

import speech_recognition as sr
from pydub import AudioSegment

@login_required
def son(request):
    """Affiche la page de l'outil de transcription vocale."""
    return render(request, "vocal.html")

@login_required
@require_http_methods(["POST"])
def transcription(request):
    """
    Reçoit un fichier audio envoyé depuis le navigateur (champ 'audio'),
    le convertit en WAV, puis renvoie sa transcription en français.

    Réponse en cas de succès : {"transcription": "..."}
    Réponse en cas d'erreur   : {"error": "..."} avec un code HTTP adapté.
    """
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({"error": "Aucun fichier audio reçu."}, status=400)

    # on garde l'extension d'origine pour aider pydub/ffmpeg à détecter le format
    _, ext = os.path.splitext(audio_file.name)
    ext = ext if ext else ".webm"

    tmp_in_path = None
    tmp_out_path = None

    try:
        # 1. on écrit le fichier reçu sur le disque (fichier temporaire)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_in:
            for chunk in audio_file.chunks():
                tmp_in.write(chunk)
            tmp_in_path = tmp_in.name

        # 2. conversion en WAV mono 16 kHz, format lisible par SpeechRecognition
        tmp_out_path = tmp_in_path + ".wav"
        son = AudioSegment.from_file(tmp_in_path)
        son = son.set_channels(1).set_frame_rate(16000)
        son.export(tmp_out_path, format="wav")

        # 3. reconnaissance vocale, équivalent de ton script mais sur un
        #    fichier (AudioFile) plutôt que sur le micro (Microphone)
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_out_path) as source:
            audio = recognizer.record(source)  # équivalent de r.listen(source) pour un fichier

        try:
            texte = recognizer.recognize_google(audio, language="fr-FR")
        except sr.UnknownValueError:
            return JsonResponse(
                {"error": "Impossible de comprendre l'audio. Réessayez en parlant plus distinctement."},
                status=422,
            )
        except sr.RequestError:
            return JsonResponse(
                {"error": "Le service de reconnaissance vocale est momentanément indisponible."},
                status=503,
            )

        return JsonResponse({"transcription": texte})

    except Exception:
        return JsonResponse(
            {"error": "Le fichier audio n'a pas pu être traité. Vérifiez son format."},
            status=400,
        )

    finally:
        # 4. nettoyage des fichiers temporaires, quoi qu'il arrive
        for path in (tmp_in_path, tmp_out_path):
            if path and os.path.exists(path):
                os.remove(path)
