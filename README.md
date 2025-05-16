# AIAssistedAutoTests
Currently, this includes a Python file that can run Test #6 (APM demo status tracking) end-to-end with no user interaction.

## Quick Start
1. Run `pip install browser-use` to install browser-use

2. Run `pip install playwright` to install PlayWright

3. Run the file with `python Test6.py`

## Debugging

You may encounter an error stating `[browser] Failed to initialize Playwright browser: To start chrome in Debug mode, you need to close all existing Chrome instances and try again otherwise we can not connect to the instance.`

If quitting your current Chrome instance does not resolve this, you can create a temporary folder which contains your user information and credentials and run Chrome on that. You will also need to include debugging on port 9222.

To do this, you can run:
1. `cp -r /Users/<username>/Library/Application\ Support/Google/Chrome/Default ~/tmp/user-data-dir/`
- This will copy your default user profile data to a temporary Default profile directory to save your login credentials and other information
- It will create a duplicate Chrome user profile that can be used without affecting the original profile
2. `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir=/Users/<username>/tmp/user-data-dir/`
- This launches a new instance of Chrome using the newly copied profile and enables debugging on port 9222 for PlayWright
