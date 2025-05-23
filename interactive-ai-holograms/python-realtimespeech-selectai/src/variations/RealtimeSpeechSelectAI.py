import asyncio
import getpass
import os
import json
import pyaudio
import oracledb
from datetime import datetime
import oci
from oci.config import from_file
from oci.auth.signers.security_token_signer import SecurityTokenSigner
from oci.ai_speech_realtime import (
    RealtimeClient,
    RealtimeClientListener,
    RealtimeParameters,
)
from aiohttp import web

latest_thetime = None
latest_question = None
latest_answer = None
compartment_id = os.getenv('COMPARTMENT_ID')
print(f"compartment_id: {compartment_id}")

connection = oracledb.connect(
    user="moviestream",
    password="Welcome12345",
    dsn="selectaidb_high",
    config_dir=r"C:\Users\paulp\Downloads\Wallet_SelectAIDB",
    wallet_location=r"C:\Users\paulp\Downloads\Wallet_SelectAIDB",
    wallet_password="Welcome12345"
)
print(f"Successfully connected to Oracle Database Connection: {connection}")

queue = asyncio.Queue()

SAMPLE_RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
BUFFER_DURATION_MS = 96
FRAMES_PER_BUFFER = int(SAMPLE_RATE * BUFFER_DURATION_MS / 1000)

cummulativeResult = ""
isSelect = False
last_result_time = None

def audio_callback(in_data, frame_count, time_info, status):
    queue.put_nowait(in_data)
    return (None, pyaudio.paContinue)

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER,
    stream_callback=audio_callback,
)

stream.start_stream()
config = from_file()
isInsertResults = True

async def send_audio(client):
    while True:
        data = await queue.get()
        await client.send_data(data)

class SpeechListener(RealtimeClientListener):
    def on_result(self, result):
        global cummulativeResult, isSelect, last_result_time
        if result["transcriptions"][0]["isFinal"]:
            transcription = result['transcriptions'][0]['transcription']
            cummulativeResult += transcription
            print(f"Received final results: {transcription}")
            print(f"Current cummulative result: {cummulativeResult}")
            if cummulativeResult.lower().startswith("hey db"):
                cummulativeResult = cummulativeResult[len("hey db"):].strip()
                isSelect = True
            elif cummulativeResult.lower().startswith("hey deebee"):
                cummulativeResult = cummulativeResult[len("hey deebee"):].strip()
                isSelect = True
            elif cummulativeResult.lower().startswith("they deebee"):
                cummulativeResult = cummulativeResult[len("they deebee"):].strip()
                isSelect = True
            elif cummulativeResult.lower().startswith("adb"):
                cummulativeResult = cummulativeResult[len("adb"):].strip()
                isSelect = True
            elif cummulativeResult.lower().startswith("a db"):
                cummulativeResult = cummulativeResult[len("a db"):].strip()
                isSelect = True
            else:
                cummulativeResult = ""
            last_result_time = asyncio.get_event_loop().time()
        else:
            print(f"Received partial results: {result['transcriptions'][0]['transcription']}")

    def on_ack_message(self, ackmessage):
        return super().on_ack_message(ackmessage)

    def on_connect(self):
        return super().on_connect()

    def on_connect_message(self, connectmessage):
        print(f"connectmessage: {connectmessage}")
        return super().on_connect_message(connectmessage)

    def on_network_event(self, ackmessage):
        return super().on_network_event(ackmessage)

    def on_error(self, exception):
        print(f"An error occurred: {exception}")

async def check_idle():
    global last_result_time, isSelect
    while True:
        if isSelect and last_result_time and (asyncio.get_event_loop().time() - last_result_time > 2):
            executeSelectAI()
            isSelect = False
        await asyncio.sleep(1)

