from django.db import models
from django.contrib.auth.models import User
from social.models import Friendship


class World(models.Model):
    """Represents a world created by a user."""
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('friends', 'Friends Only'),
        ('public', 'Public'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_worlds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    cover_image = models.ImageField(upload_to='world_covers/', blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    def can_view(self, user):
        """Check if a user can view this world."""
        if not user.is_authenticated:
            return self.visibility == 'public'
        
        # Owner always has access
        if user == self.owner:
            return True
        
        # Check collaborators (Feature 4)
        from collaboration.models import WorldCollaborator
        collaborator = WorldCollaborator.objects.filter(
            world=self, 
            user=user, 
            status='accepted'
        ).first()
        if collaborator:
            return True
        
        # Public worlds are visible to everyone
        if self.visibility == 'public':
            return True
        
        # Friends-only: check if user is a friend of the owner
        if self.visibility == 'friends':
            return Friendship.are_friends(user, self.owner)
        
        return False
    
    def can_edit(self, user):
        """Check if a user can edit this world."""
        if not user.is_authenticated:
            return False
        
        # Owner can always edit
        if user == self.owner:
            return True
        
        # Check for editor role in collaborators
        from collaboration.models import WorldCollaborator
        collaborator = WorldCollaborator.objects.filter(
            world=self, 
            user=user, 
            status='accepted', 
            role='editor'
        ).first()
        return bool(collaborator)


class WorldElement(models.Model):
    """Generic model for all world content types (creatures, peoples, maps, lore, etc.)."""
    ELEMENT_TYPE_CHOICES = [
        ('creature', 'Creature'),
        ('people', 'People/Volk'),
        ('map', 'Map'),
        ('lore', 'Lore Entry'),
    ]
    
    MAP_TYPE_CHOICES = [
        ('land', 'Land Map'),
        ('city', 'City Map'),
    ]
    
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name='elements')
    element_type = models.CharField(max_length=20, choices=ELEMENT_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)  # For maps and lore entries
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)  # Rich text/markdown for lore
    image = models.ImageField(upload_to='world_elements/', blank=True, null=True)
    map_type = models.CharField(max_length=10, choices=MAP_TYPE_CHOICES, blank=True)  # Only for maps
    habitat = models.CharField(max_length=200, blank=True)  # For creatures
    culture = models.TextField(blank=True)  # For peoples
    language_name = models.CharField(max_length=100, blank=True)  # For peoples
    attributes = models.JSONField(default=dict, blank=True)  # Flexible properties
    markers = models.JSONField(default=list, blank=True)  # For interactive map markers
    category = models.CharField(max_length=100, blank=True)  # For lore entries (custom categories)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='edited_elements')
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['world', 'element_type']),
        ]
    
    def __str__(self):
        return f"{self.get_element_type_display()}: {self.name or self.title}"
    
    def get_display_name(self):
        """Returns the appropriate name field based on element type."""
        return self.name or self.title
