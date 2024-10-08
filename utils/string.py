import re

def find_matching_substrings(string: str, substrings: list) -> str:
    """
    Find the first substring at the beginning of a word in the given string

    Parameters
    ----------
        `string`: str
            The string to search for the substrings

        `substrings`: list
            The list of substrings to search for

    Returns
    -------
    The matched substring at the beginning of a word, or None if not found
    """
    for substring in substrings:
        pattern = r'\b' + re.escape(substring) + r'\b'
        match = re.match(pattern, string.strip().lower())
        if match:
            return match.group(0)
    return None


def remove_substring(string: str, substring: str) -> str:
    """
    Remove the specified substring from the original string

    Parameters
    ----------
        `string`: str
            The original string from which to remove the substring
        `substring`: str
            The substring to remove.

    Returns
    -------
    The resulting string after removing the substring
    """
    index = string.lower().find(substring.lower())
    
    if index == -1:
        return string
    
    return string[:index] + string[index + len(substring):]
