from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    """Represents a friendship request between two users."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"


class Friendship(models.Model):
    """Represents an accepted friendship between two users (symmetric)."""
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_b')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user_a', 'user_b']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user_a.username} <-> {self.user_b.username}"
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends."""
        if not user1.is_authenticated or not user2.is_authenticated:
            return False
        # Ensure consistent ordering
        if user1.id < user2.id:
            return cls.objects.filter(user_a=user1, user_b=user2).exists()
        else:
            return cls.objects.filter(user_a=user2, user_b=user1).exists()
    
    @classmethod
    def add_friendship(cls, user1, user2):
        """Create a friendship between two users with consistent ordering."""
        if user1.id < user2.id:
            return cls.objects.create(user_a=user1, user_b=user2)
        else:
            return cls.objects.create(user_a=user2, user_b=user1)
