from webcafeApp import models

def notifications(context):
    noti = []
    aux = 0
    noti_comments = []
    aux1 = 0
    user = context.user
    if user.username:
        notification = user.notifications.unread()
        noti_sells = notification.filter(description__isnull=False)
        noti = notification.exclude(description__isnull=False)
        aux = len(noti)
        aux1 = len(noti_sells)
        return {'notification': noti,'notifications_sells': noti_sells, 'count': aux, 'count_noti_sells':aux1}
    return {}

def user_app(context):
    if context.user.username:
        user = models.UserApp.objects.filter(pk=context.user.pk)
        print(user.get().image.__str__())
        if user.count() > 0:
            return {'userPhoto': user.get().image.__str__(), "FA2": user.get().fa2}
        return {}
    return {'userPhoto': None}


