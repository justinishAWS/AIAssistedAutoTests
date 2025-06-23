async function checkAllPointAboveThreshold(chartPosition, checkboxPosition) {
  const LEADER_BOARD_DATA_POINT_SELECTOR = "circle.leaderboard-datapoint";
  const EVENT_LAYER_SELECTOR = ".event-layer";

  const ALL_DATA_POINT_SELECTOR = "circle.all-datapoint";

  const IFRAME_SELECTOR = "iframe#microConsole-Pulse";
  const LEGEND_CHECKBOX_SELECTOR = "rect.legend-checkbox";
  const CWDB_CHART_SELECTOR = "div.cwdb-chart";
  const ANNOTATION_LINE_SELECTOR = "line.annotation-line";

  const MAX_RETRIES = 10;
  const RETRY_DELAY = 500;

  // Get the iFrame
  const iframe = document.querySelector(IFRAME_SELECTOR);

  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

  // Each graph has 2+ lines graphed. To ensure the correct line is selected, we remove the other plot
  const checkboxes = iframeDoc.querySelectorAll(LEGEND_CHECKBOX_SELECTOR);

  const checkbox = checkboxes[checkboxPosition]; // TEST PARAM (3)

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
  const charts = iframeDoc.querySelectorAll(CWDB_CHART_SELECTOR);

  const chart = charts[chartPosition]; // TEST PARAM (2)
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

  const annotationLines = iframeDoc.querySelectorAll(ANNOTATION_LINE_SELECTOR);
  const annotationLineY = parseFloat(annotationLines[2].getAttribute("y1"));

  async function waitForAllDatapoints() {
    for (let i = 0; i < MAX_RETRIES; i++) {
      const allDatapoints = iframeDoc.querySelectorAll(ALL_DATA_POINT_SELECTOR);

      if (allDatapoints.length > 0) {
        for (const datapoint of allDatapoints) {
          const cy = parseFloat(datapoint.getAttribute("cy"));
          if (cy > annotationLineY) {
            return false;
          }
        }
        return true;
      }
      await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
    }
    return [];
  }

  const result = await waitForAllDatapoints();
  return result;
}
