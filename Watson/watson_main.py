from ibm_watson import SpeechToTextV1
from ibm_watson import LanguageTranslatorV3
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import keys
# import pydub
# import pydub.playback
import wave
import pyaudio


def run_translator():
    """ Call the functions that interact with Watson services"""
    # Step 1: Prompt for then record English speech into an audio file
    input('Press Enter then ask your question in English')
    record_audio('english.wav')

    # Step 2: Transcribe the English speech to English text
    english = speech_to_text(file_name='english.wav', model_id='en-US_BroadbandModel')
    print('English: ', english)

    # Step 3: Translate the English text into Spanish text
    spanish = translate(text_to_translate=english, model='en-es')
    print('Spanish: ', spanish)

    # Step 4: Synthesize the Spanish text into Spanish speech
    text_to_speech(text_to_speak=spanish, voice_to_use='es-US_SofiaVoice', file_name='spanish.wav')

    # # Step 5: Play the Spanish audio file
    # play_audio(file_name='spanish.wav')

    # Step 6: Prompt for then record Spanish speech into an audio file
    input('Press Enter then speak the Spanish answer')
    record_audio('spanish_response.wav')

    # Step 7: Transcribe the Spanish text into English text
    spanish = speech_to_text(file_name='spanish_response.wav', model_id='es-ES_BroadbandModel')
    print('Spanish response: ', spanish)

    # Step 8: Translate the Spanish text into English text
    english = translate(text_to_translate=spanish, model='es-en')
    print('English response: ', english)

    # Step 9: Synthesize the English text into English speech
    text_to_speech(text_to_speak=english, voice_to_use='en-US_AllisonVoice', file_name='english_response.wav')

    # # Step 10: Play the English audio file
    # play_audio(file_name='english_response.wav')


def speech_to_text(file_name, model_id):
    """Use Watson Speech to Text to convert audio file to text"""
    # Create Watson Speech to Text client
    sst_auth = IAMAuthenticator(keys.speech_to_text_key)
    stt = SpeechToTextV1(authenticator=sst_auth)

    # Open the audio file
    with open(file_name, 'rb') as audio_file:
        # Pass the file to Watson for transcription
        result = stt.recognize(audio=audio_file, content_type='audio/wav', model=model_id).get_result()

    # Get the 'results' list. This may contain intermediate and final
    # results, depending on method recognize's arguments. We asked
    # for only final results, so this list contains one element.
    results_list = result['results']

    # Get the final speech recognition result--the list's only element
    speech_recognition_result = results_list[0]

    # Get the 'alternatives' list. This may contain multiple alternative
    # transcriptions, depending on method recognize's arguments. We did
    # not ask for alternatives, so this list contains one element.
    alternatives_list = speech_recognition_result['alternatives']

    # Get the only alternative transcription from alternatives list.
    first_alternative = alternatives_list[0]

    # Get the transcript key's value, which contains the audio's
    # text transcription
    transcript = first_alternative['transcript']

    return transcript


def translate(text_to_translate, model):
    """Use Watson Language Translator to translate English to Spanish (en-es)
     or Spanish to English (es-en) as specified by model"""

    translate_auth = IAMAuthenticator(keys.translate_key)
    language_translator = LanguageTranslatorV3(version='2018-05-01', authenticator=translate_auth)

    # Perform the translation
    translated_text = language_translator.translate(text=text_to_translate, model_id=model).get_result()

    # Get 'translations' list. If method translate's text argument has
    # multiple strings, the list will have multiple entries.
    # We passed one string, so the list contains only one element.
    translation_list = translated_text['translations']

    # Get translations list's only element
    first_translation = translation_list[0]

    # Get 'translation' key's value, which is the translated text
    translation = first_translation['translation']

    return translation


def text_to_speech(text_to_speak, voice_to_use, file_name):
    """ Use Watson Text to Speech to convert text to specified voice
    and save to a WAV file"""
    # create Text to Speech client
    tts_auth = IAMAuthenticator(keys.text_to_speech_key)
    tts = TextToSpeechV1(authenticator=tts_auth)

    # Open file and write the synthesized audio content into the file
    with open(file_name, 'wb') as audio_file:
        audio_file.write(tts.synthesize(text_to_speak, accept='audio/wav', voice=voice_to_use).get_result().content)


def record_audio(file_name):
    """ Use pyaudio to record 5 seconds of audio to a WAV file"""
    FRAME_RATE = 44100
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    SECONDS = 5

    recorder = pyaudio.PyAudio()

    # Configure and open audio stream for recording (input=True)
    audio_stream = recorder.open(format=FORMAT, channels=CHANNELS, rate=FRAME_RATE, input=True,
                                 frames_per_buffer=CHUNK)
    audio_frames = []
    print('Recording 5 seconds of audio')

    # read 5 seconds of audio in CHUNK-size pieces
    for i in range(0, int(FRAME_RATE * SECONDS / CHUNK)):
        audio_frames.append(audio_stream.read(CHUNK))

    print('Recording complete')
    audio_stream.stop_stream()
    audio_stream.close()
    recorder.terminate()

    with wave.open(file_name, 'wb') as output_file:
        output_file.setnchannels(CHANNELS)
        output_file.setsampwidth(recorder.get_sample_size(FORMAT))
        output_file.setframerate(FRAME_RATE)
        output_file.writeframes(b''.join(audio_frames))


# def play_audio(file_name):
#     """ Use the pydub module (pip install pydub) to play a WAV file"""
#     sound = pydub.AudioSegment.from_wav(file_name)
#     pydub.playback.play(sound)


if __name__ == '__main__':
    run_translator()
