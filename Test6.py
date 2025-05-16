"""
Automated end-to-end test for Test #6 (APM demo status tracking) using Bedrock.

Ensure you have browser-use installed with `examples` extra, i.e. `uv install 'browser-use[examples]'`

@dev Ensure AWS environment variables are set correctly for Bedrock access.
"""

from browser_use.controller.service import Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use import ActionResult, Agent
from pydantic import BaseModel
import argparse
import asyncio
import os
import sys

import boto3
from botocore.config import Config
from langchain_aws import ChatBedrockConverse
from typing import Optional
from browser_use.browser.context import BrowserContext

# disable browser-use's built-in LLM API-key check
os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "True"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

controller = Controller()


@controller.action(
    'Access the graph and open the popup'
)
async def bounding_box(browser: BrowserContext):
    print("Injecting red dot...")
    page = await browser.get_current_page()

    logs = await page.evaluate("""
        () => {
                const TRIAGE_CHART_SELECTOR = '[data-testid="triage-chart"]';
                const CHART_LOADING_SELECTOR = ".cwdb-loader-container";
                const LINE_GRAPH_SELECTOR = "g.chart g.metric.line.dimmable";
                const LEADER_BOARD_DATA_POINT_SELECTOR = "circle.leaderboard-datapoint";
                const EVENT_LAYER_SELECTOR = ".event-layer";
                const DATA_POINT_SELECTOR = "circle.datapoint";
                const MAX_RETRIES = 10;
                const RETRY_DELAY = 500;

                const iframe = document.querySelector("iframe#microConsole-Pulse");

                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

                const charts = iframeDoc.querySelectorAll(TRIAGE_CHART_SELECTOR);

                const chart = charts[2];

                const test = chart.querySelector(EVENT_LAYER_SELECTOR);

                const rect = test.getBoundingClientRect();
                const hoverX = rect.left + rect.width / 2;
                const hoverY = rect.top + rect.height / 2;

                const hoverEvent = new MouseEvent("mousemove", {
                    clientX: hoverX,
                    clientY: hoverY,
                    bubbles: true,
                    cancelable: true,
                    view: window,
                });

                test.dispatchEvent(hoverEvent);

                setTimeout(() => {}, 1000);

                const leaderBoardDataPoint = chart.querySelector(
                    LEADER_BOARD_DATA_POINT_SELECTOR,
                );

                const leaderBoardDataPointRect = leaderBoardDataPoint.getBoundingClientRect();
                const leaderBoardDataPointX = leaderBoardDataPointRect.left + leaderBoardDataPointRect.width / 2;
                const leaderBoardDataPointY = leaderBoardDataPointRect.top + leaderBoardDataPointRect.height / 2;
                const leaderBoardDataPointEvent = new MouseEvent("mousemove", {
                    clientX: leaderBoardDataPointX,
                    clientY: leaderBoardDataPointY,
                    bubbles: true,
                    cancelable: true,
                    view: window,
                });
                leaderBoardDataPoint.dispatchEvent(leaderBoardDataPointEvent);

                async function waitForLowestCyElement(retries = 10, delay = 500) {
                    for (let i = 0; i < retries; i++) {
                    const allDatapoints = iframeDoc.querySelectorAll("circle.all-datapoint");

                    if (allDatapoints.length > 0) {
                        let minCy = Infinity;
                        let minCyElement = null;

                        allDatapoints.forEach((datapoint) => {
                        const cy = parseFloat(datapoint.getAttribute("cy"));
                        if (!isNaN(cy) && cy < minCy) {
                            minCy = cy;
                            minCyElement = datapoint;
                        }
                        });

                        return minCyElement;
                    }

                    await new Promise((resolve) => setTimeout(resolve, delay));
                    }

                    console.warn("No datapoints found after retries.");
                    return null;
                }

                // Usage:
                waitForLowestCyElement().then((element) => {
                    if (element) {
                    const elementRect = element.getBoundingClientRect();
                    const elementX = elementRect.left + elementRect.width / 2;
                    const elementY = elementRect.top + elementRect.height / 2;

                    const hoverEvent = new MouseEvent("mousemove", {
                        clientX: elementX,
                        clientY: elementY,
                        bubbles: true,
                        cancelable: true,
                        view: window,
                    });

                    // Dispatch hover event to the target element
                    element.dispatchEvent(hoverEvent);
                    clickDataPoint(DATA_POINT_SELECTOR);
                    } else {
                    console.warn("No element with a `cy` value found.");
                    }
                });

                async function clickDataPoint(selector) {
                    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
                    try {
                        const datapoint = chart.querySelector(selector);

                        if (!datapoint) {
                        console.warn(`Attempt ${attempt}: Datapoint not found.`);
                        await wait(RETRY_DELAY);
                        continue;
                        }

                        const cx = parseFloat(datapoint.getAttribute("cx"));
                        const cy = parseFloat(datapoint.getAttribute("cy"));

                        // Check for valid coordinates
                        if (isNaN(cx) || isNaN(cy)) {
                        console.warn(`Attempt ${attempt}: Invalid coordinates. Retrying...`);
                        await wait(RETRY_DELAY);
                        continue;
                        }

                        // Dispatch `mousedown`
                        const mousedownEvent = new MouseEvent("mousedown", {
                        clientX: cx,
                        clientY: cy,
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        });
                        datapoint.dispatchEvent(mousedownEvent);

                        // Dispatch `mouseup`
                        const mouseupEvent = new MouseEvent("mouseup", {
                        clientX: cx,
                        clientY: cy,
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        });
                        datapoint.dispatchEvent(mouseupEvent);

                        // Dispatch `click`
                        const clickEvent = new MouseEvent("click", {
                        clientX: cx,
                        clientY: cy,
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        });
                        datapoint.dispatchEvent(clickEvent);

                        return; // Exit the loop if successful
                    } catch (error) {
                        console.warn(`Attempt ${attempt}: Error occurred - ${error.message}`);
                    }

                    // Wait before retrying
                    await wait(RETRY_DELAY);
                    }

                    console.error(`Failed to click datapoint after ${MAX_RETRIES} attempts.`);
                }

                function wait(ms) {
                    return new Promise((resolve) => setTimeout(resolve, ms));
                }

                return "JavaScript injected successfully.";
        };
    """)

    print("Logs from browser context:", logs)
    return ActionResult(extracted_content=logs, include_in_memory=False)


