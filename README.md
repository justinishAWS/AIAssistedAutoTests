# AIAssistedAutoTests
This can run tests end-to-end with no user interaction.

We utilize custom Actions to authenticate and federate an AWS link automatically and inject JavaScript code to access metric graphs.

## Quick Start
After cloning the repository follow these steps to get started:
1. Generate AWS credentials (default for Bedrock, S3, and CloudWatch access, "auth-access" for account you want to read from)
2. Run `pip install browser-use==0.2.5` to install browser-use (we want to remain on version `0.2.5`, but this can be changed in the future)
3. Run `pip install "browser-use[memory]"` to install memory functionality
4. Run `pip install playwright` to install PlayWright
5. `cd libs`
6. Run the file with `python main.py tests/test-x.script.md`

## Environment Variables
To run this project, create a `.env` file in the root directory based on the provided `.env.example`:

```
AWS_REGION=<Region for default account>
AWS_ACCOUNT_ID=<Account ID for default account>
DEBUG_MODE=<True/False>
S3_BUCKET_NAME=<S3 Bucket Name to store test results>
CLOUDWATCH_NAMESPACE=<CloudWatch namespace to publish metrics>
INTERVAL_DURATION=<Interval to wait between each test run (seconds)>
AUTH_ACCESS_ACCOUNT_ID=<Account ID for auth-access>
AUTH_ACCESS_ROLE_ID=<Role name in auth-access account (used to assume role)>
```

## Debugging

If you want to view the visual browser UI, comment out the line `headless=True` in the `Browser` object.

To debug in headless mode to save screenshots of each step to your directory, update your `DEBUG_MODE` variable in `.env` to `True`:
`DEBUG_MODE=True`
