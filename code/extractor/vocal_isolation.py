
from spleeter.separator import Separator
from ..header import workspace

from pydub import AudioSegment
from pydub.effects import normalize

def apply_limiter(input_file, output_file, threshold=0.0):
    audio = AudioSegment.from_file(input_file)
    
    # Apply normalization
    normalized_audio = normalize(audio)

    # Apply compressor to limit the audio
    attack = 5  # Attack time in ms
    release = 100  # Release time in ms
    ratio = 100  # Compression ratio
    knee = 0  # Knee width in dB
   #limited_audio = compress(normalized_audio, ratio=ratio, attack=attack, release=release, threshold=threshold, knee=knee)

    # Export the processed audio file
    normalized_audio.export(output_file, format="wav")


# pip install torch torchaudio musdb
# git clone https://github.com/sigsep/open-unmix-pytorch.git
# cd open-unmix-pytorch
# wget https://zenodo.org/record/3370489/files/umxhq.tar.gz
# tar -xzf umxhq.tar.gz
"""
import os
import torch
import torchaudio
from musdb import DB
from umx import UMX

def separate_vocals(input_file, output_folder):
    separator = UMX('umxhq', niter=4, device='cpu')

    # Load the audio file
    waveform, sample_rate = torchaudio.load(input_file)

    # Perform the separation
    estimates = separator(waveform)

    # Save the vocals track
    vocals_output_file = os.path.join(output_folder, "vocals.wav")
    torchaudio.save(vocals_output_file, estimates['vocals'], sample_rate)
"""


def isolate_vocals(input_file, output_folder):
    # Use the pre-trained 2-stems model (vocals and accompaniment)
    separator = Separator('spleeter:2stems')

    # Perform the separation
    separator.separate_to_file(input_file, output_folder)

if __name__ == "__main__":
    # Define the source file
    source_file = "SVS3015 Autochtone.wav"

    # Create the workspace
    ws = workspace(source_file)

    input_path = ws.config['EXTRACTION']['input_path']
    normalised_path = ws.config['EXTRACTION']['normalised_path']
    vocal_path = ws.config['EXTRACTION']['vocal_path']

    apply_limiter(input_path,normalised_path)
    isolate_vocals(normalised_path, vocal_path)
