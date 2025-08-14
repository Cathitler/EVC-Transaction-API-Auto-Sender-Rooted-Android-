#!/data/data/com.termux/files/usr/bin/bash
# Auto-send EVC+ USSD with PIN (Optimized)
# Requirements: root, Termux, su access

# === CONFIG ===
PIN="2005"  # Your EVC+ PIN

# === INPUT ===
NUMBER="$1"    # Receiver number as argument
AMOUNT="$2"    # Amount as argument

if [ -z "$NUMBER" ] || [ -z "$AMOUNT" ]; then
    echo "Usage: ./send_evc.sh <number> <amount>"
    exit 1
fi

USSD_CODE="*712*$NUMBER*$AMOUNT%23"

# === SEND USSD ===
echo "[*] Initiating USSD..."
su -c "am start -a android.intent.action.CALL -d 'tel:$USSD_CODE'"

# === WAIT FOR POPUP TO OPEN ===
sleep 5  # wait 5 seconds for the USSD dialog to appear

# === ENTER PIN ===
echo "[*] Entering PIN..."
su -c "input text $PIN"

# === PRESS ENTER ===
sleep 2  # small delay before pressing enter
su -c "input keyevent 66"

echo "[*] Done! USSD sent with PIN."
