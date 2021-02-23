from __future__ import division
import re
import sys              
from google.cloud import speech
import pyaudio
from six.moves import queue
from time import sleep
from audiosocket import *

RATE = 16000
#CHUNK = int(RATE / 10)  # 100ms

def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0

def main():

    # Create a new Audiosocket instance, passing it binding
    audiosocket = Audiosocket(("0.0.0.0", 1121))
    
    audiosocket.prepare_output(outrate=RATE, channels=1, ulaw2lin = True)
    conn = audiosocket.listen()
    

    print('Received connection from {0}'.format(conn.peer_addr))
    print('Connection with {0} over'.format(conn.peer_addr))

    ####################################################################################
    language_code = "es-CO"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    while conn.connected:
        audio_data = conn.read()
        stream = [audio_data]
        requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
        )           
        responses = client.streaming_recognize(streaming_config, requests)
        
        #listen_print_loop(responses)
        
        for response in responses:
            for result in response.results:
                print("Finished: {}".format(result.is_final))
                print("Stability: {}".format(result.stability))
                alternatives = result.alternatives
                for alternative in alternatives:
                    print("Confidence: {}".format(alternative.confidence))
                    print(u"Transcript: {}".format(alternative.transcript))
        

if __name__ == "__main__":
    main()
