from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

import datetime
import threading
import requests
import subprocess

# ====== 設定 ======
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"   # ←自分のキーに
CITY    = "Tokyo,jp"
UNITS   = "metric"
LANG    = "en"
WEATHER_UPDATE_INTERVAL = 600
JP_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
# スクロール関連
SCROLL_INTERVAL = 0.5   # 何秒ごとに1文字進めるか
SCROLL_WINDOW   = 30    # 一度に表示する文字数の目安
# ==================


class CarDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)

        self.music_proc = None  # YouTube Music 用

        # NowPlaying の元のフルタイトル＆スクロール位置
        self.full_title = ""
        self.scroll_pos = 0

        # ---------- 一段目：時刻 ----------
        time_box = BoxLayout(
            orientation='vertical',
            size_hint_y=0.25,
            spacing=10
        )

        self.time_label = Label(
            text="00:00",
            font_size=80,
            halign='center',
            valign='middle',
        )
        self.time_label.bind(size=self._update_label_size)

        self.date_label = Label(
            text="----/--/-- (---)",
            font_size=28,
            halign='center',
            valign='middle',
        )
        self.date_label.bind(size=self._update_label_size)

        time_box.add_widget(self.time_label)
        time_box.add_widget(self.date_label)

        # ---------- 二段目：Now Playing ----------
        now_box = BoxLayout(orientation='vertical', size_hint_y=0.20, spacing=5)

        self.now_title_label = Label(
            text="♪ 何も再生していません",
            font_size=24,
            halign='center',
            valign='middle',
            font_name=JP_FONT,
        )
        self.now_title_label.bind(size=self._update_label_size)

        self.now_artist_label = Label(
            text="",
            font_size=18,
            halign='center',
            valign='middle',
            font_name=JP_FONT,
        )
        self.now_artist_label.bind(size=self._update_label_size)

        now_box.add_widget(self.now_title_label)
        now_box.add_widget(self.now_artist_label)

        # ---------- 三段目：天気 ----------
        weather_box = GridLayout(
            cols=1,
            size_hint_y=0.20,
            row_force_default=True,
            row_default_height=40,
            spacing=5
        )

        self.city_label = Label(
            text=f"City: {CITY}",
            font_size=22,
            halign='center',
            valign='middle',
            font_name=JP_FONT,
        )
        self.city_label.bind(size=self._update_label_size)

        self.temp_label = Label(
            text="Temp: -- C",
            font_size=28,
            halign='center',
            valign='middle',
            font_name=JP_FONT,
        )
        self.temp_label.bind(size=self._update_label_size)

        weather_box.add_widget(self.city_label)
        weather_box.add_widget(self.temp_label)

        # ---------- 四段目：アプリ切り替え ----------
        switch_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.15,
            spacing=40
        )

        music_btn = Button(text="Music", font_size=28, on_press=self.open_music)
        dash_btn  = Button(text="Dashboard", font_size=28, on_press=self.open_dashboard)

        switch_box.add_widget(music_btn)
        switch_box.add_widget(dash_btn)

        # ---------- 五段目：音楽操作 ----------
        controls_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.20,
            spacing=20
        )

        prev_btn = Button(text="Prev", font_size=28, on_press=self.on_prev)
        play_btn = Button(text="Play/Pause", font_size=28, on_press=self.on_play_pause)
        next_btn = Button(text="Next", font_size=28, on_press=self.on_next)

        controls_box.add_widget(prev_btn)
        controls_box.add_widget(play_btn)
        controls_box.add_widget(next_btn)

        # ---------- 全体 ----------
        self.add_widget(time_box)
        self.add_widget(now_box)
        self.add_widget(weather_box)
        self.add_widget(switch_box)
        self.add_widget(controls_box)

        # 時刻更新
        Clock.schedule_interval(self.update_time, 1)

        # 天気
        Clock.schedule_once(self.fetch_weather, 0)
        Clock.schedule_interval(self.fetch_weather, WEATHER_UPDATE_INTERVAL)

        # Now Playing 更新（曲変更検出）
        Clock.schedule_interval(self.update_now_playing, 2)

        # タイトルスクロール（見た目用）
        Clock.schedule_interval(self.scroll_title, SCROLL_INTERVAL)

    # ラベル折り返し
    def _update_label_size(self, instance, value):
        instance.text_size = (value[0], None)

    # 時刻更新
    def update_time(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime("%H:%M")

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        wd = weekdays[now.weekday()]
        self.date_label.text = now.strftime(f"%Y/%m/%d ({wd})")

    # 天気取得
    def fetch_weather(self, dt):
        if "YOUR_OPENWEATHERMAP_API_KEY" in API_KEY:
            return

        def _worker():
            try:
                url = (
                    "https://api.openweathermap.org/data/2.5/weather"
                    f"?q={CITY}&appid={API_KEY}&units={UNITS}&lang={LANG}"
                )
            except Exception as e:
                print("weather url error:", e)
                return

            try:
                resp = requests.get(url, timeout=5)
                data = resp.json()
                temp = data["main"]["temp"]
                Clock.schedule_once(
                    lambda _dt: self.update_weather_labels(temp)
                )
            except Exception as e:
                print("weather error:", e)

        threading.Thread(target=_worker, daemon=True).start()

    def update_weather_labels(self, temp):
        self.temp_label.text = f"Temp: {temp:.1f} C"

    # ----------- Now Playing 更新 -----------
    def update_now_playing(self, dt):
        """
        Playing / Paused のときは self.full_title とアーティストを更新。
        それ以外は「何も再生していません」表示に戻す。
        """
        try:
            status = subprocess.check_output(
                ["playerctl", "status"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            status = ""

        if status not in ("Playing", "Paused"):
            # 再生してない
            self.full_title = ""
            self.scroll_pos = 0
            self.now_title_label.text = "♪ 何も再生していません"
            self.now_artist_label.text = ""
            return

        # 曲名・アーティスト取得
        try:
            title = subprocess.check_output(
                ["playerctl", "metadata", "title"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            title = ""

        try:
            artist = subprocess.check_output(
                ["playerctl", "metadata", "artist"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            artist = ""

        if not title and not artist:
            self.full_title = ""
            self.scroll_pos = 0
            self.now_title_label.text = "♪ 再生中の曲情報なし"
            self.now_artist_label.text = ""
            return

        state_text = "[再生中]" if status == "Playing" else "[一時停止]"
        # スクロール用フルタイトル（ここは全部持っておく）
        self.full_title = f"{state_text} {title if title else '（タイトル不明）'}"
        self.scroll_pos = 0  # 曲が変わったら先頭に戻す

        # アーティストは固定表示
        self.now_artist_label.text = artist

    # ----------- タイトルテロップ表示 -----------
    def scroll_title(self, dt):
        """
        self.full_title を SCROLL_WINDOW 文字分だけ切り出して
        横スクロール風に表示する。
        """
        if not self.full_title:
            # 再生してない時は update_now_playing がラベルを管理
            return

        text = self.full_title + "   "  # 末尾に空白入れてループ感出す
        length = len(text)

        if length <= SCROLL_WINDOW:
            # 短いときはそのまま表示
            self.now_title_label.text = text.strip()
            return

        start = self.scroll_pos % length
        end = start + SCROLL_WINDOW

        if end <= length:
            visible = text[start:end]
        else:
            # 末尾を超えた分は先頭から
            part1 = text[start:length]
            part2 = text[0:end-length]
            visible = part1 + part2

        self.now_title_label.text = visible
        self.scroll_pos += 1

    # ----------- Music 起動 ----------
    def open_music(self, instance):
        """
        YouTube Music を画面下側に（サイズは前回調整した値を使う想定）。
        例として 1920x1080 環境で Dashboard 上 / Music 下 の形。
        必要なら window-size / position を環境に合わせて調整してOK。
        """
        if self.music_proc is None or self.music_proc.poll() is not None:
            print("launch YouTube Music (bottom big window)")
            self.music_proc = subprocess.Popen(
                [
                    "google-chrome",
                    "--new-window",
                    "--window-size=1920,650",   # ← あなたの環境でちょうど良かった値
                    "--window-position=0,430",  # ← Dashboard の高さに合わせる
                    "https://music.youtube.com",
                ]
            )
        else:
            print("YouTube Music already running")

    def open_dashboard(self, instance):
        print("Dashboard button pressed")

    # ----------- playerctl 操作 -----------
    def on_prev(self, instance):
        try:
            subprocess.run(["playerctl", "previous"])
        except Exception as e:
            print("playerctl prev error:", e)

    def on_play_pause(self, instance):
        try:
            subprocess.run(["playerctl", "play-pause"])
        except Exception as e:
            print("playerctl play-pause error:", e)

    def on_next(self, instance):
        try:
            subprocess.run(["playerctl", "next"])
        except Exception as e:
            print("playerctl next error:", e)


class CarDashboardApp(App):
    def build(self):
        self.title = "Car Dashboard"
        return CarDashboard()


if __name__ == "__main__":
    CarDashboardApp().run()

