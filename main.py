from assistant import Assistant

def main():
    try:
        # Initialize and run an assistant out-of-the-box
        Assistant()

        # # Example of standalone usage of assistant's functions

        # # Initialize an assistant in manual mode
        # assistant = Assistant(auto_start=False)

        # query = "What are large language models good for?"
        
        # response = assistant.think(
        #     query=query,
        #     is_standalone=True
        # )

        # question_speech = assistant.synthesize(
        #     sentence=response,
        #     is_standalone=True
        # )
        
        # question_transcription = assistant.transcribe(
        #     audio_file=question_speech,
        #     should_remove_audio=False,
        #     is_standalone=True
        # )
        # print(f"> {question_transcription}")

        # assistant.speak(audio_file=question_speech)

        # # Start the assistant in auto-mode
        # assistant.start()

    except KeyboardInterrupt: 
        print("\n\n👋 BYE!")
    except Exception as e:
        raise type(e)(str(e))

if __name__ == "__main__":
    main()
