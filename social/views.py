from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User

from .models import FriendRequest, Friendship


@login_required
def user_search(request):
    """Search for users by username."""
    query = request.GET.get('q', '')
    users = []
    
    if query and len(query) >= 2:
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id)[:10]
    
    return render(request, 'social/user_search.html', {
        'query': query,
        'users': users
    })


@login_required
def friend_request_send(request, username):
    """Send a friend request to a user."""
    to_user = get_object_or_404(User, username=username)
    
    if to_user == request.user:
        messages.error(request, "You can't send a friend request to yourself.")
        return redirect('user_search')
    
    # Check if already friends
    if Friendship.are_friends(request.user, to_user):
        messages.info(request, f"You are already friends with {to_user.username}.")
        return redirect('user_search')
    
    # Check if pending request exists
    existing = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing:
        messages.info(request, f"A friend request already exists between you and {to_user.username}.")
        return redirect('user_search')
    
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, f"Friend request sent to {to_user.username}!")
    return redirect('user_search')


@login_required
def friend_request_list(request):
    """List incoming and outgoing friend requests."""
    incoming = FriendRequest.objects.filter(to_user=request.user, status='pending')
    outgoing = FriendRequest.objects.filter(from_user=request.user, status='pending')
    
    return render(request, 'social/friend_request_list.html', {
        'incoming': incoming,
        'outgoing': outgoing
    })


@login_required
def friend_request_accept(request, pk):
    """Accept a friend request."""
    friend_request = get_object_or_404(FriendRequest, pk=pk, to_user=request.user)
    
    if request.method == 'POST':
        friend_request.status = 'accepted'
        friend_request.responded_at = timezone.now()
        friend_request.save()
        
        Friendship.add_friendship(friend_request.from_user, friend_request.to_user)
        
        messages.success(request, f"You are now friends with {friend_request.from_user.username}!")
        return redirect('friend_request_list')
    
    return render(request, 'social/friend_request_confirm.html', {
        'friend_request': friend_request,
        'action': 'accept'
    })


@login_required
def friend_request_decline(request, pk):
    """Decline a friend request."""
    friend_request = get_object_or_404(FriendRequest, pk=pk, to_user=request.user)
    
    if request.method == 'POST':
        friend_request.status = 'declined'
        friend_request.responded_at = timezone.now()
        friend_request.save()
        
        messages.success(request, "Friend request declined.")
        return redirect('friend_request_list')
    
    return render(request, 'social/friend_request_confirm.html', {
        'friend_request': friend_request,
        'action': 'decline'
    })


@login_required
def friend_list(request):
    """List all friends of the current user."""
    friendships = Friendship.objects.filter(
        Q(user_a=request.user) | Q(user_b=request.user)
    )
    
    friends = []
    for f in friendships:
        if f.user_a == request.user:
            friends.append(f.user_b)
        else:
            friends.append(f.user_a)
    
    return render(request, 'social/friend_list.html', {'friends': friends})


@login_required
def friend_remove(request, username):
    """Remove a friend."""
    friend = get_object_or_404(User, username=username)
    
    if not Friendship.are_friends(request.user, friend):
        messages.error(request, f"You are not friends with {username}.")
        return redirect('friend_list')
    
    if request.method == 'POST':
        # Delete the friendship
        if request.user.id < friend.id:
            Friendship.objects.filter(user_a=request.user, user_b=friend).delete()
        else:
            Friendship.objects.filter(user_a=friend, user_b=request.user).delete()
        
        messages.success(request, f"{username} removed from your friends.")
        return redirect('friend_list')
    
    return render(request, 'social/friend_confirm_remove.html', {'friend': friend})


# Import timezone for datetime
from django.utils import timezone
