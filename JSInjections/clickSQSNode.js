function clickSQSNode() {
  const iframe = document.querySelector(`iframe#microConsole-Pulse`);
  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

  setTimeout(() => {
    const node = iframeDoc.querySelector(`g[data-testid="group:AWS::SQS"]`);
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

  return "JavaScript injected successfully.";
}
