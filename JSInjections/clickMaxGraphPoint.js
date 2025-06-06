/**
 * Selectors taken from
 * https://code.amazon.com/packages/PuppetryTests-CloudWatchConsole/blobs/be137a4624e00e12b01edf31b8c5799e5a2cb454/--/src/models/metrics-polaris/metrics-page.js
 */
function clickMaxGraphPoint(chartPosition, checkboxPosition) {
  const TRIAGE_CHART_SELECTOR = '[data-testid="triage-chart"]';
  const LEADER_BOARD_DATA_POINT_SELECTOR = "circle.leaderboard-datapoint";
  const EVENT_LAYER_SELECTOR = ".event-layer";

  const DATA_POINT_SELECTOR = "circle.datapoint";
  const ALL_DATA_POINT_SELECTOR = "circle.all-datapoint:not(.hidden)";

  const MAX_RETRIES = 10;
  const RETRY_DELAY = 500;

  // Get the iFrame
  const iframe = document.querySelector("iframe#microConsole-Pulse");

  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

  // Each graph has 2+ lines graphed. To ensure the correct line is selected, we remove the other plot
  if (!iframeDoc.querySelector("g.legend.dimmable.legend-disabled")) {
    const checkboxes = iframeDoc.querySelectorAll("rect.legend-checkbox");

    const checkbox = checkboxes[checkboxPosition]; // PARAM (6)
    const checkboxBounds = checkbox.getBoundingClientRect();
    const checkboxHoverX = checkboxBounds.left + checkboxBounds.width / 2;
    const checkboxHoverY = checkboxBounds.top + checkboxBounds.height / 2;

    const checkboxHoverEvent = new MouseEvent("mousemove", {
      clientX: checkboxHoverX,
      clientY: checkboxHoverY,
      bubbles: true,
      cancelable: true,
      view: window,
    });

    checkbox.dispatchEvent(checkboxHoverEvent);

    const checkboxClickEvent = new MouseEvent("click", {
      clientX: checkboxHoverX,
      clientY: checkboxHoverY,
      bubbles: true,
      cancelable: true,
      view: window,
    });

    checkbox.dispatchEvent(checkboxClickEvent);
  }

  // This will query all of the graphs in the iFrame
  const charts = iframeDoc.querySelectorAll(TRIAGE_CHART_SELECTOR);

  // Currently, we know that we want to access the "Faults and Errors" graph on this page, but we should make this a parameter to pass in
  const chart = charts[chartPosition]; // PARAM (2)

  // Get the <rect> element within this chart. This will help us hover over the dynamic part
  const eventLayer = chart.querySelector(EVENT_LAYER_SELECTOR);

  // Get the position of this object relative to the viewport (https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)
  const rect = eventLayer.getBoundingClientRect();

  // Hover over the middle of this element (does not have to be the middle, but this step is required to access all <circle> element datapoints)
  const hoverX = rect.left + rect.width / 2;
  const hoverY = rect.top + rect.height / 2;

  // Create new MouseEvent to move the mouse to these specific hover coordinates
  const hoverEvent = new MouseEvent("mousemove", {
    clientX: hoverX,
    clientY: hoverY,
    bubbles: true,
    cancelable: true,
    view: window,
  });

  // Send this hover event to the eventLayer object (https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/dispatchEvent)
  eventLayer.dispatchEvent(hoverEvent);

  // Wait 1 second for hover event to update the graph
  setTimeout(() => {}, 1000);

  // Get the leaderboard datapoint
  const leaderBoardDataPoint = chart.querySelector(
    LEADER_BOARD_DATA_POINT_SELECTOR
  );

  // Get the position of this object relative to the viewpoint
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

      element.dispatchEvent(hoverEvent);
      clickDataPoint(DATA_POINT_SELECTOR);
    } else {
      console.warn("No element with a `cy` value found.");
    }
  });

  async function waitForLowestCyElement() {
    for (let i = 0; i < MAX_RETRIES; i++) {
      // Find all <circle> datapoints in line graph
      const allDatapoints = iframeDoc.querySelectorAll(ALL_DATA_POINT_SELECTOR);

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

      await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
    }

    console.warn("No datapoints found after retries.");
    return null;
  }

  /*
   * Mimic logic from Console team:
   * https://code.amazon.com/packages/CloudWatchConsole-ApplicationMonitoringTests/blobs/4cea84c2b68bccc4ca05269b23223004798db39f/--/src/selectors/triage/charts.ts#L233
   */
  async function clickDataPoint(selector) {
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      try {
        const datapoint = chart.querySelector(selector);

        // Sometimes, the datapoint may not be findable. If this is the case, try again
        if (!datapoint) {
          console.warn(`Attempt ${attempt}: Datapoint not found.`);
          await wait(RETRY_DELAY);
          continue;
        }

        // Parse the x/y-coordinates from string to float
        const cx = parseFloat(datapoint.getAttribute("cx"));
        const cy = parseFloat(datapoint.getAttribute("cy"));

        // Sometimes, the datapoint is not correctly found. If this is the case, try again
        if (isNaN(cx) || isNaN(cy)) {
          console.warn(`Attempt ${attempt}: Invalid coordinates. Retrying...`);
          await wait(RETRY_DELAY);
          continue;
        }

        // Create new MouseEvent to move the mouse down at these coordinates
        const mousedownEvent = new MouseEvent("mousedown", {
          clientX: cx,
          clientY: cy,
          bubbles: true,
          cancelable: true,
          view: window,
        });
        // Send this hover event to the <circle> datapoint object
        datapoint.dispatchEvent(mousedownEvent);

        // Create new MouseEvent to move the mouse up at these coordinates
        const mouseupEvent = new MouseEvent("mouseup", {
          clientX: cx,
          clientY: cy,
          bubbles: true,
          cancelable: true,
          view: window,
        });
        // Send this hover event to the <circle> datapoint object
        datapoint.dispatchEvent(mouseupEvent);

        // Create new MouseEvent to click the mouse down at these coordinates
        const clickEvent = new MouseEvent("click", {
          clientX: cx,
          clientY: cy,
          bubbles: true,
          cancelable: true,
          view: window,
        });
        // Send this hover event to the <circle> datapoint object
        datapoint.dispatchEvent(clickEvent);
        await wait(2000);
        if (
          !iframeDoc.body.textContent.includes(
            "No spans with any faults were found for the selected time range."
          )
        ) {
          return; // If this was successful, you can exit this loop
        }
      } catch (error) {
        console.warn(`Attempt ${attempt}: Error occurred - ${error.message}`);
      }

      await wait(RETRY_DELAY); // If this was not successful, delay then try again
    }

    console.error(`Failed to click datapoint after ${MAX_RETRIES} attempts.`);
  }

  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
  return "JavaScript injected successfully.";
}
