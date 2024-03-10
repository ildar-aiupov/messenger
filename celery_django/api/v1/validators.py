from django.core.exceptions import ValidationError


def phone_number_validator(value: str) -> str | None:
    """Проверяет, что поле состоит только из цифр."""
    if value[0] == "7" and all(x.isdigit() for x in value):
        return value
    else:
        raise ValidationError(
            "Номер телефона должен начинаться с цифры 7 и состоять только из цифр."
        )
