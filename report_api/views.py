from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .serializers import *
from rest_framework.exceptions import APIException, ValidationError
from django.http import Http404
from .models import Report

import requests
import pytz
import json


class UnsupportedPaymentType(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Unsupported type of payment"
    default_code = 'unsupported_payment_type'


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable, try again later."
    default_code = 'service_unavailable'


def get_payment_mean(payment_type, validated_data):
    """Get 'payment mean' value based on the type of payment"""

    if payment_type == PAY_BY_LINK:
        return validated_data['bank']

    elif payment_type == DIRECT_PAYMENT:
        return validated_data['iban']

    elif payment_type == CARD:
        card_number = validated_data['card_number']

        # mask card_number digits with '*' excluding first 4 and last 4 digits
        masked_card_number = card_number[:4] + '*' * len(card_number[4:-4]) + card_number[-4:]
        return "{cardholder_name} {cardholder_surname} {masked_card_number}".format(
            masked_card_number=masked_card_number,
            **validated_data)


def convert2PLN(amount, currency):
    """Get current PLN to 'currency' rate from api.nbp.pl
    and convert 'amount' to that 'currency'."""

    if currency == 'PLN':
        return amount

    response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/a/{currency.lower()}",
                            params={"format": "json"})
    if response.status_code == status.HTTP_200_OK:
        rate = response.json()['rates'][0]['mid']  # get PLN to 'currency' rate fetched from api.nbp.pl
        return int(amount * rate)
    else:
        raise ServiceUnavailable('api.nbp.pl cannot be reached')


def generate_report(data):
    """
    Function for generating report as a list of uniform PaymentInfo objects.
    :param data: Parsed received data (e.g from request.data)
    :return: Report - serializer (that has not undergone validation yet) with list of PaymentInfo objects.
    """

    validated_data_list = []

    for payment_type in data:
        try:
            # get serializer for proper payment type or raise 400
            obj_serializer = SERIALIZERS_DICT[payment_type]
        except KeyError:
            raise UnsupportedPaymentType()

        for obj in data[payment_type]:

            #  serialize received payment data using serializer for the proper payment type
            s = obj_serializer(data=obj)

            #  validate serialized payment data or raise 400
            if s.is_valid():
                validated_data = s.validated_data

                #   convert 'created_at' datetime value to UTC
                validated_data['created_at'] = validated_data['created_at'].astimezone(pytz.utc)
                validated_data_list.append((payment_type, validated_data))
            else:
                raise ValidationError(s.errors)

    # sort validated payment data by 'created_at' value (all 'created_at' datetime objects should already be converted to UTC)
    validated_data_list.sort(key=lambda x: x[1]['created_at'])

    payment_info_list = []

    #   populate list of payment_info dicts
    for payment_type, validated_data in validated_data_list:
        payment_info_dict = {'date': validated_data['created_at'],
                             'type': payment_type,
                             'payment_mean': get_payment_mean(payment_type, validated_data),
                             'description': validated_data['description'],
                             'currency': validated_data['currency'],
                             'amount': validated_data['amount'],
                             'amount_in_pln': convert2PLN(validated_data['amount'], validated_data['currency'])
                             }

        payment_info_list.append(payment_info_dict)

    #   serialize payment_info_list into report
    report = PaymentInfoSerializer(data=payment_info_list, many=True)
    return report


class ReportView(APIView):
    """
    View for generating uniform payment reports.
    """

    def post(self, request):

        report = generate_report(request.data)

        #   validate report and send it to user as json or raise 400
        if report.is_valid():
            return Response(data=report.validated_data, status=status.HTTP_200_OK,
                            content_type="application/json")
        else:
            return Response(data=report.errors, status=status.HTTP_400_BAD_REQUEST,
                            content_type="application/json")


class CustomerReportView(APIView):

    def get(self, request, pk):
        """
        Get report that was saved earlier by the customer (identified by 'customer_id')
        """

        #   Fetch from the database the last report saved by the customer or raise 404
        r = get_object_or_404(Report, customer_id=pk)

        report = PaymentInfoSerializer(data=json.loads(r.content), many=True)
        report.is_valid()

        return Response(data=report.validated_data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """
        Generate payment report and save it for the particular customer (identified by 'customer_id').
        """

        report = generate_report(request.data)

        #   validate report and save it for the user identified with 'customer_id' and send it to user as json or raise 400
        if report.is_valid():

            #   saves json for the report as binary in the database
            r = Report(customer_id=pk, content=JSONRenderer().render(data=report.validated_data))
            r.save()

            return Response(data=report.validated_data, status=status.HTTP_201_CREATED,
                            content_type="application/json")
        else:
            return Response(data=report.errors, status=status.HTTP_400_BAD_REQUEST,
                            content_type="application/json")
