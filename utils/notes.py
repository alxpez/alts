from macnotesapp import NotesApp
from datetime import datetime

def new_note(text):
    notesapp = NotesApp()
    current_dateTime = datetime.now()
    notesapp.make_note(f"New note {current_dateTime}", body=text)