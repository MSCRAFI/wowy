from django.urls import path
from users.views.admin_views import (
    admin_dashboard,
    admin_orders,
    admin_order_detail,
    admin_order_edit,
    admin_categories,
    admin_category_add,
    admin_category_edit,
    admin_offers,
    admin_offer_add,
    admin_offer_edit,
    admin_offer_delete,
    admin_products,
    admin_product_add,
    admin_product_view,
    admin_product_edit,
    admin_product_delete,
    admin_product_image_delete,
    update_order_status,
    generate_order_pdf,
    admin_customers,
    admin_customer_detail,
    admin_general_settings,
    admin_payment_settings,
    admin_email_settings,
)

urlpatterns = [
    path("", admin_dashboard, name="admin.index"),
    path("orders/", admin_orders, name="admin.orders"),
    path("orders/<int:order_id>/", admin_order_detail, name="admin.order_detail"),
    path("orders/<int:order_id>/edit/", admin_order_edit, name="admin.order_edit"),
    path(
        "orders/<int:order_id>/status/",
        update_order_status,
        name="admin.orders.update_status",
    ),
    path("categories/", admin_categories, name="admin_categories"),
    path("categories/add/", admin_category_add, name="admin_category_add"),
    path(
        "categories/<int:category_id>/edit/",
        admin_category_edit,
        name="admin_category_edit",
    ),
    path("offers/", admin_offers, name="admin_offers"),
    path("offers/add/", admin_offer_add, name="admin_offer_add"),
    path("offers/<int:offer_id>/edit/", admin_offer_edit, name="admin_offer_edit"),
    path(
        "offers/<int:offer_id>/delete/", admin_offer_delete, name="admin_offer_delete"
    ),
    path("products/", admin_products, name="admin_products"),
    path("products/add/", admin_product_add, name="admin_product_add"),
    path("products/<int:product_id>/", admin_product_view, name="admin_product_view"),
    path(
        "products/<int:product_id>/edit/", admin_product_edit, name="admin_product_edit"
    ),
    path(
        "products/<int:product_id>/delete/",
        admin_product_delete,
        name="admin_product_delete",
    ),
    path(
        "products/images/<int:image_id>/delete/",
        admin_product_image_delete,
        name="admin_product_image_delete",
    ),
    path('orders/<int:order_id>/pdf/', generate_order_pdf, name='admin.orders.pdf'),
    path('customers/', admin_customers, name='admin.customers'),
    path('customers/<int:user_id>/', admin_customer_detail, name='admin.customer_detail'),
    path('settings/general/', admin_general_settings, name='admin.settings.general'),
    path('settings/payment/', admin_payment_settings, name='admin.settings.payment'),
    path('settings/email/', admin_email_settings, name='admin.settings.email'),
]
