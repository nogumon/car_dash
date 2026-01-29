import math
import time
import board
import busio
import adafruit_bno055

print("[BOOT] test_bno055 starting...")

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

print("[BOOT] sensor opened.")

def norm3(v):
    if v is None:
        return None
    x, y, z = v
    return math.sqrt(x*x + y*y + z*z)

while True:
    acc = sensor.acceleration
    eul = sensor.euler
    cal = sensor.calibration_status  # (sys, gyro, accel, mag)

    acc_norm = norm3(acc)  # m/s^2
    # 重力(約9.806)との差分＝「揺れ/衝撃」っぽい値
    shock = abs(acc_norm - 9.806) if acc_norm is not None else None

    # 判定（目安）
    # 0.5未満:安定 / 0.5-2:揺れ / 2以上:衝撃
    if shock is None:
        shock_level = "?"
    elif shock < 0.5:
        shock_level = "STABLE"
    elif shock < 2.0:
        shock_level = "SHAKE"
    else:
        shock_level = "IMPACT"

    # 校正判定：車載なら gyroとaccelが2以上なら一旦OK扱い
    sysc, gyc, accc, magc = cal
    calib_ok = (gyc >= 2 and accc >= 2)

    heading, roll, pitch = eul if eul is not None else (None, None, None)

    print(
        f"acc={acc} | |a|={acc_norm:.2f} shock={shock:.2f}({shock_level}) "
        f"| euler(h,r,p)=({heading},{roll},{pitch}) "
        f"| cal={cal} calib_ok={calib_ok}"
    )
    time.sleep(0.2)
