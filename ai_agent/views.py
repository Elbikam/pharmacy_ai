from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .agent import PharmacyAIAgent  # Critical import added

from twilio.twiml.messaging_response import MessagingResponse

@csrf_exempt
def WhatsAppWebhook(request):
    if request.method == 'POST':
        message = request.POST.get('Body', '').strip()
        from_num = request.POST.get('From', '')
        
        agent = PharmacyAIAgent()
        response_text = agent.handle_whatsapp_message(message, from_num)
        
        twiml = MessagingResponse()
        twiml.message(response_text)
        
        return HttpResponse(str(twiml), content_type='text/xml')
    
    return HttpResponse(status=400)