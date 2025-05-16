const TRIAGE_CHART_SELECTOR = '[data-testid="triage-chart"]';
const LEADER_BOARD_DATA_POINT_SELECTOR = "circle.leaderboard-datapoint";
const EVENT_LAYER_SELECTOR = ".event-layer";

const DATA_POINT_SELECTOR = "circle.datapoint";
const ALL_DATA_POINT_SELECTOR = "circle.all-datapoint";

const MAX_RETRIES = 10;
const RETRY_DELAY = 500;

const iframe = document.querySelector("iframe#microConsole-Pulse");

const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

const charts = iframeDoc.querySelectorAll(TRIAGE_CHART_SELECTOR);

const chart = charts[2];

const eventLayer = chart.querySelector(EVENT_LAYER_SELECTOR);

console.log(eventLayer);

const rect = eventLayer.getBoundingClientRect();

const hoverX = rect.left + rect.width / 2;
const hoverY = rect.top + rect.height / 2;

const hoverEvent = new MouseEvent("mousemove", {
  clientX: hoverX,
  clientY: hoverY,
  bubbles: true,
  cancelable: true,
  view: window,
});

eventLayer.dispatchEvent(hoverEvent);

setTimeout(() => {}, 1000);

const leaderBoardDataPoint = chart.querySelector(
  LEADER_BOARD_DATA_POINT_SELECTOR
);

console.log(leaderBoardDataPoint);
console.log("Test: ", chart.querySelectorAll(LEADER_BOARD_DATA_POINT_SELECTOR));

const leaderBoardDataPointRect = leaderBoardDataPoint.getBoundingClientRect();

const leaderBoardDataPointX =
  leaderBoardDataPointRect.left + leaderBoardDataPointRect.width / 2;
const leaderBoardDataPointY =
  leaderBoardDataPointRect.top + leaderBoardDataPointRect.height / 2;

const leaderBoardDataPointEvent = new MouseEvent("mousemove", {
  clientX: leaderBoardDataPointX,
  clientY: leaderBoardDataPointY,
  bubbles: true,
  cancelable: true,
  view: window,
});
leaderBoardDataPoint.dispatchEvent(leaderBoardDataPointEvent);

waitForLowestCyElement().then((element) => {
  if (element) {
    console.log("Element with the lowest `cy` value:", element);

    const elementRect = element.getBoundingClientRect();
    const elementX = elementRect.left + elementRect.width / 2;
    const elementY = elementRect.top + elementRect.height / 2;

    console.log(`Hovering over coordinates: X: ${elementX}, Y: ${elementY}`);

    const hoverEvent = new MouseEvent("mousemove", {
      clientX: elementX,
      clientY: elementY,
      bubbles: true,
      cancelable: true,
      view: window,
    });

    element.dispatchEvent(hoverEvent);
    console.log("Hover event dispatched to:", element);
    clickDataPoint(DATA_POINT_SELECTOR);
  } else {
    console.warn("No element with a `cy` value found.");
  }
});

async function waitForLowestCyElement() {
  for (let i = 0; i < MAX_RETRIES; i++) {
    const allDatapoints = iframeDoc.querySelectorAll(ALL_DATA_POINT_SELECTOR);

    if (allDatapoints.length > 0) {
      console.log("Found datapoints:", allDatapoints);

      let minCy = Infinity;
      let minCyElement = null;

      allDatapoints.forEach((datapoint) => {
        const cy = parseFloat(datapoint.getAttribute("cy"));
        if (!isNaN(cy) && cy < minCy) {
          minCy = cy;
          minCyElement = datapoint;
        }
      });

      console.log(`Lowest cy value: ${minCy}`);
      return minCyElement;
    }

    console.log(`Retry ${i + 1}: No datapoints found, waiting...`);
    await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
  }

  console.warn("No datapoints found after retries.");
  return null;
}

async function clickDataPoint(selector) {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const datapoint = chart.querySelector(selector);

      if (!datapoint) {
        console.warn(`Attempt ${attempt}: Datapoint not found.`);
        await wait(RETRY_DELAY);
        continue;
      }

      console.log(`Attempt ${attempt}: Datapoint found:`, datapoint);

      const cx = parseFloat(datapoint.getAttribute("cx"));
      const cy = parseFloat(datapoint.getAttribute("cy"));

      console.log("Circle center coordinates:", cx, cy);

      if (isNaN(cx) || isNaN(cy)) {
        console.warn(`Attempt ${attempt}: Invalid coordinates. Retrying...`);
        await wait(RETRY_DELAY);
        continue;
      }

      const mousedownEvent = new MouseEvent("mousedown", {
        clientX: cx,
        clientY: cy,
        bubbles: true,
        cancelable: true,
        view: window,
      });

      datapoint.dispatchEvent(mousedownEvent);

      const mouseupEvent = new MouseEvent("mouseup", {
        clientX: cx,
        clientY: cy,
        bubbles: true,
        cancelable: true,
        view: window,
      });

      datapoint.dispatchEvent(mouseupEvent);

      const clickEvent = new MouseEvent("click", {
        clientX: cx,
        clientY: cy,
        bubbles: true,
        cancelable: true,
        view: window,
      });

      datapoint.dispatchEvent(clickEvent);

      console.log(`Attempt ${attempt}: Click dispatched to`, datapoint);
      return;
    } catch (error) {
      console.warn(`Attempt ${attempt}: Error occurred - ${error.message}`);
    }

    await wait(RETRY_DELAY);
  }

  console.error(`Failed to click datapoint after ${MAX_RETRIES} attempts.`);
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
