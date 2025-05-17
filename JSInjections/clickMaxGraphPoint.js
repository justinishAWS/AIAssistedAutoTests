// NOTE: Can remove console.log() statements before moving to .evaluate() function

/**
 * Selectors taken from
 * https://code.amazon.com/packages/PuppetryTests-CloudWatchConsole/blobs/be137a4624e00e12b01edf31b8c5799e5a2cb454/--/src/models/metrics-polaris/metrics-page.js
 */
() => {
  const TRIAGE_CHART_SELECTOR = '[data-testid="triage-chart"]';
  const LEADER_BOARD_DATA_POINT_SELECTOR = "circle.leaderboard-datapoint";
  const EVENT_LAYER_SELECTOR = ".event-layer";

  const DATA_POINT_SELECTOR = "circle.datapoint";
  const ALL_DATA_POINT_SELECTOR = "circle.all-datapoint";

  const MAX_RETRIES = 10;
  const RETRY_DELAY = 500;

  // Get the iFrame
  const iframe = document.querySelector("iframe#microConsole-Pulse");

  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

  // Each graph has 2+ lines graphed. To ensure the correct line is selected, we remove the other plot
  const checkboxes = iframeDoc.querySelectorAll("rect.legend-checkbox");

  const checkbox = checkboxes[6]; // PARAM
  const checkboxBounds = checkbox.getBoundingClientRect();
  const checkboxHoverX = checkboxBounds.left + checkboxBounds.width / 2;
  const checkboxHoverY = checkboxBounds.top + checkboxBounds.height / 2;

  console.log("Checkbox Coordinates:", checkboxHoverX, checkboxHoverY);

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

  // This will query all of the graphs in the iFrame
  const charts = iframeDoc.querySelectorAll(TRIAGE_CHART_SELECTOR);

  // Currently, we know that we want to access the "Faults and Errors" graph on this page, but we should make this a parameter to pass in
  const chart = charts[2];

  // Get the <rect> element within this chart. This will help us hover over the dynamic part
  const eventLayer = chart.querySelector(EVENT_LAYER_SELECTOR);

  console.log(eventLayer);

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
      // Find all <circle> datapoints in line graph
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

        console.log(`Attempt ${attempt}: Datapoint found:`, datapoint);

        // Parse the x/y-coordinates from string to float
        const cx = parseFloat(datapoint.getAttribute("cx"));
        const cy = parseFloat(datapoint.getAttribute("cy"));

        console.log("Circle center coordinates:", cx, cy);

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

        console.log(`Attempt ${attempt}: Click dispatched to`, datapoint);
        return; // If this was successful, you can exit this loop
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
};
