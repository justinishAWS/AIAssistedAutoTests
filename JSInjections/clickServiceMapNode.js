function clickServiceMapNode(testid) {
  const iframe = document.querySelector("iframe#microConsole-Pulse");
  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
  const bedrockRuntimeNode =
    '[data-testid="EXPAND_GROUP_TEST_ID-group:AWS::BedrockRuntime"]';

  // Currently, this just selects the BedrockRuntime node, but if this is requried for additional tests, it can be passed as a parameter.
  iframeDoc.querySelector(bedrockRuntimeNode).click();

  setTimeout(() => {
    const node = iframeDoc.querySelector(`g[data-testid="${testid}"]`);
    if (node) {
      const nodeBounds = node.getBoundingClientRect();
      const nodeHoverX = nodeBounds.left + nodeBounds.width / 2;
      const nodeHoverY = nodeBounds.top + nodeBounds.height / 2;

      const nodeHoverEvent = new MouseEvent("mousemove", {
        clientX: nodeHoverX,
        clientY: nodeHoverY,
        bubbles: true,
        cancelable: true,
        view: window,
      });

      node.dispatchEvent(nodeHoverEvent);

      const nodeClickEvent = new MouseEvent("click", {
        clientX: nodeHoverX,
        clientY: nodeHoverY,
        bubbles: true,
        cancelable: true,
        view: window,
      });

      node.dispatchEvent(nodeClickEvent);
    } else console.error("Node not found");
  }, 1000);
}
