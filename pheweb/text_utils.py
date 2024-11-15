import typing

def text_to_boolean(text) -> typing.Optional[bool]:
    """
    Convert a text string to its corresponding boolean value.
    
    This function interprets certain strings as boolean values. If the
    input text is one of 'true', 'yes', or '1' (case insensitive), it
    returns True. If the text is 'false', 'no', or '0' (case
    insensitive), it returns False. If the text does not match any of
    these values, the function returns None, indicating an undefined
    boolean value.
    
    Parameters:
    :param text: The text to convert to a boolean.
    
    :return: The boolean value of the text, or None if the text does
             not correspond to a predefined boolean value.
    """
    if text.lower() in {'true', 'yes', '1'}:
        return True
    elif text.lower() in {'false', 'no', '0'}:
        return False
    else:
        return None
