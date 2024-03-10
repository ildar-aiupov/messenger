from rest_framework import serializers

from .models import Mailing, Client


class ClientRequestSerializer(serializers.ModelSerializer):
    """Сериалайзер входящих данных при создании и обновлении клиента."""

    class Meta:
        model = Client
        fields = [
            "phone_number",
            "mobile_operator",
            "tag",
            "time_zone",
        ]


class ClientResponseSerializer(serializers.ModelSerializer):
    """Сериалайзер возвращаемого результата при успешном создании и обновлении клиента."""

    class Meta:
        model = Client
        fields = [
            "id",
            "phone_number",
            "mobile_operator",
            "tag",
            "time_zone",
        ]


class MailingRequestSerializer(serializers.ModelSerializer):
    """Сериалайзер входящих данных при создании и обновлении рассылки."""

    class Meta:
        model = Mailing
        fields = [
            "start_time",
            "stop_time",
            "text",
            "mobile_operator",
            "tag",
        ]


class MailingResponseSerializer(serializers.ModelSerializer):
    """Сериалайзер возвращаемого результата при успешном создании и обновлении рассылки."""

    class Meta:
        model = Mailing
        fields = [
            "id",
            "start_time",
            "stop_time",
            "text",
            "mobile_operator",
            "tag",
        ]


class InfoSerializer(serializers.Serializer):
    """Сериалайзер статистики рассылок."""

    mailing_id = serializers.SerializerMethodField()
    sent_messages = serializers.SerializerMethodField()
    not_sent_messages = serializers.SerializerMethodField()

    def get_mailing_id(self, obj: Mailing):
        return obj.id

    def get_sent_messages(self, obj: Mailing):
        return obj.message_set.filter(mailing=obj).filter(is_sent=True).count()

    def get_not_sent_messages(self, obj: Mailing):
        return obj.message_set.filter(mailing=obj).filter(is_sent=False).count()
