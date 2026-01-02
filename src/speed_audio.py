from audiostretchy.stretch import stretch_audio
import soundfile as sf
import numpy as np

def stretch_file(in_path, out_path, ratio=0.7):
    """
    Stretch (time-scale) in_path -> out_path, then remove trailing silence.
    """
    stretch_audio(in_path, out_path, ratio=ratio)
    trim_trailing_silence(out_path)

def trim_trailing_silence(wav_path, threshold=0.002, pad_seconds=0.01):
    data, sr = sf.read(wav_path)
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
    sf.write(wav_path, trimmed, sr)

in_path = "/Users/mgrzhdnv/Documents/dev/academic_reader/output/Rose Singing at the piano.wav"
out_path = "/Users/mgrzhdnv/Documents/dev/academic_reader/output/Rose Singing at the piano_1.3.wav"

stretch_file(in_path, out_path, ratio=0.7)