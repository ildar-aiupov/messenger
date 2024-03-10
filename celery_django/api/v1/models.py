import pytz

from django.db import models

from .validators import phone_number_validator


TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


class MobileOperator(models.Model):
    """Модель мобильного оператора."""

    code = models.CharField(
        max_length=200, blank=False, unique=True, verbose_name="Код оператора"
    )

    def __str__(self) -> str:
        return self.code
    
    class Meta:
        verbose_name = "Мобильный оператор"
        verbose_name_plural = "Мобильные операторы"


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(
        max_length=200, blank=False, unique=True, verbose_name="Тэг"
    )

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"



class Mailing(models.Model):
    """Модель рассылки."""

    start_time = models.DateTimeField(blank=False, verbose_name="Время запуска")
    stop_time = models.DateTimeField(blank=False, verbose_name="Время окончания")
    text = models.TextField(
        max_length=1000, blank=False, verbose_name="Текст сообщения"
    )
    mobile_operator = models.ForeignKey(
        MobileOperator,
        on_delete=models.DO_NOTHING,
        blank=False,
        to_field="code",
        verbose_name="Код мобильного оператора",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.DO_NOTHING,
        blank=False,
        to_field="name",
        verbose_name="Тэг",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class Client(models.Model):
    """Модель клиента."""

    phone_number = models.CharField(
        max_length=11,
        blank=False,
        validators=[phone_number_validator],
        verbose_name="Номер телефона",
    )
    mobile_operator = models.ForeignKey(
        MobileOperator,
        on_delete=models.DO_NOTHING,
        blank=False,
        to_field="code",
        verbose_name="Код мобильного оператора",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.DO_NOTHING,
        blank=False,
        to_field="name",
        verbose_name="Тэг",
    )
    time_zone = models.CharField(
        max_length=32, choices=TIMEZONES, verbose_name="Часовой пояс"
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Message(models.Model):
    """Модель сообщения."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    is_sent = models.BooleanField(
        blank=False, default=False, verbose_name="Статус отправки"
    )
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, blank=False, verbose_name="Рассылка"
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, blank=False, verbose_name="Клиент"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
