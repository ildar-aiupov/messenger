from django.contrib import admin

from .models import Tag, MobileOperator, Mailing, Client, Message


@admin.register(MobileOperator)
class MobileOperatorAdmin(admin.ModelAdmin):
    """Админпанель мобильного оператора."""

    list_display = ["id", "code"]
    list_editable = ["code"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админпанель тэгов."""

    list_display = ["id", "name"]
    list_editable = ["name"]


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Админпанель рассылки."""

    list_display = [
        "id",
        "start_time",
        "stop_time",
        "text",
        "mobile_operator",
        "tag",
    ]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Админпанель клиента."""

    list_display = [
        "id",
        "phone_number",
        "mobile_operator",
        "tag",
        "time_zone",
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админпанель сообщения."""

    list_display = [
        "id",
        "created_at",
        "is_sent",
        "mailing",
        "client",
    ]
