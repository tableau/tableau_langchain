import re
import json

def get_utterance():
    query = input('What would you like to know about your data? Reply with "stop" if you are done. ')
    return query

def get_payload(output):
    # print reasoning
    print(output.split('JSON_payload')[0])
    # parse LLM output and query headless BI
    parsed_output = output.split('JSON_payload')[1]

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        payload = json.loads(json_string)
        return payload

