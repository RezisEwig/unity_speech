#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division
from __future__ import unicode_literals, print_function

# GCP 에서 사용하는 요소들 시작

import re
import sys

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

# GCP 에서 사용하는 요소들 끝

# Snips NLU 에서 사용하는 요소들 시작

import io
import json
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_KO
import pyautogui

# Snips NLU 에서 사용하는 요소들 끝

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms



class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


# 음성인식이 계속 돌아가는 루프

def listen_print_loop(responses, nlu_engine):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            
            # 한문장이 끝나면 Snips NLU로 넘겨줌
            running(transcript, nlu_engine)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            # 밑에 적힌 키워드 말하면 프로그램 종료
            if re.search(r'\b(종료|그만)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0

# Snips NLU 동작 시작
def running(input, nlu_engine):
    parsing = nlu_engine.parse(input)
        
    print(parsing)
        
    try:
        if (parsing['intent']['intentName'] == "turnLightOn"):
            if (parsing['slots'][0]['rawValue'] == "부엌"):
                #print("kitchen lights on")
                pyautogui.keyUp('1')
                pyautogui.keyDown('1')
            
            if (parsing['slots'][0]['rawValue'] == "거실"):
                #print("living room lights on")
                pyautogui.keyUp('2')
                pyautogui.keyDown('2')
                
            if (parsing['slots'][0]['rawValue'] == "손님방"):
                #print("guest room lights on")
                pyautogui.keyUp('3')
                pyautogui.keyDown('3')
                
            if (parsing['slots'][0]['rawValue'] == "내 방"):
                #print("my room lights on")
                pyautogui.keyUp('4')
                pyautogui.keyDown('4')

            if (parsing['slots'][0]['rawValue'] == "안방"):
                #print("bedroom lights on")
                pyautogui.keyUp('5')
                pyautogui.keyDown('5')

            if (parsing['slots'][0]['rawValue'] == "화장실"):
                #print("washroom lights on")
                pyautogui.keyUp('6')
                pyautogui.keyDown('6')

            if ((parsing['slots'][0]['rawValue'] == "전부") or (parsing['slots'][0]['rawValue'] == "전체")):
                #print("all lights on")
                pyautogui.keyUp('1')
                pyautogui.keyDown('1')
                pyautogui.keyUp('2')
                pyautogui.keyDown('2')
                pyautogui.keyUp('3')
                pyautogui.keyDown('3')
                pyautogui.keyUp('4')
                pyautogui.keyDown('4')
                pyautogui.keyUp('5')
                pyautogui.keyDown('5')
                pyautogui.keyUp('6')
                pyautogui.keyDown('6')

        if (parsing['intent']['intentName'] == "turnLightOff"):
            if (parsing['slots'][0]['rawValue'] == "부엌" or parsing['slots'][0]['rawValue'] == "부억"):
                # print("kitchen lights off")
                pyautogui.keyUp('q')
                pyautogui.keyDown('q')

            if (parsing['slots'][0]['rawValue'] == "거실"):
                # print("living room lights off")
                pyautogui.keyUp('w')
                pyautogui.keyDown('w')

            if (parsing['slots'][0]['rawValue'] == "손님방"):
                # print("guest room lights off")
                pyautogui.keyUp('e')
                pyautogui.keyDown('e')

            if ((parsing['slots'][0]['rawValue'] == "내 방") or (parsing['slots'][0]['rawValue'] == "내방")):
                # print("my room lights off")
                pyautogui.keyUp('r')
                pyautogui.keyDown('r')

            if (parsing['slots'][0]['rawValue'] == "안방"):
                # print("bedroom lights off")
                pyautogui.keyUp('t')
                pyautogui.keyDown('t')

            if (parsing['slots'][0]['rawValue'] == "화장실"):
                # print("washroom lights off")
                pyautogui.keyUp('y')
                pyautogui.keyDown('y')

            if (parsing['slots'][0]['rawValue'] == "전부" or (parsing['slots'][0]['rawValue'] == "전체")):
                #print("all lights on")
                pyautogui.keyUp('q')
                pyautogui.keyDown('q')
                pyautogui.keyUp('w')
                pyautogui.keyDown('w')
                pyautogui.keyUp('e')
                pyautogui.keyDown('e')
                pyautogui.keyUp('r')
                pyautogui.keyDown('r')
                pyautogui.keyUp('t')
                pyautogui.keyDown('t')
                pyautogui.keyUp('y')
                pyautogui.keyDown('y')
                    
    except Exception as ex:
        print()
            
            
            
def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    # 언어 설정코드 변경 가능
    language_code = 'ko-KR'  # a BCP-47 language tag
    
    # 언어 데이터셋을 Snips NLU에 넣어주기
    with io.open("./lights_dataset_train_ko.json", encoding="utf8") as f:
        sample_dataset = json.load(f)
        
    nlu_engine = SnipsNLUEngine(config=CONFIG_KO)
    nlu_engine = nlu_engine.fit(sample_dataset)
        
    print("성공")
    
    # 전처리 종료
    
    # 음성인식 시작

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        # 무한루프 시작
        listen_print_loop(responses, nlu_engine)


if __name__ == '__main__':
    main()
# [END speech_transcribe_streaming_mic]