def get_llm():
    config = Config(retries={'max_attempts': 10, 'mode': 'adaptive'})
    bedrock_client = boto3.client(
        'bedrock-runtime', region_name='us-east-1', config=config)

    return ChatBedrockConverse(
        model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
        temperature=0.0,
        max_tokens=None,
        client=bedrock_client,
    )


task = """
        1. Navigate to https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#application-signals:services/Environment%3Deks%3Ademo%2Fdefault%26Name%3Dvisits-service-java%26Type%3DService/operations?selectedOperation=POST+%2Fowners%2F%7BownerId%7D%2Fpets%2F%7BpetId%7D%2Fvisits
        2. Access the graph and open the popup
        3. In the popup, under "Trace ID", click the first link navigate to the new page.
        4. Wait a few seconds for the page to render. Under "visits-service-java AWS::EKS::Container", click on the row with "visits-service-java" and wait a few seconds
        5. In the popup, click the "Exceptions" tab and look for the messge "The level of configured provisioned throughput for the table was exceeded.". If this is there, notify me with a checkmark and if not, notify me with an X.
        """

parser = argparse.ArgumentParser()
parser.add_argument('--query', type=str,
                    help='The query for the agent to execute', default=task)
args = parser.parse_args()

llm = get_llm()

browser = Browser(
    config=BrowserConfig(
        browser_binary_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
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
    history = await agent.run(max_steps=100)
    print(history.action_results())
    await browser.close()

asyncio.run(main())
