import subprocess
import datetime
import sys
import os
from dotenv import load_dotenv
import onepush
import traceback


def load_environment():
    """Load environment variables from .env file."""
    try:
        load_dotenv()
    except Exception as e:
        print(f"ql_guard: Error loading environment variables: {e}")
        sys.exit(1)

def run_guarded():
    command = sys.argv[1:]
    if not command:
        print("ql_guard: No command provided.")
        print("ql_guard: Usage: python3 ql_guard.py <command>")
        return 0
    try:
        result = subprocess.run(command, check=False,shell=True)
        return result.returncode
    except Exception as e:
        print(f"ql_guard: Error executing command:")
        traceback.print_exc()
        return 127

def environ(key):
    """Get environment variable value."""
    return os.environ.get(key)

def push(return_code):
    try:
        now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notifier = onepush.get_notifier(environ("NOTIFIER"))
        response = notifier.notify(token=environ("TOKEN"),secret=environ("SECRET"),
                                      title="QL执行失败提醒",
                                      content=f"命令：{' '.join(sys.argv[1:])} 执行失败，错误码：{return_code}\n时间：{now_date}",
        )
        print(response.text)
        success = False
        errcode = None
        errmsg = None
        try:
            success = response.json().get("errcode") == 0
            errcode = response.json().get("errcode", None)
            errmsg = response.json().get("errmsg","")
        except Exception as e:
            pass
        if success:
            print("ql_guard: Notification sent successfully.")
        else:
            print(f"ql_guard: Failed to send notification, error code: {errcode}, message: {errmsg}")
            print(response.text)
    except Exception as e:
        print(f"ql_guard: Error sending notification:")
        traceback.print_exc()
    

def main():
    load_dotenv()
    return_code = run_guarded()
    if return_code is not None and return_code != 0:
        push(return_code)
        sys.exit(return_code)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()