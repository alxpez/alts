import os
import sys
import queue
import tempfile
import keyboard
import whisper

from sounddevice import InputStream, query_devices
from soundfile import SoundFile

from TTS.api import TTS
from simpleaudio import WaveObject

from operator import itemgetter
from langchain.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Load STT model
stt_model = whisper.load_model("tiny.en")

# Configure/initialize LLM chain
model = ChatOllama(
    model="dolphin-phi:2.7b-v2.6-q6_K",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Your responses to user queries are concise. Don't waste tokens on unwanted explanations or possible follow up questions. STICK TO WHAT THE USER REQUESTED. DO NOT MAKE THINGS UP. If there's anything you don't know, just reply: 'Sorry, I don't know'."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
memory = ConversationBufferMemory(return_messages=True)

chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables)
        | itemgetter("history")
    )
    | prompt
    | model
    # | StrOutputParser() # 👀 https://github.com/langchain-ai/langchain/issues/14980 > NotImplementedError: Need to determine which default deprecation schedule to use. within ?? minor releases
)

# Initialize TTS model
tts = TTS(
    model_name="tts_models/en/vctk/vits",
    progress_bar=False
)

# Lists the audio devices available
# print(query_devices())
print(f"\n('cmd+i' to chat)")

def main():
    """Listen for keyboard events"""
    try:
        keyboard.add_hotkey('cmd+i', lambda: record_mic())
        keyboard.wait()

    except KeyboardInterrupt:
        print("\n\n👋 BYE!")
    except Exception as e:
        raise type(e)(str(e))

def record_mic():
    """Start recording audio"""
    q = queue.Queue()
    device = 1 
    channels = 1

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block"""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    try:
        device_info = query_devices(device, 'input')
        samplerate = int(device_info['default_samplerate'])

        filename = tempfile.mktemp(suffix='.wav', dir='')
        file = SoundFile(
            filename,
            mode='x',
            samplerate=samplerate,
            channels=channels
        )

        stream = InputStream(
            samplerate=samplerate,
            device=device,
            channels=channels,
            callback=callback
        )
        stream.start()

        print("\n🎙️  LISTENING...")
        while keyboard.is_pressed('command') and keyboard.is_pressed('i'):
            file.write(q.get())

    except Exception as e:
        raise type(e)(str(e))
    finally:
        stream.close()
        file.close()
        transcribe_audio(file.name)

def transcribe_audio(filename):
    """Transcribe the audio file"""
    try:
        print("📝 TRANSCRIBING...")
        transcription = stt_model.transcribe(filename, fp16=False)
        print(f"💬 >>>{transcription['text']}")
        os.remove(filename)

    except Exception as e:
        raise type(e)(str(e))
    finally:
        query_llm(transcription['text'])

def query_llm(query):
    """Send transcription to llm and persist chat history"""
    try:
        print(f"\n🤖 THINKING...")
        inputs = {"input": query}
        response = chain.invoke(inputs)
        memory.save_context(inputs, {"output": response.content})

    except Exception as e:
        raise type(e)(str(e))
    finally:
        synthesize_llm_response(response.content)

def synthesize_llm_response(input):
    """Synthesize the llm response and play audio"""
    try:
        print(f"\n🤖 SYNTHESIZING...")
        tts.tts_to_file(
            text=input,
            speaker="p244",
            file_path="speech.wav"
        )

        print(f"\n🔊 SPEAKING...")
        wave_obj = WaveObject.from_wave_file("speech.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        raise type(e)(str(e))
    finally:
        os.remove("speech.wav")
        print(f"\n('cmd+i' to chat)")

if __name__ == "__main__":
    main()