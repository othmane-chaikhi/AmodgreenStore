# runn.py - DEBUG VERSION
import pywhatkit
import time
from datetime import datetime

def debug_send():
    print("=== DEBUG MODE ===")
    print("1. Preparing to send...")
    
    recipient = "+212714900687"  # DIRECTLY use formatted number
    test_msg = "🛠️ DEBUG TEST - Please reply 'OK'"
    
    try:
        print("2. Opening browser...")
        # SLOWER but more reliable method
        pywhatkit.sendwhatmsg(
            phone_no=recipient,
            message=test_msg,
            time_hour=datetime.now().hour,
            time_min=datetime.now().minute + 1,  # Send in 1 minute
            wait_time=45,
            tab_close=False,
            close_time=10
        )
        
        print("3. ACTION REQUIRED:")
        print("- Keep Chrome window in foreground")
        print("- Watch it type and send the message")
        print("- Check recipient's phone within 2 minutes")
        
    except Exception as e:
        print(f"🚨 CRITICAL ERROR: {str(e)}")
        print("Immediate checks:")
        print("- Is Chrome installed?")
        print("- Is WhatsApp Web already open in another tab?")
        print("- Is the recipient number blocked?")

if __name__ == "__main__":
    debug_send()
    time.sleep(10)
    input("Press Enter after verifying message status...")