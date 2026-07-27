from django.db import models
from django.contrib.auth.models import User
from worlds.models import World


class WorldCollaborator(models.Model):
    """Represents a collaborator (non-owner) with access to a world."""
    ROLE_CHOICES = [
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    ]
    
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='world_collaborations')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='editor')
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_collab_invites')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['world', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.world.name} ({self.role}, {self.status})"
