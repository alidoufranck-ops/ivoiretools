from django.db import models
import uuid
from django.contrib.auth.models import User
# Create your models here.
class table (models.Model):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   nom = models.CharField(max_length=100)
   photo_original = models.URLField("URL de l'image")
   utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="travaux"
    )

   photo_original_fichie =  models.ImageField(
        upload_to='images_originales/',
        blank=True,
        null=True
    )
   photo_modifier = models.ImageField(upload_to='images_modifier/', blank=True,
        null=True)
   
def __str__(self):
    return self.nom