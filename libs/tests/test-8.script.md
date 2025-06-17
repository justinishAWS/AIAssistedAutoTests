## Steps

### 1. Click 'Service Map'

In the left panel, under Application Signals, click 'Service Map'.

### 2. Access the node in the Service Map

Access the node in the Service Map, PASS in "group:AWS::SQS" as the PARAMETER.

**Constraints:**
- You MUST pass in "group:AWS::SQS" as a parameter

### 3. Wait

Wait a few seconds.

### 4. Click bottom link in right panel

Click on the bottom link in the 'Top three paths by error rate' dropdown in the right panel.

### 5. Click 'Dependencies'

Click the 'Dependencies' button.

### 6. Access the graph and open the popup.

**Constraints:**
- You MUST pass in parameters 2 and 3

### 7. Wait

Wait a few seconds.

### 8. Click the first 'Trace ID'

In the right panel, click the first blue hyperlink under 'Trace ID'.

**Constraints:**
- You MUST ensure that the link you are trying to click is a hexadecimal string

### 9. Wait

Wait a few seconds for the page to render.

### 10. Click 'Open Segment Details Panel' button

In the top right corner, open segment details panel IF it is not already expanded.

### 11. Click 'Exceptions' button

In the right panel, click the 'Exceptions' button.

### 12. Look for 'Only one PurgeQueue operation on apm_test is allowed every 60 seconds.'.

Look for the message 'Only one PurgeQueue operation on apm_test is allowed every 60 seconds.'.