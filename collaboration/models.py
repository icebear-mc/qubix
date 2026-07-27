from django.db import models
from worlds.models import World
import uuid


class WorldCollaborator(models.Model):
    """Represents a collaborator with access to a world via unique code."""
    ROLE_CHOICES = [
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name='collaborators')
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='editor')
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.CharField(max_length=50, blank=True, help_text="Optional identifier for who used this code")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Collaborator access for {self.world.name} ({self.role}) - Code: {self.code}"
