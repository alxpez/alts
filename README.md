<h1 align="center">alts</h1>
<p align="center">
  <a href="https://github.com/alxpez/alts" target="_blank">
    <img width="180" style="border-radius:50%" src="logo.png">
  </a>
</p>
<p align="center">( <strong>a</strong>ssistant: <strong>l</strong>istent | <strong>t</strong>hink | <strong>s</strong>peak )</p>

</br>

## about
100% free, local and offline voice assistant with speech recognition.

## requirements
By default, this project is configured to work with [Ollama](https://ollama.ai/), running the [`dolphin-phi` model](https://ollama.ai/library/dolphin-phi); an uncensored, very tiny and quick model, great for low resources machines. This set up makes the whole system completely free to run locally.

However, ALTS uses [LiteLLM](https://github.com/BerriAI/litellm) in order to be provider agnostic, so you have full freedom to pick and choose your own combination.
Take a look at the supported [Models/Providers](https://docs.litellm.ai/docs/providers) for more details on configurations.
> See `.env.template` and `config.yaml`

`whisper` is a general-purpose speech recognition model. ALTS uses it to transcribe your voice queries - [setup](https://github.com/openai/whisper?tab=readme-ov-file#setup)
> The whisper model might need to be downloaded prior to running the assistant

`TTS` is a library for advanced Text-to-Speech generation. ALTS uses it to talk back to you - [setup](https://github.com/coqui-ai/TTS/tree/dev#installation)
> The TTS model might need to be downloaded prior to running the assistant

## installation
```python
pip install -r requirements.txt
```

## run
```python
sudo python main.py
```
> the `keyboard` package requires to be run as admin (in macOS and Linux)

---

> TODO: Include extra information and examples of LLM configurations

> TODO: Include extra requirements for windows installation
