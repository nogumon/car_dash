import serial
import time

PORT = "/dev/serial0"
BAUD = 9600

def nmea_to_deg(value: str, direction: str):
    if not value or not direction:
        return None
    try:
        if direction in ("N", "S"):
            deg = int(value[:2])
            minute = float(value[2:])
        else:  # E, W
            deg = int(value[:3])
            minute = float(value[3:])
        dec = deg + minute / 60.0
        if direction in ("S", "W"):
            dec = -dec
        return dec
    except Exception:
        return None

def judge(fixq, sats, hdop):
    # fixq: 0=invalid, 1=GPS fix, 2=DGPS...
    if fixq is None or fixq == 0:
        return "NG"
    # ここからFixあり
    if sats is not None and hdop is not None:
        if sats >= 5 and hdop <= 2.5:
            return "OK"
        if sats >= 4 and hdop <= 4.0:
            return "WARN"
        return "NG"
    # データ欠けたら一旦WARN
    return "WARN"

def parse_gga(line: str):
    # $GPGGA / $GNGGA
    p = line.split(",")
    # index: 2=lat,3=N/S,4=lon,5=E/W,6=fixq,7=sats,8=hdop,9=alt
    if len(p) < 10:
        return None

    lat = nmea_to_deg(p[2], p[3])
    lon = nmea_to_deg(p[4], p[5])

    def to_int(x):
        try:
            return int(x) if x != "" else None
        except Exception:
            return None

    def to_float(x):
        try:
            return float(x) if x != "" else None
        except Exception:
            return None

    fixq = to_int(p[6])
    sats = to_int(p[7])
    hdop = to_float(p[8])
    alt = to_float(p[9])

    return {
        "lat": lat,
        "lon": lon,
        "fixq": fixq,
        "sats": sats,
        "hdop": hdop,
        "alt": alt,
    }

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(1)

    print("lat, lon, sats, hdop, fixq, alt -> status")
    while True:
        line = ser.readline().decode("ascii", errors="ignore").strip()
        if not (line.startswith("$GNGGA") or line.startswith("$GPGGA")):
            continue

        data = parse_gga(line)
        if not data:
            continue

        status = judge(data["fixq"], data["sats"], data["hdop"])

        lat = data["lat"]
        lon = data["lon"]
        sats = data["sats"]
        hdop = data["hdop"]
        fixq = data["fixq"]
        alt = data["alt"]

        # lat/lonはFix無いとNoneになることがあるので安全に
        lat_s = f"{lat:.6f}" if isinstance(lat, float) else "None"
        lon_s = f"{lon:.6f}" if isinstance(lon, float) else "None"
        hdop_s = f"{hdop:.1f}" if isinstance(hdop, float) else "None"
        alt_s  = f"{alt:.1f}m" if isinstance(alt, float) else "None"

        print(f"lat={lat_s}, lon={lon_s}, sats={sats}, hdop={hdop_s}, fixq={fixq}, alt={alt_s} -> {status}")

if __name__ == "__main__":
    main()