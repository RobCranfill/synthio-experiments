# Test outputting stereo audio via a PCM5102 board
# cran, based on:
#   SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#   SPDX-License-Identifier: MIT

import board
import audiocore, audiobusio, audiomixer, synthio

# WAV_FILE_NAME = "M1F1-int16-AFsp.wav"
# WAV_RATE = 8000

WAV_FILE_NAME = "GoWild1.wav"
WAV_RATE = 44100


# Pico
#
# I2S clock: CircuitPython GP16 = Pico pin 21 -> "BCK" on PCM5102 board
PIN_BIT_CLOCK = board.GP16

# I2S LR clock (aka WS clock): GP17 = pin 22 -> "LCK" on board
PIN_WORD_SELECT = board.GP17

# I2S data: GP18 = pin 24 -> "DIN" on board
PIN_DATA = board.GP18

# NOTE: The 5102 board's "SCK" pin must be pulled to ground!

# wav file from https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples.html
wave_file = audiocore.WaveFile(open(WAV_FILE_NAME, "rb"))

audio = audiobusio.I2SOut(PIN_BIT_CLOCK, PIN_WORD_SELECT, PIN_DATA)

# As per https://github.com/todbot/circuitpython-synthio-tricks use a mixer:
_mixer = audiomixer.Mixer(channel_count=2, sample_rate=WAV_RATE, buffer_size=2*1024)
_mixer.voice[0].level = 0  # 10% volume to start seems plenty
_synth = synthio.Synthesizer(channel_count=2, sample_rate=WAV_RATE)

audio.play(_mixer)

def playIt(mixer, level):
    mixer.voice[0].level = level
    print(f"playing at {level}....")
    mixer.voice[0].play(wave_file)
    while mixer.voice[0].playing:
        pass


while True:
    for lvl in (20, 40, 60, 80, 100, 80, 60, 40):
        playIt(_mixer, lvl/100)
    

print("Done!")


# ---- No mixer - not so good.
#
# wave_file = audiocore.WaveFile(open(WAV_FILE_NAME, "rb"))
# wave = audiocore.WaveFile(wave_file)
# mixer = audiomixer.Mixer(voice_count=1, sample_rate=16000, channel_count=2,
#                          bits_per_sample=16, samples_signed=True)
# while True:
#     print("playing....")
#     mixer.voice[0].play(wave_file)
#     while audio.playing:
#         pass

