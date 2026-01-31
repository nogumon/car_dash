import csv
from pathlib import Path
import folium

LOG = Path("logs/drive.csv")
OUT = Path("logs/drive_map.html")

def to_float(s):
    try:
        return float(s)
    except:
        return None

def shock_color(shock):
    if shock is None:
        return "#808080"
    if shock < 0.5:
        return "#00aa00"
    if shock < 2.0:
        return "#ff9900"
    return "#ff0000"

def main():
    if not LOG.exists():
        raise SystemExit(f"not found: {LOG}")

    pts = []
    with LOG.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            lat = to_float(row.get("lat", ""))
            lon = to_float(row.get("lon", ""))
            if lat is None or lon is None:
                continue

            shock = to_float(row.get("shock", ""))
            judge = row.get("judge", "")
            event = row.get("event", "")
            stop_sec = to_float(row.get("stop_sec", ""))

            pts.append((lat, lon, shock, judge, event, stop_sec))

    if len(pts) < 2:
        raise SystemExit("not enough points")

    m = folium.Map(location=(pts[0][0], pts[0][1]), zoom_start=16, control_scale=True)

    # ルート
    for (lat1, lon1, _s1, _j1, _e1, _t1), (lat2, lon2, s2, j2, _e2, _t2) in zip(pts, pts[1:]):
        folium.PolyLine(
            [(lat1, lon1), (lat2, lon2)],
            weight=5,
            color=shock_color(s2),
            opacity=0.9,
        ).add_to(m)

    for lat, lon, shock, judge, event, stop_sec in pts:
        if event == "STOP_START":
            popup_html = (
                f"<b>STOP</b><br>"
                f"停止時間: {stop_sec:.1f} 秒<br>"
                f"判定: {judge}"
            )

            folium.CircleMarker(
                location=(lat, lon),
                radius=7,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.95,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

    folium.Marker((pts[0][0], pts[0][1]), tooltip="START", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker((pts[-1][0], pts[-1][1]), tooltip="GOAL", icon=folium.Icon(color="red")).add_to(m)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(OUT))
    print(f"wrote: {OUT.resolve()}")

if __name__ == "__main__":
    main()
