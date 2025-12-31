import os
import sys
import subprocess
from datetime import datetime

import requests

from kivy.config import Config

# =====================
# Display mode
# =====================
DEV_MODE = True  # 開発中は True / 実機は False

if DEV_MODE:
    Config.set("graphics", "width", "800")
    Config.set("graphics", "height", "480")
    Config.set("graphics", "fullscreen", "0")
else:
    Config.set("graphics", "fullscreen", "auto")

Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.stencilview import StencilView

Window.minimum_width = 0
Window.minimum_height = 0

# =====================
# Weather (optional)
# =====================
OPENWEATHER_API_KEY = "ee5aa98cd49e728da0f0bad2e059e8fb"  # 必要なら入れる
CITY_QUERY = "Tokyo,jp"
LANG = "ja"
UNITS = "metric"

# =====================
# YouTube Music
# =====================
YTM_URL = "https://music.youtube.com/"
CHROME_PROFILE_DIR = os.path.expanduser("~/.config/chromium_ytm_profile")

# =====================
# Fonts (Japanese)
# =====================
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


def run_cmd(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:
        return 999, "", str(e)


def get_players():
    code, out, _ = run_cmd(["playerctl", "-l"])  # -l (エル)
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
        self._last_music_press = 0.0
        super().__init__(orientation="vertical", padding=18, spacing=10, **kwargs)

        # ===== marquee state =====
        self._marquee_ev = None
        self._is_marquee_running = False
        self._marquee_speed = 40.0        # px/秒
        self._marquee_blank_sec = 0.6     # 無表示の間（秒）
        self._marquee_pause_until = 0.0
        self._last_track_key = None       # (allow_marquee, text)

        # プレイヤー名
        self.player_name = ""

        # ===== UI =====
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)

        info = BoxLayout(orientation="vertical", spacing=2, size_hint_y=1)

        self.time_label = Label(
            text="--:--",
            font_name=FONT_NAME,
            font_size=72,
            bold=True,
            size_hint_y=None,
            height=100,
        )
        self.date_label = Label(
            text="----/--/-- (---)",
            font_name=FONT_NAME,
            font_size=22,
            size_hint_y=None,
            height=34,
        )

        # 曲名表示（clip）
        self.title_clip = StencilView(size_hint=(1, None), height=48)

        self.now_title_label = Label(
            text="♪ プレイヤー未検出（Music再生で検出）",
            font_name=FONT_NAME,
            font_size=18,
            halign="left",
            valign="middle",
            size_hint=(None, None),
        )
        self.title_clip.add_widget(self.now_title_label)

        # clipレイアウト変化でもスクロール位置を維持
        self._clip_last_x = None
        self.title_clip.bind(size=self._on_title_clip_layout, pos=self._on_title_clip_layout)
        self.now_title_label.bind(text=self._layout_title)

        self.city_label = Label(
            text="City: --",
            font_name=FONT_NAME,
            font_size=16,
            size_hint_y=None,
            height=26,
        )
        self.temp_label = Label(
            text="Temp: -- ℃",
            font_name=FONT_NAME,
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=44,
        )

        info.add_widget(self.time_label)
        info.add_widget(self.date_label)
        info.add_widget(self.title_clip)
        info.add_widget(self.city_label)
        info.add_widget(self.temp_label)
        root.add_widget(info)

        # --- buttons ---
        btn_area = BoxLayout(orientation="vertical", spacing=8, size_hint_y=1, height=140)

        row1 = BoxLayout(spacing=10, size_hint_y=None, height=56)
        music_btn = Button(text="Music", font_name=FONT_NAME, font_size=26)
        dash_btn = Button(text="Dashboard", font_name=FONT_NAME, font_size=26)
        sys_btn = Button(text="System", font_name=FONT_NAME, font_size=26)

        music_btn.bind(on_press=self.open_music)
        dash_btn.bind(on_press=self.on_dashboard)
        sys_btn.bind(on_press=self.open_system)

        row1.add_widget(music_btn)
        row1.add_widget(dash_btn)
        row1.add_widget(sys_btn)

        row2 = BoxLayout(spacing=10, size_hint_y=None, height=56)
        prev_btn = Button(text="Prev", font_name=FONT_NAME, font_size=26)
        pp_btn = Button(text="Play/Pause", font_name=FONT_NAME, font_size=26)
        next_btn = Button(text="Next", font_name=FONT_NAME, font_size=26)

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

        # ----- periodic updates -----
        Clock.schedule_interval(self.update_clock, 1.0)
        Clock.schedule_interval(self.update_music_info, 1.0)
        Clock.schedule_interval(self.update_weather_info, 60.0)

        self.update_clock(0)
        self.update_weather_info(0)
        self.update_music_info(0)

    # =====================
    # Clock / Weather
    # =====================
    def update_clock(self, _dt):
        now = datetime.now()
        self.time_label.text = now.strftime("%H:%M")
        # 曜日（日本語）
        week = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]
        self.date_label.text = now.strftime(f"%Y/%m/%d ({week})")

    def update_weather_info(self, _dt):
        city, temp = get_weather()
        if city is None:
            # API未設定/失敗
            self.city_label.text = "City: --"
            self.temp_label.text = "Temp: -- ℃"
            return
        self.city_label.text = f"City: {city}"
        self.temp_label.text = f"Temp: {temp:.1f} ℃" if isinstance(temp, (int, float)) else f"Temp: {temp} ℃"

    # =====================
    # Title layout / clip move
    # =====================
    def _on_title_clip_layout(self, *_):
        if self._clip_last_x is None:
            self._clip_last_x = self.title_clip.x
            self._layout_title()
            return

        dx = self.title_clip.x - self._clip_last_x
        if abs(dx) > 0.0001:
            # clip移動分だけ平行移動（スクロール位置維持）
            self.now_title_label.x += dx

        self._clip_last_x = self.title_clip.x
        self._layout_title()

    def _layout_title(self, *args):
        self.now_title_label.texture_update()
        lw, _ = self.now_title_label.texture_size

        self.now_title_label.size = (lw, self.title_clip.height)
        self.now_title_label.y = self.title_clip.y

        # 短い → 中央固定（スクロールしない）
        if lw <= self.title_clip.width:
            self.now_title_label.x = self.title_clip.x + (self.title_clip.width - lw) / 2

    # =====================
    # Music update (IMPORTANT: no reset)
    # =====================
    def refresh_player(self):
        self.player_name = pick_chromium_player()

    def update_music_info(self, _dt):
        # プレイヤー未検出：スクロール禁止
        if not self.player_name:
            self.refresh_player()
            self._set_title_text("♪ プレイヤー未検出（Music再生で検出）", allow_marquee=False)
            return

        title, _artist, status = get_metadata(self.player_name)

        st = status.lower()
        if st == "playing":
            prefix = "▶"
        elif st == "paused":
            prefix = "⏸"
        else:
            prefix = "♪"

        if title:
            display = f"{prefix}{title}"
            allow = (st == "playing")  # ★ playing の時だけスクロール
            self._set_title_text(display, allow_marquee=allow)
        else:
            self._set_title_text("♪ 何も再生していません", allow_marquee=False)

    def _set_title_text(self, text: str, allow_marquee: bool):
        # ★ 同じ表示なら何もしない（毎秒リセット防止）
        key = (allow_marquee, text)
        if key == self._last_track_key:
            return

        self._last_track_key = key
        self.now_title_label.text = text
        self._layout_title()

        if allow_marquee:
            # 曲が変わった時だけ再起動
            Clock.schedule_once(lambda dt: self._start_marquee_if_needed(force_restart=True), 0)
        else:
            self._stop_marquee()

    # =====================
    # Marquee (train style)
    # =====================
    def _stop_marquee(self):
        if self._marquee_ev is not None:
            self._marquee_ev.cancel()
            self._marquee_ev = None
        self._is_marquee_running = False
        self._marquee_pause_until = 0.0
        self.now_title_label.opacity = 1

    def _start_marquee_if_needed(self, force_restart: bool = False):
        self.now_title_label.texture_update()
        lw, _ = self.now_title_label.texture_size

        # 短文ならスクロール不要
        if lw <= self.title_clip.width:
            self._stop_marquee()
            self._layout_title()
            return

        # 既に動いていて強制じゃないなら維持
        if self._is_marquee_running and (not force_restart):
            return

        self._stop_marquee()

        # 電車方式：左へ流れ切る→無表示→右端から再出現
        self.now_title_label.opacity = 1
        self.now_title_label.x = self.title_clip.x  # 左端開始
        self._is_marquee_running = True
        self._marquee_ev = Clock.schedule_interval(self._tick_marquee, 1 / 60)

    def _tick_marquee(self, dt):
        import time

        clip_left = self.title_clip.x
        clip_right = self.title_clip.x + self.title_clip.width

        # 無表示待ち中
        if time.time() < self._marquee_pause_until:
            return

        self.now_title_label.x -= self._marquee_speed * dt

        # 末尾が左に完全に消えたら、右端外へ & 無表示時間
        if self.now_title_label.right < clip_left:
            # 右外へ（チラ見え防止に少しオフセット）
            self.now_title_label.x = clip_right + 10
            self._marquee_pause_until = time.time() + self._marquee_blank_sec

    # =====================
    # System popup
    # =====================
    def open_system(self, *_):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=60)
        restart_btn = Button(text="アプリ再起動", font_name=FONT_NAME, font_size=22)
        quit_btn = Button(text="アプリ終了", font_name=FONT_NAME, font_size=22)
        row.add_widget(restart_btn)
        row.add_widget(quit_btn)

        back_btn = Button(text="戻る", font_name=FONT_NAME, font_size=22, size_hint_y=None, height=60)

        content.add_widget(row)
        content.add_widget(back_btn)

        self._system_popup = Popup(
            title="System",
            title_font=FONT_NAME,
            content=content,
            size_hint=(None, None),
            size=(520, 260),
            auto_dismiss=False,
        )

        restart_btn.bind(on_press=lambda *_: self._restart_app())
        quit_btn.bind(on_press=lambda *_: self._quit_app())
        back_btn.bind(on_press=lambda *_: self._system_popup.dismiss())

        self._system_popup.open()

    def _restart_app(self):
        try:
            if hasattr(self, "_system_popup") and self._system_popup:
                self._system_popup.dismiss()
        except Exception:
            pass
        # Kivy のイベントループを止めずにプロセスを入れ替える
        python = sys.executable
        os.execv(python, [python] + sys.argv)

    def _quit_app(self):
        try:
            if hasattr(self, "_system_popup") and self._system_popup:
                self._system_popup.dismiss()
        except Exception:
            pass
        app = App.get_running_app()
        if app:
            app.stop()
        Window.close()

    # =====================
    # Music: chromium focus & prevent duplication
    # =====================
    def open_music(self, *_):
        import time
        import shutil

        now = time.time()
        if now - getattr(self, "_last_music_press", 0.0) < 0.7:
            print("[UI] Music pressed too soon (debounced)")
            return
        self._last_music_press = now

        user_data_dir = os.path.expanduser("~/chromium_ytm_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        chromium_cmd = (
            shutil.which("chromium")
            or shutil.which("chromium-browser")
            or "chromium"
        )

        def pgrep_pids() -> list[str]:
            cmd = f'pgrep -f "chrom(e|ium).*--user-data-dir={user_data_dir}"'
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                return []
            return [line.strip() for line in r.stdout.splitlines() if line.strip().isdigit()]

        def focus_by_pid(pid: str) -> bool:
            cmd = f"xdotool search --all --pid {pid} windowactivate --sync %@"
            r = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return r.returncode == 0

        def focus_any_chromium_window() -> bool:
            for cls in ("chromium", "Chromium", "chromium-browser"):
                r = subprocess.run(["wmctrl", "-xa", cls], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if r.returncode == 0:
                    return True
            return False

        pids = pgrep_pids()
        if pids:
            print("[UI] Chromium already running. Focusing window...")
            ok = focus_by_pid(pids[0]) or focus_any_chromium_window()
            if not ok:
                subprocess.Popen(
                    [chromium_cmd, f"--user-data-dir={user_data_dir}", "--new-tab", YTM_URL],
                    start_new_session=True,
                )
            return

        print("[UI] Launching Chromium (app mode)...")
        subprocess.Popen(
            [chromium_cmd, f"--user-data-dir={user_data_dir}", f"--app={YTM_URL}"],
            start_new_session=True,
        )

        time.sleep(0.6)
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
