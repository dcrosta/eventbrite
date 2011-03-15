import logging

from eventbrite.client import EventbriteClient

__version__ = '0.20-beta'

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

eventbrite_root_logger = logging.getLogger('eventbrite')
eventbrite_root_logger.addHandler(NullHandler())