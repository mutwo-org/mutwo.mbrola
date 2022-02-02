import os
import random
import unittest

import crepe
import numpy as np
import sox
from scipy.io import wavfile
import voxpopuli

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import mbrola_converters


class EventToPhonemeListTest(unittest.TestCase):
    def setUp(cls):
        cls.converter = mbrola_converters.EventToPhonemeList()

    def test_duration_conversion(self):
        self.assertEqual(
            self.converter.convert(core_events.SimpleEvent(2))[0].duration, 2000
        )
        self.assertEqual(
            self.converter.convert(core_events.SimpleEvent(5))[0].duration, 5000
        )
        self.assertEqual(
            self.converter.convert(core_events.SimpleEvent(0.1))[0].duration, 100
        )

    def test_pitch_conversion(self):
        # One pitch
        self.assertEqual(
            self.converter.convert(music_events.NoteLike("a"))[0].pitch_modifiers,
            [(0, 440), (100, 440)],
        )
        # No pitch
        self.assertEqual(
            self.converter.convert(core_events.SimpleEvent(1))[0].pitch_modifiers,
            [],
        )
        # Pitch with envelope
        pitch = music_parameters.WesternPitch("a")
        pitch.envelope = [
            [0, music_parameters.DirectPitchInterval(-1200)],
            [1, music_parameters.DirectPitchInterval(1200)],
        ]
        self.assertEqual(
            self.converter.convert(music_events.NoteLike(pitch))[0].pitch_modifiers,
            [(0, 220), (100, 879)],
        )

    def test_phoneme_conversion(self):
        # No phoneme
        self.assertEqual(
            self.converter.convert(core_events.SimpleEvent(1))[0].name, "_"
        )
        # With phoneme
        simple_event = core_events.SimpleEvent(1)
        # monkeypatch
        simple_event.phoneme = "a"  # type: ignore
        self.assertEqual(self.converter.convert(simple_event)[0].name, "a")

    def test_nested_conversion(self):
        simple_event0 = core_events.SimpleEvent(1)
        simple_event1 = core_events.SimpleEvent(0.5)
        # Monkey patch simple events
        simple_event0.phoneme = "R"  # type: ignore
        simple_event1.phoneme = "@"  # type: ignore
        simple_event1.pitch_list = [music_parameters.WesternPitch("a")]  # type: ignore
        sequential_event = core_events.SequentialEvent(
            [simple_event0, simple_event1, simple_event0]
        )

        phoneme0 = voxpopuli.Phoneme("R", 1000)
        phoneme1 = voxpopuli.Phoneme("@", 500, [(0, 440), (100, 440)])
        expected_phoneme_list = voxpopuli.PhonemeList([phoneme0, phoneme1, phoneme0])

        result_phoneme_list = self.converter.convert(sequential_event)

        self.assertEqual(type(result_phoneme_list), type(expected_phoneme_list))

        for phoneme_result, phoneme_expected in zip(
            result_phoneme_list, expected_phoneme_list
        ):
            self.assertEqual(phoneme_result.name, phoneme_expected.name)
            self.assertEqual(phoneme_result.duration, phoneme_expected.duration)
            self.assertEqual(
                phoneme_result.pitch_modifiers, phoneme_expected.pitch_modifiers
            )


class EventToSpeakSynthesisTest(unittest.TestCase):
    test_file_name = "tests/converters/test_soundfile.wav"

    @classmethod
    def _clean_up(cls):
        try:
            os.remove(cls.test_file_name)
        # If the file doesn't exist it is already cleaned up
        except FileNotFoundError:
            pass

    def setUp(cls):
        cls.converter = mbrola_converters.EventToSpeakSynthesis()

    def tearDown(self):
        self._clean_up()

    def test_render_happens(self):
        """Checks if the converter creates a soundfile

        The test is very simple and only checks if the
        converter successfully creates a soundfile.
        """

        test_event = music_events.NoteLike("c", 2)
        # We monkey patch our NoteLike
        test_event.phoneme = "@"  # type: ignore

        # Ensure the file doesn't exist yet
        self.assertTrue(not os.path.exists(self.test_file_name))

        self.converter.convert(test_event, self.test_file_name)

        # Ensure the file exists now
        self.assertTrue(os.path.exists(self.test_file_name))

        self._clean_up()

    def test_render_with_correct_duration(self):
        """Test if the rendered sound files have the expected duration"""

        test_event0 = music_events.NoteLike("c", 1.25)
        test_event1 = music_events.NoteLike([], 0.75)  # no pitch for consonant
        test_event2 = music_events.NoteLike([], 1.35)  # should be rest

        test_event0.phoneme = "@"  # type: ignore
        test_event1.phoneme = "u"  # type: ignore
        # test_event2 should be a rest

        sequential_event = core_events.SequentialEvent([])

        random.seed(100)
        for _ in range(10000):
            sequential_event.append(
                random.choice((test_event0, test_event1, test_event2))
            )

        self.converter.convert(sequential_event, self.test_file_name)

        # Mbrola isn't 100% precise, but it is still pretty good.
        # It also seems like it doesn't matter how long the
        # created sound file is, the imprecision keeps in a similar
        # range.
        self.assertAlmostEqual(
            sox.file_info.duration(self.test_file_name),  # type: ignore
            sequential_event.duration,  # type: ignore
            places=2,
        )

        self._clean_up()

    def test_render_with_correct_pitch(self):
        """Test if the rendered sound file has the correct pitch"""

        test_event = music_events.NoteLike("1/1", 2)
        test_event.phoneme = "a"  # type: ignore
        self.converter.convert(test_event, self.test_file_name)

        sampling_rate, audio = wavfile.read(self.test_file_name)

        _, frequency_array, confidence_array, _ = crepe.predict(audio, sampling_rate)

        filtered_frequency_array = tuple(
            frequency
            for frequency, confidence in zip(frequency_array, confidence_array)
            if confidence > 0.8
        )

        frequency = float(np.median(filtered_frequency_array))
        # We have a 16 cents tolerance
        #   - the prediction is not 100% precise
        #   - there are fluctuations in the signal which don't affect the
        #     main audible frequency but the resulting analysis data
        print(
            abs(
                music_parameters.abc.Pitch.hertz_to_cents(
                    frequency, test_event.pitch_list[0].frequency
                )
            )
        )
        self.assertTrue(
            abs(
                music_parameters.abc.Pitch.hertz_to_cents(
                    frequency, test_event.pitch_list[0].frequency
                )
            )
            < 16
        )

        self._clean_up()


if __name__ == "__main__":
    unittest.main()
