import os
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from natsort import natsorted

load_dotenv()
auth_access_account_id = os.environ['AUTH_ACCESS_ACCOUNT_ID']
auth_access_role_id = os.environ['AUTH_ACCESS_ROLE_ID']
interval_duration = int(os.environ['INTERVAL_DURATION'])

def run_test(script_file, test_dir):
    env = os.environ.copy()
    env["AWS_SHARED_CREDENTIALS_FILE"] = os.path.expanduser("~/auth-access-creds")

    script_path = os.path.join(test_dir, script_file)
    print(f"[{datetime.now()}] Running test: {script_path}")
    result = subprocess.run(['python3.11', 'main.py', script_path], env=env)
    return script_file, result.returncode

def run_tests_parallel():
    test_dir = "tests"
    all_tests = [f for f in os.listdir(test_dir) if f.endswith('.script.md')]
    all_tests = natsorted(all_tests)

    with ThreadPoolExecutor(max_workers=len(all_tests)) as executor:
        futures = [
            executor.submit(run_test, script, test_dir)
            for script in all_tests
        ]

        for future in as_completed(futures):
            script, returncode = future.result()
            print(f"[{datetime.now()}] Test {script} finished with code {returncode}")

def assume_role():
    cmd = f"""
        export AWS_SHARED_CREDENTIALS_FILE=~/auth-access-creds

        aws sts assume-role \
        --role-arn arn:aws:iam::{auth_access_account_id}:role/{auth_access_role_id} \
        --role-session-name auth-session \
        --output json | jq -r '.Credentials |
            "[auth-access]",
            "aws_access_key_id = " + .AccessKeyId,
            "aws_secret_access_key = " + .SecretAccessKey,
            "aws_session_token = " + .SessionToken' \
        > "$AWS_SHARED_CREDENTIALS_FILE"
        """

    subprocess.run(cmd, shell=True, executable="/bin/bash", check=True)

def main():
    while True:
        print(f"[{datetime.now()}] Starting test run loop")
        assume_role()
        run_tests_parallel()
        print(f"[{datetime.now()}] Test run complete. Waiting {interval_duration} seconds.\n")

        time.sleep(interval_duration)  # Wait 'interval_duration' seconds until running the tests again

if __name__ == '__main__':
    main()