def executeSelectAI():
    global cummulativeResult, isInsertResults, latest_thetime, latest_question, latest_answer
    print(f"executeSelectAI called cummulative result: {cummulativeResult}")

    contains_logic = [
        {"containsWord": "reset", "latestQuestion": "reset", "latestAnswer": "reset"},
        {"containsWord": "selectai", "latestQuestion": "selectai", "latestAnswer": "selectai"},
        {"containsWord": "multicloud", "latestQuestion": "multicloud", "latestAnswer": "multicloud"},
        {"containsWord": "multi-cloud", "latestQuestion": "multicloud", "latestAnswer": "multicloud"},
        {"containsWord": "vector", "latestQuestion": "vector", "latestAnswer": "vector"},
        {"containsWord": "apex", "latestQuestion": "apex", "latestAnswer": "apex"},
        {"containsWord": "dev", "latestQuestion": "dev", "latestAnswer": "dev"},
        {"containsWord": "development", "latestQuestion": "dev", "latestAnswer": "dev"},
        {"containsWord": "multitenant", "latestQuestion": "multitenant", "latestAnswer": "multitenant"},
        {"containsWord": "security", "latestQuestion": "security", "latestAnswer": "security"},
        {"containsWord": "goldengate", "latestQuestion": "goldengate", "latestAnswer": "goldengate"},
        {"containsWord": "exadata", "latestQuestion": "exadata", "latestAnswer": "exadata"},
        {"containsWord": "sharding", "latestQuestion": "sharding", "latestAnswer": "sharding"},
        {"containsWord": "maa", "latestQuestion": "maa", "latestAnswer": "maa"},
        {"containsWord": "23ai", "latestQuestion": "23ai", "latestAnswer": "23ai"},
        {"containsWord": "spatial", "latestQuestion": "spatial", "latestAnswer": "spatial"},
        {"containsWord": "performance", "latestQuestion": "performance", "latestAnswer": "performance"},
        {"containsWord": "upgrade", "latestQuestion": "upgrade", "latestAnswer": "upgrade"},
        {"containsWord": "holograms", "latestQuestion": "holograms", "latestAnswer": "holograms"},
        {"containsWord": "stickers", "latestQuestion": "stickers", "latestAnswer": "stickers"},
        {"containsWord": "swag", "latestQuestion": "swag", "latestAnswer": "swag"}
    ]

    # BEGIN
    # DBMS_CLOUD_AI.CREATE_PROFILE(
    #     profile_name= > 'OCWPODS_PROFILE',
    # attributes = >
    # '{"provider": "openai",
    # "credential_name": "OPENAI_CRED",
    # "model": "gpt-4",
    # "object_list": [{"owner": "MOVIESTREAM", "name": "OCWPODS"}]}'
    # );
    # END;
    # /

    # https: // blogs.oracle.com / datawarehousing / post / how - to - help - ai - models - generate - better - natural - language - queries - in -autonomous - database
    # COMMENT ON TABLE OCWPODS IS 'Contains pod short name, products, title, abstract, pod name, points of contact, location, and other keywords';
    # COMMENT ON COLUMN OCWPODS.PODSHORTNAME IS 'the short name of the pod';
    # COMMENT ON COLUMN OCWPODS.PRODUCTS IS 'abstract describing the pod';
    # COMMENT ON COLUMN OCWPODS.TITLE IS 'the title the pod';
    # COMMENT ON COLUMN OCWPODS.ABSTRACT IS 'abstract describing the pod';
    # COMMENT ON COLUMN OCWPODS.PODNAME IS 'the name of the pod';
    # COMMENT ON COLUMN OCWPODS.POCS IS 'the people at the pod';
    # COMMENT ON COLUMN OCWPODS.LOCATION IS 'the location of the pod';
    # COMMENT ON COLUMN OCWPODS.OTHERKEYWORDS IS 'other keywords describing the pod that can be searched on';

    # profile_name => 'openai_gpt35',
    promptSuffix = " . In a single word, tell me  the most appropriate PODSHORTNAME"
    # promptSuffix = ""
    query = """SELECT DBMS_CLOUD_AI.GENERATE(
                prompt       => :prompt || :promptSuffix,
                profile_name => 'OCWPODS_PROFILE', 
                action       => 'narrate')
            FROM dual"""

    try:
        with connection.cursor() as cursor:
            try:
                if handleContainsLogic(cummulativeResult.lower(), contains_logic):
                    print(f"executeSelectAI handled directly with cummulative result: {cummulativeResult}")
                else:
                    cursor.execute(query, {'prompt': cummulativeResult, 'promptSuffix': promptSuffix})
                    result = cursor.fetchone()
                    if result and isinstance(result[0], oracledb.LOB):
                        text_result = result[0].read()
                        print(text_result)

                        latest_thetime = datetime.now()
                        latest_question = cummulativeResult
                        latest_answer = text_result[:3000]
                    else:
                        print(result)
            except Exception as query_error:
                print(f"An error occurred during query execution: {query_error}")
                latest_thetime = datetime.now()
                latest_question = "default"
                latest_answer = "default"

            cummulativeResult = ""

            if isInsertResults:
                insert_query = """
                INSERT INTO selectai_data (thetime, question, answer)
                VALUES (:thetime, :question, :answer)
                """
                cursor.execute(insert_query, {
                    'thetime': latest_thetime,
                    'question': latest_question,
                    'answer': latest_answer
                })
                connection.commit()
                print("Insert successful.")

    except Exception as e:
        print(f"An error occurred: {e}")

    cummulativeResult = ""

def handleContainsLogic(cummulative_result, logic_array):
    global latest_thetime, latest_question, latest_answer

    for item in logic_array:
        if item["containsWord"] in cummulative_result:
            latest_thetime = datetime.now()
            latest_question = item["latestQuestion"]
            latest_answer = item["latestAnswer"]
            # print("item containsWord: " + item["containsWord"])
            return True
    return False

async def handle_request(request):
    global latest_thetime, latest_question, latest_answer
    data = {
        "thetime": latest_thetime.isoformat() if latest_thetime else None,
        "question": latest_question,
        "answer": latest_answer
    }
    return web.json_response(data)

async def connect_with_retry(client, max_retries=5, initial_delay=2):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            await client.connect()
            print("Connection successful.")
            break  # Exit the loop if the connection is successful
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("Max retries reached. Exiting.")

if __name__ == "__main__":
    realtime_speech_parameters = RealtimeParameters()
    realtime_speech_parameters.language_code = "en-US"
    realtime_speech_parameters.model_domain = (
        realtime_speech_parameters.MODEL_DOMAIN_GENERIC
    )
    realtime_speech_parameters.partial_silence_threshold_in_ms = 0
    realtime_speech_parameters.final_silence_threshold_in_ms = 2000
    realtime_speech_parameters.should_ignore_invalid_customizations = False
    realtime_speech_parameters.stabilize_partial_results = (
        realtime_speech_parameters.STABILIZE_PARTIAL_RESULTS_NONE
    )

    realtime_speech_url = "wss://realtime.aiservice.us-phoenix-1.oci.oraclecloud.com"
    client = RealtimeClient(
        config=config,
        realtime_speech_parameters=realtime_speech_parameters,
        listener=SpeechListener(),
        service_endpoint=realtime_speech_url,
        signer=None,
        compartment_id=compartment_id,
    )

    loop = asyncio.get_event_loop()
    loop.create_task(send_audio(client))
    loop.create_task(check_idle())

    app = web.Application()
    app.router.add_get('/selectai_data', handle_request)
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', 8080)
    loop.run_until_complete(site.start())

    loop.run_until_complete(connect_with_retry(client))

    if stream.is_active():
        stream.close()

    print("Closed")
