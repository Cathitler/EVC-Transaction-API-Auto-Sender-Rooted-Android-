import subprocess

def send_evc(number, amount):
    subprocess.run(["/data/data/com.termux/files/home/send_evc.sh", number, str(amount)])

# Example
send_evc("615555555", 5)
#replace the number with the number you want to send to or auto it in your app/server, and the 5 is the amount
