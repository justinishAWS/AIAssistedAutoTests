# AIAssistedAutoTests
This can run Test #6 (from the APM demo status tracking Quip file) end-to-end with no user interaction.

We utilize custom Actions to authenticate and federate an AWS link automatically and inject JavaScript code to access metric graphs.

## Quick Start
To try running this on your local machine, ensure that you have at least `ReadOnly` access to the apm-demo1 acccount and run the following commands after cloning the repository:
1. Run `mwinit` to generate new credentials  

2. Run `ada credentials update --account=<apm-demo1_account_id> --provider=isengard --once --role=<Role>`

3. Run `pip install browser-use` to install browser-use
4. Run `pip install "browser-use[memory]"` to install memory functionality

5. Run `pip install playwright` to install PlayWright

6. Run the file with `python Test6.py`

## Debugging

If you want to view the visual browser UI, comment out the line `headless=True` in the `Browser` object.

To debug in headless mode, add the following code to your `main()` to save screenshots of each step to your directory:

```python
history = await agent.run(max_steps=100)
for i, screenshot in enumerate(history.screenshots()):
    with open(f"screenshot_{i}.png", "wb") as f:
        f.write(base64.b64decode(screenshot))
```


Note: Also ensure to add `import base64` at the top of the file.
