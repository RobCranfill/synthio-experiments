"""Trying to get a more theremin-y sound.

Pure sine wave, for now.
TODO: morph wavetable as per @todbot? 
TODO: instead of simple ramp for frequency LFO, use an S-like ramp ("sigmoid"?)

References:
    http://www.thereminworld.com/Forums/T/31291/modelling-the-theremin-wave-in-software
    https://paia.com/thereton/

"""

import audiobusio
import audiocore
import audiomixer
import board
import math
import synthio
import time

import ulab.numpy as np


# interferes with the audio?
import supervisor
supervisor.runtime.autoreload = False  # CirPy 8 and above
print(f"supervisor.runtime.autoreload = {supervisor.runtime.autoreload}")


# ---------------- setup
# RP Pico testbed
# PIN_BIT_CLOCK   = board.GP16
# PIN_WORD_SELECT = board.GP17
# PIN_DATA        = board.GP18

# Feather RP2040
PIN_BIT_CLOCK   = board.D9
PIN_WORD_SELECT = board.D10
PIN_DATA        = board.D11


# We need a pretty big buffer to stop I/O noise! Why?
# If we use 2 channels, 32K is insufficient on Feather! 48K is mostly ok, 64K almost entirely :-/
MIXER_BUFFER_SIZE = 32*1024 

SYNTH_SAMPLE_RATE = 22050
WAVE_SAMPLE_SIZE   =  1024
WAVE_SAMPLE_VOLUME = 32767

sine_wave = np.array(
    np.sin(np.linspace(0, 2*np.pi, WAVE_SAMPLE_SIZE, endpoint=False)) * WAVE_SAMPLE_VOLUME, dtype=np.int16)

# FIXME: ramp num could be rather low, for a coarse LFO, right? why not?
RAMP_SAMPLE_SIZE = 100
linear_ramp = np.linspace(0, WAVE_SAMPLE_VOLUME, num=RAMP_SAMPLE_SIZE, dtype=np.int16)

# the 'sigmoid' function
# as per https://stackoverflow.com/a/43024799/981435
#
# all values are in range (-1, 1)
def sigmoid(x_array, full_scale):
    # the basic function, 1 / (1 + np.exp(-x_array)), is range (0,1)
    # 
    return full_scale * (2.0 / (1.0 + np.exp(-x_array)) - 1.0)

print("Generating sigmoids....")
# The range of these is (-1, 1)
sigmoid_ramp_10_f = sigmoid(np.linspace(-10, 10, num=RAMP_SAMPLE_SIZE, dtype=np.float), WAVE_SAMPLE_VOLUME)
sigmoid_ramp_5_f  = sigmoid(np.linspace( -5,  5, num=RAMP_SAMPLE_SIZE, dtype=np.float), WAVE_SAMPLE_VOLUME)
print("Done!")

# Now change to 16-it signed int
sigmoid_ramp_10 = np.array(sigmoid_ramp_10_f, dtype=np.int16)
sigmoid_ramp_5  = np.array(sigmoid_ramp_5_f,  dtype=np.int16)

## for plotting, debugging
# for x in sigmoid_ramp_10:
#     print(x)
# for x in sigmoid_ramp_5:
#     print(x)


audio = audiobusio.I2SOut(PIN_BIT_CLOCK, PIN_WORD_SELECT, PIN_DATA)

# As per https://github.com/todbot/circuitpython-synthio-tricks use a mixer:
_mixer = audiomixer.Mixer(channel_count=1, sample_rate=SYNTH_SAMPLE_RATE, buffer_size=MIXER_BUFFER_SIZE)
_synth = synthio.Synthesizer(channel_count=1, sample_rate=SYNTH_SAMPLE_RATE)

# the audio plays the mixer, and the mixer plays the synth. right? whatev.
audio.play(_mixer)
_mixer.voice[0].level = 0.25 # not too loud
_mixer.voice[0].play(_synth)


# ---------------- end setup


def test_1(synth):

    ## Pick one:
    # lfo_waveform = linear_ramp
    # lfo_waveform = sigmoid_ramp_10
    lfo_waveform = sigmoid_ramp_5

    # Song data:
    # start_note = 65
    # song_notes = (start_note+0, start_note+5, start_note-3) # @todbot's melody
    # song_notes = (60, 63, 65, 60, 63, 66, 65) # smoke on the water?
    song_notes = (60, 67, 72) # C G C
 
    # We create just one Note, and bend it for all our "song notes".
    #
    f1 = synthio.midi_to_hz(song_notes[0])
    lfo = synthio.LFO(waveform=lfo_waveform, once=True, scale=0) # scale=0: no bend to start with
    n = synthio.Note(f1, waveform=sine_wave, bend=lfo)
    synth.press(n)

    while True:
        time.sleep(2)
        for sn in song_notes:
            f2 = synthio.midi_to_hz(sn)
            slide_from_f1_to_f2(n, f1, f2, seconds=0.1)
            f1 = f2
            time.sleep(1)


def slide_from_f1_to_f2(note: synthio.Note, start_freq, target_freq, seconds=1.0):
    """ Create the proper LFO to take us from current to target freq, and trigger it. 
    
    seconds: number of seconds to take to move from start to target (inverse of LFO rate).
    """

    # Get the bend LFO
    lfo = note.bend

    # In order to bend to the target freq, 
    # the lfo 'scale' is the base-2 log of the ratio of the frequencies.
    lfo.scale = math.log(target_freq/start_freq, 2)
    print(f"  slide: {start_freq:.0f} -> {target_freq:.0f} (lfo.scale = {lfo.scale:.2f})")

    # reset the note's freq to the starting freq
    note.frequency = start_freq
    lfo.rate = 1/seconds

    lfo.retrigger()


test_1(_synth)

print("test_theremin_2.py done!")
while True:
    pass
