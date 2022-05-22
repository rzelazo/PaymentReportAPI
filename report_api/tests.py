from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .serializers import *
from .models import Report
from .views import convert2PLN
from datetime import timedelta
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from copy import deepcopy


class BasePaymentSerializerTests(TestCase):
    """
    Class for testing the BasePaymentSerializer.
    """

    def test_base_payment_serializer_with_future_created_at_date(self):
        """
        BasePaymentSerializer(data=data).is_valid() method returns False
        for data with future 'created_at' date and a proper
        error message is set inside BasePaymentSerializer instance.
        """

        serializer = BasePaymentSerializer(data=dict(
            created_at=timezone.now() + timedelta(days=1),
            currency="PLN",
            amount=1000,
            description="test"
        ))

        #   serializer with future 'created_at' date should fail validation and a proper error message should be set
        with self.assertRaisesMessage(ValidationError, 'Date cannot be from the future!'):
            serializer.is_valid(raise_exception=True)

    def test_base_payment_serializer_with_past_created_at_date(self):
        """
        BasePaymentSerializer(data=data).is_valid() method returns True
        for data with past 'created_at' date.
        """

        serializer = BasePaymentSerializer(data=dict(
            created_at=timezone.now(),  # this date will already be from the past when the .is_valid() method is run
            currency="PLN",
            amount=1000,
            description="test"
        ))

        #   serializer with past 'created_at' date should pass validation
        self.assertTrue(serializer.is_valid())

    def test_base_payment_serializer_with_past_and_future_created_at_dates(self):
        """
        BasePaymentSerializer(data=data_list, many=True).is_valid() method returns False
        if at least one data instance from data_list has future 'created_at' date and a proper
        error message is set inside BasePaymentSerializer instance.
        """

        data_list = [
            dict(
                created_at=timezone.now(),  # this date will already be from the past when the .is_valid() method is run
                currency="PLN",
                amount=1000,
                description="test"),

            dict(
                created_at=timezone.now() + timedelta(days=1),
                currency="PLN",
                amount=1000,
                description="test")
        ]

        serializer = BasePaymentSerializer(data=data_list, many=True)

        #   list serializer with at least one data instance with future 'created_at' date should fail validation
        #   and a proper error message should be set
        with self.assertRaisesMessage(ValidationError, 'Date cannot be from the future!'):
            serializer.is_valid(raise_exception=True)

    def test_base_payment_serializer_with_two_past_created_at_dates(self):
        """
        BasePaymentSerializer(data=data_list, many=True).is_valid() method returns True
        all data instance from data_list has past 'created_at' date.
        """

        data_list = [
            dict(
                created_at=timezone.now(),
                currency="PLN",
                amount=1000,
                description="test"),

            dict(
                created_at=timezone.now() - timedelta(minutes=1),
                currency="PLN",
                amount=1000,
                description="test")
        ]

        serializer = BasePaymentSerializer(data=data_list, many=True)

        #   serializer with list of data instances with past 'created_at' dates should pass validation
        self.assertTrue(serializer.is_valid())


