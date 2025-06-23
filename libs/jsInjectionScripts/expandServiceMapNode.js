function expandServiceMapNode(testid) {
  const iframe = document.querySelector("iframe#microConsole-Pulse");
  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
  const expandNode = `[data-testid="EXPAND_GROUP_TEST_ID-group:AWS::${testid}"]`;
  iframeDoc.querySelector(expandNode).click();
}
