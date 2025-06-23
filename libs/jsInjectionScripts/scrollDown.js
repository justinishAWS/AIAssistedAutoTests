function scrollDown(iframeId, elementId, scrollTimes) {
  const iframe = document.getElementById(`microConsole-${iframeId}`);
  const iframeWindow = iframe.contentWindow;

  if (elementId === "#html") {
    const viewportHeight = iframeWindow.innerHeight;
    iframeWindow.scrollBy(0, viewportHeight * scrollTimes);
  } else {
    const doc = iframeWindow.document;
    const main = doc.querySelector(elementId);
    main.scrollBy(0, main.clientHeight * scrollTimes);
  }
  return "JavaScript injected successfully.";
}
