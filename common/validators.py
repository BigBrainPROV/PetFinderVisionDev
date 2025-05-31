from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="Номер телефона в формате: '+ХХХХХХХХХХ'. Максимальная длина 15 цифр",
)
