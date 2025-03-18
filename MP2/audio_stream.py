import wave

class audio_stream:
    def __init__(self, filename):
        self.filename = filename
        try:
            self.file = wave.open(filename, 'rb')
        except:
            raise IOError
        self.frameNum = 0

    def nextFrame(self):
        """Get the next audio chunk."""
        data = self.file.readframes(160)  # 160 frames = 20ms audio for G.711
        if data:
            self.frameNum += 1
        return data

    def frameNbr(self):
        """Return the current frame number."""
        return self.frameNum
