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

class TestResult(BaseModel):
    z: Any # result

@controller.action(
    'Access the graph and open the popup',
    param_model=PositionParameters
)
async def bounding_box(params: PositionParameters, browser: BrowserContext):
    page = await browser.get_current_page()

    js_file_path = os.path.join(os.path.dirname(
        __file__), "..", "JSInjections", "clickMaxGraphPoint.js")
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
    'Test result status',
    param_model=TestResult
)
async def test_result(params: TestResult):
    # TODO: When access is granted to publish metrics, add functionality to publish metric
    print(f"test result is {params.z}!!!")
    return ActionResult(extracted_content="The task is COMPLETE - you can EXIT now. DO NOT conduct anymore steps!!!", is_done=True)

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

task = """
        Determine if the given test passed or failed with the following steps:

        1. Authenticate and open the link.
        2. Open this link.
        3. In the left panel, under Application Signals, click 'Services'.
        4. In the search field with placeholder text 'Filter services and resources by text, property or value', type 'visits-service-java' and press Enter.
        5. Click the hyperlink 'visits-service-java' in the 'Services' list in the main panel.
        6. Click the 'Service operations' button.
        7. In the search field under 'Service operations' type 'POST /owners/*/pets/{petId}/visits' and press Enter.
        8. Access the graph and open the popup, PASS in 2 and 6 as a PARAMETERS.
        9. Wait a few seconds.
        10. In the right panel, click the first link under 'Trace ID'.
        11. Wait a few seconds for the page to render. 
        12. Scroll down a page.
        13. Under 'visits-service-java', click on the row with 'visits-service-java' and wait a few seconds.
        14. In the right panel, click right arrow.
        15. In the right panel, click the 'Exceptions' button.
        16. Wait a few seconds.
        17. Look for the message 'The level of configured provisioned throughput for the table was exceeded.'.

        Considerations:
        - If you make it to the end, the test result is passed. If ANY of these steps fail, the test result is failed. 

        If this test fails, the task is COMPLETE. DO NOT conduct more steps!!!
"""

parser = argparse.ArgumentParser()
parser.add_argument('--query', type=str,
                    help='The query for the agent to execute', default=task)
args = parser.parse_args()

llm = get_llm()

browser = Browser(
    config=BrowserConfig(
        headless=True,
    )
)
# Click 'Open Segment details panel' button in the top right corner
agent = Agent(
    task=args.query,
    llm=llm,
    controller=controller,
    browser=browser,
    validate_output=True,
    extend_system_message="""REMEMBER it is ok if the test fails. When the test result is determined, DO NOT continue steps!!! JUST EXIT!!!"""
)

async def main():
    await agent.run(max_steps=100)
    await browser.close()

asyncio.run(main())
