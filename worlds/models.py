from django.db import models
from django.utils import timezone


class World(models.Model):
    """Represents a world created by a user."""
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner_id = models.IntegerField(help_text="Session-basierte Owner-ID (ohne User-Account)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    cover_image = models.ImageField(upload_to='world_covers/', blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    @property
    def owner(self):
        """Dummy property for compatibility with templates."""
        return type('obj', (object,), {'id': self.owner_id})
    
    def can_view(self, request):
        """Check if request can view this world (based on session or visibility)."""
        # Owner always has access
        if request.session.get('owner_id') == self.owner_id:
            return True
        
        # Public worlds are visible to everyone
        if self.visibility == 'public':
            return True
        
        # Private worlds require access code
        return False
    
    def can_edit(self, request):
        """Check if request can edit this world."""
        return request.session.get('owner_id') == self.owner_id


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
    last_edited_by_id = models.IntegerField(null=True, blank=True, help_text="Session-basierte ID")
    
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
    
    @property
    def last_edited_by(self):
        """Dummy property for compatibility."""
        if self.last_edited_by_id:
            return type('obj', (object,), {'id': self.last_edited_by_id})
        return None
