# Ideas for Keywords feature


EXPLOTE:
- use `whisper`
- keywords actions
- (no llm locally)


## examples:

keyword: "quick note"
action: 
    - open notes app (OS dependant)
    - paste the rest of the transcription directly (don't even open the note, just save it)

keyword: "perplex"
action:
    - pytest run playwright test
    - operating browser to perplexity.ai, inserting the rest of the transcription in the main input area and search.
    - is it possible to keep the test open? (so user can keep on using the browser)
    - other possibility would be getting the main paragraph of the response and synthesize it as a voice response
    - if both options are possible, then make them options in the tray

---
- tested using playwright:
    - more control over the browser
    - more complex to use, threads pending etc

- other options: (flimsy)
    - limited control, `open https://perplexity.ai`
    - clipboard
    - keyboard -> `cmd+v`

---

# Ideas Tray Interactions feature

`MenuItem` for system Notes (fetch all notes on start and allow for access from there). On click of a note, ALTS will enter "Edit Note" mode (SHOW a notification?)

The note should be marked as checked.

Any message sent to ALTS will now go through a different process. The transcriptions will be taken by the following llm persona:

```
You're a professional copywriter, expert on PA tasks, catching quick notes and editing them on the fly. You take your job very seriously and are incredibly thorough.

This is what we have so far:

"""{NOTE FETCHED}"""

Now, incorporate the following new information:
"""{TRANSCRIPTION}"""
```
