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


@receiver(SignalHandler.item_deleted)
def handle_matlab_question_template_generator_xblock_deleted(sender, usage_key, user_id, **kwargs):
    """
    Receives the item_deleted signal sent by Studio when an XBlock is removed from
    the course structure and removes any gating milestone data associated with it or
    its descendants.

    Arguments:
        kwargs (dict): Contains the content usage key of the item deleted

    Returns:
        None
    """
    # log.info('BEFORE CUSTOM_handle_xblock_deleted: str(usage_key) :: ' + str(usage_key))
    usage_key = usage_key.for_branch(None)
    # log.info('DELETING Xblock with xblock_id :: ' + str(usage_key))
    # qgb_db_service.delete_xblock(str(usage_key))
    # log.info('AFTER DELETING Xblock with xblock_id :: ' + str(usage_key))
