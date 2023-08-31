# based on:
#   SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#   SPDX-License-Identifier: MIT
# but tweaked for RP Pico

import time
import array
import math
import audiocore
import board
import audiobusio

tone_volume = 0.9   # Increase this to increase the volume of the tone.
frequency = 440     # Set this to the Hz of the tone you want to generate.

length = 8000 // frequency
sine_wave = array.array("h", [0] * length)
for i in range(length):
    sine_wave[i] = int((math.sin(math.pi * 2 * i / length)) * tone_volume * (2 ** 15 -1))

# Pico
#
# I2S clock: GP16 = pin x -> "BCK" on board
PIN_BIT_CLOCK = board.GP16

# I2S LR clock (aka WS clock): GP14 = pin x -> "LCK" on board
PIN_WORD_SELECT = board.GP17

# I2S data: GP15 = pin x -> "DIN" on board
PIN_DATA = board.GP18

# NOTE: The board's "SCK" pin must be pulled to ground!

audio = audiobusio.I2SOut(PIN_BIT_CLOCK, PIN_WORD_SELECT, PIN_DATA)


sine_wave_sample = audiocore.RawSample(sine_wave)

print("Running....")
while True:
    print("  boop!")
    audio.play(sine_wave_sample, loop=True)
    time.sleep(1)
    audio.stop()
    time.sleep(1)
