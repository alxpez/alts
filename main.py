from assistant import Assistant

def main():
    assistant = Assistant(False)
    
    try:
        assistant.start()

    except Exception as e:
        raise type(e)(str(e))

if __name__ == "__main__":
    main()
