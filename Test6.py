"""
Automated end-to-end test for Test #6 (from the APM demo status tracking) using Bedrock Claude 3.7 Sonnet.

@dev Ensure AWS environment variables are set correctly for Console (Bedrock and CloudWatch) access.
"""

import argparse
import asyncio
import os
import sys
import botocore.session
import requests
import urllib.parse
import json
import boto3

from botocore.config import Config
from langchain_aws import ChatBedrockConverse
from browser_use.browser.context import BrowserContext
from pydantic import BaseModel
from typing import Any
from browser_use.controller.service import Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use import ActionResult, Agent

# disable browser-use's built-in LLM API-key check
os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "True"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

controller = Controller()

class PositionParameters(BaseModel):
     x: Any # chartPosition
     y: Any # checkboxPosition

@controller.action(
    'Access the graph and open the popup',
    param_model=PositionParameters
)
async def bounding_box(params: PositionParameters, browser: BrowserContext):
    page = await browser.get_current_page()

    js_file_path = os.path.join(os.path.dirname(
        __file__), "JSInjections", "clickMaxGraphPoint.js")
    with open(js_file_path, 'r') as file:
        js_code = file.read()

    args = {
        "chartPosition": int(params.x),
        "checkboxPosition": int(params.y)
    }

    logs = await page.evaluate(f"""
        (args) => {{
            {js_code}
            return clickMaxGraphPoint(args.chartPosition, args.checkboxPosition);
        }}
        """, args)
    return ActionResult(extracted_content=logs, include_in_memory=False)

@controller.action(
    'Authenticate and open the link'
)
async def authentication_open():
    session = botocore.session.get_session()
    creds = session.get_credentials().get_frozen_credentials()

    session_dict = {
        "sessionId": creds.access_key,
        "sessionKey": creds.secret_key,
        "sessionToken": creds.token,
    }

    session_json = urllib.parse.quote(json.dumps(session_dict))
    signin_token_url = f"https://signin.aws.amazon.com/federation?Action=getSigninToken&Session={session_json}"
    signin_token_response = requests.get(signin_token_url)
    signin_token = signin_token_response.json()["SigninToken"]

    destination = "https://console.aws.amazon.com/cloudwatch/home"
    login_url = (
        "https://signin.aws.amazon.com/federation"
        f"?Action=login"
        f"&Issuer=my-script"
        f"&Destination={urllib.parse.quote(destination)}"
        f"&SigninToken={signin_token}"
    )

    # Current link is too long for browser-use to navigate to, so we need to shorten it
    def shorten_url(long_url):
        api_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}"
        response = requests.get(api_url)
        return response.text

    short_url = shorten_url(login_url)
    return short_url

@controller.action(
    'test result passed'
)
async def test_result():
    # TODO: When access is granted to publish metrics, add functionality to publish metric
    print("test result passed")
    return ActionResult(extracted_content="Test result passed. You can exit now.", is_done=True)

def get_llm():
    config = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
    bedrock_client = boto3.client(
        'bedrock-runtime', region_name='us-east-1', config=config)

    return ChatBedrockConverse(
        model_id='arn:aws:bedrock:us-east-1:140023401067:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0',
        temperature=0.0,
        max_tokens=None,
        client=bedrock_client,
        provider='Antropic'
    )

task = (
        "Authenticate and open the link"
        "Open this link"
        "In the left panel, under Application Signals, click Services"
        "In the search field with placeholder text 'Filter services and resources by text, property or value', type 'visits-service-java' and press Enter."
        "Click the hyperlink 'visits-service-java' in the 'Services' list in the main panel."
        "Click the 'Service operations' button."
        "In the search field under 'Service operations' type 'POST /owners/*/pets/{petId}/visits' and press Enter."
        "Access the graph and open the popup, pass in 2 and 6 as a parameters"
        "In the right panel, click the first link under 'Trace ID'."
        "Wait a few seconds for the page to render. Under 'visits-service-java AWS::EKS::Container', click on the row with 'visits-service-java' and wait a few seconds"
        "In the right panel, click right arrow."
        "In the right panel, click the 'Exceptions' button."
        "Look for the message 'The level of configured provisioned throughput for the table was exceeded.' and if it is there, the test result passed"
)

parser = argparse.ArgumentParser()
parser.add_argument('--query', type=str,
                    help='The query for the agent to execute', default=task)
args = parser.parse_args()

llm = get_llm()

browser = Browser(
    config=BrowserConfig(
        # browser_binary_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # headless=True,
    )
)

agent = Agent(
    task=args.query,
    llm=llm,
    controller=controller,
    browser=browser,
    validate_output=True,
)

async def main():
    await agent.run(max_steps=100)
    await browser.close()

asyncio.run(main())
