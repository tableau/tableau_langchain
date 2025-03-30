import os
import json
import aiohttp
import getpass


def _set_env(var: str):
    """
    if environment variable not set, safely prompts user for value returns the newly resolved variable
    """
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# reusable asynchronous HTTP GET requests
async def http_get(endpoint, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers) as response:
            responseHeaders = dict(response.headers)
            responseBody = await response.json()

            responseObject = {
                "headers": responseHeaders,
                "body": responseBody
            }
            return responseObject

# reusable asynchronous HTTP POST requests
async def http_post(endpoint, headers, payload):
    formattedPayload = json.dumps(payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, data=formattedPayload) as response:
            responseHeaders = dict(response.headers)
            responseBody = await response.json()

            responseObject = {
                "headers": responseHeaders,
                "body": responseBody
            }
            return responseObject
