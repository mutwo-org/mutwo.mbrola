"""Convert :class:`voxpopuli.PhonemeList` to mutwo events.

"""

import typing
import warnings

import voxpopuli

from mutwo import core_constants
from mutwo import core_converters
from mutwo import core_events
from mutwo import music_converters
from mutwo import music_parameters

__all__ = (
    "EventToPhonemeList",
    "EventToSpeakSynthesis",
    "SimpleEventToPitch",
    "SimpleEventToPhonemeString",
)


class SimpleEventToPhonemeString(core_converters.SimpleEventToAttribute):
    """Convert a simple event to a phoneme string."""

    def __init__(self, attribute_name: str = "phoneme", exception_value: str = "_"):
        super().__init__(attribute_name, exception_value)


class SimpleEventToPitch(music_converters.SimpleEventToPitchList):
    """Convert a simple event to a pitch."""

    def convert(self, *args, **kwargs) -> typing.Optional[music_parameters.abc.Pitch]:
        pitch_list = super().convert(*args, **kwargs)
        n_pitches = len(pitch_list)
        if not n_pitches:
            return None
        elif n_pitches > 1:
            warnings.warn(
                "mutwo.music_converters.SimpleEventToPitch: "
                f"Found pitch list with {n_pitches} pitches. "
                f"Only the first pitch will be used: {pitch_list[0]}. "
                "All remaining pitches will be ignored.",
                RuntimeWarning,
            )
        return pitch_list[0]


class EventToPhonemeList(core_converters.abc.EventConverter):
    """Convert mutwo event to :class:`voxpopuli.PhonemeList`.

    :param simple_event_to_pitch: Function or converter which receives
        a :class:`mutwo.core_events.SimpleEvent` as an input and has to
        return a :class`mutwo.music_parameters.abc.Pitch` or `None`.
    :type simple_event_to_pitch: typing.Callable[[core_events.SimpleEvent], typing.Optional[music_parameters.abc.Pitch]]
    :param simple_event_to_phoneme_string: Function or converter which receives
        a :class:`mutwo.core_events.SimpleEvent` as an input and has to
        return a string which belongs to the phonetic alphabet SAMPA.
    :type simple_event_to_phoneme_string: typing.Callable[[core_events.SimpleEvent], str]

    **Warning:**

    This converter assumes that the duration attribute of the input
    event is in seconds. It multiplies the input duration by a factor
    of 1000 and parses it to the `voxpopuli.Phoneme` object which expects duration in milliseconds. It is the responsibility of the user
    to ensure that the duration has the right format.
    """

    def __init__(
        self,
        simple_event_to_pitch: typing.Callable[
            [core_events.SimpleEvent], typing.Optional[music_parameters.abc.Pitch]
        ] = SimpleEventToPitch(),
        simple_event_to_phoneme_string: typing.Callable[
            [core_events.SimpleEvent], str
        ] = SimpleEventToPhonemeString(),
    ):
        self._simple_event_to_pitch = simple_event_to_pitch
        self._simple_event_to_phoneme_string = simple_event_to_phoneme_string

    def _pitch_to_pitch_modification_list(
        self, pitch: typing.Optional[music_parameters.abc.Pitch]
    ) -> list[tuple[int, int]]:
        pitch_modification_list = []
        if pitch:
            pitch_envelope = pitch.resolve_envelope(100)
            for (pitch, time,) in zip(
                pitch_envelope.parameter_tuple, pitch_envelope.absolute_time_tuple
            ):
                pitch_modification_list.append(
                    (int(time), int(pitch.frequency))  # type: ignore
                )
            # We have to add a second value to ensure the pitch keeps
            # constant.
            if len(pitch_modification_list) == 1:
                pitch_modification_list.append((100, pitch_modification_list[0][-1]))
        return pitch_modification_list

    def _convert_simple_event(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        _: core_constants.DurationType,
    ) -> tuple[voxpopuli.Phoneme]:
        pitch = self._simple_event_to_pitch(simple_event_to_convert)
        phoneme_string = self._simple_event_to_phoneme_string(simple_event_to_convert)
        pitch_modification_list = self._pitch_to_pitch_modification_list(pitch)
        # From seconds to milliseconds (the converter assumes
        # that the input duration is in seconds!)
        duration = int(simple_event_to_convert.duration * 1000)
        phoneme = voxpopuli.Phoneme(phoneme_string, duration, pitch_modification_list)
        return (phoneme,)

    def convert(self, event_to_convert: core_events.abc.Event) -> voxpopuli.PhonemeList:
        converted_event = self._convert_event(event_to_convert, 0)
        return voxpopuli.PhonemeList(converted_event)


class EventToSpeakSynthesis(core_converters.abc.Converter):
    """Render event to soundfile with speak synthesis engine mbrola.

    :param voice: The voice object which is responsible in rendering the
        soundfile.
    :type voice: voxpopuli.Voice
    :param event_to_phoneme_list: A converter or function which transforms
        an event to a :class:`voxpopuli.PhonemeList`. By default this is a
        :class:`mutwo.mbrola_converters.EventToPhonemeList` object..
    :type event_to_phoneme_list: typing.Callable[[core_events.abc.Event], voxpopuli.PhonemeList]

    **Warning:**

    You need to install the non-python dependencies for `voxpopuli`, otherwise
    the converter won't work.
    """

    def __init__(
        self,
        voice: voxpopuli.Voice = voxpopuli.Voice(),
        event_to_phoneme_list: typing.Callable[
            [core_events.abc.Event], voxpopuli.PhonemeList
        ] = EventToPhonemeList(),
    ):
        self._event_to_phoneme_list = event_to_phoneme_list
        self._voice = voice

    def convert(self, event_to_convert: core_events.abc.Event, sound_file_name: str):
        phoneme_list = self._event_to_phoneme_list(event_to_convert)
        self._voice.to_audio(phoneme_list, sound_file_name)
