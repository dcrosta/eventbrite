import datetime
import httplib
import logging
import urllib

from eventbrite import json_lib

EVENTBRITE_URL = 'www.eventbrite.com'
EVENTBRITE_API_TEMPLATE = 'https://%(host)s/json/%(method)s?%(arguments)s'
EVENTBRITE_DATE_STRING = "%Y-%m-%d %H:%M:%S"
GET_REQUEST = 'GET'

def _datetime_to_string(incoming_datetime):
    return incoming_datetime.strftime(EVENTBRITE_DATE_STRING)

def _string_to_datetime(incoming_string):
    return datetime.strptime(incoming_string, EVENTBRITE_DATE_STRING)

def _boolean_one_or_zero(is_true):
    return (is_true and '1') or '0'

def _boolean_true_or_false(is_true):
    return (is_true and 'true') or 'false'

def _comma_separated_list(input_list):
    return ",".join(input_list)

def _status_check(current_status):
    assert current_status in ('draft', 'live', None)
    return current_status

class EventbriteClient(object):
    """Client for Eventbrite's HTTP-based API"""
    def __init__(self, app_key=None, user_key=None):
        self._app_key = app_key
        self._user_key = user_key

        self._https_connection = httplib.HTTPSConnection(EVENTBRITE_URL)

    ###########################################################################
    ############################ BEGIN DISCOUNTS ##############################
    ###########################################################################
    # COMPLETE
    def new_discount(self, event_id=None, discount_code=None, amount_off=None, percent_off=None, tickets=None, quantity_available=None, start_date=None, end_date=None):
        method_arguments = dict(
            event_id           = dict(type=int, target='event_id', value=event_id, required=True),
            discount_code      = dict(type=str, target='code', value=discount_code, required=True),
            amount_off         = dict(type=float, target='amount_off', value=amount_off),
            percent_off        = dict(type=float, target='percent_off', value=percent_off),
            tickets            = dict(type=list, target='tickets', value=tickets, transform=_comma_separated_list),
            quantity_available = dict(type=int, target='quantity_available', value=quantity_available),
            start_date         = dict(type=datetime.datetime, target='start_date', value=start_date, transform=_datetime_to_string, required=True),
            end_date           = dict(type=datetime.datetime, target='end_date', value=end_date, transform=_datetime_to_string, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)

        observed_amount_off = bool('amount_off' in api_arguments)
        observed_percent_off = bool('percent_off' in api_arguments)
        if not bool(observed_amount_off ^ observed_percent_off):
            raise ValueError("Expected amount_off OR percent_off, not neither or both")

        api_response = self._execute_api_call('discount_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_discount(self, discount_id=None, discount_code=None, amount_off=None, percent_off=None, tickets=None, quantity_available=None, start_date=None, end_date=None):
        method_arguments = dict(
            discount_id        = dict(type=int, target='discount_id', value=discount_id, required=True),
            discount_code      = dict(type=str, target='code', value=discount_code, required=True),
            amount_off         = dict(type=float, target='amount_off', value=amount_off),
            percent_off        = dict(type=float, target='percent_off', value=percent_off),
            tickets            = dict(type=list, target='tickets', value=tickets, transform=_comma_separated_list),
            quantity_available = dict(type=int, target='quantity_available', value=quantity_available),
            start_date         = dict(type=datetime.datetime, target='start_date', value=start_date, transform=_datetime_to_string, required=True),
            end_date           = dict(type=datetime.datetime, target='end_date', value=end_date, transform=_datetime_to_string, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)

        observed_amount_off = bool('amount_off' in api_arguments)
        observed_percent_off = bool('percent_off' in api_arguments)
        if not bool(observed_amount_off ^ observed_percent_off):
            raise ValueError("Expected amount_off OR percent_off, not neither or both")

        api_response = self._execute_api_call('discount_update', api_arguments, authenticate=True)
        return api_response

    ###########################################################################
    ############################# END DISCOUNTS ###############################
    ###########################################################################

    ###########################################################################
    ############################## BEGIN EVENTS ###############################
    ###########################################################################
    # UNTESTED
    def copy_event(self, event_id=None, event_name=None):
        method_arguments = dict(
            event_id     = dict(type=int, target='event_id', value=event_id, required=True),
            event_name   = dict(type=str, target='event_name', value=event_name, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_copy', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def get_event(self, event_id=None):
        method_arguments = dict(
            event_id     = dict(type=int, target='id', value=event_id, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_get', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def list_event_attendees(self, event_id=None, count=None, page=None, exclude_profile=False, exclude_answers=False, exclude_address=False, show_full_barcodes=False):
        exclusion_list = []
        if exclude_profile:
            exclusion_list.append('profile')
        if exclude_answers:
            exclusion_list.append('answers')
        if exclude_address:
            exclusion_list.append('address')

        exclusion_list = exclusion_list or None
        method_arguments = dict(
            event_id           = dict(type=int, target='id', value=event_id, required=True),
            count              = dict(type=int, target='count', value=count),
            page               = dict(type=int, target='page', value=page),
            do_not_display     = dict(type=list, target='do_not_display', value=exclusion_list, transform=_comma_separated_list),
            show_full_barcodes = dict(type=bool, target='show_full_barcodes', value=show_full_barcodes, transform=_boolean_true_or_false),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_list_attendees', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def list_event_discounts(self, event_id=None):
        method_arguments = dict(
            event_id     = dict(type=int, target='id', value=event_id, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_list_discounts', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def new_event(self, title=None, description=None, start_date=None, end_date=None, timezone=None, public=True,
        personalized_url=None, venue_id=None, organizer_id=None, capacity=None, currency=None, status=None,
        custom_header=None, custom_footer=None, background_color=None, text_color=None, link_color=None, title_text_color=None,
        box_background_color=None, box_text_color=None, box_border_color=None, box_header_background_color=None, box_header_text_color=None
    ):
        timezone = timezone or "GMT-08"
        public = False

        method_arguments = dict(
            title       = dict(type=str, target='title', value=title, required=True),
            description = dict(type=str, target='description', value=description),
            start_date  = dict(type=datetime.datetime, target='start_date', value=start_date, transform=_datetime_to_string, required=True),
            end_date    = dict(type=datetime.datetime, target='end_date', value=end_date, transform=_datetime_to_string, required=True),
            timezone    = dict(type=str, target='timezone', value=timezone, required=True),
            public      = dict(type=bool, target='privacy', value=public, transform=_boolean_one_or_zero),

            personalized_url = dict(type=str, target='personalized_url', value=personalized_url),
            venue_id         = dict(type=int, target='venue_id', value=venue_id),
            organizer_id     = dict(type=int, target='organizer_id', value=organizer_id),
            capacity         = dict(type=int, target='capacity', value=capacity),
            currency         = dict(type=str, target='currency', value=currency),
            status           = dict(type=str, target='status', value=status, transform=_status_check),

            custom_header    = dict(type=str, target='custom_header', value=custom_header),
            custom_footer    = dict(type=str, target='custom_footer', value=custom_footer),
            background_color = dict(type=str, target='background_color', value=background_color),
            text_color       = dict(type=str, target='text_color', value=text_color),
            link_color       = dict(type=str, target='link_color', value=link_color),
            title_text_color = dict(type=str, target='title_text_color', value=title_text_color),

            box_background_color        = dict(type=str, target='box_background_color', value=box_background_color),
            box_text_color              = dict(type=str, target='box_text_color', value=box_text_color),
            box_border_color            = dict(type=str, target='box_border_color', value=box_border_color),
            box_header_background_color = dict(type=str, target='box_header_background_color', value=box_header_background_color),
            box_header_text_color       = dict(type=str, target='box_header_text_color', value=box_header_text_color),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_new', api_arguments, authenticate=True)
        return api_response

    # NOT IMPLEMENTED
    def search_events(self, *args, **kwargs):
        raise NotImplementedError

    # UNTESTED
    def update_event(self, event_id=None, title=None, description=None, start_date=None, end_date=None, timezone=None, public=True,
        personalized_url=None, venue_id=None, organizer_id=None, capacity=None, currency=None, status=None,
        custom_header=None, custom_footer=None, background_color=None, text_color=None, link_color=None, title_text_color=None,
        box_background_color=None, box_text_color=None, box_border_color=None, box_header_background_color=None, box_header_text_color=None
    ):
        timezone = timezone or "GMT-08"
        public = False

        method_arguments = dict(
            event_id    = dict(type=str, target='event_id', value=event_id, required=True),
            title       = dict(type=str, target='title', value=title),
            description = dict(type=str, target='description', value=description),
            start_date  = dict(type=datetime.datetime, target='start_date', value=start_date, transform=_datetime_to_string),
            end_date    = dict(type=datetime.datetime, target='end_date', value=end_date, transform=_datetime_to_string),
            timezone    = dict(type=str, target='timezone', value=timezone, required=True),
            public      = dict(type=bool, target='privacy', value=public, transform=_boolean_one_or_zero),

            personalized_url = dict(type=str, target='personalized_url', value=personalized_url),
            venue_id         = dict(type=int, target='venue_id', value=venue_id),
            organizer_id     = dict(type=int, target='organizer_id', value=organizer_id),
            capacity         = dict(type=int, target='capacity', value=capacity),
            currency         = dict(type=str, target='currency', value=currency),
            status           = dict(type=str, target='status', value=status, transform=_status_check),

            custom_header    = dict(type=str, target='custom_header', value=custom_header),
            custom_footer    = dict(type=str, target='custom_footer', value=custom_footer),
            background_color = dict(type=str, target='background_color', value=background_color),
            text_color       = dict(type=str, target='text_color', value=text_color),
            link_color       = dict(type=str, target='link_color', value=link_color),
            title_text_color = dict(type=str, target='title_text_color', value=title_text_color),

            box_background_color        = dict(type=str, target='box_background_color', value=box_background_color),
            box_text_color              = dict(type=str, target='box_text_color', value=box_text_color),
            box_border_color            = dict(type=str, target='box_border_color', value=box_border_color),
            box_header_background_color = dict(type=str, target='box_header_background_color', value=box_header_background_color),
            box_header_text_color       = dict(type=str, target='box_header_text_color', value=box_header_text_color),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_update', api_arguments, authenticate=True)
        return api_response
    ###########################################################################
    ############################### END EVENTS ################################
    ###########################################################################


    ###########################################################################
    ########################## BEGIN ORGANIZER ################################
    ###########################################################################
    # COMPLETE
    def list_organizer_events(self, organizer_id=None):
        method_arguments = dict(
            organizer_id = dict(type=int, target='id', value=organizer_id, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('organizer_list_events', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def new_organizer(self, name=None, description=None):
        method_arguments = dict(
            name        = dict(type=str, target='name', value=name, required=True),
            description = dict(type=str, target='description', value=description),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('organizer_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_organizer(self, organizer_id=None, name=None, description=None):
        method_arguments = dict(
            organizer_id = dict(type=int, target='organizer_id', value=organizer_id, required=True),
            name         = dict(type=str, target='name', value=name),
            description  = dict(type=str, target='description', value=description),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('organizer_update', api_arguments, authenticate=True)
        return api_response
    ###########################################################################
    ############################ END ORGANIZER ################################
    ###########################################################################

    ###########################################################################
    ############################ BEGIN PAYMENT ################################
    ###########################################################################

    # COMPLETE
    def update_payment(self, event_id=None,
        accept_paypal=None, paypal_email=None,
        accept_google=None, google_merchant_id=None, google_merchant_key=None,
        accept_check=None, instructions_check=None,
        accept_cash=None, instructions_cash=None,
        accept_invoice=None, instructions_invoice=None,
    ):
        method_arguments = dict(
            event_id = dict(type=int, target='event_id', value=event_id, required=True),

            accept_paypal         = dict(type=bool, target='accept_paypal', value=accept_paypal, transform=_boolean_one_or_zero),
            paypal_email          = dict(type=str, target='paypal_email', value=paypal_email),

            accept_google         = dict(type=bool, target='accept_google', value=accept_google, transform=_boolean_one_or_zero),
            google_merchant_id    = dict(type=str, target='google_merchant_id', value=google_merchant_id),
            google_merchant_key   = dict(type=str, target='google_merchant_key', value=google_merchant_key),

            accept_check          = dict(type=bool, target='accept_check', value=accept_check, transform=_boolean_one_or_zero),
            instructions_check    = dict(type=str, target='instructions_check', value=instructions_check),

            accept_cash           = dict(type=bool, target='accept_cash', value=accept_cash, transform=_boolean_one_or_zero),
            instructions_cash     = dict(type=str, target='instructions_cash', value=instructions_cash),

            accept_invoice         = dict(type=bool, target='accept_invoice', value=accept_invoice, transform=_boolean_one_or_zero),
            instructions_invoice   = dict(type=str, target='instructions_invoice', value=instructions_invoice),
        )

        api_arguments = self._process_arguments(method_arguments)

        if 'accept_paypal' in api_arguments and 'paypal_email' not in api_arguments:
            raise ValueError("Expected 'paypal_email' when 'accept_paypal' specified")

        if 'accept_google' in api_arguments and ('google_merchant_id' not in api_arguments or 'google_merchant_key' not in api_arguments):
            raise ValueError("Expected 'google_merchant_id' and 'google_merchant_key' when 'accept_google' specified")

        if 'accept_check' in api_arguments and 'instructions_check' not in api_arguments:
            raise ValueError("Expected 'instructions_check' when 'accept_check' specified")

        if 'accept_cash' in api_arguments and 'instructions_cash' not in api_arguments:
            raise ValueError("Expected 'instructions_cash' when 'accept_cash' specified")

        if 'accept_invoice' in api_arguments and 'instructions_invoice' not in api_arguments:
            raise ValueError("Expected 'instructions_invoice' when 'accept_invoice' specified")

        api_response = self._execute_api_call('payment_update', api_arguments, authenticate=True)
        return api_response
    ###########################################################################
    ############################# END PAYMENT #################################
    ###########################################################################

    ###########################################################################
    ########################### BEGIN TICKETS #################################
    ###########################################################################

    # COMPLETE
    def new_ticket(self, event_id=None, is_donation=False, name=None, description=None, price=None, quantity=None,
        start_sales=None, end_sales=None, include_fee=False, min_tickets_per_order=None, max_tickets_per_order=None):
        method_arguments = dict(
            event_id = dict(type=int, target='event_id', value=event_id, required=True),
            is_donation = dict(type=bool, target='is_donation', value=is_donation, transform=_boolean_one_or_zero),
            name        = dict(type=str, target='name', value=name, required=True),
            description = dict(type=str, target='description', value=description),
            price       = dict(type=float, target='price', value=price, required=True),
            quantity    = dict(type=int, target='quantity', value=quantity, required=True),

            start_sales = dict(type=datetime.datetime, target='start_sales', value=start_sales, transform=_datetime_to_string),
            end_sales   = dict(type=datetime.datetime, target='end_sales', value=end_sales, transform=_datetime_to_string),
            include_fee = dict(type=bool, target='include_fee', value=include_fee, transform=_boolean_one_or_zero),
            min_tickets_per_order = dict(type=int, target='min', value=min_tickets_per_order),
            max_tickets_per_order = dict(type=int, target='max', value=max_tickets_per_order),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('ticket_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_ticket(self, ticket_id=None, is_donation=None, name=None, description=None, price=None, quantity=None,
        start_sales=None, end_sales=None, include_fee=None, min_tickets_per_order=None, max_tickets_per_order=None):
        method_arguments = dict(
            ticket_id   = dict(type=int, target='ticket_id', value=ticket_id, required=True),
            is_donation = dict(type=bool, target='is_donation', value=is_donation, transform=_boolean_one_or_zero),
            name        = dict(type=str, target='name', value=name),
            description = dict(type=str, target='description', value=description),
            price       = dict(type=float, target='price', value=price, required=True),
            quantity    = dict(type=int, target='quantity', value=quantity, required=True),

            start_sales = dict(type=datetime.datetime, target='start_sales', value=start_sales, transform=_datetime_to_string),
            end_sales   = dict(type=datetime.datetime, target='end_sales', value=end_sales, transform=_datetime_to_string),
            include_fee = dict(type=bool, target='include_fee', value=include_fee, transform=_boolean_one_or_zero),
            min_tickets_per_order = dict(type=int, target='min', value=min_tickets_per_order),
            max_tickets_per_order = dict(type=int, target='max', value=max_tickets_per_order),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('ticket_update', api_arguments, authenticate=True)
        return api_response

    ###########################################################################
    ############################# END TICKETS #################################
    ###########################################################################


    ###########################################################################
    ############################## BEGIN USERS ################################
    ###########################################################################

    # UNTESTED
    def get_user(self, user_id=None, user_email=None):
        method_arguments = dict(
            user_id     = dict(type=int, target='user_id', value=user_id),
            user_email  = dict(type=str, target='email', value=user_email),

        )
        api_arguments = self._process_arguments(method_arguments)

        observed_user_id = bool('user_id' in api_arguments)
        observed_user_email = bool('email' in api_arguments)
        if not bool(observed_user_id ^ observed_user_email):
            raise ValueError("Expected observed_user_id OR observed_user_email, not neither or both")

        api_response = self._execute_api_call('user_get', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def list_user_events(self, user_email=None,
        exclude_description=False, exclude_venue=False, exclude_logo=False, exclude_style=False, exclude_organizer=False,
        status_live=False, status_started=False, status_ended=False, ascending=True):
        # Prepare do_not_display
        exclusion_list = []
        if exclude_description:
            exclusion_list.append('description')
        if exclude_venue:
            exclusion_list.append('venue')
        if exclude_logo:
            exclusion_list.append('logo')
        if exclude_style:
            exclusion_list.append('style')
        if exclude_organizer:
            exclusion_list.append('organizer')

        exclusion_list = exclusion_list or None

        # Prepare event_statuses
        status_list = []
        if status_live:
            status_list.append('live')
        if status_started:
            status_list.append('started')
        if status_ended:
            status_list.append('ended')

        status_list = status_list or None

        # Prepare asc_or_desc
        if ascending:
            asc_or_desc = 'asc'
        else:
            asc_or_desc = 'desc'

        method_arguments = dict(
            user_email     = dict(type=int, target='user', value=user_email),
            do_not_display = dict(type=list, target='do_not_display', value=exclusion_list, transform=_comma_separated_list),
            event_statuses = dict(type=list, target='status_list', value=status_list, transform=_comma_separated_list),
            asc_or_desc    = dict(type=str, target='asc_or_desc', value=asc_or_desc)
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_list_events', api_arguments, authenticate=True)
        return api_response

    def list_user_organizers(self, *args, **kwargs):
        # WARNING: Spec indicates passing passwords through the GET request
        raise NotImplementedError

    def list_user_tickets(self):
        method_arguments = dict()
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_list_tickets', api_arguments, authenticate=True)
        return api_response

    def list_user_venues(self, *args, **kwargs):
        # WARNING: Spec indicates passing passwords through the GET request
        raise NotImplementedError

    def new_user(self, *args, **kwargs):
        # WARNING: Spec indicates passing passwords through the GET request
        raise NotImplementedError

    def update_user(self, *args, **kwargs):
        # WARNING: Spec indicates passing passwords through the GET request
        raise NotImplementedError

    ###########################################################################
    ############################### END USERS #################################
    ###########################################################################

    ###########################################################################
    ############################# BEGIN VENUES ################################
    ###########################################################################
    # COMPLETE
    def new_venue(self, organizer_id=None, venue_name=None, address=None, address2=None, city=None, region=None, postal_code=None, country_code=None):
        method_arguments = dict(
            organizer_id = dict(type=int, target='organizer_id', value=organizer_id, required=True),
            venue_name   = dict(type=str, target='venue', value=venue_name, required=True),
            address      = dict(type=str, target='adress', value=address),
            address2     = dict(type=str, target='adress_2', value=address2),
            city         = dict(type=str, target='city', value=city),
            region       = dict(type=str, target='region', value=region, required=True),
            postal_code  = dict(type=str, target='postal_code', value=postal_code),
            country_code = dict(type=str, target='country_code', value=country_code, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('venue_new', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def update_venue(self, venue_id=None, venue_name=None, address=None, address2=None, city=None, region=None, postal_code=None, country_code=None):
        method_arguments = dict(
            venue_id     = dict(type=int, target='id', value=venue_id, required=True),
            venue_name   = dict(type=str, target='venue', value=venue_name, required=True),
            address      = dict(type=str, target='adress', value=address),
            address2     = dict(type=str, target='adress_2', value=address2),
            city         = dict(type=str, target='city', value=city),
            region       = dict(type=str, target='region', value=region),
            postal_code  = dict(type=str, target='postal_code', value=postal_code),
            country_code = dict(type=str, target='country_code', value=country_code),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('venue_update', api_arguments, authenticate=True)
        return api_response

    ###########################################################################
    ############################## END VENUES #################################
    ###########################################################################

    def _process_arguments(self, method_arguments):
        api_arguments = {}
        for param_name, param_reqs in method_arguments.iteritems():
            param_value = param_reqs['value']
            is_required = param_reqs.get('required', False)

            if param_value is None:
                if is_required:
                    raise ValueError("%s - Required value, got None" % (param_name, ))
                else:
                    continue

            expected_type = param_reqs['type']
            actual_type = type(param_value)
            if expected_type != actual_type:
                raise TypeError("%s - Expected type: %s, Got type: %s" % (param_name, expected_type, actual_type))

            target_name = param_reqs['target']
            transform_fxn = param_reqs.get('transform')
            if transform_fxn:
                api_arguments[target_name] = transform_fxn(param_value)
            else:
                api_arguments[target_name] = param_value

        return api_arguments

    def _execute_api_call(self, api_method, api_arguments, authenticate=True):
        url_arguments = dict(api_arguments)
        if authenticate:
            assert self._app_key and self._user_key
            url_arguments['app_key'] = self._app_key
            url_arguments['user_key'] = self._user_key

        final_url_arguments = urllib.urlencode(url_arguments)
        url_string = EVENTBRITE_API_TEMPLATE % dict(host=EVENTBRITE_URL, method=api_method, arguments=final_url_arguments)

        self._https_connection.request(GET_REQUEST, url_string)

        response = self._https_connection.getresponse()
        response_data = response.read()

        response_dict = json_lib.loads(response_data)

        return response_dict
