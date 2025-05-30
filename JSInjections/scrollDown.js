// Browser Use's built-in scroll (https://github.com/browser-use/browser-use/blob/03524523be378d77935039bb4ae0fddee30a8557/browser_use/controller/service.py#L287)
// option does not work on the AWS Console. We must override this.

function scrollDown() {
  const iframe = document.getElementById("microConsole-ApmXray");
  const iframeWindow = iframe.contentWindow;

  const viewportHeight = iframeWindow.innerHeight;
  iframeWindow.scrollBy(0, viewportHeight);
}
