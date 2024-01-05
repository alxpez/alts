import os
import sys
import yaml
import json
import queue
import whisper
import keyboard
import requests
import tempfile
import threading
from sounddevice import InputStream, default, query_devices
from soundfile import SoundFile
from TTS.api import TTS
from simpleaudio import WaveObject
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv('LLM_API_KEY')
BASE_REQ_HEADERS = {"Content-Type": "application/json"}
SENTENCE_DELIMITERS = (".", "?", "!", ";", ":", ": ", " (", ")", "\n-", " -", "\n–", " –")

# TODO: improve logging (use a proper logger), remove hardcoded stdout prints.
# TODO: better handling of KeyboardInterrupt to exit more gracefully
# TODO: implement cancelling of assistant jobs (automatically when querying something new? by keyboard?)
class Assistant:
    def __init__(self, auto_start=True):
        self._config()

        if auto_start:
            self.start()

            
    def _config(self):
        self.speech_q = queue.Queue()
        self.user_input_thread = threading.Thread(target = self._user_text_input_worker, daemon=True)

        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        self.hotkey = config["hotkey"]
        self.input_message = f"'{self.hotkey}' {config['messages']['userInput']}\n"

        # Load STT model
        stt_model = config["whisper"]["model"]
        if not config["whisper"]["isMulti"]:
            stt_model += f".en"

        self.stt = whisper.load_model(stt_model)

        # Load TTS model
        self.tts = TTS(model_name=config["tts"]["model"], progress_bar=False)
        self.speaker_id = config["tts"]["speakerId"]

        # Load LLM config: initialize messages and config req. headers
        self.llm = config["llm"]
        self.llm["messages"] = [{ "role": "system", "content": self.llm["system"] }]
        self.llm["headers"] = BASE_REQ_HEADERS
        if LLM_API_KEY:
            self.llm["headers"]["Authorization"] = f"Bearer {LLM_API_KEY}"
        else:
            # TODO
            print("TODO: preload local model in memory")


    def _user_audio_input_worker(self):
        """Process user audio input"""

        print("\n🎙️  LISTENING...")
        audio_file = self.listen()

        print("\n📝 TRANSCRIBING...")
        transcription = self.transcribe(audio_file=audio_file)
        print(f"💬 >>>{transcription}")

        self._llm_worker(transcription)
        
    
    def _user_text_input_worker(self):
        """Process user text input"""
        while True:
            self._llm_worker(input())


    def _llm_worker(self, query):
        """Process llm response"""
        print(f"\n🤔 THINKING...\n")
        speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        speech_thread.start()
        for sentence in self.think(query=query):
            audio_file = self.synthesize(sentence)
            self.speech_q.put(audio_file)
        
        self.speech_q.put(None)
        speech_thread.join()


    def _speech_worker(self):
        """Process speech audio files"""
        while True:
            audio_file = self.speech_q.get()
            
            if audio_file is None:
                print(self.input_message)
                break

            print(f"\n🔊 SPEAKING...\n")
            self.speak(audio_file)


    def start(self):
        """Start assistant with default behavior"""
        os.system('cls||clear')
        print(self.input_message)

        keyboard.add_hotkey(self.hotkey, lambda: self._user_audio_input_worker())

        self.user_input_thread.start()
        self.user_input_thread.join()

        keyboard.wait()

        
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


    def transcribe(self, audio_file, remove_audio=True):
        """Transcribe an audio file"""
        try:
            transcription = self.stt.transcribe(audio_file, fp16=False)

            if remove_audio:
                os.remove(audio_file)

            return transcription['text']

        except Exception as e:
            raise type(e)(str(e))
            

    def think(self, query, buffer_sentences=True):
        """Send a query to an LLM and stream response"""
        try:
            self.llm["messages"].append({ "role": "user", "content": query })

            params = {
                "model": self.llm["model"],
                "messages": self.llm["messages"],
                "stream": True
            }
            response = requests.post(
                self.llm["url"],
                headers=self.llm["headers"],
                json=params
            )
            response.raise_for_status()

            full_response = buffer = ""
            for line in response.iter_lines():
                body = json.loads(line)
                token = body["message"]["content"]
                full_response += token

                if buffer_sentences:
                    if token.startswith(SENTENCE_DELIMITERS):
                        yield buffer + token[0]
                        buffer = token[1:]
                    else:
                        buffer += token
                else:
                    yield token

                # TODO: handle llm API errors
                # if "error" in body and auto:
                #     self.synthesis_q.put(f"Error: {body['error']}")

                if body.get("done", False):
                    self.llm["messages"].append({"role": "assistant", "content": full_response})
            
            if buffer_sentences and buffer != "":
                yield buffer
        
        except Exception as e:
            raise type(e)(str(e))

    def synthesize(self, sentence):
        """Synthesize text into an audio file"""
        try:
            return self.tts.tts_to_file(
                text=sentence,
                speaker=self.speaker_id,
                file_path=tempfile.mktemp(suffix='.wav', dir=''),
                split_sentences=False
            )
        
        except Exception as e:
            raise type(e)(str(e))
        

    def speak(self, audio_file, remove_audio=True):
        """Play an audio file"""
        try:
            wave_obj = WaveObject.from_wave_file(audio_file)
            play_obj = wave_obj.play()
            play_obj.wait_done()

            if remove_audio:
                os.remove(audio_file)
        
        except Exception as e:
            raise type(e)(str(e))
