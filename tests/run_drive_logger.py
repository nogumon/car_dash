import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import time
import math
from collections import deque

from sensors.gps_reader import GPSReader

import board
import busio
import adafruit_bno055


def norm3(v):
    if v is None:
        return None
    try:
        x, y, z = v
    except Exception:
        return None
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


def f_float(x, n=6):
    return f"{x:.{n}f}" if isinstance(x, float) else ""


def main():
    gps = GPSReader(port="/dev/serial0", baud=9600)

    i2c = busio.I2C(board.SCL, board.SDA)
    imu = adafruit_bno055.BNO055_I2C(i2c)

    # 停止検出用
    speed_hist = deque(maxlen=5)  # 直近5サンプル(1Hz想定)
    stopped = False
    stop_started_ts = None

    print("ts,lat,lon,gps_status,sats,hdop,alt_m,acc_norm,shock,shock_level,roll,pitch,cal,calib_ok,move_m,judge,speed_kmh,ax,is_stopped,stop_sec,event")

    prev = None
    try:
        while True:
            ts = time.time()
            event = ""

            # --- GPS ---
            fix = gps.read()
            if fix is None:
                time.sleep(0.2)
                continue

            speed_kmh = getattr(fix, "speed_kmh", 0.0) or 0.0
            lat = fix.lat
            lon = fix.lon

            # --- IMU ---
            acc = imu.acceleration
            ax = None
            if acc is not None and len(acc) >= 1 and acc[0] is not None:
                ax = acc[0]

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

            # calibration
            calib_ok = False
            if cal is not None and len(cal) == 4:
                sysc, gyc, accc, magc = cal
                calib_ok = (gyc >= 2 and accc >= 2)
            else:
                cal = (None, None, None, None)

            heading, roll, pitch = eul if eul is not None else (None, None, None)

            # --- 位置ジャンプ検知 ---
            move_m = None
            jump_flag = False
            if (
                prev
                and isinstance(lat, float) and isinstance(lon, float)
                and isinstance(prev["lat"], float) and isinstance(prev["lon"], float)
            ):
                move_m = haversine_m(prev["lat"], prev["lon"], lat, lon)
                # 1秒で150m超は異常（約540km/h）
                if move_m > 150:
                    jump_flag = True

            # --- 停止/発進判定 ---
            speed_hist.append(float(speed_kmh))

            if not stopped:
                # 低速が3回(約3秒)続いたら停止開始
                if len(speed_hist) >= 3 and all(v < 1.0 for v in list(speed_hist)[-3:]):
                    stopped = True
                    stop_started_ts = ts
                    event = "STOP_START"
            else:
                # 発進：速度上昇 or 前後加速
                if speed_kmh > 3.0 or (ax is not None and ax > 0.3):
                    stopped = False
                    event = "STOP_END"
                    stop_started_ts = None

            stop_sec = (ts - stop_started_ts) if (stopped and stop_started_ts) else 0.0

            judge = judge_run(fix.status, calib_ok, shock, jump_flag)

            line = ",".join([
                f"{ts:.3f}",
                f_float(lat, 6),
                f_float(lon, 6),
                fix.status,
                str(fix.sats if fix.sats is not None else ""),
                f"{fix.hdop:.1f}" if isinstance(fix.hdop, float) else "",
                f"{fix.alt_m:.1f}" if isinstance(fix.alt_m, float) else "",
                f"{acc_norm:.2f}" if isinstance(acc_norm, float) else "",
                f"{shock:.2f}" if isinstance(shock, float) else "",
                shock_level,
                f"{roll:.1f}" if isinstance(roll, float) else "",
                f"{pitch:.1f}" if isinstance(pitch, float) else "",
                str(cal),
                str(calib_ok),
                f"{move_m:.1f}" if isinstance(move_m, float) else "",
                judge,
                f"{speed_kmh:.2f}",
                f"{ax:.2f}" if isinstance(ax, float) else "",
                str(stopped),
                f"{stop_sec:.1f}",
                event,
            ])

            print(line)
            prev = {"lat": lat, "lon": lon}

            time.sleep(1)

    finally:
        gps.close()


if __name__ == "__main__":
    main()
