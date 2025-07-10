import os
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
auth_access_account_id = os.environ['AUTH_ACCESS_ACCOUNT_ID']
auth_access_role_id = os.environ['AUTH_ACCESS_ROLE_ID']
interval_duration = int(os.environ['INTERVAL_DURATION'])

def run_tests():
    test_dir = 'tests'
    selected_tests = ['test-5.script.md', 'test-6.script.md', 'test-8.script.md', 'test-9.script.md', 'test-10.script.md']

    env = os.environ.copy()
    env["AWS_SHARED_CREDENTIALS_FILE"] = os.path.expanduser("~/auth-access-creds")

    for i, script_file in enumerate(selected_tests):
        script_path = os.path.join(test_dir, script_file)
        print(f"[{datetime.now()}] Running test: {script_path}")
        subprocess.run(['python3.11', 'main.py', script_path], env=env)

        if i < len(selected_tests) - 1:
            print("Waiting 30 seconds before next test.\n")
            time.sleep(30)

def assume_role():
    cmd = f"""
        export AWS_SHARED_CREDENTIALS_FILE=~/auth-access-creds

        aws sts assume-role \
        --role-arn arn:aws:iam::{auth_access_account_id}:role/{auth_access_role_id} \
        --role-session-name auth-session \
        --duration-seconds 43200 \
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
        run_tests()
        print(f"[{datetime.now()}] Test run complete. Waiting {interval_duration} seconds.\n")
        time.sleep(interval_duration)  # Wait 'interval_duration' seconds until running the tests again

if __name__ == '__main__':
    main()