from .models import Message, Notification

def notifications_processor(request):
    """
    Add notification counts to all templates
    """
    if request.user.is_authenticated:
        unread_messages_count = Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        unread_notifications_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return {
            'unread_messages_count': unread_messages_count,
            'unread_notifications_count': unread_notifications_count,
        }
    
    return {
        'unread_messages_count': 0,
        'unread_notifications_count': 0,
    }