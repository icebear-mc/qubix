from django.db import models
from django.contrib.auth.models import User
from worlds.models import World


class NixonConversation(models.Model):
    """Represents a conversation with the Nixon AI assistant."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nixon_conversations')
    world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True, blank=True, related_name='nixon_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        world_name = self.world.name if self.world else "No World"
        return f"{self.user.username} - {world_name} ({self.created_at})"


class NixonMessage(models.Model):
    """Represents a single message in a Nixon conversation."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('nixon', 'Nixon'),
    ]
    
    conversation = models.ForeignKey(NixonConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}..."