class ReportViewTests(APITestCase):
    """
    Class for testing the views ReportView and CustomerReportView.
    """
    view_url = reverse('report_api:report')
    mixed_test_data = {
        "pay_by_link": [
            {
                "created_at": "2022-05-13T19:12:02.370518+02:00",
                "currency": "EUR",
                "amount": 40000,
                "description": "Car",
                "bank": "idea_bank"
            },

            {
                "created_at": "2022-01-02T11:58:02.370518+07:00",
                "currency": "USD",
                "amount": 9999,
                "description": "Clothing store",
                "bank": "mbank"
            }
        ],
        "dp": [
            {
                "created_at": "2022-03-21T11:32:11.370518+03:00",
                "currency": "PLN",
                "amount": 31700,
                "description": "Restaurant",
                "iban": "PLNOA123435467887653"
            },
            {
                "created_at": "2022-04-21T21:34:11.370518+01:00",
                "currency": "USD",
                "amount": 2200,
                "description": "Toy Store",
                "iban": "GERSXOA86756435435465468"
            }
        ],
        "card": [
            {
                "created_at": "2022-05-21T19:20:02.370518+02:00",
                "currency": "EUR",
                "amount": 2000,
                "description": "Restaurant",
                "cardholder_name": "Jan",
                "cardholder_surname": "Kowalski",
                "card_number": "1234567890000"
            },

            {
                "created_at": "2021-11-21T11:02:02.370518+04:00",
                "currency": "GBP",
                "amount": 200,
                "description": "Ice cream shop",
                "cardholder_name": "Steven",
                "cardholder_surname": "Gerrard",
                "card_number": "11112222333344445555"
            }
        ]
    }
    expected_report_data_for_mixed_test_data = [
        {
            "date": "2021-11-21T07:02:02.370518Z",
            "type": "card",
            "payment_mean": "Steven Gerrard 1111************5555",
            "description": "Ice cream shop",
            "amount": 200,
            "currency": "GBP",
            "amount_in_pln": None
        },
        {
            "date": "2022-01-02T04:58:02.370518Z",
            "type": "pay_by_link",
            "payment_mean": "mbank",
            "description": "Clothing store",
            "amount": 9999,
            "currency": "USD",
            "amount_in_pln": None
        },
        {
            "date": "2022-03-21T08:32:11.370518Z",
            "type": "dp",
            "payment_mean": "PLNOA123435467887653",
            "description": "Restaurant",
            "amount": 31700,
            "currency": "PLN",
            "amount_in_pln": None
        },
        {
            "date": "2022-04-21T20:34:11.370518Z",
            "type": "dp",
            "payment_mean": "GERSXOA86756435435465468",
            "description": "Toy Store",
            "amount": 2200,
            "currency": "USD",
            "amount_in_pln": None
        },
        {
            "date": "2022-05-13T17:12:02.370518Z",
            "type": "pay_by_link",
            "payment_mean": "idea_bank",
            "description": "Car",
            "amount": 40000,
            "currency": "EUR",
            "amount_in_pln": None
        },
        {
            "date": "2022-05-21T17:20:02.370518Z",
            "type": "card",
            "payment_mean": "Jan Kowalski 1234*****0000",
            "description": "Restaurant",
            "amount": 2000,
            "currency": "EUR",
            "amount_in_pln": None
        }
    ]

    def set_amount_in_pln(self, expected_report_data):
        """
        Helper function to dynamically set (in place) amount_in_pln field value
        for each payment_info instance inside expected_report_data.
        :param expected_report_data:
        :return: None
        """
        for payment_info in expected_report_data:
            payment_info['amount_in_pln'] = convert2PLN(payment_info['amount'], payment_info['currency'])

    def send_data_and_compare_reports(self, post_data, expected_report_data, url):
        """
        Helper function to perform tests that are common to different forms of post_data (eg. different payment types etc.).
        :param post_data: data to be sent in a post request
        :param expected_report_data: data that is expected to be received in response to POST request with 'post_data'
        :param url: url to an api endpoint to be tested
        :return the response to the post request
        """

        # expected amount_in_pln need to be evaluated dynamically
        # (they can differ depending on the current exchange rates)
        self.set_amount_in_pln(expected_report_data)

        # make POST request to /report with data rendered as json
        response = self.client.post(url, data=post_data, format='json')

        # check if response status code begins with 2..
        self.assertTrue(status.is_success(response.status_code))

        # compare received report with the expected one
        self.assertJSONEqual(response.content, expected_report_data)

        return response

    def test_report_view_with_single_pay_by_link_data(self):
        """
        Sends data containing single pay_by_link instance in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing single pay_by_link data instance
        data = {"pay_by_link": [
            {
                "created_at": "2022-05-13T19:12:02.370518+02:00",
                "currency": "EUR",
                "amount": 40000,
                "description": "Car",
                "bank": "idea_bank"
            }
        ]}

        # create expected_report_data
        expected_report_data = [
            {
                "date": "2022-05-13T17:12:02.370518Z",
                "type": "pay_by_link",
                "payment_mean": "idea_bank",
                "description": "Car",
                "amount": 40000,
                "currency": "EUR",
                "amount_in_pln": None
            }
        ]
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_with_many_pay_by_link_data(self):
        """
        Sends data containing two pay_by_link instances in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing two pay_by_link data instance
        data = {"pay_by_link": [
            {
                "created_at": "2022-05-13T19:12:02.370518+02:00",
                "currency": "EUR",
                "amount": 40000,
                "description": "Car",
                "bank": "idea_bank"
            },

            {
                "created_at": "2022-01-02T11:58:02.370518+07:00",
                "currency": "USD",
                "amount": 9999,
                "description": "Clothing store",
                "bank": "mbank"
            }
        ]}

        # create expected_report_data
        expected_report_data = [
            {
                "date": "2022-01-02T04:58:02.370518Z",
                "type": "pay_by_link",
                "payment_mean": "mbank",
                "description": "Clothing store",
                "amount": 9999,
                "currency": "USD",
                "amount_in_pln": None
            },
            {
                "date": "2022-05-13T17:12:02.370518Z",
                "type": "pay_by_link",
                "payment_mean": "idea_bank",
                "description": "Car",
                "amount": 40000,
                "currency": "EUR",
                "amount_in_pln": None
            }
        ]
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_with_single_dp_data(self):
        """
        Sends data containing single dp instance in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing single dp data instance
        data = {"dp": [
            {
                "created_at": "2022-03-21T11:32:11.370518+03:00",
                "currency": "PLN",
                "amount": 31700,
                "description": "Restaurant",
                "iban": "PLNOA123435467887653"
            }
        ]}

        # create expected_report_data
        expected_report_data = [
            {
                "date": "2022-03-21T08:32:11.370518Z",
                "type": "dp",
                "payment_mean": "PLNOA123435467887653",
                "description": "Restaurant",
                "amount": 31700,
                "currency": "PLN",
                "amount_in_pln": None
            }
        ]
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_with_many_dp_data(self):
        """
        Sends data containing two dp instances in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing two dp data instance
        data = {"dp": [
            {
                "created_at": "2022-03-21T11:32:11.370518+03:00",
                "currency": "PLN",
                "amount": 31700,
                "description": "Restaurant",
                "iban": "PLNOA123435467887653"
            },
            {
                "created_at": "2022-04-21T21:34:11.370518+01:00",
                "currency": "USD",
                "amount": 2200,
                "description": "Toy Store",
                "iban": "GERSXOA86756435435465468"
            }
        ]}

        # create expected_report_data
        expected_report_data = [
            {
                "date": "2022-03-21T08:32:11.370518Z",
                "type": "dp",
                "payment_mean": "PLNOA123435467887653",
                "description": "Restaurant",
                "amount": 31700,
                "currency": "PLN",
                "amount_in_pln": None
            },
            {
                "date": "2022-04-21T20:34:11.370518Z",
                "type": "dp",
                "payment_mean": "GERSXOA86756435435465468",
                "description": "Toy Store",
                "amount": 2200,
                "currency": "USD",
                "amount_in_pln": None
            }
        ]
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_with_single_card_data(self):
        """
        Sends data containing single card instance in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing single card data instance
        data = {"card": [
            {
                "created_at": "2022-05-21T19:20:02.370518+02:00",
                "currency": "EUR",
                "amount": 2000,
                "description": "Restaurant",
                "cardholder_name": "Jan",
                "cardholder_surname": "Kowalski",
                "card_number": "1234567890000"
            }
        ]}

        # create expected_report_data
        expected_report_data = [
            {
                "date": "2022-05-21T17:20:02.370518Z",
                "type": "card",
                "payment_mean": "Jan Kowalski 1234*****0000",
                "description": "Restaurant",
                "amount": 2000,
                "currency": "EUR",
                "amount_in_pln": None
            }
        ]
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_with_many_card_data(self):
        """
        Sends data containing two card instances in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing two card data instances
        data = {"card": [
            {
                "created_at": "2022-05-21T19:20:02.370518+02:00",
                "currency": "EUR",
                "amount": 2000,
                "description": "Restaurant",
                "cardholder_name": "Jan",
                "cardholder_surname": "Kowalski",
                "card_number": "1234567890000"
            },

            {
                "created_at": "2021-11-21T11:02:02.370518+04:00",
                "currency": "GBP",
                "amount": 200,
                "description": "Ice cream shop",
                "cardholder_name": "Steven",
                "cardholder_surname": "Gerrard",
                "card_number": "11112222333344445555"
            }
        ]}

        # create expected_report_data
        expected_report_data = [
            {
                "date": "2021-11-21T07:02:02.370518Z",
                "type": "card",
                "payment_mean": "Steven Gerrard 1111************5555",
                "description": "Ice cream shop",
                "amount": 200,
                "currency": "GBP",
                "amount_in_pln": None
            },
            {
                "date": "2022-05-21T17:20:02.370518Z",
                "type": "card",
                "payment_mean": "Jan Kowalski 1234*****0000",
                "description": "Restaurant",
                "amount": 2000,
                "currency": "EUR",
                "amount_in_pln": None
            }
        ]
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_with_mixed_data(self):
        """
        Sends data containing mix of 6 instances of different
        payment types (2 x pay_by_link, 2 x dp, 2 x card) in post request to the api.
        The report received in response is equal to the expected one.
        """
        # create test json containing 6 mixed data instances
        data = ReportViewTests.mixed_test_data

        # create expected_report_data
        expected_report_data = ReportViewTests.expected_report_data_for_mixed_test_data
        # fields 'amount_in_pln' need to be set dynamically
        # inside self.send_data_and_compare_reports

        # use helper function to conduct tests using created data
        self.send_data_and_compare_reports(post_data=data,
                                           expected_report_data=expected_report_data,
                                           url=ReportViewTests.view_url)

    def test_report_view_report_ordered_by_date(self):
        """
        PaymentInfo instances inside received report are sorted by date (ascending).
        """
        response = self.client.post(ReportViewTests.view_url,
                                    data=ReportViewTests.mixed_test_data,
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test whether PaymentInfo instances are sorted by date (ascending)
        previous_payment_info, *rest_payment_infos = response.data
        for payment_info in rest_payment_infos:
            self.assertGreaterEqual(payment_info['date'], previous_payment_info['date'])
            previous_payment_info = payment_info

    def test_report_view_data_with_future_date(self):
        """
        Response for posting data with at least one data instance
        with future 'created_at' date has status code 400 bad request and
        a proper error message is set.
        """
        data = deepcopy(ReportViewTests.mixed_test_data)

        # set created_at date to future in one of the card data instances
        data['card'][0]['created_at'] = "3000-05-13T19:12:02.370518+02:00"

        response = self.client.post(ReportViewTests.view_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"created_at": ["Date cannot be from the future!"]})

    def test_report_view_data_with_unsupported_payment_type(self):
        """
        Response for posting data with at least one data instance
        with unsupported payment type (other than pay_by_link, dp, card)
        has status code 400 bad request and a proper error message is set.
        """
        data = deepcopy(ReportViewTests.mixed_test_data)

        # change 'card' payment type to 'blik' (unsupported payment type)
        data['blik'] = data.pop('card')

        response = self.client.post(ReportViewTests.view_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Unsupported type of payment"})

    def test_report_view_data_with_unsupported_currency(self):
        """
        Response for posting data with at least one data instance
        with unsupported currency (other than PLN, USD, EUR, GBP)
        has status code 400 bad request and a proper error message is set.
        """
        data = deepcopy(ReportViewTests.mixed_test_data)

        # set currency to an unsupported one in one of the card data instances
        unsupported_currency = 'CHF'
        data['card'][0]['currency'] = unsupported_currency

        response = self.client.post(ReportViewTests.view_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"currency": [f"\"{unsupported_currency}\" is not a valid choice."]})

    def test_customer_report_view_save_report(self):
        """
        Last report generated by a particular customer (identified with 'pk' parameter)
        is saved to the database.
        :return:
        """
        first_data = {"pay_by_link": [
            {
                "created_at": "2022-05-13T19:12:02.370518+02:00",
                "currency": "EUR",
                "amount": 40000,
                "description": "Car",
                "bank": "idea_bank"
            }
        ]}

        first_expected_report_data = [
            {
                "date": "2022-05-13T17:12:02.370518Z",
                "type": "pay_by_link",
                "payment_mean": "idea_bank",
                "description": "Car",
                "amount": 40000,
                "currency": "EUR",
                "amount_in_pln": None
            }
        ]

        customer1_url = reverse('report_api:customer-report', kwargs={"pk": 1})

        # post first_data and test whether the api yielded expected result
        post_response1 = self.send_data_and_compare_reports(post_data=first_data,
                                                            expected_report_data=first_expected_report_data,
                                                            url=customer1_url)

        # check if report has been saved in database
        self.assertEqual(Report.objects.all().count(), 1)

        # get the last report that has been saved to the database
        get_response1 = self.client.get(customer1_url)

        self.assertEqual(get_response1.status_code, status.HTTP_200_OK)

        second_data = ReportViewTests.mixed_test_data
        second_expected_report_data = ReportViewTests.expected_report_data_for_mixed_test_data

        # check if report received from get request is equal to the report generated as a result
        # of the first post request
        self.assertEqual(get_response1.data, post_response1.data)

        # post second_data and test whether the api yielded expected result
        post_response2 = self.send_data_and_compare_reports(post_data=second_data,
                                                            expected_report_data=second_expected_report_data,
                                                            url=customer1_url)

        # check if report has been saved in database (overwriting the previously saved report)
        self.assertEqual(Report.objects.all().count(), 1)  # report count should still be 1

        # get the last report that has been saved to the database
        get_response2 = self.client.get(customer1_url)

        # check if report received from the second get request is different from the report
        # generated as a result of the first post request
        self.assertNotEqual(get_response2.data, post_response1.data)

        # check if report received from the second get request is equal to the report
        # generated as a result of the second post request
        self.assertEqual(get_response2.data, post_response2.data)
