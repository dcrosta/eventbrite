"""Simple Eventbrite client for the HTTP-based API

This client provides:
1) Basic type validation of arguments
2) Basic checks for required arguments
3) Dictionary-based returns as described at http://developer.eventbrite.com/doc/
"""
import datetime
import httplib
import logging
import urllib

from eventbrite import json_lib

EVENTBRITE_URL = 'www.eventbrite.com'
EVENTBRITE_API_TEMPLATE = 'https://%(host)s/json/%(method)s?%(arguments)s'
EVENTBRITE_DATE_STRING = "%Y-%m-%d %H:%M:%S"
GET_REQUEST = 'GET'

EVENTBRITE_LOGGER = logging.getLogger(__name__)

# Input transformations
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

class EventbriteClient(object):
    """Client for Eventbrite's HTTP-based API"""
    def __init__(self, app_key=None, user_key=None):
        """Initialize the client with the given app key and the user key"""
        self._app_key = app_key
        self._user_key = user_key

        self._https_connection = httplib.HTTPSConnection(EVENTBRITE_URL)

    ###########################################################################
    ############################ BEGIN DISCOUNTS ##############################
    ###########################################################################
    # COMPLETE
    def new_discount(self, event_id=None, discount_code=None, amount_off=None, percent_off=None, tickets=None, quantity_available=None, start_date=None, end_date=None):
        # tickets - LIST of integers of ticket ids
        method_arguments = dict(
            event_id           = dict(target='event_id', type=int, value=event_id, required=True),
            discount_code      = dict(target='code', type=str, value=discount_code, required=True),
            amount_off         = dict(target='amount_off', type=float, value=amount_off),
            percent_off        = dict(target='percent_off', type=float, value=percent_off),
            tickets            = dict(target='tickets', type=list, value=tickets, transform=_comma_separated_list),
            quantity_available = dict(target='quantity_available', type=int, value=quantity_available),
            start_date         = dict(target='start_date', type=datetime.datetime, value=start_date, transform=_datetime_to_string, required=True),
            end_date           = dict(target='end_date', type=datetime.datetime, value=end_date, transform=_datetime_to_string, required=True),
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
            discount_id        = dict(target='discount_id', type=int, value=discount_id, required=True),
            discount_code      = dict(target='code', type=str, value=discount_code, required=True),
            amount_off         = dict(target='amount_off', type=float, value=amount_off),
            percent_off        = dict(target='percent_off', type=float, value=percent_off),
            tickets            = dict(target='tickets', type=list, value=tickets, transform=_comma_separated_list),
            quantity_available = dict(target='quantity_available', type=int, value=quantity_available),
            start_date         = dict(target='start_date', type=datetime.datetime, value=start_date, transform=_datetime_to_string, required=True),
            end_date           = dict(target='end_date', type=datetime.datetime, value=end_date, transform=_datetime_to_string, required=True),
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
            event_id     = dict(target='event_id', type=int, value=event_id, required=True),
            event_name   = dict(target='event_name', type=str, value=event_name, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_copy', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def get_event(self, event_id=None):
        method_arguments = dict(
            event_id     = dict(target='id', type=int, value=event_id, required=True),
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
            event_id           = dict(target='id', type=int, value=event_id, required=True),
            count              = dict(target='count', type=int, value=count),
            page               = dict(target='page', type=int, value=page),
            do_not_display     = dict(target='do_not_display', type=list, value=exclusion_list, transform=_comma_separated_list),
            show_full_barcodes = dict(target='show_full_barcodes', type=bool, value=show_full_barcodes, transform=_boolean_true_or_false),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_list_attendees', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def list_event_discounts(self, event_id=None):
        method_arguments = dict(
            event_id     = dict(target='id', type=int, value=event_id, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_list_discounts', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def new_event(self, title=None, description=None, start_date=None, end_date=None, timezone=None, public=False,
        personalized_url=None, venue_id=None, organizer_id=None, capacity=None, currency=None, status=None,
        custom_header=None, custom_footer=None, background_color=None, text_color=None, link_color=None, title_text_color=None,
        box_background_color=None, box_text_color=None, box_border_color=None, box_header_background_color=None, box_header_text_color=None
    ):
        # For no good reason, default to PST
        timezone = timezone or "GMT-08"

        if status:
            assert status in ("draft", "live"), "Invalid status"

        method_arguments = dict(
            title       = dict(target='title', type=str, value=title, required=True),
            description = dict(target='description', type=str, value=description),
            start_date  = dict(target='start_date', type=datetime.datetime, value=start_date, transform=_datetime_to_string, required=True),
            end_date    = dict(target='end_date', type=datetime.datetime, value=end_date, transform=_datetime_to_string, required=True),
            timezone    = dict(target='timezone', type=str, value=timezone, required=True),
            public      = dict(target='privacy', type=bool, value=public, transform=_boolean_one_or_zero),

            personalized_url = dict(target='personalized_url', type=str, value=personalized_url),
            venue_id         = dict(target='venue_id', type=int, value=venue_id),
            organizer_id     = dict(target='organizer_id', type=int, value=organizer_id),
            capacity         = dict(target='capacity', type=int, value=capacity),
            currency         = dict(target='currency', type=str, value=currency),
            status           = dict(target='status', type=str, value=status),

            custom_header    = dict(target='custom_header', type=str, value=custom_header),
            custom_footer    = dict(target='custom_footer', type=str, value=custom_footer),
            background_color = dict(target='background_color', type=str, value=background_color),
            text_color       = dict(target='text_color', type=str, value=text_color),
            link_color       = dict(target='link_color', type=str, value=link_color),
            title_text_color = dict(target='title_text_color', type=str, value=title_text_color),

            box_background_color        = dict(target='box_background_color', type=str, value=box_background_color),
            box_text_color              = dict(target='box_text_color', type=str, value=box_text_color),
            box_border_color            = dict(target='box_border_color', type=str, value=box_border_color),
            box_header_background_color = dict(target='box_header_background_color', type=str, value=box_header_background_color),
            box_header_text_color       = dict(target='box_header_text_color', type=str, value=box_header_text_color),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def search_events(self, keywords=None, categories=None,
        address=None, city=None, region=None, postal_code=None, country_code=None, latitude=None, longitude=None,
        within_distance=None, within_unit=None,
        date_start=None, date_created=None, date_modified=None, organizer_name=None,
        max_events=None, count_only=False, sort_by=None, page=None, since_id=None,
        tracking_link=None):

        allowed_categories = set(['conference', 'conventions', 'entertainment', 'fundraisers', 'meetings', 'other', 'performances', 'reunions', 'sales', 'seminars', 'social', 'sports', 'tradeshows', 'travel', 'religion', 'fairs', 'food', 'music', 'recreation'])
        allowed_within_unit = set(['M', 'K'])
        allowed_sorts = set(['id', 'date', 'name', 'city'])

        if categories:
            assert set(categories) <= allowed_categories, "%r not a subset of %r" % (categories, allowed_categories)
        if within_unit:
            assert within_unit in allowed_within_unit, "%r not in %r" % (within_unit, allowed_within_unit)
        if sort_by:
            assert sort_by in allowed_sorts, "%r not in %r" % (sort_by, allowed_sorts)

        method_arguments = dict(
            keywords         = dict(target='keywords', type=str, value=keywords),
            categories       = dict(target='category', type=list, value=categories, transform=_comma_separated_list),

            address          = dict(target='address', type=str, value=address),
            city             = dict(target='city', type=str, value=city),
            region           = dict(target='region', type=str, value=region),
            postal_code      = dict(target='postal_code', type=str, value=postal_code),
            country_code     = dict(target='country', type=str, value=country_code),
            within_distance  = dict(target='within', type=int, value=within_distance),
            within_unit      = dict(target='within_unit', type=str, value=within_unit),

            latitude         = dict(target='latitude', type=float, value=latitude),
            longitude        = dict(target='longitude', type=float, value=longitude),

            # The data format for 'date_start', 'date_created', and 'date_modified' is crazy.
            # We're going to punt on turning these fields into something Python friendly for now
            #
            # For acceptable values, see http://developer.eventbrite.com/doc/events/event_search/
            date_start     = dict(target='date', type=str, value=date_start),
            date_created   = dict(target='date_created', type=str, value=date_created),
            date_modified  = dict(target='date_modified', type=str, value=date_modified),

            organizer_name   = dict(target='organizer', type=str, value=organizer_name),
            max_events       = dict(target='max', type=int, value=since_id),

            count_only       = dict(target='count_only', type=bool, value=count_only, transform=_boolean_true_or_false),
            sort_by          = dict(target='sort_by', type=str, value=sort_by),
            page             = dict(target='page', type=int, value=page),
            since_id         = dict(target='since_id', type=int, value=since_id),
            tracking_link    = dict(target='tracking_link', type=str, value=tracking_link),
        )

        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('event_search', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_event(self, event_id=None, title=None, description=None, start_date=None, end_date=None, timezone=None, public=False,
        personalized_url=None, venue_id=None, organizer_id=None, capacity=None, currency=None, status=None,
        custom_header=None, custom_footer=None, background_color=None, text_color=None, link_color=None, title_text_color=None,
        box_background_color=None, box_text_color=None, box_border_color=None, box_header_background_color=None, box_header_text_color=None
    ):
        # For no good reason, default to PST
        timezone = timezone or "GMT-08"

        method_arguments = dict(
            event_id    = dict(target='event_id', type=int, value=event_id, required=True),
            title       = dict(target='title', type=str, value=title),
            description = dict(target='description', type=str, value=description),
            start_date  = dict(target='start_date', type=datetime.datetime, value=start_date, transform=_datetime_to_string),
            end_date    = dict(target='end_date', type=datetime.datetime, value=end_date, transform=_datetime_to_string),
            timezone    = dict(target='timezone', type=str, value=timezone, required=True),
            public      = dict(target='privacy', type=bool, value=public, transform=_boolean_one_or_zero),

            personalized_url = dict(target='personalized_url', type=str, value=personalized_url),
            venue_id         = dict(target='venue_id', type=int, value=venue_id),
            organizer_id     = dict(target='organizer_id', type=int, value=organizer_id),
            capacity         = dict(target='capacity', type=int, value=capacity),
            currency         = dict(target='currency', type=str, value=currency),
            status           = dict(target='status', type=str, value=status, transform=_status_check),

            custom_header    = dict(target='custom_header', type=str, value=custom_header),
            custom_footer    = dict(target='custom_footer', type=str, value=custom_footer),
            background_color = dict(target='background_color', type=str, value=background_color),
            text_color       = dict(target='text_color', type=str, value=text_color),
            link_color       = dict(target='link_color', type=str, value=link_color),
            title_text_color = dict(target='title_text_color', type=str, value=title_text_color),

            box_background_color        = dict(target='box_background_color', type=str, value=box_background_color),
            box_text_color              = dict(target='box_text_color', type=str, value=box_text_color),
            box_border_color            = dict(target='box_border_color', type=str, value=box_border_color),
            box_header_background_color = dict(target='box_header_background_color', type=str, value=box_header_background_color),
            box_header_text_color       = dict(target='box_header_text_color', type=str, value=box_header_text_color),
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
            organizer_id = dict(target='id', type=int, value=organizer_id, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('organizer_list_events', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def new_organizer(self, name=None, description=None):
        method_arguments = dict(
            name        = dict(target='name', type=str, value=name, required=True),
            description = dict(target='description', type=str, value=description),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('organizer_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_organizer(self, organizer_id=None, name=None, description=None):
        method_arguments = dict(
            organizer_id = dict(target='organizer_id', type=int, value=organizer_id, required=True),
            name         = dict(target='name', type=str, value=name),
            description  = dict(target='description', type=str, value=description),
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
            event_id = dict(target='event_id', type=int, value=event_id, required=True),

            accept_paypal         = dict(target='accept_paypal', type=bool, value=accept_paypal, transform=_boolean_one_or_zero),
            paypal_email          = dict(target='paypal_email', type=str, value=paypal_email),

            accept_google         = dict(target='accept_google', type=bool, value=accept_google, transform=_boolean_one_or_zero),
            google_merchant_id    = dict(target='google_merchant_id', type=str, value=google_merchant_id),
            google_merchant_key   = dict(target='google_merchant_key', type=str, value=google_merchant_key),

            accept_check          = dict(target='accept_check', type=bool, value=accept_check, transform=_boolean_one_or_zero),
            instructions_check    = dict(target='instructions_check', type=str, value=instructions_check),

            accept_cash           = dict(target='accept_cash', type=bool, value=accept_cash, transform=_boolean_one_or_zero),
            instructions_cash     = dict(target='instructions_cash', type=str, value=instructions_cash),

            accept_invoice        = dict(target='accept_invoice', type=bool, value=accept_invoice, transform=_boolean_one_or_zero),
            instructions_invoice  = dict(target='instructions_invoice', type=str, value=instructions_invoice),
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
            event_id = dict(target='event_id', type=int, value=event_id, required=True),
            is_donation = dict(target='is_donation', type=bool, value=is_donation, transform=_boolean_one_or_zero),
            name        = dict(target='name', type=str, value=name, required=True),
            description = dict(target='description', type=str, value=description),
            price       = dict(target='price', type=float, value=price, required=True),
            quantity    = dict(target='quantity', type=int, value=quantity, required=True),

            start_sales = dict(target='start_sales', type=datetime.datetime, value=start_sales, transform=_datetime_to_string),
            end_sales   = dict(target='end_sales', type=datetime.datetime, value=end_sales, transform=_datetime_to_string),
            include_fee = dict(target='include_fee', type=bool, value=include_fee, transform=_boolean_one_or_zero),
            min_tickets_per_order = dict(target='min', type=int, value=min_tickets_per_order),
            max_tickets_per_order = dict(target='max', type=int, value=max_tickets_per_order),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('ticket_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_ticket(self, ticket_id=None, is_donation=None, name=None, description=None, price=None, quantity=None,
        start_sales=None, end_sales=None, include_fee=None, min_tickets_per_order=None, max_tickets_per_order=None):
        method_arguments = dict(
            ticket_id   = dict(target='ticket_id', type=int, value=ticket_id, required=True),
            is_donation = dict(target='is_donation', type=bool, value=is_donation, transform=_boolean_one_or_zero),
            name        = dict(target='name', type=str, value=name),
            description = dict(target='description', type=str, value=description),
            price       = dict(target='price', type=float, value=price, required=True),
            quantity    = dict(target='quantity', type=int, value=quantity, required=True),

            start_sales = dict(target='start_sales', type=datetime.datetime, value=start_sales, transform=_datetime_to_string),
            end_sales   = dict(target='end_sales', type=datetime.datetime, value=end_sales, transform=_datetime_to_string),
            include_fee = dict(target='include_fee', type=bool, value=include_fee, transform=_boolean_one_or_zero),
            min_tickets_per_order = dict(target='min', type=int, value=min_tickets_per_order),
            max_tickets_per_order = dict(target='max', type=int, value=max_tickets_per_order),
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
            user_id     = dict(target='user_id', type=int, value=user_id),
            user_email  = dict(target='email', type=str, value=user_email),

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
            user_email     = dict(target='user', type=int, value=user_email),
            do_not_display = dict(target='do_not_display', type=list, value=exclusion_list, transform=_comma_separated_list),
            event_statuses = dict(target='status_list', type=list, value=status_list, transform=_comma_separated_list),
            asc_or_desc    = dict(target='asc_or_desc', type=str, value=asc_or_desc)
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_list_events', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def list_user_organizers(self, user_email=None, password=None):
        # WARNING: Spec indicates passing passwords through the GET request
        method_arguments = dict(
            user_email   = dict(target='user', type=str, value=user_email, required=True),
            password     = dict(target='password', type=str, value=password, required=True),
        )

        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_list_organizers', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def list_user_tickets(self):
        method_arguments = dict()
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_list_tickets', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def list_user_venues(self, user_email=None, password=None):
        # WARNING: Spec indicates passing passwords through the GET request
        method_arguments = dict(
            user_email   = dict(target='user', type=str, value=user_email, required=True),
            password     = dict(target='password', type=str, value=password, required=True),
        )

        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_list_venues', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def new_user(self, user_email=None, password=None):
        # WARNING: Spec indicates passing passwords through the GET request
        method_arguments = dict(
            user_email   = dict(target='email', type=str, value=user_email, required=True),
            password     = dict(target='passwd', type=str, value=password, required=True),
        )

        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('user_new', api_arguments, authenticate=True)
        return api_response

    # UNTESTED
    def update_user(self, *args, **kwargs):
        # WARNING: Spec indicates passing passwords through the GET request

        # NOT IMPLEMENTED: Ambiguous API docs.  No user_id required?
        # See http://developer.eventbrite.com/doc/users/user_update/
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
            organizer_id = dict(target='organizer_id', type=int, value=organizer_id, required=True),
            venue_name   = dict(target='venue', type=str, value=venue_name, required=True),
            address      = dict(target='adress', type=str, value=address),
            address2     = dict(target='adress_2', type=str, value=address2),
            city         = dict(target='city', type=str, value=city),
            region       = dict(target='region', type=str, value=region, required=True),
            postal_code  = dict(target='postal_code', type=str, value=postal_code),
            country_code = dict(target='country_code', type=str, value=country_code, required=True),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('venue_new', api_arguments, authenticate=True)
        return api_response

    # COMPLETE
    def update_venue(self, venue_id=None, venue_name=None, address=None, address2=None, city=None, region=None, postal_code=None, country_code=None):
        method_arguments = dict(
            venue_id     = dict(target='id', type=int, value=venue_id, required=True),
            venue_name   = dict(target='venue', type=str, value=venue_name, required=True),
            address      = dict(target='adress', type=str, value=address),
            address2     = dict(target='adress_2', type=str, value=address2),
            city         = dict(target='city', type=str, value=city),
            region       = dict(target='region', type=str, value=region),
            postal_code  = dict(target='postal_code', type=str, value=postal_code),
            country_code = dict(target='country_code', type=str, value=country_code),
        )
        api_arguments = self._process_arguments(method_arguments)
        api_response = self._execute_api_call('venue_update', api_arguments, authenticate=True)
        return api_response

    ###########################################################################
    ############################## END VENUES #################################
    ###########################################################################

    def _process_arguments(self, method_arguments):
        """Takes a dictionary with the following keys

        target               - string   - Output field name
        type                 - type     - Expected data type of the input
        value                - anything - Any input value to validate / transform
        required (optional)  - boolean  - raises a ValueError if value is None
        transform (optional) - function - If specified, value will be passed as an argument to the transform function

        Returns: A dictionary with the validated transformed data
        """
        api_arguments = {}
        for param_name, param_reqs in method_arguments.iteritems():
            param_value = param_reqs['value']
            is_required = param_reqs.get('required', False)

            # None is special - we interpret this as no argument was specified
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
        """Execute an API call on Eventbrite using their HTTP-based API

        api_method    - string  - Action identified - https://www.eventbrite.com/json/<api_method>
        api_arguments - dict    - Arguments to pass along as GET parameters
        authenticate  - boolean - API call should be authenticated

        Returns: A dictionary with a return structure defined at http://developer.eventbrite.com/doc/
        """
        url_arguments = dict(api_arguments)
        if authenticate:
            assert self._app_key and self._user_key
            url_arguments['app_key'] = self._app_key
            url_arguments['user_key'] = self._user_key

        final_url_arguments = urllib.urlencode(url_arguments)
        url_string = EVENTBRITE_API_TEMPLATE % dict(host=EVENTBRITE_URL, method=api_method, arguments=final_url_arguments)

        EVENTBRITE_LOGGER.debug("REQ - %s", url_string)

        # Send a GET request to Eventbrite
        self._https_connection.request(GET_REQUEST, url_string)

        # Read the JSON response and automatically JSON deserialize
        response = self._https_connection.getresponse()
        response_data = response.read()

        EVENTBRITE_LOGGER.debug("RES - %s", response_data)

        response_dict = json_lib.loads(response_data)
        return response_dict
