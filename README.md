<h1 align="center">alts</h1>
<p align="center">
  <a href="https://github.com/alxpez/alts" target="_blank">
    <img width="180" src="logo.png">
  </a>
</p>
<p align="center">( 🤖 <strong>a</strong>ssistant: 🎙️ <strong>l</strong>isten | 💭 <strong>t</strong>hink | 🔊 <strong>s</strong>peak )</p>

</br>

## 💬 about
100% free, local and offline assistant with speech recognition and talk-back functionalities.

## 🤖 default usage
<!-- 
TODO: FUTURE FEATURES:
- long-term-memory: ability to save conversations
(thinking of redis - ease of use and speed)

- voice-to-clipboard: talk to take notes, write emails... paste raw or parsed text.
(Use the LLM to reshape/process/parse the whisper result to get a refined result)
(research if possible to paste automatically in the focused text-box)

- task-bar-icon: make the python script into a proper app
(or a simple installable package at least)
(include interface to text too)
-->
ALTS runs in the background and waits for you to press `ctrl+space` (you can modify the hotkey combination in `config.yaml`).
- 🎙️ While holding the hotkey, your voice will be recorded by your mic.
- 💭 On release, the recording stops and a transcript is sent to the LLM.
- 🔊 The LLM responses then get synthesized and played back to you.

You can also write your query directly into your terminal (if you don't wanna talk), the assistant will still speak back to you.

> ALL processes are local and __NONE__ of your recordings or queries are leave your environment; the recordings are deleted as soon as they are used; it's __ALL PRIVATE__ by _default_

> Be aware that if you configure ALTS with external providers (eg. OpenAI) your queries will be sent to their servers

## ⚙️ pre-requisites
- ### python
  > (tested on) version \>=3.11 on macOS and version \>=3.8 on windows

- ### llm
  By default, the project is configured to work with [Ollama](https://ollama.ai/), running the [`dolphin-phi` model](https://ollama.ai/library/dolphin-phi) (an uncensored, very tiny and quick model). This setup makes the whole system completely free to run locally and great for low resource machines.

  However, we use [LiteLLM](https://github.com/BerriAI/litellm) in order to be provider agnostic, so you have full freedom to pick and choose your own combinations.
  Take a look at the supported [Models/Providers](https://docs.litellm.ai/docs/providers) for more details on LLM configuration.
  > See `.env.template` and `config.yaml` for customizing your setup

<!-- TODO: Include extra information and examples of LLM configurations -->

- ### stt
  We use `openAI's whisper` to transcribe your voice queries. It's a general-purpose speech recognition model.

  You will need to have [`ffmepg`](https://ffmpeg.org/) installed in your environment, you can [download](https://ffmpeg.org/download.html) it from the official site.

  Make sure to check out their [setup](https://github.com/openai/whisper?tab=readme-ov-file#setup) docs, for any other requirement.
  > if you stumble into errors, one reason could be the model not downloading automatically. If that's the case you can run a `whisper` example transcription in your terminal ([see examples](https://github.com/openai/whisper?tab=readme-ov-file#command-line-usage)) or manually download it and place the model-file in the [correct folder](https://github.com/openai/whisper/discussions/63)


- ### tts
  We use `coqui-TTS` for ALTS to talk-back to you. It's a library for advanced Text-to-Speech generation.

  You will need to install [`eSpeak-ng`](https://github.com/espeak-ng/espeak-ng) in your environment:
  - macOS – `brew install espeak`
  - linux – `sudo apt-get install espeak -y`
  - windows – [download](https://github.com/espeak-ng/espeak-ng/releases) the executable from their repo
    > on __windows__ you'll also need `Desktop development with C++` and `.NET desktop build tools`.
    > Download the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and install these dependencies.

  Make sure to check out their [setup](https://github.com/coqui-ai/TTS/tree/dev#installation) docs, for any other requirement.
  > if you don't have the configured model already downloaded it should download automatically during startup, however if you encounter any problems, the default model can be pre-downloaded by running the following:
  >  ```ssh
  >  tts --text "this is a setup test" --out_path test_output.wav --model_name tts_models/en/vctk/vits --speaker_idx p244
  >  ```

## ✅ get it running
clone the repo
```ssh
git clone https://github.com/alxpez/alts.git
```

go to the main folder
```ssh
cd alts/
```

install the project dependencies
```ssh
pip install -r requirements.txt
```
> see the [pre-requisites](#%EF%B8%8F-pre-requisites) section, to make sure your machine is ready to start the ALTS

start up the assistant
```ssh
sudo python assistant.py
```
> the `keyboard` package requires to be run as admin (in macOS and Linux), it's not the case on Windows

