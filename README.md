# EVC-Transaction-API-Auto-Sender-Rooted-Android-


---

📡 EVC+ Transaction API & Auto-Sender (Rooted Android)

This project turns your rooted Android phone into a mini EVC+ gateway:

✅ Parse Hormuud EVC+ messages (send/receive) in real time

✅ Save clean JSON records (with unique IDs)

✅ Serve transactions via a tiny Flask API

✅ Send EVC+ via USSD from Termux (auto-PIN, hands-free)


> Built and tested on a Samsung A51 (rooted with Magisk). Other rooted Androids should work similarly.




---

🧩 requirements
 Flask 




---

✅ Prerequisites

Rooted Android (Magisk)

Termux installed

Python 3 on Termux (or chroot, but Termux is easiest)

Flask: pip install flask

For USSD sending: SIM with active EVC+ (*712*<number>*<amount># works in your dialer)



---

🚀 Part 1 — Run the Message Parser API (Flask)

A) Put the file in place

Copy parser/MSgforward.py to your device (Termux or your Kali chroot—Termux recommended).

B) Install Flask

pip install flask

C) Run the server

python3 MSgforward.py

You’ll see something like:

* Running on http://127.0.0.1:5000
* Running on http://<your-lan-ip>:5000

> Keep this running while you test forwarding.




---

🔔 Part 2 — Forward Notifications from Messages → Flask

We’re using the Android app Notification Forward/Save App to shoot message details into your Flask server.

If you don’t see it on Play Store, install the APK from APKPure:
https://apkpure.com/push-notification-forward-http/com.jojoagogogo.nf


One-time setup (step-by-step)

1. Install & open “Notification Forward/Save App”.


2. It’ll ask for Notification Access. Enable it (Settings → Notifications → Notification access → allow for this app).


3. In the app, scroll the list and find your default Messages app (e.g., “Messages”, package com.samsung.android.messaging).


4. Tap it.


5. Find “Forward URL” and set it to your Flask server:

If the forwarder app and Flask run on the same phone:
http://127.0.0.1:5000

If Flask runs elsewhere on your LAN:
http://<your-phone-or-computer-lan-ip>:5000



6. HTTP Method: set to GET (important).


7. Scroll down and Save.


8. Send yourself a test EVC+ (or wait for one).


9. In the Flask console, you should see a parsed JSON like:

{
  "type": "received",
  "amount": 0.5,
  "counterparty": "06",
  "transaction_datetime": "2025-08-14T16:43:28",
  "new_balance": 1.99,
  "id": "8878ef30-c464-4fb2-99d8-5c6e9ea4a665"
}



What gets parsed

Received:
[-EVCPlus-] waxaad $X ka heshay <number>, Tar: dd/mm/yy HH:MM:SS haraagagu waa $Y.

Send:
[-EVCPLUS-] $X ayaad uwareejisay <number>, Tar: dd/mm/yy HH:MM:SS, Haraagaagu waa $Y.


We also ignore non-Hormuud messages (title must be 192),

Where it stores data

A local JSON file: evc_messages.json (same folder as MSgforward.py)


API endpoints (from your Flask server)

GET /transactions → full list (the JSON file contents)

GET /transactions/<id> → a single transaction by its unique id



---

📲 Part 3 — Send EVC+ Automatically (USSD + auto PIN)

We’ll do this entirely on the phone with Termux (root).

A) Give Termux storage access (first time only)

termux-setup-storage

Allow the permission prompt.

B) Create/edit the shell script (with nano)

1. Open Termux and run:

cd ~
nano send_evc.sh


2. Paste this (edit PIN to yours):

#!/data/data/com.termux/files/usr/bin/bash
# Auto-send EVC+ USSD with PIN (root required)

PIN="2005"  # CHANGE THIS to your real PIN

NUMBER="$1"    # arg1: receiver number (e.g. 615555555)
AMOUNT="$2"    # arg2: amount (e.g. 1)

if [ -z "$NUMBER" ] || [ -z "$AMOUNT" ]; then
    echo "Usage: ./send_evc.sh <number> <amount>"
    exit 1
fi

USSD_CODE="*712*$NUMBER*$AMOUNT%23"  # %23 is '#'

echo "[*] Initiating USSD..."
su -c "am start -a android.intent.action.CALL -d 'tel:$USSD_CODE'"

# Wait for the USSD popup
sleep 3

echo "[*] Entering PIN..."
su -c "input text $PIN"

# Small delay, then press ENTER (OK)
sleep 1
su -c "input keyevent 66"

echo "[*] Done! USSD sent with PIN."


3. Save & exit nano: CTRL+X, then Y, then ENTER.


4. Make it executable:

chmod +x ~/send_evc.sh



C) Run it

./send_evc.sh 615555555 1

You should see:

[*] Initiating USSD...
[*] Entering PIN...
[*] Done! USSD sent with PIN.

> If PIN isn’t entered, increase sleep 3 to sleep 4 or sleep 5 depending on your phone speed.




---

🐍 Optional: Call the sender from Python

If you prefer Python (e.g., to integrate with your bot):

1. Put send_EVCPlus.py anywhere (e.g., /storage/emulated/0/cex_exchange/send_EVCPlus.py)


2. In Termux:

cd /storage/emulated/0/cex_exchange/
python3 send_EVCPlus.py

(Make sure send_EVCPlus.py calls your script path, e.g. ~/send_evc.sh)



A minimal Python wrapper looks like:

import subprocess

def send_evc(number: str, amount):
    subprocess.run(["/data/data/com.termux/files/home/send_evc.sh",
                    number, str(amount)])

# Example
send_evc("615555555", 5)


---

🔐 Security tips (important!)

Do not commit your real PIN or phone numbers to GitHub.

Add a .gitignore entry for local files:

evc_messages.json
*.log
__pycache__/
*.pyc

Consider keeping your PIN in an environment variable or a separate, ignored config file.



---

🛠 Troubleshooting

No PIN entry / USSD popup too slow
Increase the first sleep 3 to 4–5.

Permission Denied / CALL_PHONE error
Make sure commands run via su -c ... so they have system privileges.

Flask not receiving anything

Ensure the Forward URL points to your phone’s correct IP or 127.0.0.1 if same device.

Make sure HTTP Method = GET in the forwarder app.

Confirm you see the “Messages” app selected in the forwarder list.


Wrong sender
The parser only trusts title=192 (official Hormuud short code). Anything else is ignored.



---

Disclaimer

You’re interacting with a mobile wallet via USSD. Test with tiny amounts first. You are responsible for all transactions sent with these scripts.
