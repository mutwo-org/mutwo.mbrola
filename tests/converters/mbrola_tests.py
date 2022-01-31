import unittest

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
            [(0, 440)],
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
        phoneme1 = voxpopuli.Phoneme("@", 500, [(0, 440)])
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


if __name__ == "__main__":
    unittest.main()
