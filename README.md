<h1 align="center">alts</h1>
<p align="center">
  <a href="https://github.com/alxpez/alts" target="_blank">
    <img width="180" src="logo.png">
  </a>
</p>
<p align="center">( <strong>a</strong>ssistant: <strong>l</strong>istent | <strong>t</strong>hink | <strong>s</strong>peak )</p>

</br>

## about
100% free, local and offline voice assistant with speech recognition.

<!-- 
TODO: explain features

ALTS runs in the background and waits for you to press a hotkey/key combination of your choosing; while holding the hotkey your default input sound device will record your voice, once you release the recording stops and this .wav file is transcribed with whisper and sent to your configured LLM.

The response from the LLM will be synthesized to another .wav file and played through your output sound device.

All this process happens locally by _default*_ and NONE of your recordings or any other information is shared with anyone; it's all private by _default*_.

_*_: be aware that if you configure ALTS with external providers your information might be exposed.

FUTURE FEATURES:
- voice-to-clipboard: talk to take notes, write emails... paste raw or parsed text.
(Use the LLM to reshape/process/parse the whisper result to get a refined result)
(research if possible to paste automatically in the focused text-box)
- task-bar icon: make the python script into a proper app (or a simple installable at least)
-->

## requirements

### LLM
By default, the project is configured to work with [Ollama](https://ollama.ai/), running the [`dolphin-phi` model](https://ollama.ai/library/dolphin-phi) (an uncensored, very tiny and quick model). This setup makes the whole system completely free to run locally and great for low resource machines.

However, we use [LiteLLM](https://github.com/BerriAI/litellm) in order to be provider agnostic, so you have full freedom to pick and choose your own combinations.
Take a look at the supported [Models/Providers](https://docs.litellm.ai/docs/providers) for more details on LLM configuration.
> See `.env.template` and `config.yaml` for customizing your setup

<!-- TODO: Include extra information and examples of LLM configurations -->


### STT
We use `whisper` to transcribe your voice queries. It's a general-purpose speech recognition model - [setup](https://github.com/openai/whisper?tab=readme-ov-file#setup)
> You might need to manually download a whisper model before running the assistant


### TTS
We use `TTS` for ALTS to talk-back to you. It's a library for advanced Text-to-Speech generation - [setup](https://github.com/coqui-ai/TTS/tree/dev#installation)
> You might need to manually download a TTS model before running the assistant

<!-- TODO: Include extra requirements for windows installation -->

## installation
```python
pip install -r requirements.txt
```

## run
```python
sudo python assistant.py
```
> the `keyboard` package requires to be run as admin (in macOS and Linux)
