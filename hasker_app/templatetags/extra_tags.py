from django import template

register = template.Library()


@register.inclusion_tag('hasker_app/vote.html')
def vote(obj, user):
    current_rate = 0
    if user.is_authenticated:
        user_rate = obj.rates.filter(user__user=user).all()
        if list(user_rate):
            current_rate = user_rate[0].rate
    return {
        'rate': obj.rate,
        'current': current_rate,
        'object': obj,
        'type': type(obj).__name__.lower(),
        'user': user
    }


@register.simple_tag
def define(val=None):
    return val
