import os
import sys
import queue
import tempfile
import whisper
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


# Configuration
SENTENCE_DELIMITERS = (".", "?", "!", ";", ":", " (", ")", "\n-")
STT_MODEL = "tiny.en"
CHAT_MODEL = "dolphin-phi:2.7b-v2.6-q6_K"
SYSTEM_PROMPT="You are a helpful assistant. Your responses to user queries are concise. Don't waste tokens on unwanted explanations or possible follow up questions. STICK TO WHAT THE USER REQUESTED. DO NOT MAKE THINGS UP. If there's anything you don't know, just reply: 'Sorry, I don't know'."
TTS_MODEL = "tts_models/en/vctk/vits"
SPEAKER_ID = "p244"

# Load STT model
stt_model = whisper.load_model(STT_MODEL)

def output_chunker(chunks):
    """Used during input streaming to chunk sentences"""
    buffer = ""
    for text in chunks:
        if text.content.startswith(SENTENCE_DELIMITERS):
            yield buffer + text.content[0]
            buffer = text.content[1:]
        else:
            buffer += text.content
    if buffer != "":
        yield buffer

# Configure/initialize LLM chain
chat_model = ChatOllama(model=CHAT_MODEL)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
memory = ConversationBufferMemory(return_messages=True)
chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )
    | prompt
    | chat_model
    | output_chunker
)

# Initialize TTS model
tts = TTS(model_name=TTS_MODEL, progress_bar=False)

# Lists the audio devices available
# print(query_devices())

def main():
    """Listen for keyboard events"""
    try:
        os.system('cls||clear')
        print(f"\n('cmd+i' to chat)")
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
        print(f"\n('cmd+i' to chat)")

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
        print(f"\n🤔 THINKING...\n")
        print("#" * 50)
        input = {"input": query}
        output = ""
        for sentence in chain.stream(input):
            output += sentence
            synthesize_llm_response(sentence)

    except Exception as e:
        raise type(e)(str(e))
    finally:
        memory.save_context(input, {"output": output})
        print("#" * 50)
        print(f"\n💬 <<< {output}")

def synthesize_llm_response(sentence):
    """Synthesize the llm response and play audio"""
    try:
        print(f"\n🤖 SYNTHESIZING...")
        tts.tts_to_file(
            text=sentence,
            speaker=SPEAKER_ID,
            file_path="speech.wav",
            split_sentences=False
        )

        print(f"🔊 SPEAKING...\n")
        wave_obj = WaveObject.from_wave_file("speech.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        raise type(e)(str(e))
    finally:
        os.remove("speech.wav")

if __name__ == "__main__":
    main()