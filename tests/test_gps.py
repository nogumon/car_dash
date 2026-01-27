import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import time
import traceback
from sensors.gps_reader import GPSReader

print("[BOOT] test_gps starting...")

def fmt(x, nd=6):
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return "None"

try:
    gps = GPSReader(port="/dev/serial0", baud=9600)
    print("[BOOT] GPSReader opened")

    while True:
        fix = gps.read()
        hdop = f"{fix.hdop:.1f}" if isinstance(fix.hdop, float) else "None"
        alt  = f"{fix.alt_m:.1f}m" if isinstance(fix.alt_m, float) else "None"
        print(
            f"lat={fmt(fix.lat)}, lon={fmt(fix.lon)}, "
            f"sats={fix.sats}, hdop={hdop}, fixq={fix.fixq}, alt={alt} -> {fix.status}"
        )
        time.sleep(1)

except Exception as e:
    print("[ERROR]", e)
    traceback.print_exc()

finally:
    try:
        gps.close()
        print("[BOOT] closed")
    except Exception:
        pass