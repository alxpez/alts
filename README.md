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

Simple to use, easy to (hack)extend.

> disclaimer: only tested on a macbook pro (intel)

## requirements
- `ollama` - [mac](https://github.com/jmorganca/ollama?tab=readme-ov-file#macos) | [windows & linux](https://github.com/jmorganca/ollama?tab=readme-ov-file#linux--wsl2)
  - ```
    ollama pull dolphin-phi
    ```
  - > by default we use `dolphin-phi`; an uncensored, very tiny and quick model, great for low resources machines (but feel free to download and use any model you like, just change `CHAT_MODEL` variable)

- `whisper` - [setup](https://github.com/openai/whisper?tab=readme-ov-file#setup)

## installation
```python
pip install -r requirements.txt
```

## run
```python
sudo python main.py
```
> the `keyboard` package requires to be run as admin