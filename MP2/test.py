import wave
audio = wave.open("arcane.wav", 'rb')
print(f"Channels: {audio.getnchannels()}, Sample Rate: {audio.getframerate()}, Sample Width: {audio.getsampwidth()}")