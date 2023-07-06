import subprocess

def cmd(cmd_str: str):
    output = subprocess.run(cmd_str, shell=True, capture_output=True)
    return output.stdout.decode('UTF-8')
