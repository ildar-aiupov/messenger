import json

from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from django_celery_beat.models import PeriodicTask, ClockedSchedule

from .models import Mailing, Client
from celery_django.logger import mylogger
from api.v1.serializers import (
    ClientRequestSerializer,
    ClientResponseSerializer,
    MailingRequestSerializer,
    MailingResponseSerializer,
    InfoSerializer,
)


class InfoViewSet(viewsets.ModelViewSet):
    """Вьюсет статистики."""

    http_method_names = ["get"]
    queryset = Mailing.objects.all()
    serializer_class = InfoSerializer

    @extend_schema(
        summary="Shows general statistics on all mailings",
        description="Shows general statistics on all mailings",
        responses={200: InfoSerializer},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Shows statistics on specific mailing",
        description="Shows statistics on specific mailing",
        responses={200: InfoSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ClientViewSet(viewsets.ModelViewSet):
    """Вьюсет клиентов."""

    http_method_names = ["post", "put", "delete"]
    queryset = Client.objects.all()
    serializer_class = ClientRequestSerializer

    @extend_schema(
        summary="Creates a new client",
        description="Creates a new client",
        responses={201: ClientResponseSerializer},
    )
    def create(self, request):
        """Создает нового клиента."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_client = Client.objects.create(**serializer.validated_data)
        mylogger.info(f"Создан новый клиент id {new_client.id}")
        return Response(
            ClientResponseSerializer(new_client).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Updates a client",
        description="Updates a client",
        responses={200: ClientResponseSerializer},
    )
    def update(self, request, pk):
        """Обновляет клиента."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = get_object_or_404(Client, id=pk)
        client.phone_number = serializer.validated_data["phone_number"]
        client.mobile_operator = serializer.validated_data["mobile_operator"]
        client.tag = serializer.validated_data["tag"]
        client.time_zone = serializer.validated_data["time_zone"]
        client.save()
        mylogger.info(f"Обновлена запись клиента id {client.id}")
        return Response(
            ClientResponseSerializer(client).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Deletes a client",
        description="Deletes a client",
        responses={204: None},
    )
    def destroy(self, request, pk=None):
        """Удаляет клиента."""
        client = get_object_or_404(Client, id=pk)
        client.delete()
        mylogger.info(f"Удален клиент id {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class MailingViewSet(viewsets.ModelViewSet):
    """Вьюсет рассылок."""

    http_method_names = ["post", "put", "delete"]
    queryset = Mailing.objects.all()
    serializer_class = MailingRequestSerializer

    @extend_schema(
        summary="Creates a new mailing",
        description="Creates a new mailing",
        responses={201: MailingResponseSerializer},
    )
    def create(self, request):
        """Создает новую рассылку."""
        serializer = self.get_serializer(data=request.data)
        # проверяем данные и создаем новую рассылку
        serializer.is_valid(raise_exception=True)
        new_mailing = Mailing.objects.create(**serializer.validated_data)
        mylogger.info(f"Создана новая рассылка id {new_mailing.id}")
        # создаем задачу celery
        clocked = ClockedSchedule.objects.create(clocked_time=new_mailing.start_time)
        args = json.dumps((str(new_mailing.stop_time), new_mailing.id))
        PeriodicTask.objects.create(
            name=f"Mailing {str(new_mailing.id)}",
            task="celery_django.celery.send_messages_to_api",
            one_off=True,
            clocked=clocked,
            args=args,
        )
        return Response(
            MailingResponseSerializer(new_mailing).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Updates a mailing",
        description="Updates a mailing",
        responses={200: MailingResponseSerializer},
    )
    def update(self, request, pk):
        """Обновляет рассылку."""
        serializer = self.get_serializer(data=request.data)
        # проверяем данные и обновляем рассылку
        serializer.is_valid(raise_exception=True)
        mailing = get_object_or_404(Mailing, id=pk)
        mailing.start_time = serializer.validated_data["start_time"]
        mailing.stop_time = serializer.validated_data["stop_time"]
        mailing.text = serializer.validated_data["text"]
        mailing.mobile_operator = serializer.validated_data["mobile_operator"]
        mailing.tag = serializer.validated_data["tag"]
        mailing.save()
        mylogger.info(f"Обновлена рассылка id {mailing.id}")
        # обновляем соответствующую задачу celery
        periodic_task = PeriodicTask.objects.get(name=f"Mailing {str(mailing.id)}")
        periodic_task.clocked = ClockedSchedule.objects.create(
            clocked_time=mailing.start_time
        )
        periodic_task.args = json.dumps((str(mailing.stop_time), mailing.id))
        periodic_task.enabled = True
        periodic_task.save()
        return Response(
            MailingResponseSerializer(mailing).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Deletes a mailing",
        description="Deletes a mailing",
        responses={204: None},
    )
    def destroy(self, request, pk=None):
        """Удаляет рассылку."""
        # проверяем данные и удаляем рассылку
        mailing = get_object_or_404(Mailing, id=pk)
        mailing.delete()
        mylogger.info(f"Удалена рассылка id {pk}")
        # удаляем соответствующую задачу celery
        periodic_task = PeriodicTask.objects.get(name=f"Mailing {pk}")
        periodic_task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
