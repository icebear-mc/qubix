from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import World, WorldElement


def world_list(request):
    """Display list of worlds accessible to the user."""
    if request.user.is_authenticated:
        # Show owned worlds + worlds where user is collaborator + public worlds + friends' worlds
        owned = World.objects.filter(owner=request.user)
        collab_world_ids = request.user.world_collaborations.filter(status='accepted').values_list('world_id', flat=True)
        collab_worlds = World.objects.filter(id__in=collab_world_ids)
        public = World.objects.filter(visibility='public')
        
        # Friends' worlds (friends-only visibility)
        from social.models import Friendship
        friend_ids = Friendship.objects.filter(
            Q(user_a=request.user) | Q(user_b=request.user)
        ).values_list('user_b', flat=True) if True else []
        # Get actual friend IDs (need to handle both directions)
        friendships = Friendship.objects.filter(Q(user_a=request.user) | Q(user_b=request.user))
        friend_ids = set()
        for f in friendships:
            if f.user_a == request.user:
                friend_ids.add(f.user_b.id)
            else:
                friend_ids.add(f.user_a.id)
        
        friends_worlds = World.objects.filter(
            visibility='friends',
            owner__id__in=friend_ids
        )
        
        worlds = (owned | collab_worlds | public | friends_worlds).distinct()
    else:
        # Anonymous users only see public worlds
        worlds = World.objects.filter(visibility='public')
    
    return render(request, 'worlds/world_list.html', {'worlds': worlds})


def world_detail(request, pk):
    """Display details of a single world."""
    world = get_object_or_404(World, pk=pk)
    
    if not world.can_view(request.user):
        messages.error(request, "You don't have permission to view this world.")
        return redirect('world_list')
    
    can_edit = world.can_edit(request.user) if request.user.is_authenticated else False
    
    # Group elements by type
    creatures = world.elements.filter(element_type='creature')
    peoples = world.elements.filter(element_type='people')
    maps = world.elements.filter(element_type='map')
    lore = world.elements.filter(element_type='lore')
    
    return render(request, 'worlds/world_detail.html', {
        'world': world,
        'can_edit': can_edit,
        'creatures': creatures,
        'peoples': peoples,
        'maps': maps,
        'lore': lore,
    })


@login_required
def world_create(request):
    """Create a new world."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        visibility = request.POST.get('visibility', 'private')
        
        world = World.objects.create(
            name=name,
            description=description,
            owner=request.user,
            visibility=visibility
        )
        
        messages.success(request, f"World '{world.name}' created successfully!")
        return redirect('world_detail', pk=world.pk)
    
    return render(request, 'worlds/world_form.html', {'action': 'create'})


@login_required
def world_edit(request, pk):
    """Edit an existing world."""
    world = get_object_or_404(World, pk=pk)
    
    if not world.can_edit(request.user):
        messages.error(request, "You don't have permission to edit this world.")
        return redirect('world_detail', pk=world.pk)
    
    if request.method == 'POST':
        world.name = request.POST.get('name')
        world.description = request.POST.get('description')
        world.visibility = request.POST.get('visibility', world.visibility)
        world.save()
        
        messages.success(request, f"World '{world.name}' updated successfully!")
        return redirect('world_detail', pk=world.pk)
    
    return render(request, 'worlds/world_form.html', {'world': world, 'action': 'edit'})


@login_required
def world_delete(request, pk):
    """Delete a world (owner only)."""
    world = get_object_or_404(World, pk=pk)
    
    if request.user != world.owner:
        messages.error(request, "Only the owner can delete this world.")
        return redirect('world_detail', pk=world.pk)
    
    if request.method == 'POST':
        world_name = world.name
        world.delete()
        messages.success(request, f"World '{world_name}' deleted successfully!")
        return redirect('world_list')
    
    return render(request, 'worlds/world_confirm_delete.html', {'world': world})


@login_required
def element_create(request, world_pk, element_type):
    """Create a new world element."""
    world = get_object_or_404(World, pk=world_pk)
    
    if not world.can_edit(request.user):
        messages.error(request, "You don't have permission to add elements to this world.")
        return redirect('world_detail', pk=world.pk)
    
    if request.method == 'POST':
        element = WorldElement.objects.create(
            world=world,
            element_type=element_type,
            name=request.POST.get('name', ''),
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            content=request.POST.get('content', ''),
            habitat=request.POST.get('habitat', ''),
            culture=request.POST.get('culture', ''),
            language_name=request.POST.get('language_name', ''),
            map_type=request.POST.get('map_type', ''),
            category=request.POST.get('category', ''),
            last_edited_by=request.user
        )
        
        # Handle image upload
        if request.FILES.get('image'):
            element.image = request.FILES['image']
            element.save()
        
        messages.success(request, f"{element.get_element_type_display()} '{element.get_display_name()}' created!")
        return redirect('world_detail', pk=world.pk)
    
    return render(request, 'worlds/element_form.html', {
        'world': world,
        'element_type': element_type,
        'action': 'create'
    })


@login_required
def element_edit(request, pk):
    """Edit an existing world element."""
    element = get_object_or_404(WorldElement, pk=pk)
    
    if not element.world.can_edit(request.user):
        messages.error(request, "You don't have permission to edit this element.")
        return redirect('world_detail', pk=element.world.pk)
    
    if request.method == 'POST':
        element.name = request.POST.get('name', element.name)
        element.title = request.POST.get('title', element.title)
        element.description = request.POST.get('description', element.description)
        element.content = request.POST.get('content', element.content)
        element.habitat = request.POST.get('habitat', element.habitat)
        element.culture = request.POST.get('culture', element.culture)
        element.language_name = request.POST.get('language_name', element.language_name)
        element.map_type = request.POST.get('map_type', element.map_type)
        element.category = request.POST.get('category', element.category)
        element.last_edited_by = request.user
        
        if request.FILES.get('image'):
            element.image = request.FILES['image']
        
        element.save()
        
        messages.success(request, f"'{element.get_display_name()}' updated!")
        return redirect('world_detail', pk=element.world.pk)
    
    return render(request, 'worlds/element_form.html', {
        'element': element,
        'action': 'edit'
    })


@login_required
def element_delete(request, pk):
    """Delete a world element."""
    element = get_object_or_404(WorldElement, pk=pk)
    world_pk = element.world.pk
    
    if not element.world.can_edit(request.user):
        messages.error(request, "You don't have permission to delete this element.")
        return redirect('world_detail', pk=world_pk)
    
    if request.method == 'POST':
        element.delete()
        messages.success(request, f"'{element.get_display_name()}' deleted!")
        return redirect('world_detail', pk=world_pk)
    
    return render(request, 'worlds/element_confirm_delete.html', {'element': element})


def element_detail(request, pk):
    """Display details of a single world element."""
    element = get_object_or_404(WorldElement, pk=pk)
    
    if not element.world.can_view(request.user):
        messages.error(request, "You don't have permission to view this element.")
        return redirect('world_list')
    
    can_edit = element.world.can_edit(request.user) if request.user.is_authenticated else False
    
    return render(request, 'worlds/element_detail.html', {
        'element': element,
        'can_edit': can_edit
    })


def map_view(request, pk):
    """Display an interactive map view with markers."""
    map_entry = get_object_or_404(WorldElement, pk=pk, element_type='map')
    
    if not map_entry.world.can_view(request.user):
        messages.error(request, "You don't have permission to view this map.")
        return redirect('world_list')
    
    return render(request, 'worlds/map_view.html', {
        'map_entry': map_entry,
        'markers': map_entry.markers
    })
