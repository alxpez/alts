import os
import sys
import yaml
import whisper
import queue
import threading
import tempfile
import keyboard
from sounddevice import InputStream, default, query_devices
from soundfile import SoundFile
from TTS.api import TTS
from simpleaudio import WaveObject
from operator import itemgetter
from langchain.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

SENTENCE_DELIMITERS = (".", "?", "!", ";", ":", " (", ")", "\n-")

# TODO: improve logging (use a proper logger), remove hardcoded stdout prints.
class Assistant:
    def __init__(self, auto_start=True):
        self._config()

        if auto_start:
            self.start()

    def _config(self):
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        self.q = queue.Queue()
        
        self.system_prompt = config["llm"]["systemPrompt"]
        self.speaker_id = config["tts"]["speakerId"]
        self.hotkey = config["hotkey"]
        self.input_message = f"\n'{self.hotkey}' {config['messages']['userInput']}"

        # Load STT model
        stt_model = config["whisper"]["model"]
        if not config["whisper"]["isMulti"]:
            stt_model += f".en"

        self.stt = whisper.load_model(stt_model)

        # Load TTS model
        self.tts = TTS(model_name=config["tts"]["model"], progress_bar=False)

        # Load LLM
        self.llm = ChatOllama(model=config["llm"]["model"])

        # Configure LLM memory
        self.memory = ConversationBufferMemory(return_messages=True)

        # Create LLM chain
        self.chain = self._initialize_chain()


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
            if text.content.startswith(SENTENCE_DELIMITERS):
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

        def _wait_input():
            """Process user input"""
            print(self.input_message)
            while True:
                self.think(query=input())

        user_input_thread = threading.Thread(target=_wait_input)
        user_input_thread.start()
        user_input_thread.join()

        keyboard.wait()


    def listen(self, is_auto=True):
        """Record microphone audio to a .wav file"""
        try:
            device_info = query_devices(default.device, 'input')
            samplerate = int(device_info['default_samplerate'])
            channels = device_info['max_input_channels']
            device = device_info['index']

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
                self.q.put(indata.copy())

            stream = InputStream(
                samplerate=samplerate,
                device=device,
                channels=channels,
                callback=_input_stream_callback
            )
            stream.start()

            print("\n🎙️  LISTENING...")
            while keyboard.is_pressed(self.hotkey):
                file.write(self.q.get())
            
            stream.close()
            file.close()

            if is_auto:
                self.transcribe(audio_file=file.name)
            
            return file.name

        except Exception as e:
            raise type(e)(str(e))


    def transcribe(self, audio_file, should_remove_audio=True, is_auto=True):
        """Transcribe an audio file"""
        try:
            print("📝 TRANSCRIBING...")
            transcription = self.stt.transcribe(audio_file, fp16=False)
            print(f"💬 >>>{transcription['text']}")

            if should_remove_audio:
                os.remove(audio_file)

            if is_auto:
                self.think(query=transcription['text'])
            
            return transcription['text']

        except Exception as e:
            raise type(e)(str(e))
            

    def think(self, query, is_auto=True):
        """Send a query to an LLM and stream response sentence-by-sentence"""
        try:
            print(f"\n🤔 THINKING...\n")
            print("#" * 50)
            input_data = {"input": query}
            output = ""
            for sentence in self.chain.stream(input_data):
                output += sentence
                if is_auto:
                    self.synthesize(sentence)
            
            self.memory.save_context(input_data, {"output": output}) 
            print("#" * 50)
            print(f"\n💬 <<< {output}")
            print(self.input_message)
            return output
        
        except Exception as e:
            raise type(e)(str(e))
            

    def synthesize(self, sentence, is_auto=True):
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

            if is_auto:
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
