import logging
#import qgb_db_service

from django.dispatch import receiver
from xmodule.modulestore.django import SignalHandler

log = logging.getLogger(__name__)


@receiver(SignalHandler.item_deleted)
def handle_generate_question_xblock_deleted(sender, usage_key, user_id, **kwargs):
    """
    Receives the item_deleted signal sent by Studio when an XBlock is removed from
    the course structure and removes any gating milestone data associated with it or
    its descendants.
    Arguments:
        kwargs (dict): Contains the content usage key of the item deleted
    Returns:
        None
    """
    log.error('Tammd BEFORE CUSTOM_handle_xblock_deleted: str(usage_key) :: %s', str(usage_key) )
    usage_key = usage_key.for_branch(None)

