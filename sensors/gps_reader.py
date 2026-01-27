import time
import serial
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class GPSFix:
    lat: Optional[float] = None
    lon: Optional[float] = None
    alt_m: Optional[float] = None
    sats: Optional[int] = None
    hdop: Optional[float] = None
    fixq: Optional[int] = None  # 0 invalid, 1 GPS, 2 DGPS...
    status: str = "NG"          # OK / WARN / NG
    ts: float = 0.0             # time.time()


def _nmea_to_deg(value: str, direction: str) -> Optional[float]:
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


def _to_int(x: str) -> Optional[int]:
    try:
        return int(x) if x != "" else None
    except Exception:
        return None


def _to_float(x: str) -> Optional[float]:
    try:
        return float(x) if x != "" else None
    except Exception:
        return None


def _judge(fixq: Optional[int], sats: Optional[int], hdop: Optional[float]) -> str:
    if fixq is None or fixq == 0:
        return "NG"
    # Fixあり
    if sats is not None and hdop is not None:
        if sats >= 5 and hdop <= 2.5:
            return "OK"
        if sats >= 4 and hdop <= 4.0:
            return "WARN"
        return "NG"
    return "WARN"


class GPSReader:
    """
    GGAから緯度経度・衛星数・HDOP・高度・Fix品質を取り、OK/WARN/NG判定して返す。
    - read(): 最新のGPSFixを返す（データ無ければ最後の値）
    - close(): シリアルを閉じる
    """

    def __init__(self, port: str = "/dev/serial0", baud: int = 9600, timeout: float = 1.0,
                 reopen_wait: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.reopen_wait = reopen_wait

        self._ser: Optional[serial.Serial] = None
        self._last = GPSFix(ts=time.time())

        self._open()

    def _open(self):
        self._ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        time.sleep(0.3)

    def close(self):
        try:
            if self._ser:
                self._ser.close()
        except Exception:
            pass
        self._ser = None

    def _reopen(self):
        self.close()
        time.sleep(self.reopen_wait)
        self._open()

    def _parse_gga(self, line: str) -> Optional[GPSFix]:
        p = line.split(",")
        if len(p) < 10:
            return None

        lat = _nmea_to_deg(p[2], p[3])
        lon = _nmea_to_deg(p[4], p[5])
        fixq = _to_int(p[6])
        sats = _to_int(p[7])
        hdop = _to_float(p[8])
        alt = _to_float(p[9])

        status = _judge(fixq, sats, hdop)

        return GPSFix(
            lat=lat,
            lon=lon,
            alt_m=alt,
            sats=sats,
            hdop=hdop,
            fixq=fixq,
            status=status,
            ts=time.time(),
        )

    def read(self, max_lines: int = 50) -> GPSFix:
        """
        最大 max_lines 行だけ読み、GGAが来たら最新値を更新して返す。
        """
        if not self._ser:
            self._reopen()

        try:
            for _ in range(max_lines):
                raw = self._ser.readline()
                if not raw:
                    break
                line = raw.decode("ascii", errors="ignore").strip()
                if line.startswith("$GNGGA") or line.startswith("$GPGGA"):
                    fix = self._parse_gga(line)
                    if fix:
                        self._last = fix
                        break
        except serial.SerialException:
            # 一瞬途切れても復帰
            self._reopen()
        except Exception:
            # 予期せぬ例外でも落とさない（テスト用途）
            pass

        return self._last