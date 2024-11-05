from ...exceptions.error_messages import ErrorMessages

def get_error_message(error_key: str) -> str:
    """
    Get the error message corresponding to the error key.
    If the key doesn't exist, returns the unexpected error message.
    
    Args:
        error_key (str): The error message key defined in ErrorMessages class
        
    Returns:
        str: The corresponding error message
    """
    return getattr(ErrorMessages, error_key, ErrorMessages.UNEXPECTED_ERROR)