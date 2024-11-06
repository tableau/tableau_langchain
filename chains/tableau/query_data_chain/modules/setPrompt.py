from hbiQuery import get_data
from readMetadata import read
from prompts.nlq_to_vds import prompt
import json, requests, os

def get_values(caption):
     column_values = {'fields': [{'fieldCaption': caption}]}
     output = get_data(query_url= os.getenv('QUERY_DATASOURCE'), datasource_luid=os.getenv('DATASOURCE_LUID'),auth_secret=os.getenv('AUTH_TOKEN'),query=column_values)
     if output is None:
        return None
     sample_values = [list(item.values())[0] for item in output][:4]
     return sample_values


def instantiate_prompt(metadata):
    datasource_metadata = metadata

    counter = 0
    for field in datasource_metadata:
        if counter == 1:
            print("reading in your field metadata...")
        elif counter == 10:
            print("looking up field values...")
        del field['fieldName']
        del field['logicalTableId']
        if field['dataType'] == 'STRING':
            string_values = get_values(field['fieldCaption'])
            field['sampleValues'] = string_values
        counter+=1
        if counter == len(datasource_metadata) - 1:
            print("prompt is ready!")

    # add the datasource metadata of the connected datasource to the system prompt
    prompt['data_model'] = datasource_metadata
    return prompt