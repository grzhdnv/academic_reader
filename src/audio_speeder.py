from audiostretchy.stretch import stretch_audio
import soundfile as sf
import numpy as np

# Class to handle audio speeding and trimming
class AudioSpeeder:
    file_path = "" # Path to the audio file
    ratio = 0.7   # Speed-up ratio

    # Initialize with file path
    def __init__(self, file_path, ratio=0.7):
        self.file_path = file_path
        self.ratio = ratio

    def stretch_file(self):
        """
        Stretch (time-scale) in_path -> out_path.
        """
        out_path = self.file_path.replace(".wav", f"_{2-self.ratio}.wav")
        stretch_audio(self.file_path, out_path, ratio=self.ratio)

    def trim_trailing_silence(self, threshold=0.002, pad_seconds=0.01):
        """
        Trim trailing silence from wav_path.
        """
        data, sr = sf.read(self.file_path)
        # handle mono/stereo: take max absolute across channels per frame
        if data.ndim == 1:
            abs_env = np.abs(data)
        else:
            abs_env = np.max(np.abs(data), axis=1)
        above = np.where(abs_env > threshold)[0]
        if above.size == 0:
            # nothing above threshold — leave as is
            return
        end_idx = above[-1] + 1
        pad = int(pad_seconds * sr)
        end_idx = min(end_idx + pad, data.shape[0])
        trimmed = data[:end_idx]
        # overwrite the file with trimmed audio
        sf.write(self.file_path, trimmed, sr)

    def apply(self):
        self.trim_trailing_silence()
        self.stretch_file()
