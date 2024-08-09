import json

from langchain.chains import TransformChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

def vds_query():
#    print('******   vds_query    *****\n', type(parameters), '\n', parameters)
    # sets up parser to respond with reliable outputs
   parser = JsonOutputParser(pydantic_object=VDS_Query_Response)
   return parser

# Define the data structure for the response
class VDS_Query_Response(BaseModel):
    data: str = Field(description="the table of data containing the response to the query")
    behavioral: str = Field(description="a behavioral summary of the reasoning and explanation behind the action taken")


def vds_transform(parameters: dict) -> dict:
    response = TransformChain(
        input_variables=["pandas_agent_output"],
        output_variables=["analysis"],
        transform=create_response
    )

    return response


def create_response(parameters: dict) -> dict:
    # split the string before and after data
    split_string = parameters['pandas_agent_output'].split('\n\n|', 1)
    # store behavioral data in natural language
    pandas_behavioral = split_string[0]
    print('******* pandas_behavior *******\n', pandas_behavioral)
    # add back the '|' character and extract the data
    pandas_data = '|' + split_string[1] if len(split_string) > 1 else ''
    print('******* data *******\n', pandas_data)

    response_template = {
        'analysis': {
            'analyst_behavior': pandas_behavioral,
            'analyst_result': pandas_data
        }
    }

    return response_template
