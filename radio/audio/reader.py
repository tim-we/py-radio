import numpy as np
import ffmpeg
import os
from time import sleep


# load_audio can not detect the input type
def ffmpeg_load_audio(filename: str, mono: bool = False, normalize: bool = True) -> np.ndarray:  # type: ignore
    channels = 1 if mono else 2
    sample_rate = 48000
    in_type = np.int16
    num_bytes = 2*channels
    out_type = np.float32
    num_threads = max(1, (os.cpu_count() or 1)//2)

    out, err = (ffmpeg
                .input(filename, threads=num_threads)
                .output('-', format='s16le', acodec='pcm_s16le', ar=str(sample_rate), ac=str(channels))
                .overwrite_output()
                .run(capture_stdout=True, quiet=True)
                )

    audio = np.zeros((len(out) // num_bytes, channels), out_type)
    frame_shift = 1024
    peak = 0 if normalize else np.iinfo(in_type).max
    for i in range(audio.shape[0] // frame_shift):
        audio[i*frame_shift:(i+1)*frame_shift, :] \
            = np.frombuffer(out[i*num_bytes*frame_shift:(i+1)*num_bytes*frame_shift], dtype=in_type
                            ).astype(out_type).reshape((-1, channels))
        if normalize:
            new_peak = np.max(audio[i*frame_shift:(i+1)*frame_shift+1, :])
            if peak < new_peak:
                peak = new_peak
        sleep(0)
    audio = np.divide(audio, peak)
    return audio, sample_rate
