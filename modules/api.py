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
        input_variables=["analysis"],
        output_variables=["response"],
        transform=create_response
    )

    return response


def create_response(parameters: dict) -> dict:

    response_template = {
        'response': parameters['analysis']
    }

    return response_template
