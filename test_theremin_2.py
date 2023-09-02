"""Trying to get a more theremin-y sound.

Pure sine wave, for now. 
TODO: morph wavetable as per @todbot? 
"""

import audiocore, audiobusio, audiomixer, board, math, synthio, time

import ulab.numpy as np


# interferes with the audio?
import supervisor
supervisor.runtime.autoreload = False  # CirPy 8 and above
print(f"supervisor.runtime.autoreload = {supervisor.runtime.autoreload}")


# ---------------- setup

# my Pico testbed
#
PIN_BIT_CLOCK = board.GP16
PIN_WORD_SELECT = board.GP17
PIN_DATA = board.GP18

SYNTH_SAMPLE_RATE = 22050 # good enuf?
MIXER_BUFFER_SIZE = 2*1024

WAVE_SAMPLE_SIZE   =  1024
WAVE_SAMPLE_VOLUME = 32767

sine_wave = np.array(
    np.sin(np.linspace(0, 2*np.pi, WAVE_SAMPLE_SIZE, endpoint=False)) * WAVE_SAMPLE_VOLUME, 
    dtype=np.int16)
ramp_up = np.linspace(
    -WAVE_SAMPLE_VOLUME, WAVE_SAMPLE_VOLUME, WAVE_SAMPLE_SIZE, endpoint=False, dtype=np.int16)


audio = audiobusio.I2SOut(PIN_BIT_CLOCK, PIN_WORD_SELECT, PIN_DATA)

# As per https://github.com/todbot/circuitpython-synthio-tricks use a mixer:
_mixer = audiomixer.Mixer(channel_count=2, sample_rate=SYNTH_SAMPLE_RATE, buffer_size=MIXER_BUFFER_SIZE)
_synth = synthio.Synthesizer(channel_count=2, sample_rate=SYNTH_SAMPLE_RATE)

# the audio plays the mixer, and the mixer plays the synth. right? whatev.
audio.play(_mixer)
_mixer.voice[0].level = 0.25 # not too loud
_mixer.voice[0].play(_synth)


# ---------------- end setup


def test1(synth):

    # start_note = 65
    # song_notes = (start_note+0, start_note+5, start_note-3) # @todbot's melody

    # song_notes = (60, 63, 65, 60, 63, 66, 65) # smoke on the water
    song_notes = (60, 67, 72) # C G C
 

    # Starting note
    f1 = synthio.midi_to_hz(song_notes[0])

    lfo = synthio.LFO(waveform=ramp_up, once=True, scale=0) # scale=0: hit the initial note only
    n = synthio.Note(f1, waveform=sine_wave, bend=lfo)
    synth.press(n)

    while True:
        time.sleep(1)
        for sn in song_notes:
            f2 = synthio.midi_to_hz(sn)
            slideFromF1toF2(n, f1, f2)
            f1 = f2
            time.sleep(2)


def slideFromF1toF2(note: synthio.Note, startfreq, targetFreq, nSeconds=1.0):
    """ Create the proper LFO to take us from current to target freq, and trigger it. 
    
    nSeconds: number of seconds to take to move from start to target (inverse of LFO rate).
    """

    # Get the bend LFO
    lfo = note.bend

    # lfo 'scale' is just the base-2 log of the ratio of the frequencies.
    lfo.scale = math.log(targetFreq/startfreq, 2)

    lfo.rate = 1/nSeconds
    print(f"  goToNote: {startfreq:.0f} -> {targetFreq:.0f} => lfo.scale {lfo.scale:.2f}")

    note.frequency = startfreq
    lfo.retrigger()


test1(_synth)

print("test_theremin_2.py done!")
while True:
    pass
