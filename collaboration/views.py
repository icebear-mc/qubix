from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from worlds.models import World
from .models import WorldCollaborator


def world_invite_collaborator(request, world_pk):
    """Invite someone to collaborate on a world via access code (no account needed)."""
    world = get_object_or_404(World, pk=world_pk)
    
    # Only owner can invite collaborators
    if request.session.get('owner_id') != world.owner_id:
        messages.error(request, "Nur der Welt-Ersteller kann Mitarbeiter einladen.")
        return redirect('world_detail', pk=world.pk)
    
    # Redirect to access code management instead
    return redirect('social:manage_access_codes', world_id=world.pk)


def collaborator_invite_accept(request, pk):
    """Not used anymore - access codes handle this."""
    return redirect('world_list')


def collaborator_invite_decline(request, pk):
    """Not used anymore - access codes handle this."""
    return redirect('world_list')


def world_collaborators(request, world_pk):
    """List and manage collaborators for a world (owner only)."""
    world = get_object_or_404(World, pk=world_pk)
    
    if request.session.get('owner_id') != world.owner_id:
        messages.error(request, "Nur der Welt-Ersteller kann Mitarbeiter verwalten.")
        return redirect('world_detail', pk=world.pk)
    
    # Redirect to access code management
    return redirect('social:manage_access_codes', world_id=world.pk)


def collaborator_remove(request, pk):
    """Remove a collaborator from a world (owner only)."""
    collaborator = get_object_or_404(WorldCollaborator, pk=pk)
    
    if request.session.get('owner_id') != collaborator.world.owner_id:
        messages.error(request, "Nur der Welt-Ersteller kann Mitarbeiter entfernen.")
        return redirect('world_collaborators', world_pk=collaborator.world.pk)
    
    if request.method == 'POST':
        collaborator.delete()
        messages.success(request, "Mitarbeiter entfernt.")
        return redirect('social:manage_access_codes', world_id=collaborator.world.pk)
    
    return redirect('social:manage_access_codes', world_id=collaborator.world.pk)
