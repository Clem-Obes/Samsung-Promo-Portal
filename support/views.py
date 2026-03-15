from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatMessage


@login_required
def chat_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(
                user=request.user,
                message=message,
                sender='user'
            )

    chat_messages = ChatMessage.objects.filter(user=request.user)
    return render(request, 'support/chat.html', {'chat_messages': chat_messages})


def faq_view(request):
    return render(request, 'support/faq.html')
