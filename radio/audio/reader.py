import numpy as np
import ffmpeg
import os


# load_audio can not detect the input type
def ffmpeg_load_audio(filename: str, sample_rate: int = 48000, mono: bool = False, normalize: bool = True,
                      in_type: int = np.int16, out_type: float = np.float32) -> np.ndarray:  # type: ignore
    channels = 1 if mono else 2
    format_strings = {
        np.float64: 'f64le',
        np.float32: 'f32le',
        np.int16: 's16le',
        np.int32: 's32le',
        np.uint32: 'u32le'
    }
    format_string = format_strings[in_type]
    num_threads = max(1, os.cpu_count()//2)

    out, err = (ffmpeg
                .input(filename, threads=num_threads)
                .output('-', format=format_string, acodec='pcm_'+format_string, ar=str(sample_rate), ac=str(channels))
                .overwrite_output()
                .run(capture_stdout=True, quiet=True)
                )

    audio = np.frombuffer(out, dtype=in_type).astype(out_type)
    if normalize:
        peak = np.max(audio)
    else:
        peak = np.iinfo(in_type).max
    if channels > 1:
        audio = audio.reshape((-1, channels))
    audio = np.divide(audio, peak)
    return audio, sample_rate
