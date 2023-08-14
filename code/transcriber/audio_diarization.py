import sys
import os
from ..header import workspace
from ..tokens import HUGGING_FACE_TOKEN
from lib.pyannote_audio.pyannote.audio import Pipeline
import numpy as np

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                    use_auth_token=HUGGING_FACE_TOKEN)

def diarization_task(ws):
    audio_file = ws.config['TRANSCRIPTION']['combined_audio_path']

    # 4. apply pretrained pipeline
    diarization = pipeline(audio_file)

    #np.save('diarization.npy', diarization, dtype=object)

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")


if __name__ == '__main__':
    source_file = "tst00.wav"

    ws = workspace(source_file)

    diarization_task(ws)

