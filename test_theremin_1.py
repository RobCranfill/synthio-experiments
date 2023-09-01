# Test outputting stereo audio via a PCM5102 board
# cran, based on:
#   SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#   SPDX-License-Identifier: MIT

import board
import audiocore, audiobusio, audiomixer, synthio
import time

import ulab.numpy as np


# interferes with the audio?
import supervisor
supervisor.runtime.autoreload = False  # CirPy 8 and above
print(f"supervisor.runtime.autoreload = {supervisor.runtime.autoreload}")

# my Pico testbed
#
PIN_BIT_CLOCK = board.GP16
PIN_WORD_SELECT = board.GP17
PIN_DATA = board.GP18

SAMPLE_RATE = 22050 # good enuf?
BUFFER_SIZE = 2*1024

SAMPLE_SIZE   =  1024
SAMPLE_VOLUME = 32767
wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)


audio = audiobusio.I2SOut(PIN_BIT_CLOCK, PIN_WORD_SELECT, PIN_DATA)

# As per https://github.com/todbot/circuitpython-synthio-tricks use a mixer:
_mixer = audiomixer.Mixer(channel_count=2, sample_rate=SAMPLE_RATE, buffer_size=BUFFER_SIZE)
_synth = synthio.Synthesizer(channel_count=2, sample_rate=SAMPLE_RATE)

# the audio plays the mixer, and the mixer plays the synth. right? whatev.
audio.play(_mixer)
_mixer.voice[0].level = 0.1 # just in case
_mixer.voice[0].play(_synth)


def makeSine3(synth):

    pitchBend = synthio.LFO(rate=0.5, scale=1.0)  # rate 0.5 Hz so the lfo cycles at 2 per second

    synth_note = synthio.Note(200, waveform=wave_sine, bend=pitchBend)
    synth.press(synth_note)

    while True:
        print("cycling....")
        time.sleep(6.66)
        pitchBend.retrigger()



def makeSine2(synth):
    """
    create a sine single-cycle waveform to act as oscillators.
    
    https://github.com/todbot/circuitpython-synthio-tricks#making-your-own-waves
    """
    SAMPLE_SIZE   =   512
    SAMPLE_VOLUME = 32000  # 0-32767
    wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)

    little_sleep = 0.0
    pitch_increment = 0.1

    synth_note = synthio.Note(20, waveform=wave_sine)
    synth.press(synth_note)

    # with a sleep of 0.05 second you can hear the stair-step of the freqeuncy sweep. don't want that.
    # if you don't have any kind of call to sleep (not even sleep(0)), you get a crazy effect!
    
    little_sleep = 0.01
    
    # sweep thru audio range
    while True:
        f = 20.0
        while f < 20000:
            synth_note.frequency = f
            f *= 1.05
            time.sleep(little_sleep)


def makeSine1(synth):
    """
    create a sine single-cycle waveform to act as oscillators.
    
    https://github.com/todbot/circuitpython-synthio-tricks#making-your-own-waves
    """
    SAMPLE_SIZE   =   512
    SAMPLE_VOLUME = 32000  # 0-32767
    wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)

    little_sleep = 0.0
    pitch_increment = 0.1

    synth_note = synthio.Note(20, waveform=wave_sine)
    synth.press(synth_note)

    # works fine
    while True:
        # time.sleep(little_sleep)
        synth_note.frequency += pitch_increment


def makeWaves(synth):
    """
    create sine & sawtooth single-cycle waveforms to act as oscillators.
    
    https://github.com/todbot/circuitpython-synthio-tricks#making-your-own-waves
    """
    SAMPLE_SIZE = 512
    SAMPLE_VOLUME = 32000  # 0-32767
    wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)
    wave_saw = np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)

    midi_note = 65
    my_wave = wave_saw
    while True:
        # create notes using those waveforms
        note1 = synthio.Note(synthio.midi_to_hz(midi_note), waveform=my_wave)
        note2 = synthio.Note(synthio.midi_to_hz(midi_note-7), waveform=my_wave)
        synth.press(note1)
        time.sleep(0.5)
        synth.press(note2)
        time.sleep(1)
        synth.release((note1,note2))
        time.sleep(0.1)
        my_wave = wave_sine if my_wave is wave_saw else wave_saw  # toggle waveform


def beep(synth):
    """super simple sound test"""
    synth.press(65) # midi note 65 = F4
    time.sleep(0.5)
    synth.release(65) # release the note we pressed
    time.sleep(0.5)


makeSine3(_synth)
# makeSine2(_synth)
# makeSine1(_synth)
# makeWaves(_synth)

# while True:
#     for lvl in (5, 10, 20, 40, 60, 80, 100, 80, 60, 40):
#         print(f"Level {lvl}%")
#         _mixer.voice[0].level = level = lvl/100
#         beep(_synth)

print("test_theremin_1.py done!")
while True:
    pass
