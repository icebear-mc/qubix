from django.db import models
import uuid


class WorldAccessCode(models.Model):
    """
    Ein einfacher Zugangscode für eine Welt, der ohne Benutzerkonto funktioniert.
    Jeder Code gewährt Zugriff auf eine spezifische Welt.
    """
    world = models.ForeignKey('worlds.World', on_delete=models.CASCADE, related_name='access_codes')
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.CharField(max_length=100, blank=True, help_text="Optional: Beschreibung wofür dieser Code ist (z.B. 'Für Spielergruppe A')")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Code für {self.world.name}: {str(self.code)[:8]}..."
    
    def use_code(self):
        """Erhöht den Nutzungszähler und aktualisiert last_used."""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save()


class WorldComment(models.Model):
    """
    Kommentare zu einer Welt - anonym oder mit optionalem Namen.
    Ermöglicht Feedback ohne Account.
    """
    world = models.ForeignKey('worlds.World', on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=50, blank=True, default="Anonym", help_text="Dein Name (optional)")
    content = models.TextField(help_text="Dein Kommentar")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Muss vom Welt-Ersteller genehmigt werden")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Kommentar von {self.author_name} zu {self.world.name}"
