"""Simple speech-to-text demo using the SpeechRecognition library."""

import argparse
import sys

try:
    import speech_recognition as sr
except ImportError:
    print("Missing dependency: speechrecognition. Install with: pip install SpeechRecognition")
    sys.exit(1)

# Optional fallback for environments where PyAudio cannot be installed (e.g., Python 3.14 on Windows)
try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd = None
    np = None


def record_with_sounddevice(duration: float = 5.0, sample_rate: int = 16000):
    """Record audio from the default microphone using sounddevice."""
    if sd is None:
        raise RuntimeError("sounddevice is not installed. Install with: pip install sounddevice numpy")

    print(f"Recording {duration:.1f}s from the default microphone...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    raw_data = audio.tobytes()
    return raw_data, sample_rate


def recognize_from_microphone():
    r = sr.Recognizer()

    try:
        mic = sr.Microphone()
        with mic as source:
            print("Adjusting for ambient noise... (1 sec)")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now.")
            audio = r.listen(source)
    except AttributeError:
        # PyAudio is not available; fall back to sounddevice-based recording
        print("PyAudio not found - falling back to sounddevice for microphone input.")
        raw_data, sample_rate = record_with_sounddevice(duration=5.0, sample_rate=16000)
        audio = sr.AudioData(raw_data, sample_rate, sample_width=2)

    print("Recognizing...")
    try:
        text = r.recognize_google(audio)
        print("\n=== Transcription ===")
        print(text)
        print("====================")
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Recognition request failed: {e}")


def recognize_from_file(wav_path: str):
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)

    print("Recognizing...")
    try:
        text = r.recognize_google(audio)
        print("\n=== Transcription ===")
        print(text)
        print("====================")
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Recognition request failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Speech-to-text demo (microphone or WAV file)")
    parser.add_argument("--file", "-f", metavar="PATH", help="Path to a WAV file to transcribe")
    args = parser.parse_args()

    if args.file:
        recognize_from_file(args.file)
    else:
        recognize_from_microphone()


if __name__ == "__main__":
    main()
