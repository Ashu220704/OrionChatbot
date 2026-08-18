from .whisper import model

def speech_to_text(audio_file):
    """
        Converts speech into text
    """

    segments, info = model.transcribe(audio_file, beam_size=5)

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()

