import requests

from kivy.config import Config

DEV_MODE = True  # 開発中は True / 実機は False

if DEV_MODE:
    Config.set('graphics', 'width', '1024')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'fullscreen', '0')
else:
    Config.set('graphics', 'fullscreen', 'auto')

Config.set('graphics', 'resizable', '0')

from kivy.core.window import Window

Window.minimum_width = 0
Window.minimum_height = 0


import os
import subprocess
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


OPENWEATHER_API_KEY = ""  # 必要なら入れる
CITY_QUERY = "Tokyo,jp"
LANG = "ja"
UNITS = "metric"

YTM_URL = "https://music.youtube.com/"
CHROME_PROFILE_DIR = os.path.expanduser("~/.config/chromium_ytm_profile")

# 日本語フォント（fonts-noto-cjk を入れてる前提）
FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
FONT_NAME = "NotoCJK"

def find_font_path():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

def which_cmd(cmd):
    from shutil import which
    return which(cmd)

def detect_chrome_cmd():
    for cmd in ["chromium-browser", "chromium", "google-chrome", "google-chrome-stable"]:
        if which_cmd(cmd):
            return cmd
    return None

def run_cmd(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:
        return 999, "", str(e)

def get_players():
    code, out, _ = run_cmd(["playerctl", "-l"])  # ← -l (エル) が正しい
    if code != 0:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]

def pick_chromium_player():
    players = get_players()
    for p in players:
        if p.startswith("chromium"):
            return p
    return players[0] if players else None

def playerctl(player, *cmd):
    if not player:
        return (1, "", "no player")
    return run_cmd(["playerctl", "-p", player, *cmd])

def get_metadata(player):
    _, title, _ = playerctl(player, "metadata", "xesam:title")
    _, artist, _ = playerctl(player, "metadata", "xesam:artist")
    _, status, _ = playerctl(player, "status")
    return title.strip(), artist.strip().strip("[]"), status.strip()

def get_weather():
    if not OPENWEATHER_API_KEY:
        return None, None
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": CITY_QUERY, "appid": OPENWEATHER_API_KEY, "units": UNITS, "lang": LANG}
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        city = data.get("name")
        temp = data.get("main", {}).get("temp")
        return city, temp
    except Exception:
        return None, None

class CarDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=18, spacing=10, **kwargs)

        # ===== ここから UI 全体 =====
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)

        # --- 上：情報エリア ---
        info = BoxLayout(orientation="vertical", spacing=2, size_hint_y=1)

        self.time_label = Label(
            text="--:--",
            font_size=72,
            bold=True,
            size_hint_y=None,
            height=100,
        )

        self.date_label = Label(
            text="----/--/-- (---)",
            font_size=22,
            size_hint_y=None,
            height=34,
        )

        self.now_title_label = Label(
            text="♪ プレイヤー未検出（Music→再生で検出）",
            font_size=18,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=48,
        )
        self.now_title_label.bind(
            width=lambda *_: setattr(self.now_title_label, "text_size", (self.now_title_label.width, None))
        )

        self.city_label = Label(
            text="City: --",
            font_size=16,
            size_hint_y=None,
            height=26,
        )

        self.temp_label = Label(
            text="Temp: -- ℃",
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=44,
        )

        info.add_widget(self.time_label)
        info.add_widget(self.date_label)
        info.add_widget(self.now_title_label)
        info.add_widget(self.city_label)
        info.add_widget(self.temp_label)
        root.add_widget(info)

        # --- 下：ボタンエリア ---
        btn_area = BoxLayout(orientation="vertical", spacing=8,
                             size_hint_y=1, height=140)

        row1 = BoxLayout(spacing=10, size_hint_y=None, height=56)
        music_btn = Button(text="Music", font_size=26)
        dash_btn = Button(text="Dashboard", font_size=26)
        music_btn.bind(on_press=self.open_music)
        dash_btn.bind(on_press=self.on_dashboard)
        row1.add_widget(music_btn)
        row1.add_widget(dash_btn)

        row2 = BoxLayout(spacing=10, size_hint_y=None, height=56)
        prev_btn = Button(text="Prev", font_size=26)
        pp_btn = Button(text="Play/Pause", font_size=26)
        next_btn = Button(text="Next", font_size=26)
        prev_btn.bind(on_press=self.on_prev)
        pp_btn.bind(on_press=self.on_play_pause)
        next_btn.bind(on_press=self.on_next)
        row2.add_widget(prev_btn)
        row2.add_widget(pp_btn)
        row2.add_widget(next_btn)

        btn_area.add_widget(row1)
        btn_area.add_widget(row2)

        root.add_widget(btn_area)

        self.add_widget(root)
        self.chrome_launched = False
        # ===== ここまで =====


    def update_clock(self, _dt):
        now = datetime.now()
        self.time_label.text = now.strftime("%H:%M")
        self.date_label.text = now.strftime("%Y/%m/%d (%a)")

    def update_weather(self, _dt):
        city, temp = get_weather()
        if city:
            self.city_label.text = f"City: {city}"
        if temp is not None:
            self.temp_label.text = f"Temp: {temp:.1f} °C"

    def refresh_player(self):
        self.player_name = pick_chromium_player()

    def update_music_info(self, _dt):
        if not self.player_name:
            self.refresh_player()
            self.track_label.text = "♪ プレイヤー未検出（Music→再生で検出）"
            self.artist_label.text = ""
            return

        title, artist, status = get_metadata(self.player_name)

        if status.lower() == "playing":
            prefix = "▶"
        elif status.lower() == "paused":
            prefix = "⏸"
        else:
            prefix = "♪"

        if title:
            self.track_label.text = f"{prefix} {title}"
            self.artist_label.text = artist
        else:
            self.track_label.text = "♪ 何も再生していません"
            self.artist_label.text = ""

    # ===== Music：増殖防止 =====
    def open_music(self, *_):
        import os, subprocess, time, shutil

        YTM_URL = "https://music.youtube.com/"
        user_data_dir = os.path.expanduser("~/chromium_ytm_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        # chromium コマンド名が環境で違うことがあるので吸収
        chromium_cmd = (shutil.which("chromium")
                        or shutil.which("chromium-browser")
                        or "chromium")

        def pgrep_pids() -> list[str]:
            cmd = f'pgrep -f "chrom(e|ium).*--user-data-dir={user_data_dir}"'
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                return []
            return [line.strip() for line in r.stdout.splitlines() if line.strip().isdigit()]

        def focus_by_pid(pid: str) -> bool:
            # そのPIDのウィンドウをアクティブ化（複数あっても先頭でOK）
            cmd = f"xdotool search --all --pid {pid} windowactivate --sync %@"
            r = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return r.returncode == 0

        def focus_any_chromium_window() -> bool:
            # クラス名で前面化（環境差あるので複数試す）
            for cls in ("chromium", "Chromium", "chromium-browser"):
                r = subprocess.run(["wmctrl", "-xa", cls],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if r.returncode == 0:
                    return True
            return False

        pids = pgrep_pids()

        # 起動済みなら：前面化を最優先。ダメなら最後に1回だけURLを開く（開かない対策）
        if pids:
            print("[UI] Chromium already running. Focusing window...")
            ok = focus_by_pid(pids[0]) or focus_any_chromium_window()
            if not ok:
                print("[UI] Focus failed -> opening YTM in existing session (fallback)")
                subprocess.Popen([
                    chromium_cmd,
                    f"--user-data-dir={user_data_dir}",
                    "--new-tab",
                    YTM_URL,
                ], start_new_session=True)
            return

        # 起動して前面に
        print("[UI] Launching Chromium (app mode)...")
        subprocess.Popen([
            chromium_cmd,
            f"--user-data-dir={user_data_dir}",
            f"--app={YTM_URL}",
        ], start_new_session=True)

        time.sleep(0.6)
        # 起動直後も前面化を試す
        pids = pgrep_pids()
        if pids:
            focus_by_pid(pids[0]) or focus_any_chromium_window()


    def on_dashboard(self, _instance):
        print("[UI] Dashboard pressed")

    def on_prev(self, _instance):
        print("[UI] Prev pressed")
        self.refresh_player()
        if self.player_name:
            playerctl(self.player_name, "previous")

    def on_play_pause(self, _instance):
        print("[UI] Play/Pause pressed")
        self.refresh_player()
        if self.player_name:
            playerctl(self.player_name, "play-pause")

    def on_next(self, _instance):
        print("[UI] Next pressed")
        self.refresh_player()
        if self.player_name:
            playerctl(self.player_name, "next")

class CarDashboardApp(App):
    def build(self):
        fp = find_font_path()
        if fp:
            LabelBase.register(name=FONT_NAME, fn_regular=fp)
        return CarDashboard()

if __name__ == "__main__":
    CarDashboardApp().run()

