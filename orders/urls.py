from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("menu/", views.menu, name="menu"),
    path("about-us", views.about_us, name="about_us"),
    path("contact", views.contact, name="contact"),
    path("detail/<int:product_id>", views.detail, name="detail"),
    path("add-to-cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart_view"),
    path("remove-cart-item/<int:order_product_id>", views.remove_cart_item, name="remove_cart_item"),
    path("plus-cart-item/<int:order_product_id>", views.plus_cart_item, name="plus_cart_item"),
    path("minus-cart-item/<int:order_product_id>", views.minus_cart_item, name="minus_cart_item"),
    path("clear-cart", views.clear_cart, name='clear_cart'),
    path("checkout", views.checkout, name='checkout'),
    path("order-history", views.order_history, name='order_history'),
    path("order-history-detail/<int:order_id>", views.order_history_detail, name='order_history_detail'),
    path("change-password", views.change_password, name='change_password'),
    path("change-email", views.change_email, name='change_email'),
]
