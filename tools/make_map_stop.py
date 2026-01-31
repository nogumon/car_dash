# tools/make_map_stop.py
from pathlib import Path
import math
import datetime as dt
import folium

LOG = Path("logs/drive.csv")
OUT = Path("logs/drive_map_stop.html")

def to_float(s):
    try:
        return float(s)
    except:
        return None

def shock_color(shock):
    if shock is None:
        return "#808080"
    if shock < 0.5:
        return "#00aa00"   # green
    if shock < 2.0:
        return "#ff9900"   # orange
    return "#ff0000"       # red

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def ts_str(ts):
    # Unix epoch -> readable local time
    try:
        return dt.datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(ts)

def parse_line(line: str):
    line = line.strip()
    if not line:
        return None
    if line.startswith("ts,"):
        return None  # header

    # 先頭から必要なところだけ安全に取る（calのカンマ崩れの影響を受けない位置）
    # ts,lat,lon,gps_status,sats,hdop,alt_m,acc_norm,shock,....
    head = line.split(",", 9)
    if len(head) < 9:
        return None

    ts = to_float(head[0])
    lat = to_float(head[1])
    lon = to_float(head[2])
    shock = to_float(head[8])  # 9番目がshock（calより前）

    if lat is None or lon is None:
        return None

    # 末尾から event / stop_sec / is_stopped / ax を取る（calのカンマ崩れの影響を受けない）
    # ..., ax, is_stopped, stop_sec, event
    tail = line.rsplit(",", 4)
    # tail = [<head...>, ax, is_stopped, stop_sec, event]
    if len(tail) >= 5:
        ax = to_float(tail[1])
        is_stopped = tail[2].strip()  # "True"/"False"
        stop_sec = to_float(tail[3])
        event = tail[4].strip()
    else:
        ax = None
        is_stopped = ""
        stop_sec = None
        event = ""

    return {
        "ts": ts,
        "lat": lat,
        "lon": lon,
        "shock": shock,
        "ax": ax,
        "is_stopped": is_stopped,
        "stop_sec": stop_sec,
        "event": event,
        "raw": line,
    }

def main():
    if not LOG.exists():
        raise SystemExit(f"not found: {LOG}")

    pts = []
    stops = []  # STOP_START の点を入れる

    for line in LOG.read_text(encoding="utf-8", errors="ignore").splitlines():
        row = parse_line(line)
        if row is None:
            continue

        pts.append(row)

        # STOP_START を赤丸にする（必要なら STOP_END も追加できる）
        if row["event"] == "STOP_START":
            stops.append(row)

    if len(pts) < 2:
        raise SystemExit("not enough points (need >=2). try moving a bit.")

    m = folium.Map(location=(pts[0]["lat"], pts[0]["lon"]), zoom_start=16, control_scale=True)

    # 走行線（shock色）
    for a, b in zip(pts, pts[1:]):
        folium.PolyLine(
            [(a["lat"], a["lon"]), (b["lat"], b["lon"])],
            weight=5,
            color=shock_color(b["shock"]),
            opacity=0.9,
        ).add_to(m)

    # START/GOAL
    folium.Marker((pts[0]["lat"], pts[0]["lon"]), tooltip="START", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker((pts[-1]["lat"], pts[-1]["lon"]), tooltip="GOAL", icon=folium.Icon(color="red")).add_to(m)

    # 停止点（赤丸）＋ popup/tooltip
    # popupは「クリック」で出る。tooltipは「ホバー」で出る。
    last = None
    MIN_DIST_M = 30  # 20〜50mあたりがちょうどいい

    for s in stops:
        if last is not None:
            d = haversine_m(last["lat"], last["lon"], s["lat"], s["lon"])
            if d < MIN_DIST_M:
                continue
        last = s

        title = f"STOP_START {ts_str(s['ts'])}"
        detail = f"ax={s['ax']}, stop_sec={s['stop_sec']}"
        folium.CircleMarker(
            location=(s["lat"], s["lon"]),
            radius=7,
            color="#ff0000",
            fill=True,
            fill_color="#ff0000",
            fill_opacity=0.9,
            tooltip=title,
            popup=folium.Popup(f"<b>{title}</b><br>{detail}", max_width=300),
        ).add_to(m)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(OUT))
    print(f"wrote: {OUT.resolve()}")
    print(f"STOP_START points: {len(stops)}")

if __name__ == "__main__":
    main()
