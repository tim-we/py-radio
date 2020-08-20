import numpy as np
import ffmpeg
import os


# load_audio can not detect the input type
def ffmpeg_load_audio(filename: str, normalize: bool = True) -> np.ndarray:  # type: ignore
    num_threads = max(1, (os.cpu_count() or 1)//2)
    file_info = ffmpeg.probe(filename, threads=num_threads)

    # get audio info
    for stream_id, stream in enumerate(file_info['streams']):
        if stream['codec_type'] == 'audio':
            sample_rate = int(stream['sample_rate'])
            channels = int(stream['channels'])
            samples = int(float(stream['duration']) * sample_rate)
            break
    else:
        return np.empty()

    # start async decoding process to copy stdout frame-wise
    decode = (ffmpeg
              .input(filename, threads=num_threads)
              .output('-', format='s16le', acodec='pcm_s16le', ar=str(sample_rate), ac=str(channels))
              .overwrite_output()
              .run_async(pipe_stdout=True, quiet=True)
              )

    # prepare output array and frame shift processing
    frame_shift = 1024
    num_shifts = samples//frame_shift
    audio = np.zeros((num_shifts*frame_shift, channels), dtype=np.float32)
    num_bytes = 2*channels
    # initialize peak for int->float conversion and normalizing
    peak = 0 if normalize else np.iinfo(np.int16).max
    for i in range(num_shifts):
        in_bytes = decode.stdout.read(frame_shift*num_bytes)
        if len(in_bytes) < frame_shift*num_bytes:
            break
        # convert bytes and shape into audio array if multiple channels
        audio[i * frame_shift:(i + 1) * frame_shift, :] = np.frombuffer(in_bytes, dtype=np.int16)\
            .astype(np.float32).reshape((-1, channels))
        if normalize:
            new_peak = np.max(audio[i*frame_shift:(i+1)*frame_shift+1, :])
            if peak < new_peak:
                peak = new_peak

    # normalize (or convert from int range)
    audio = np.divide(audio, peak)
    return audio, sample_rate
