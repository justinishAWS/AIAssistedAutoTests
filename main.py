"""
Automated end-to-end implementation for tests (from the APM demo status tracking) using Bedrock Claude 3.7 Sonnet.

@dev Ensure AWS environment variables are set correctly for Console (Bedrock and CloudWatch) access.
"""

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
async def click_graph_spike(params: PositionParameters, browser: BrowserContext):
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
    'Test result status',
    param_model=TestResult
)
async def test_result(params: TestResult):
    # TODO: When access is granted to publish metrics, add functionality to publish metric
    print(f"test result is {params.z}!!!")
    return ActionResult(extracted_content="The task is COMPLETE - you can EXIT now. DO NOT conduct anymore steps!!!", is_done=True)

@controller.action(
    'Scroll injection down',
)
async def scrolling(browser: BrowserContext):
    page = await browser.get_current_page()

    js_file_path = os.path.join(os.path.dirname(
        __file__), "JSInjections", "scrollDown.js")
    with open(js_file_path, 'r') as file:
        js_code = file.read()

    logs = await page.evaluate(f"""
        () => {{
            {js_code}
            return scrollDown();
        }}
        """)
    return ActionResult(extracted_content=logs, include_in_memory=False)

@controller.action(
    'Access the node',
)
async def click_node(browser: BrowserContext):
    page = await browser.get_current_page()

    js_file_path = os.path.join(os.path.dirname(
        __file__), "JSInjections", "clickSQSNode.js")
    with open(js_file_path, 'r') as file:
        js_code = file.read()

    logs = await page.evaluate(f"""
        () => {{
            {js_code}
            return clickSQSNode();
        }}
        """)
    return ActionResult(extracted_content=logs, include_in_memory=True)

def get_llm():
    config = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
    bedrock_client = boto3.client(
        'bedrock-runtime', region_name='us-west-2', config=config)

    return ChatBedrockConverse(
        model_id='arn:aws:bedrock:us-west-2:868155213681:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0',
        temperature=0.0,
        max_tokens=None,
        client=bedrock_client,
        provider='Antropic',
        cache=False
    )


def authentication_open():
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

    destination = "https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#home:"
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

async def main():
    # Get test prompt file
    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as file:
        task = file.read()

    llm = get_llm()
    authenticated_url = authentication_open()

    browser = Browser(
        config=BrowserConfig(
            headless=True,
        )
    )

    initial_actions = [
        {'open_tab': {'url': authenticated_url}}
    ]

    agent = Agent(
        task=task,
        initial_actions=initial_actions,
        llm=llm,
        controller=controller,
        browser=browser,
        validate_output=True,
        extend_system_message="""REMEMBER it is ok if the test fails. When the test result is determined, DO NOT continue steps!!! JUST EXIT!!!"""
    )

    await agent.run(max_steps=25)
    await browser.close()

asyncio.run(main())
