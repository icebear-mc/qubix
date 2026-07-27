from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from worlds.models import World
from .models import WorldCollaborator
from social.models import Friendship


@login_required
def world_invite_collaborator(request, world_pk):
    """Invite a friend to collaborate on a world."""
    world = get_object_or_404(World, pk=world_pk)
    
    # Only owner can invite collaborators
    if request.user != world.owner:
        messages.error(request, "Only the world owner can invite collaborators.")
        return redirect('world_detail', pk=world.pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'editor')
        
        user = get_object_or_404(User, username=username)
        
        # Can't invite yourself
        if user == world.owner:
            messages.error(request, "You are already the owner of this world.")
            return redirect('world_detail', pk=world.pk)
        
        # Check if already a collaborator
        existing = WorldCollaborator.objects.filter(world=world, user=user).first()
        if existing:
            messages.info(request, f"{user.username} is already a collaborator on this world.")
            return redirect('world_detail', pk=world.pk)
        
        # Create invitation
        WorldCollaborator.objects.create(
            world=world,
            user=user,
            role=role,
            invited_by=request.user,
            status='pending'
        )
        
        messages.success(request, f"Invitation sent to {user.username}!")
        return redirect('world_detail', pk=world.pk)
    
    # Get list of friends for selection
    friendships = Friendship.objects.filter(
        Q(user_a=request.user) | Q(user_b=request.user)
    )
    friends = []
    for f in friendships:
        friend = f.user_b if f.user_a == request.user else f.user_a
        # Exclude existing collaborators
        is_collaborator = WorldCollaborator.objects.filter(world=world, user=friend).exists()
        if not is_collaborator:
            friends.append(friend)
    
    return render(request, 'collaboration/invite_collaborator.html', {
        'world': world,
        'friends': friends
    })


@login_required
def collaborator_invite_accept(request, pk):
    """Accept a collaboration invitation."""
    invite = get_object_or_404(WorldCollaborator, pk=pk, user=request.user)
    
    if request.method == 'POST':
        invite.status = 'accepted'
        invite.save()
        
        messages.success(request, f"You are now a collaborator on '{invite.world.name}'!")
        return redirect('world_detail', pk=invite.world.pk)
    
    return render(request, 'collaboration/invite_confirm.html', {
        'invite': invite,
        'action': 'accept'
    })


@login_required
def collaborator_invite_decline(request, pk):
    """Decline a collaboration invitation."""
    invite = get_object_or_404(WorldCollaborator, pk=pk, user=request.user)
    
    if request.method == 'POST':
        invite.delete()
        
        messages.success(request, "Invitation declined.")
        return redirect('world_list')
    
    return render(request, 'collaboration/invite_confirm.html', {
        'invite': invite,
        'action': 'decline'
    })


@login_required
def world_collaborators(request, world_pk):
    """List and manage collaborators for a world (owner only)."""
    world = get_object_or_404(World, pk=world_pk)
    
    if request.user != world.owner:
        messages.error(request, "Only the world owner can manage collaborators.")
        return redirect('world_detail', pk=world.pk)
    
    pending = world.collaborators.filter(status='pending')
    accepted = world.collaborators.filter(status='accepted')
    
    return render(request, 'collaboration/collaborators_list.html', {
        'world': world,
        'pending': pending,
        'accepted': accepted
    })


@login_required
def collaborator_remove(request, pk):
    """Remove a collaborator from a world (owner only)."""
    collaborator = get_object_or_404(WorldCollaborator, pk=pk)
    
    if request.user != collaborator.world.owner:
        messages.error(request, "Only the world owner can remove collaborators.")
        return redirect('world_collaborators', world_pk=collaborator.world.pk)
    
    if request.method == 'POST':
        collaborator.delete()
        messages.success(request, f"{collaborator.user.username} removed from '{collaborator.world.name}'.")
        return redirect('world_collaborators', world_pk=collaborator.world.pk)
    
    return render(request, 'collaboration/collaborator_confirm_remove.html', {
        'collaborator': collaborator
    })
