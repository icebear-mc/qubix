from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from worlds.models import World
from .models import WorldAccessCode, WorldComment


def access_world(request, code):
    """
    Zugriff auf eine Welt über einen Zugangscode.
    Prüft den Code, aktualisiert Nutzungsstatistiken und leitet zur Welt weiter.
    """
    access_code = get_object_or_404(WorldAccessCode, code=code)
    
    if not access_code.is_active:
        messages.error(request, "Dieser Zugangscode ist nicht mehr aktiv.")
        return redirect('world_list')
    
    # Code-Nutzung registrieren
    access_code.use_code()
    
    messages.success(request, f"Zugriff gewährt für: {access_code.world.name}")
    return redirect('world_detail', pk=access_code.world.pk)


def create_access_code(request, world_id):
    """
    Erstellt einen neuen Zugangscode für eine Welt (nur für Owner).
    """
    world = get_object_or_404(World, pk=world_id)
    
    # Einfache Prüfung: Nur Owner kann Codes erstellen
    if request.session.get('owner_id') != world.owner_id:
        messages.error(request, "Nur der Ersteller dieser Welt kann Zugangscodes erzeugen.")
        return redirect('world_detail', pk=world.pk)
    
    if request.method == 'POST':
        description = request.POST.get('description', '')
        access_code = WorldAccessCode.objects.create(
            world=world,
            description=description
        )
        messages.success(request, f"Neuer Zugangscode erstellt: {access_code.code}")
        return redirect('world_detail', pk=world.pk)
    
    return render(request, 'social/create_access_code.html', {'world': world})


def add_comment(request, world_id):
    """
    Fügt einen anonymen Kommentar zu einer Welt hinzu.
    """
    world = get_object_or_404(World, pk=world_id)
    
    if request.method == 'POST':
        author_name = request.POST.get('author_name', 'Anonym')
        content = request.POST.get('content', '')
        
        if not content:
            messages.error(request, "Bitte gib einen Kommentar ein.")
        else:
            WorldComment.objects.create(
                world=world,
                author_name=author_name or 'Anonym',
                content=content,
                is_approved=False  # Muss genehmigt werden
            )
            messages.success(request, "Dein Kommentar wurde eingereicht und wartet auf Genehmigung.")
        
        return redirect('world_detail', pk=world.pk)
    
    return redirect('world_detail', pk=world.pk)


def approve_comment(request, comment_id):
    """
    Genehmigt einen Kommentar (nur für World-Owner).
    """
    comment = get_object_or_404(WorldComment, pk=comment_id)
    
    # Einfache Owner-Prüfung
    if request.session.get('owner_id') != comment.world.owner_id:
        messages.error(request, "Nur der Ersteller dieser Welt kann Kommentare genehmigen.")
        return redirect('world_detail', pk=comment.world.pk)
    
    comment.is_approved = True
    comment.save()
    messages.success(request, "Kommentar genehmigt.")
    return redirect('world_detail', pk=comment.world.pk)


def delete_comment(request, comment_id):
    """
    Löscht einen Kommentar (nur für World-Owner oder Autor).
    """
    comment = get_object_or_404(WorldComment, pk=comment_id)
    world_pk = comment.world.pk
    
    # Owner oder Autor darf löschen
    if request.session.get('owner_id') != comment.world.owner_id:
        messages.error(request, "Du darfst diesen Kommentar nicht löschen.")
        return redirect('world_detail', pk=world_pk)
    
    comment.delete()
    messages.success(request, "Kommentar gelöscht.")
    return redirect('world_detail', pk=world_pk)


def manage_access_codes(request, world_id):
    """
    Übersicht aller Zugangscodes für eine Welt (nur für Owner).
    """
    world = get_object_or_404(World, pk=world_id)
    
    if request.session.get('owner_id') != world.owner_id:
        messages.error(request, "Nur der Ersteller dieser Welt kann Zugangscodes verwalten.")
        return redirect('world_detail', pk=world.pk)
    
    codes = WorldAccessCode.objects.filter(world=world)
    return render(request, 'social/manage_access_codes.html', {
        'world': world,
        'codes': codes
    })


def deactivate_code(request, code_id):
    """
    Deaktiviert einen Zugangscode.
    """
    access_code = get_object_or_404(WorldAccessCode, pk=code_id)
    
    if request.session.get('owner_id') != access_code.world.owner_id:
        messages.error(request, "Du darfst diesen Code nicht deaktivieren.")
        return redirect('world_detail', pk=access_code.world.pk)
    
    access_code.is_active = False
    access_code.save()
    messages.success(request, "Zugangscode deaktiviert.")
    return redirect('social:manage_access_codes', world_id=access_code.world.pk)
