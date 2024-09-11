class DropMessageError(Exception):
    """Do not process the message and do not return it back to the queue"""
