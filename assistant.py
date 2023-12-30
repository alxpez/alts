import os
import sys
import whisper
import queue
import threading
import tempfile
import keyboard
from sounddevice import InputStream, query_devices
from soundfile import SoundFile
from TTS.api import TTS
from simpleaudio import WaveObject
from operator import itemgetter
from langchain.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# TODO: move defaults to config.yaml
HOTKEY = "cmd+i"
USER_INPUT_MESSAGE = f"\n('{HOTKEY}' to TALK or TYPE your query)"
STT_MODEL = "tiny.en"
CHAT_MODEL = "dolphin-phi"
SYSTEM_PROMPT="Your responses are concise. Do not give unwanted explanations. STICK TO WHAT IS REQUESTED. DO NOT MAKE THINGS UP. If there is anything you do not know, just reply: 'Sorry, I don't know'."
SENTENCE_DELIMITERS = (".", "?", "!", ";", ":", " (", ")", "\n-")
TTS_MODEL = "tts_models/en/vctk/vits"
SPEAKER_ID = "p244"

# TODO: improve logging (use a proper logger), remove hardcoded stdout prints.
class Assistant:
    def __init__(self, ollama_model=CHAT_MODEL, system_prompt=SYSTEM_PROMPT, delimiters=SENTENCE_DELIMITERS, stt_model=STT_MODEL, tts_model=TTS_MODEL, speaker_id=SPEAKER_ID, hotkey=HOTKEY, input_message=USER_INPUT_MESSAGE, auto_start=True):
        self.q = queue.Queue()
        self.device = 1 # TODO: allow choosing a different input device
        self.channels = 1
        self.ollama_model = ollama_model
        self.system_prompt = system_prompt
        self.delimiters = delimiters
        self.speaker_id = speaker_id
        self.hotkey = hotkey
        self.input_message = input_message

        # Load STT model
        self.stt = whisper.load_model(stt_model)

        # Load TTS model
        self.tts = TTS(model_name=tts_model, progress_bar=False)

        # Load LLM
        self.llm = ChatOllama(model=ollama_model)

        # Configure LLM memory
        self.memory = ConversationBufferMemory(return_messages=True)

        # Create LLM chain
        self.chain = self._initialize_chain()

        if auto_start:
            self.start()


    def _initialize_chain(self):
        """Create LLM chat chain with memory"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        return (
            RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history")
            )
            | prompt
            | self.llm
            | self._split_sentences
        )

    # TODO: improve parsing abbreviations, markdown... for proper talk-back
    def _split_sentences(self, chunks):
        """Split/compile chunks into sentences"""
        buffer = ""
        for text in chunks:
            if text.content.startswith(self.delimiters):
                yield buffer + text.content[0]
                buffer = text.content[1:]
            else:
                buffer += text.content
        if buffer != "":
            yield buffer


    def start(self):
        """Start assistant with default behavior"""
        os.system('cls||clear')

        keyboard.add_hotkey(self.hotkey, lambda: self.listen())

        user_input_thread = threading.Thread(target=self._wait_input)
        user_input_thread.start()
        user_input_thread.join()

        keyboard.wait()

    def _wait_input(self):
        """Process user input"""
        print(self.input_message)
        while True:
            self.think(query=input())


    def listen(self, is_standalone=False):
        """Record microphone audio to a .wav file"""
        try:
            device_info = query_devices(self.device, 'input')
            samplerate = int(device_info['default_samplerate'])

            filename = tempfile.mktemp(suffix='.wav', dir='')
            file = SoundFile(
                filename,
                mode='x',
                samplerate=samplerate,
                channels=self.channels
            )

            stream = InputStream(
                samplerate=samplerate,
                device=self.device,
                channels=self.channels,
                callback=self._input_stream_callback
            )
            stream.start()

            print("\n🎙️  LISTENING...")
            while keyboard.is_pressed('command') and keyboard.is_pressed('i'):
                file.write(self.q.get())
            
            stream.close()
            file.close()

            if not is_standalone:
                self.transcribe(audio_file=file.name)
            
            return file.name

        except Exception as e:
            raise type(e)(str(e))

    def _input_stream_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())


    def transcribe(self, audio_file, should_remove_audio=True, is_standalone=False):
        """Transcribe an audio file"""
        try:
            print("📝 TRANSCRIBING...")
            transcription = self.stt.transcribe(audio_file, fp16=False)
            print(f"💬 >>>{transcription['text']}")

            if should_remove_audio:
                os.remove(audio_file)

            if not is_standalone:
                self.think(query=transcription['text'])
            
            return transcription['text']

        except Exception as e:
            raise type(e)(str(e))
            

    def think(self, query, is_standalone=False):
        """Send a query to an LLM and stream response sentence-by-sentence"""
        try:
            print(f"\n🤔 THINKING...\n")
            print("#" * 50)
            input_data = {"input": query}
            output = ""
            for sentence in self.chain.stream(input_data):
                output += sentence
                if not is_standalone:
                    self.synthesize(sentence)
            
            self.memory.save_context(input_data, {"output": output}) 
            print("#" * 50)
            print(f"\n💬 <<< {output}")
            print(self.input_message)
            return output
        
        except Exception as e:
            raise type(e)(str(e))
            

    def synthesize(self, sentence, is_standalone=False):
        """Synthesize text into an audio file"""
        try:
            print(f"\n🤖 SYNTHESIZING...")
            filename = tempfile.mktemp(suffix='.wav', dir='')

            self.tts.tts_to_file(
                text=sentence,
                speaker=self.speaker_id,
                file_path=filename,
                split_sentences=False
            )

            if not is_standalone:
                self.speak(filename)
                
            return filename
        
        except Exception as e:
            raise type(e)(str(e))
        

    def speak(self, audio_file, should_remove_audio=True):
        """Play an audio file"""
        try:
            print(f"🔊 SPEAKING...\n")
            wave_obj = WaveObject.from_wave_file(audio_file)
            play_obj = wave_obj.play()
            play_obj.wait_done()

            if should_remove_audio:
                os.remove(audio_file)
        
        except Exception as e:
            raise type(e)(str(e))
