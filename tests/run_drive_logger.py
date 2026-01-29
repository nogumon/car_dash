import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import time
import math

from sensors.gps_reader import GPSReader

import board
import busio
import adafruit_bno055


def norm3(v):
    if v is None:
        return None
    x, y, z = v
    if x is None or y is None or z is None:
        return None
    return math.sqrt(x*x + y*y + z*z)


def judge_run(gps_status, calib_ok, shock, jump_flag):
    # “走行ログの品質”判定
    if gps_status == "NG":
        return "NG(GPS)"
    if not calib_ok:
        return "WARN(CAL)"
    if jump_flag:
        return "WARN(JUMP)"
    if shock is None:
        return "WARN(SHOCK?)"
    if shock >= 2.0:
        return "WARN(IMPACT)"
    return "OK"


def haversine_m(lat1, lon1, lat2, lon2):
    # lat/lon: degrees
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def main():
    gps = GPSReader(port="/dev/serial0", baud=9600)

    i2c = busio.I2C(board.SCL, board.SDA)
    imu = adafruit_bno055.BNO055_I2C(i2c)

    print("ts,lat,lon,gps_status,sats,hdop,alt_m,acc_norm,shock,shock_level,roll,pitch,cal,calib_ok,move_m,judge")

    prev = None
    try:
        while True:
            ts = time.time()

            fix = gps.read()
            lat = fix.lat
            lon = fix.lon

            acc = imu.acceleration
            eul = imu.euler
            cal = imu.calibration_status  # (sys, gyro, accel, mag)

            acc_norm = norm3(acc)
            shock = abs(acc_norm - 9.806) if acc_norm is not None else None

            if shock is None:
                shock_level = "?"
            elif shock < 0.5:
                shock_level = "STABLE"
            elif shock < 2.0:
                shock_level = "SHAKE"
            else:
                shock_level = "IMPACT"

            sysc, gyc, accc, magc = cal
            calib_ok = (gyc >= 2 and accc >= 2)

            heading, roll, pitch = eul if eul is not None else (None, None, None)

            # 位置ジャンプ検知（1秒間の移動距離が異常ならWARN）
            move_m = None
            jump_flag = False
            if prev and isinstance(lat, float) and isinstance(lon, float) and isinstance(prev["lat"], float) and isinstance(prev["lon"], float):
                move_m = haversine_m(prev["lat"], prev["lon"], lat, lon)
                # 1秒で150m超は普通の車載ではほぼ異常（=540km/h相当）
                if move_m > 150:
                    jump_flag = True

            judge = judge_run(fix.status, calib_ok, shock, jump_flag)

            def f(x, n=6):
                return f"{x:.{n}f}" if isinstance(x, float) else ""

            line = ",".join([
                f"{ts:.3f}",
                f(lat, 6),
                f(lon, 6),
                fix.status,
                str(fix.sats if fix.sats is not None else ""),
                f"{fix.hdop:.1f}" if isinstance(fix.hdop, float) else "",
                f"{fix.alt_m:.1f}" if isinstance(fix.alt_m, float) else "",
                f"{acc_norm:.2f}" if isinstance(acc_norm, float) else "",
                f"{shock:.2f}" if isinstance(shock, float) else "",
                shock_level,
                f"{roll:.1f}" if isinstance(roll, float) else "",
                f"{pitch:.1f}" if isinstance(pitch, float) else "",
                f"{cal}",
                str(calib_ok),
                f"{move_m:.1f}" if isinstance(move_m, float) else "",
                judge,
            ])

            print(line)

            prev = {"lat": lat, "lon": lon}
            time.sleep(1)

    finally:
        gps.close()


if __name__ == "__main__":
    main()
