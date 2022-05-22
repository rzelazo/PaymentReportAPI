from .models import *
from rest_framework import serializers
from django.utils import timezone

PAY_BY_LINK = "pay_by_link"
DIRECT_PAYMENT = "dp"
CARD = "card"

CURRENCY_CHOICES = (('EUR', 'EUR'),
                    ('USD', 'USD'),
                    ('GBP', 'GBP'),
                    ('PLN', 'PLN'))


def validateDate(date):
    if date > timezone.now():
        raise serializers.ValidationError("Date cannot be from the future!")
    else:
        return date


class BasePaymentSerializer(serializers.Serializer):
    """
    Base for various payment type serializers.
    Encapsulates fields that are common to all payment types.
    """
    created_at = serializers.DateTimeField(validators=[validateDate])
    currency = serializers.ChoiceField(choices=CURRENCY_CHOICES)
    amount = serializers.IntegerField()
    description = serializers.CharField(max_length=300)


class PayByLinkSerializer(BasePaymentSerializer):
    """
    Class for serialization of payments done by link.
    """
    bank = serializers.CharField(max_length=100)


class DirectPaymentSerializer(BasePaymentSerializer):
    """
    Class for serialization of direct payments.
    """
    iban = serializers.CharField(max_length=32)


class CardSerializer(BasePaymentSerializer):
    """
    Class for serialization of card payments.
    """
    cardholder_name = serializers.CharField(max_length=40)
    cardholder_surname = serializers.CharField(max_length=40)
    card_number = serializers.CharField(max_length=20)


SERIALIZERS_DICT = {PAY_BY_LINK: PayByLinkSerializer,
                    DIRECT_PAYMENT: DirectPaymentSerializer,
                    CARD: CardSerializer}


class PaymentInfoSerializer(serializers.Serializer):
    """
    Class for serialization of payment reports.
    """
    date = serializers.DateTimeField(validators=[validateDate])
    type = serializers.CharField(max_length=20)
    payment_mean = serializers.CharField(max_length=130)
    description = serializers.CharField(max_length=300)
    amount = serializers.IntegerField()
    currency = serializers.ChoiceField(choices=CURRENCY_CHOICES)
    amount_in_pln = serializers.IntegerField()
