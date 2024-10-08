from playwright.sync_api import sync_playwright
from threading import Event

def youtube(text):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://www.youtube.com/")
    search = page.get_by_placeholder("Search")
    search.click()
    search.fill(text)
    search.press("Enter")
    
    page.locator("ytd-video-renderer").first.click()

    return page

def perplex(text, on_close):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.on("close", on_close)
    page.goto("https://www.perplexity.ai/")
    
    search = page.get_by_placeholder("Ask anything...")
    search.click()
    search.fill(text)
    search.press("Enter")



def close():
    print("close")
    event.set()


if __name__ == "__main__":
    try:
        event = Event()
        perplex("what's the genos of the pangolin", close)
        # event.wait()

    except Exception as e:
        print(e)
    



# from macnotesapp import NotesApp

# notesapp = NotesApp()
# note = notesapp.make_note("Test Note", body="<div>This is a test note</div>")
# note.body = note.body + "<div>This is a second paragraph</div>"


# import re

# def find_matching_substrings(string: str, substrings: list) -> str:
#     """
#     Find the first substring at the beginning of a word in the given string

#     Parameters
#     ----------
#         `string`: str
#             The string to search for the substrings

#         `substrings`: list
#             The list of substrings to search for

#     Returns
#     -------
#     The matched substring at the beginning of a word, or None if not found
#     """
#     for substring in substrings:
#         pattern = r'\b' + re.escape(substring) + r'\b'
#         match = re.match(pattern, string.strip().lower())
#         if match:
#             return match.group(0)
#     return None


# def find_matching_substring(string: str, substring: str) -> str:
#     """
#     Find the substring at the beginning of a word in the given string.

#     Parameters:
#         string (str): The string to search for the substring.
#         substring (str): The substring to search for.

#     Returns:
#         str: The matched substring at the beginning of a word, or None if not found.
#     """
#     # Constructing the regular expression pattern to match the substring at the beginning of a word
#     pattern = r'\b' + re.escape(substring) + r'\b'
#     print(pattern)

#     # Using re.search to find the first match
#     match = re.search(pattern, string.strip())

#     # Returning the matched substring or None if no match found (or match not at the start)
#     return match.group(0) if match and match.start() == 0 else None


# def remove_substring(string: str, substring: str) -> str:
#     """
#     Remove the specified substring from the original string.

#     Parameters:
#         string (str): The original string from which to remove the substring.
#         substring (str): The substring to remove.

#     Returns:
#         str: The resulting string after removing the substring.
#     """
#     # Find the index of the first occurrence of the substring
#     index = string.lower().find(substring.lower())
    
#     # If the substring is not found, return the original string
#     if index == -1:
#         return string
    
#     # Remove the substring and return the result
#     return string[index + len(substring):].strip()


# string = input("sample text: ")

# while True:
#     substring = input("keyword: ")
#     print(f"[KEYWORD] {find_matching_substrings(string, [substring, 'puto'])}")
    # print(f"[CONTENT] {remove_substring(string.lower(), substring.lower())}")

# find_matching_substring(' YouTube bonobos in the wild', ['youtube', 'search'])