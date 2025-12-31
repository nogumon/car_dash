import requests

from kivy.config import Config

DEV_MODE = True  # 開発中は True / 実機は False

if DEV_MODE:
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '480')
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
from kivy.uix.stencilview import StencilView

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
        self._last_music_press = 0.0
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

        # --- 曲名表示（スクロール対応） ---
        self.title_clip = StencilView(
            size_hint=(1, None),
            height=48,
        )

        self.now_title_label = Label(
            text="♪ プレイヤー未検出 (Music再生で検出)",
            font_size=18,
            halign="left",
            valign="middle",
            size_hint=(None, None),
        )

        self.title_clip.add_widget(self.now_title_label)

        # レイアウト更新（size/pos）でスクロール位置が飛ばないようにする
        self._clip_last_x = None
        self._clip_last_w = None
        self.title_clip.bind(size=self._on_title_clip_layout, pos=self._on_title_clip_layout)

        # textが変わった時はサイズ確定だけ（xはスクロール中なら触らない）
        self.now_title_label.bind(text=self._layout_title)

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
        info.add_widget(self.title_clip)
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

        # ===== marquee state =====
        self._marquee_ev = None
        self._is_marquee_running = False
        self._marquee_speed = 40.0          # px/秒
        self._marquee_blank_sec = 0.6       # 無表示の間（秒）
        self._marquee_pause_until = 0.0

        # 「曲名更新/状態更新」があった時だけ表示を変える
        self._last_track_key = None  # (status, title) を覚える

        self.player_name = ""

        Clock.schedule_interval(self.update_music_info, 1.0)
        self.update_music_info(0)

        # ===== ここまで =====

    # --- clip が動いた時、スクロール位置を維持する ---
    def _on_title_clip_layout(self, *_):
        # 初回だけ記録して抜ける
        if self._clip_last_x is None:
            self._clip_last_x = self.title_clip.x
            self._clip_last_w = self.title_clip.width
            # 初回は普通にレイアウト確定
            self._layout_title()
            return

        dx = self.title_clip.x - self._clip_last_x
        # clipが動いた分だけ、ラベルも平行移動（＝見た目の位置を維持）
        if abs(dx) > 0.0001:
            self.now_title_label.x += dx
            if hasattr(self, "now_title_label2"):
                self.now_title_label2.x += dx

        self._clip_last_x = self.title_clip.x
        self._clip_last_w = self.title_clip.width

        # サイズ確定（xは基本触らない）
        self._layout_title()

    def _layout_title(self, *args):
        # texture確定
        self.now_title_label.texture_update()
        lw, lh = self.now_title_label.texture_size

        # ラベルのサイズと縦位置だけ決める（xはスクロール中なら触らない）
        self.now_title_label.size = (lw, self.title_clip.height)
        self.now_title_label.y = self.title_clip.y

        # 短い → 中央固定（スクロールしない）
        if lw <= self.title_clip.width:
            self.now_title_label.x = self.title_clip.x + (self.title_clip.width - lw) / 2

    def refresh_player(self):
        self.player_name = pick_chromium_player()

    def update_music_info(self, _dt):
        # プレイヤー未検出中はスクロールさせない
        if not self.player_name:
            self.refresh_player()
            self._set_title_text("♪ プレイヤー未検出（Music再生で検出）", allow_marquee=False)
            return

        title, artist, status = get_metadata(self.player_name)

        if status.lower() == "playing":
            prefix = "▶"
        elif status.lower() == "paused":
            prefix = "⏸"
        else:
            prefix = "♪"

        if title:
            display = f"{prefix}{title}"
            allow = (status.lower() == "playing")  # ★playingの時だけスクロール
            self._set_title_text(display, allow_marquee=allow)
        else:
            # 何も再生してない → スクロール停止
            self._set_title_text("♪ 何も再生していません", allow_marquee=False)

    # --- 「同じ曲名なら触らない」：これで毎秒リセットが消える ---
    def _set_title_text(self, text: str, allow_marquee: bool):
        # ここでは status/title の変化のみを検出したいのでキー化
        key = (allow_marquee, text)

        if key == self._last_track_key:
            # 同じ表示なら何もしない（＝スクロール位置が維持される）
            return

        self._last_track_key = key
        self.now_title_label.text = text

        # サイズ確定（短いなら中央へ）
        self._layout_title()

        if allow_marquee:
            # 曲が変わった時だけ marquee を始動（最初からやり直しでOK）
            Clock.schedule_once(lambda dt: self._start_marquee_if_needed(force_restart=True), 0)
        else:
            self._stop_marquee()

    def _stop_marquee(self):
        ev = getattr(self, "_marquee_ev", None)
        if ev is not None:
            ev.cancel()
            self._marquee_ev = None
        self._is_marquee_running = False

        # 2枚目があれば隠す（今は使わないが一応）
        if hasattr(self, "now_title_label2"):
            self.now_title_label2.opacity = 0

    def _start_marquee_if_needed(self, force_restart: bool = False):
        # playing以外や、短文ならここに来ない想定だが保険で止める
        self.now_title_label.texture_update()
        lw, _ = self.now_title_label.texture_size

        if lw <= self.title_clip.width:
            self._stop_marquee()
            self._layout_title()
            return

        # すでに動いてて、強制再起動じゃないなら何もしない（位置維持）
        if self._is_marquee_running and (not force_restart):
            return

        # 再起動する
        self._stop_marquee()

        self._marquee_pause_until = 0.0

        # 「電車内案内」方式：末尾が流れ切る→無表示→右端から出てくる
        self.now_title_label.opacity = 1
        self.now_title_label.x = self.title_clip.x  # 左端から開始
        self._is_marquee_running = True
        self._marquee_ev = Clock.schedule_interval(self._tick_marquee, 1/60)

    def _tick_marquee(self, dt):
        import time

        speed = getattr(self, "_marquee_speed", 40.0)
        blank = getattr(self, "_marquee_blank_sec", 0.6)

        a = self.now_title_label
        clip_left = self.title_clip.x
        clip_right = self.title_clip.x + self.title_clip.width

        # 無表示(待ち)中なら何もしない（＝「一度消える」を作る）
        pause_until = getattr(self, "_marquee_pause_until", 0.0)
        if time.time() < pause_until:
            return

        # 左へ移動
        dx = speed * dt
        a.x -= dx

        # 末尾が完全に左へ消えたら
        if a.right < clip_left:
            # ほんの少し右にオフセット（チラ見え防止）
            a.x = clip_right + 6

            # 無表示の間を作る
            self._marquee_pause_until = time.time() + blank

    # ===== Music：増殖防止 =====
    def open_music(self, *_):
        import time

        now = time.time()
        if now - getattr(self, "_last_music_press", 0.0) < 0.7:
            print("[UI] Music pressed too soon (debounced)")
            return
        self._last_music_press = now

        import os, subprocess, time, shutil

        YTM_URL = "https://music.youtube.com/"
        user_data_dir = os.path.expanduser("~/chromium_ytm_profile")
        os.makedirs(user_data_dir, exist_ok=True)

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
            cmd = f"xdotool search --all --pid {pid} windowactivate --sync %@"
            r = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return r.returncode == 0

        def focus_any_chromium_window() -> bool:
            for cls in ("chromium", "Chromium", "chromium-browser"):
                r = subprocess.run(["wmctrl", "-xa", cls],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if r.returncode == 0:
                    return True
            return False

        pids = pgrep_pids()

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

        print("[UI] Launching Chromium (app mode)...")
        subprocess.Popen([
            chromium_cmd,
            f"--user-data-dir={user_data_dir}",
            f"--app={YTM_URL}",
        ], start_new_session=True)

        time.sleep(0.6)
        pids = pgrep_pids()
        if pids:
            focus_by_pid(pids[0]) or focus_any_chromium_window()

    def is_music_ready(self) -> bool:
        import subprocess
        r = subprocess.run(
            "playerctl -l",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        if r.returncode != 0:
            return False

        players = [line.strip() for line in r.stdout.splitlines() if line.strip()]
        return len(players) > 0

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


