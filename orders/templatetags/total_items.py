from django import template
from orders.models import Order

register = template.Library()


@register.filter(name='get_total_cart')
def get_total_cart(user):
    order_qs = Order.objects.filter(user=user, finished=False)
    if order_qs.exists():
        order = order_qs[0]
        return order.total_item()
    return 0
