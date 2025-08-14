import subprocess

def send_evc(number, amount):
    subprocess.run(["/data/data/com.termux/files/home/send_evc.sh", number, str(amount)])

# Example
send_evc("615925885", 5)