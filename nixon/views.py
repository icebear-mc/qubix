from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from worlds.models import World
from .models import NixonConversation, NixonMessage


@login_required
def nixon_chat(request, world_pk=None):
    """Display the Nixon AI chat interface."""
    world = None
    conversation = None
    
    if world_pk:
        world = get_object_or_404(World, pk=world_pk)
        if not world.can_view(request.user):
            return redirect('world_list')
        
        # Get or create conversation for this world
        conversation = NixonConversation.objects.filter(
            user=request.user,
            world=world
        ).first()
    
    if not conversation:
        # Create a general conversation (no world context)
        conversation = NixonConversation.objects.create(user=request.user)
    
    messages = conversation.messages.all()
    
    return render(request, 'nixon/chat.html', {
        'conversation': conversation,
        'world': world,
        'messages': messages
    })


@login_required
@require_POST
def nixon_send_message(request):
    """Send a message to Nixon and get a response."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        world_pk = data.get('world_id')
        
        if not user_message.strip():
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        world = None
        if world_pk:
            world = get_object_or_404(World, pk=world_pk)
            if not world.can_view(request.user):
                return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get or create conversation
        if world:
            conversation, _ = NixonConversation.objects.get_or_create(
                user=request.user,
                world=world
            )
        else:
            conversation, _ = NixonConversation.objects.get_or_create(
                user=request.user,
                world=None
            )
        
        # Save user message
        NixonMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Build context for the AI prompt
        context = build_nixon_context(world, conversation)
        
        # Generate Nixon's response (placeholder - would call LLM API in production)
        nixon_response = generate_nixon_response(user_message, context)
        
        # Save Nixon's response
        nixon_msg = NixonMessage.objects.create(
            conversation=conversation,
            role='nixon',
            content=nixon_response
        )
        
        return JsonResponse({
            'response': nixon_response,
            'message_id': nixon_msg.id,
            'created_at': nixon_msg.created_at.isoformat()
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def build_nixon_context(world, conversation):
    """Build context information for Nixon's AI prompt."""
    context = {
        'world_name': world.name if world else None,
        'world_description': world.description if world else None,
        'elements': []
    }
    
    if world:
        # Get recent elements from the world
        elements = world.elements.all()[:10]
        for elem in elements:
            context['elements'].append({
                'type': elem.get_element_type_display(),
                'name': elem.get_display_name(),
                'description': elem.description[:200] if elem.description else ''
            })
    
    # Get recent conversation history
    recent_messages = conversation.messages.all().order_by('-created_at')[:5]
    context['recent_messages'] = [
        {'role': m.role, 'content': m.content}
        for m in reversed(recent_messages)
    ]
    
    return context


def generate_nixon_response(user_message, context):
    """
    Generate Nixon's response.
    
    In production, this would call an LLM API (OpenAI, Anthropic, etc.).
    For now, returns placeholder responses based on keywords.
    """
    message_lower = user_message.lower()
    
    # System prompt context
    system_prompt = f"""You are Nixon, a creative Worldbuilding Assistant. 
    The user is working on the world '{context['world_name']}' ({context['world_description'][:100] if context['world_description'] else 'no description'})
    
    Give concrete, original suggestions for creatures, peoples, places, or stories that fit the existing style of the world.
    Keep answers short and inspiring, no long essays."""
    
    # Placeholder responses (would be replaced with actual LLM API call)
    if 'creature' in message_lower or 'monster' in message_lower:
        return "Here's a creature idea: **The Shadowmaw** - A pack hunter that exists partially in shadow, able to step between dimly lit areas. Its eyes glow with captured starlight, and it communicates through harmonic humming. Weakness: bright light disrupts its shadow-phase."
    
    if 'people' in message_lower or 'volk' in message_lower or 'culture' in message_lower:
        return "Here's a people concept: **The Tidecallers** - A coastal civilization that has developed a unique language based on wave patterns. They believe the moon whispers secrets to them, and their architecture is built to amplify ocean sounds into music."
    
    if 'city' in message_lower or 'place' in message_lower or 'location' in message_lower:
        return "Location idea: **The Whispering Market** - A bazaar that only appears during eclipses, where merchants trade memories instead of goods. Visitors can purchase forgotten skills or sell unwanted recollections."
    
    if 'story' in message_lower or 'plot' in message_lower or 'history' in message_lower:
        return "Plot twist idea: The ancient prophecy everyone fears? It was actually written by the villains themselves as a self-fulfilling manipulation. The real heroes were erased from history."
    
    if 'name' in message_lower:
        return "Name suggestions: **Aethermoor**, **Shadowfen**, **Crystalheim**, **The Gilded Wastes**, **Mount Seraphim**"
    
    # Default response
    return f"I'm Nixon, your Worldbuilding Assistant! I see you're working on '{context['world_name']}'. Ask me about creatures, peoples, locations, stories, or names - I'll give you creative suggestions tailored to your world!"
