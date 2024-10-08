from dotenv import load_dotenv
import keyboard
from litellm import completion
from notifypy import Notify
import os
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import queue
from simpleaudio import WaveObject
from sounddevice import InputStream, default, query_devices
from soundfile import SoundFile
import sys
import tempfile
import threading
from TTS.api import TTS
import whisper
import yaml


load_dotenv()

icon=Image.open("icon_v2.png")
notification = Notify(
    default_notification_application_name="alts ",
    default_notification_title="",
    default_notification_icon="icon_v2.png",
    # custom_mac_notificator="ALTS.app"
)

SENTENCE_DELIMITERS = (".", "?", "!", ";", ":", ": ", " (", ")", "\n-", "\n- ", " -", "- ", "\n–", "\n– ", " –", "– ")

# TODO: improve logging (use a proper logger), remove hardcoded stdout prints.
# TODO: implement cancelling of assistant jobs (automatically when querying something new? by keyboard?)
class ALTS:
    def __init__(self, auto_start=True):
        self._config()

        if auto_start:
            self.start()

            
    def _config(self):
        self.current_lang = None
        self.speech_q = queue.Queue()

        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        self.hotkey = config["hotkey"]
        self.messages = config["messages"]
        self.show_notifications = config["showNotifications"]

        self._notify(message=self.messages["starting"])

        # Load STT model
        self.stt_config = config["whisper"]
        self.stt = whisper.load_model(self.stt_config["model"])

        # Load TTS model
        self.tts_config = config["tts"]
        self.tts = TTS(model_name=config["tts"]["model"], progress_bar=False)

        # Load LLM config
        self.llm = config["llm"]

        self.tray_icon = Icon("alts", icon, "alts")


    def _quit(self):
        os._exit(0)


    def _notify(self, message=""):
        if(self.show_notifications):
            notification.message = message
            notification.send(block=False)


    def _toggle_notifications(self):
        self.show_notifications = not self.show_notifications


    def _initialize_chat(self, chat=None):
        self.current_chat = chat["title"] if chat else ""
        self.llm["messages"] = chat["messages"] if chat else []

        if not self.llm["messages"] and self.llm["system"]:
            self.llm["messages"] = [{ "role": "system", "content": self.llm["system"] }]
        
        os.system('cls||clear')

        self.tray_icon.menu = self._tray_menu()
        
        self._notify(message=self.messages["ready"])
        print(self.messages["ready"])


    def _tray_menu(self):
        return Menu(
            MenuItem(
                text="Show Notifications",
                action=self._toggle_notifications,
                checked=lambda _: self.show_notifications
            ),
            Menu.SEPARATOR,
            MenuItem(
                text="Quit",
                action=self._quit,
            ),
        )
    

    def _user_audio_input_worker(self):
        """Process user audio input"""
        print("\n🎙️  LISTENING...")
        self._notify(message=self.messages["listening"])

        audio = self.listen()

        print("\n💬 TRANSCRIBING...")
        transcription_data = self.transcribe(audio=audio)
        transcription = transcription_data["text"]
        self.current_lang = transcription_data["language"]

        print(f">>>{transcription}")

        self._llm_worker(transcription)
        
    
    def _user_text_input_worker(self):
        """Process user text input"""
        while True:
            self._llm_worker(input(self.messages["textInput"]))


    def _llm_worker(self, query):
        """Process llm response"""
        print("\n💭 THINKING...\n")

        self._notify(message=self.messages["thinking"])

        speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        speech_thread.start()

        for sentence in self.think(query=query):
            synth_data = self.synthesize(text=sentence)
            self.speech_q.put(synth_data)
        
        self.speech_q.put(None)
        speech_thread.join()


    def _speech_worker(self):
        """Process speech audio files"""
        while True:
            synth_data = self.speech_q.get()
            
            if synth_data is None:
                print(self.messages["ready"])
                self._notify(message=self.messages["ready"])
                break

            self._notify(message=f'"{synth_data["text"].strip()}"')
            print("\n🔊 SPEAKING...\n")
            self.speak(synth_data["audio"])

    def start(self):
        """Start assistant with default behavior"""
        self._initialize_chat()

        keyboard.add_hotkey(self.hotkey, lambda: self._user_audio_input_worker())

        user_input_thread = threading.Thread(target = self._user_text_input_worker, daemon=True)
        user_input_thread.start()

        self.tray_icon.run()
        keyboard.wait()
        
        user_input_thread.join()
        
        
    def listen(self):
        """Record microphone audio to a .wav file"""
        try:
            device_info = query_devices(default.device, 'input')
            samplerate = int(device_info['default_samplerate'])
            channels = device_info['max_input_channels']
            device = device_info['index']

            mic_record_q = queue.Queue()

            filename = tempfile.mktemp(suffix='.wav', dir='')
            file = SoundFile(
                filename,
                mode='x',
                samplerate=samplerate,
                channels=channels
            )

            def _input_stream_callback(indata, frames, time, status):
                if status:
                    print(status, file=sys.stderr)
                mic_record_q.put(indata.copy())

            stream = InputStream(
                samplerate=samplerate,
                device=device,
                channels=channels,
                callback=_input_stream_callback
            )
            stream.start()

            while keyboard.is_pressed(self.hotkey):
                file.write(mic_record_q.get())
            
            stream.close()
            file.close()

            return file.name

        except Exception as e:
            raise type(e)(str(e))


    def transcribe(self, audio, remove_audio=True):
        """
        Transcribe an audio file using Whisper

        Parameters
        ----------
        `audio`: str
            Path to the audio file to transcribe

        `remove_audio`: bool
            Whether to delete the audio file after transcribing it

        Returns
        -------
        A dictionary containing the resulting text ("text") and segment-level details ("segments"), and
        the spoken language ("language") detected.
        """
        try:
            result = self.stt.transcribe(audio, fp16=False)

            if remove_audio:
                os.remove(audio)

            return result

        except Exception as e:
            raise type(e)(str(e))


    def think(self, query, buffer_sentences=True):
        """
        Send a query to an LLM and stream the response

        Parameters
        ----------
        `query`: str
            Query to prompt the LLM with

        `buffer_sentences`: bool
            Whether to buffer and return the result sentence by sentence

        Returns
        -------
        A generator object containing strings.
        """
        try:
            self.llm["messages"].append({ "role": "user", "content": query })
            full_response = ""

            if not self.llm["custom_provider"] or "":
                response = completion(
                    model=self.llm["model"], 
                    messages=self.llm["messages"], 
                    api_base=self.llm["url"],
                    stream=True
                )
            else:
                response = completion(
                    model=self.llm["model"], 
                    messages=self.llm["messages"], 
                    api_base=self.llm["url"],
                    custom_llm_provider=self.llm["custom_provider"],
                    stream=True
                )

            for sentence in self._parse_response(response, buffer_sentences):
                full_response += sentence
                yield sentence

            self.llm["messages"].append({"role": "assistant", "content": full_response})
        
        except Exception as e:
            raise type(e)(str(e))
    
    # TODO: move to helpers
    # TODO: improve parsing abbreviations, markdown?... for proper talk-back edge-cases
    def _parse_response(self, chunks, buffer_sentences):
        """Split/compile LLM response chunks into sentences"""
        buffer = ""
        for chunk in chunks:
            token = chunk['choices'][0]['delta']['content'] or ""

            if not buffer_sentences:
                yield token

            if token.startswith(SENTENCE_DELIMITERS):
                yield buffer + token[0]
                buffer = token[1:]
            else:
                buffer += token

        if buffer != "":
            yield buffer


    def synthesize(self, text, split_sentences=True):
        """
        Synthesize text into an audio file

        Parameters
        ----------
        `sentence`: str
            Text to be synthesized into audio
        
        `lang`: str
            Language code of the text to synthesize (only applies to multilingual models)

        `split_sentences`: bool
            Whether the text should be splitted into sentences

        Returns
        -------
        A dictionary containing the path to the audio file of the synthesized text ("audio") and the text itself ("text").
        """
        try:
            speaker = self.tts_config["speakerId"] if self.tts.is_multi_speaker else None
            language = self.current_lang if self.tts.is_multi_lingual and self.current_lang in self.tts.languages else None

            audio = self.tts.tts_to_file(
                text=text,
                speaker=speaker,
                language=language,
                split_sentences=split_sentences,
                file_path=tempfile.mktemp(suffix='.wav', dir='')
            )
        
            return dict(audio=audio, text=text)
        
        except Exception as e:
            raise type(e)(str(e))
        

    def speak(self, audio, remove_audio=True):
        """
        Play an audio file

        Parameters
        ----------
        `audio`: str
            Path to the audio file to play

        `remove_audio`: bool
            Whether to delete the audio file after transcribing it
        """
        try:
            wave_obj = WaveObject.from_wave_file(audio)
            play_obj = wave_obj.play()
            play_obj.wait_done()

            if remove_audio:
                os.remove(audio)
        
        except Exception as e:
            raise type(e)(str(e))


def main():
    try:
        ALTS()

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()