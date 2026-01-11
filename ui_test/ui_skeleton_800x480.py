# ui_test/ui_skeleton_800x480.py

from kivy.config import Config
Config.set("graphics", "width", "800")
Config.set("graphics", "height", "480")
Config.set("graphics", "resizable", "0")

import os
import sys
from kivy.core.text import LabelBase

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.factory import Factory

from datetime import datetime
from collections import deque
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.uix.boxlayout import BoxLayout

from kivy.animation import Animation
from kivy.core.window import Window

from kivy.graphics import Color, RoundedRectangle, Line

from kivy.uix.floatlayout import FloatLayout

from kivy.uix.screenmanager import SlideTransition


THEME = {
    "bg": "#0B0F14",          # 少し深く
    "panel": "#121925",       # 少し青寄り
    "stroke": "#2A3646",      # 枠線を明るく（見やすさUP）
    "stroke_hi": "#3A4A60",   # ハイライト用（うっすら）
    "text_main": "#E6EBF2",
    "text_sub": "#A6B2C2",    # 少しだけ明るく
    "accent": "#3A86FF",
    "accent_muted": "#5E7FBF",
    "danger": "#D32F2F",
    "danger_down": "#9A0007",
    "radius": 16,
    "panel_down": "#0A1019",
}

UI = {
    # spacing
    "s6": dp(6),
    "s8": dp(8),
    "s10": dp(10),
    "s12": dp(12),
    "s14": dp(14),
    "s16": dp(16),

    # radii
    "r_panel": dp(16),
    "r_card": dp(18),

    # strokes / depth
    "stroke_outer": 1.35,
    "stroke_inner": 1.0,
    "stroke_shadow": 1.0,
    "hi_a": 0.38,
    "shadow_a": 0.35,

    # heights
    "h_status": dp(40),
    "h_bottom": dp(66),
    "h_btn": dp(46),
    "h_sysbtn": dp(52),

    # widths
    "w_time": dp(72),
    "w_right": dp(220),
    "w_map_panel": dp(250),

    # radius
    "r_card": 16,
    "r_toast": 14,

    # strokes
    "stroke_outer": 1.35,
    "stroke_inner": 1.0,
    "stroke_shadow": 1.0,

    # overlay alpha
    "hi_a": 0.35,
    "shadow_a": 0.30,

    # spacing / sizes
    "gap": 10,
    "pad": 10,
    "bottom_h": 66,
}

KV = """

#:import dp kivy.metrics.dp

<Label>:
    font_name: "JP"

<ThemedPanel@BoxLayout>:
    canvas.before:
        # base
        Color:
            rgba: app.hex_to_rgba(app.theme["panel"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(app.ui["r_card"]),]

        # outer stroke
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(app.ui["r_card"]))
            width: app.ui["stroke_outer"]

        # inner highlight (top-ish)
        Color:
            rgba: app.hex_to_rgba_a(app.theme["stroke_hi"], app.ui["hi_a"])
        Line:
            rounded_rectangle: (self.x + dp(1), self.y + dp(1), self.width - dp(2), self.height - dp(2), dp(app.ui["r_card"]))
            width: app.ui["stroke_inner"]

        # inner shadow (bottom-ish)
        Color:
            rgba: 0, 0, 0, app.ui["shadow_a"]
        Line:
            rounded_rectangle: (self.x + dp(2), self.y + dp(2), self.width - dp(4), self.height - dp(4), dp(app.ui["r_card"]))
            width: app.ui["stroke_shadow"]

<ThemedDialog@BoxLayout>:
    padding: dp(16)
    canvas.before:
        # backdropっぽい暗色
        Color:
            rgba: 0, 0, 0, 0.35
        Rectangle:
            pos: -dp(2000), -dp(2000)
            size: dp(4000), dp(4000)

        # card (dialog本体)
        Color:
            rgba: app.hex_to_rgba(app.theme["panel"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.ui["r_card"],]

        # stroke (枠線)
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, app.ui["r_card"])
            width: 1.0

<ThemedButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: app.hex_to_rgba(app.theme["text_main"])
    font_size: "18sp"

    canvas.before:
        # outer stroke
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]

        # fill (downなら暗く)
        Color:
            rgba: app.hex_to_rgba(app.theme["panel_down"] if self.state == "down" else app.theme["panel"])
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

        # press highlight（押してる間だけ青く光る）
        Color:
            rgba: app.hex_to_rgba_a(app.theme["accent"], 0.18 if self.state == "down" else 0)
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

        # top highlight（常にうっすら）
        Color:
            rgba: app.hex_to_rgba_a(app.theme["stroke_hi"], 0.22)
        Line:
            rounded_rectangle: (self.x + dp(1), self.y + dp(1), self.width - dp(2), self.height - dp(2), app.theme["radius"])
            width: 1.0

<IconButton@Button>:
    font_name: "SYM"
    font_size: "20sp"
    bold: True
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: app.hex_to_rgba(app.theme["text_main"])

    canvas.before:
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]

        Color:
            rgba: app.hex_to_rgba(app.theme["panel_down"] if self.state == "down" else app.theme["panel"])
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

        Color:
            rgba: app.hex_to_rgba_a(app.theme["accent"], 0.22 if self.state == "down" else 0)
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

<StatusBar@BoxLayout>:
    size_hint_y: None
    height: app.ui["h_status"]
    padding: app.ui["s10"], app.ui["s6"]
    spacing: app.ui["s8"]
    canvas.before:
        Color:
            rgba: app.hex_to_rgba(app.theme["bg"])
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        Line:
            points: (self.x, self.y, self.right, self.y)
            width: 1.0

<HomeScreen>:
    name: "home"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: app.hex_to_rgba(app.theme["bg"])
            Rectangle:
                pos: self.pos
                size: self.size

        StatusBar:
            Label:
                text: root.time_text
                color: app.hex_to_rgba(app.theme["text_main"])
                font_size: "16sp"
                size_hint_x: None
                width: app.ui["w_time"]
                halign: "left"
                valign: "middle"
                text_size: self.size
            Label:
                text: root.mode_text
                color: app.hex_to_rgba(app.theme["text_sub"])
                font_size: "14sp"
                halign: "center"
                valign: "middle"
                text_size: self.size
            BoxLayout:
                size_hint_x: None
                width: app.ui["w_right"]
                spacing: dp(8)

                # SPEED
                Label:
                    text: "SPD"
                    color: app.hex_to_rgba(app.theme["text_sub"])
                    font_size: "13sp"
                    size_hint_x: None
                    width: dp(34)
                    halign: "right"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: root.speed_text
                    color: app.hex_to_rgba(app.theme["text_main"])
                    font_size: "14sp"
                    bold: True
                    size_hint_x: None
                    width: dp(74)
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                # GPS
                Label:
                    text: "GPS"
                    color: app.hex_to_rgba(app.theme["text_sub"])
                    font_size: "13sp"
                    size_hint_x: None
                    width: dp(34)
                    halign: "right"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: "●"
                    color: app.hex_to_rgba(app.theme["accent"])
                    font_size: "16sp"
                    size_hint_x: None
                    width: dp(18)

                Widget:

        BoxLayout:
            padding: dp(10)
            spacing: dp(10)

            # Left: Music info
            ThemedPanel:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(8)

                Label:
                    text: "Now Playing"
                    color: app.hex_to_rgba(app.theme["text_sub"])
                    font_size: "13sp"
                    size_hint_y: None
                    height: dp(18)
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: root.title_text
                    color: app.hex_to_rgba(app.theme["accent"])
                    font_size: "26sp"
                    bold: True
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: root.artist_text
                    color: app.hex_to_rgba(app.theme["text_main"])
                    font_size: "18sp"
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                BoxLayout:
                    size_hint_y: None
                    height: dp(28)
                    spacing: dp(8)
                    Label:
                        text: root.play_state_text
                        color: app.hex_to_rgba(app.theme["text_sub"])
                        font_size: "14sp"
                        halign: "left"
                        valign: "middle"
                        text_size: self.size
                    Widget:

                Widget:

                ThemedButton:
                    text: "MUSIC (Browser)"
                    size_hint_y: None
                    height: app.ui["h_btn"]
                    on_release: app.goto("music", "left")

            # Right: Mini map
            ThemedPanel:
                orientation: "vertical"
                padding: dp(10)
                spacing: dp(8)
                size_hint_x: None
                width: dp(250)

                # Mini map box (dummy)
                BoxLayout:
                    size_hint_y: 1
                    canvas.before:
                        Color:
                            rgba: app.hex_to_rgba(app.theme["bg"])
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [app.theme["radius"],]
                        Color:
                            rgba: app.hex_to_rgba(app.theme["stroke"])
                        Line:
                            rounded_rectangle: (self.x, self.y, self.width, self.height, app.theme["radius"])
                            width: 1.0
                    Label:
                        text: "MINI MAP\\n(dummy)"
                        color: app.hex_to_rgba(app.theme["text_sub"])
                        halign: "center"
                        valign: "middle"
                        text_size: self.size

                # Location + Temp under map
                BoxLayout:
                    size_hint_y: None
                    height: dp(40)
                    padding: dp(6), 0
                    Label:
                        text: root.location_text
                        color: app.hex_to_rgba(app.theme["text_main"])
                        font_size: "13sp"
                        halign: "left"
                        valign: "middle"
                        text_size: self.size
                    Label:
                        text: root.temp_text
                        color: app.hex_to_rgba(app.theme["text_main"])
                        font_size: "16sp"
                        bold: True
                        size_hint_x: None
                        width: dp(58)
                        halign: "right"
                        valign: "middle"
                        text_size: self.size

                ThemedButton:
                    text: "MAP (Full)"
                    size_hint_y: None
                    height: app.ui["h_btn"]
                    on_release: app.goto("map_full", "left")

        BoxLayout:
            size_hint_y: None
            height: app.ui["h_bottom"]
            padding: app.ui["s10"], app.ui["s8"]
            spacing: app.ui["s10"]
            canvas.before:
                Color:
                    rgba: app.hex_to_rgba(app.theme["bg"])
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: app.hex_to_rgba(app.theme["stroke"])
                Line:
                    points: (self.x, self.top, self.right, self.top)
                    width: 1.0

            IconButton:
                text: "⏮"
                on_release: app.stub("prev")

            IconButton:
                text: "⏯"
                on_release: app.stub("play_pause")

            IconButton:
                text: "⏭"
                on_release: app.stub("next")

            IconButton:
                text: "☰"
                on_release: app.open_system_popup()

<MusicScreen>:
    name: "music"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: app.hex_to_rgba(app.theme["bg"])
            Rectangle:
                pos: self.pos
                size: self.size

        StatusBar:
            Label:
                text: root.time_text
                color: app.hex_to_rgba(app.theme["text_main"])
                font_size: "16sp"
                size_hint_x: None
                width: dp(72)
                halign: "left"
                valign: "middle"
                text_size: self.size
            Label:
                text: root.mode_text
                color: app.hex_to_rgba(app.theme["text_sub"])
                font_size: "14sp"
                halign: "center"
                valign: "middle"
                text_size: self.size
            Widget:

        BoxLayout:
            padding: dp(10)
            spacing: dp(8)

            ThemedPanel:
                padding: dp(12)
                Label:
                    text: "Browser Area (YouTube Music)\\n※ここは将来、Chromium/ブラウザ表示に置き換え"
                    color: app.hex_to_rgba(app.theme["text_sub"])
                    halign: "center"
                    valign: "middle"
                    text_size: self.size

        BoxLayout:
            size_hint_y: None
            height: app.ui["h_bottom"]
            padding: app.ui["s10"], app.ui["s8"]
            spacing: app.ui["s10"]
            canvas.before:
                Color:
                    rgba: app.hex_to_rgba(app.theme["bg"])
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: app.hex_to_rgba(app.theme["stroke"])
                Line:
                    points: (self.x, self.top, self.right, self.top)
                    width: 1.0

            IconButton:
                text: "⏮"
                on_release: app.stub("prev")

            IconButton:
                text: "⏯"
                on_release: app.stub("play_pause")

            IconButton:
                text: "⏭"
                on_release: app.stub("next")

            ThemedButton:
                text: "HOME"
                size_hint_x: None
                width: dp(120)
                on_release: app.goto("home", "right")

<MapFullScreen>:
    name: "map_full"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: app.hex_to_rgba(app.theme["bg"])
            Rectangle:
                pos: self.pos
                size: self.size

        StatusBar:
            Label:
                text: root.time_text
                color: app.hex_to_rgba(app.theme["text_main"])
                font_size: "16sp"
                size_hint_x: None
                width: dp(72)
                halign: "left"
                valign: "middle"
                text_size: self.size
            Label:
                text: root.mode_text
                color: app.hex_to_rgba(app.theme["text_sub"])
                font_size: "14sp"
                halign: "center"
                valign: "middle"
                text_size: self.size
            BoxLayout:
                size_hint_x: None
                width: dp(140)
                spacing: dp(6)
                Label:
                    text: "GPS"
                    color: app.hex_to_rgba(app.theme["text_sub"])
                    font_size: "14sp"
                    size_hint_x: None
                    width: dp(38)
                    halign: "right"
                    valign: "middle"
                    text_size: self.size
                Label:
                    text: "●"
                    color: app.hex_to_rgba(app.theme["accent"])
                    font_size: "16sp"
                    size_hint_x: None
                    width: dp(18)
                Widget:

        ThemedPanel:
            padding: dp(12)
            Label:
                text: "FULL MAP AREA (dummy)\\n将来ここにGoogleマップ/ナビを表示"
                color: app.hex_to_rgba(app.theme["text_sub"])
                halign: "center"
                valign: "middle"
                text_size: self.size

        BoxLayout:
            size_hint_y: None
            height: app.ui["h_bottom"]
            padding: app.ui["s10"], app.ui["s8"]
            spacing: app.ui["s10"]
            canvas.before:
                Color:
                    rgba: app.hex_to_rgba(app.theme["bg"])
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: app.hex_to_rgba(app.theme["stroke"])
                Line:
                    points: (self.x, self.top, self.right, self.top)
                    width: 1.0

            ThemedButton:
                text: "HOME"
                on_release: app.goto("home", "right")
            ThemedButton:
                text: "+"
                size_hint_x: None
                width: dp(86)
                on_release: app.stub("zoom_in")
            ThemedButton:
                text: "-"
                size_hint_x: None
                width: dp(86)
                on_release: app.stub("zoom_out")
            Widget:

<DangerButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: "18sp"

    canvas.before:
        # outer stroke（赤枠）
        Color:
            rgba: app.hex_to_rgba(app.theme["danger"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]

        # fill（押したら暗い赤）
        Color:
            rgba: app.hex_to_rgba(app.theme["danger_down"] if self.state == "down" else app.theme["danger"])
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

        # 押下中ハイライト（ほんの少し）
        Color:
            rgba: (1, 1, 1, 0.10) if self.state == "down" else (1, 1, 1, 0)
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

<SystemPopup@Popup>:
    title: "SYSTEM"
    size_hint: None, None
    size: dp(440), dp(250)
    auto_dismiss: True

    ThemedDialog:
        orientation: "vertical"
        spacing: dp(14)

        Label:
            text: "System Menu"
            font_size: "18sp"
            color: app.hex_to_rgba(app.theme["text_main"])
            size_hint_y: None
            height: dp(28)

        GridLayout:
            cols: 2
            spacing: dp(10)
            padding: 0, 0, 0, 0
            size_hint_y: None
            height: self.minimum_height
            row_force_default: True
            row_default_height: app.ui["h_sysbtn"]

            ThemedButton:
                text: "再起動"
                on_release:
                    root.dismiss()
                    app.restart_app()

            ThemedButton:
                text: "ログ保存"
                on_release:
                    root.dismiss()
                    app.save_log()

            DangerButton:
                text: "終了"
                on_release:
                    root.dismiss()
                    app.quit_app()

            ThemedButton:
                text: "戻る"
                on_release: root.dismiss()

"""
class _TeeStream:
    """
    print() / 例外 / Kivyのstderrなどを、(元のstdout/stderrにも出しつつ)
    メモリに保存するための簡易Tee
    """
    def __init__(self, original, buffer_deque: deque, prefix: str = ""):
        self.original = original
        self.buffer = buffer_deque
        self.prefix = prefix

    def write(self, s):
        # 元にも出す
        try:
            self.original.write(s)
        except Exception:
            pass

        # バッファにも溜める（行単位じゃなくてもOK。後でファイルにそのまま吐く）
        if s:
            self.buffer.append(f"{self.prefix}{s}")

    def flush(self):
        try:
            self.original.flush()
        except Exception:
            pass

class HomeScreen(Screen):
    time_text = StringProperty("12:34")
    mode_text = StringProperty("HOME")   # 追加
    speed_text = StringProperty("0 km/h")  # 追加
    title_text = StringProperty("Ocean Waves")
    artist_text = StringProperty("Chillout Lounge")
    play_state_text = StringProperty("Playing")
    location_text = StringProperty("埼玉県 草加市")
    temp_text = StringProperty("14℃")

class MusicScreen(Screen):
    time_text = StringProperty("12:34")
    mode_text = StringProperty("MUSIC")  # 追加
    speed_text = StringProperty("0 km/h")  # 追加

class MapFullScreen(Screen):
    time_text = StringProperty("12:34")
    mode_text = StringProperty("MAP")    # 追加
    speed_text = StringProperty("0 km/h")  # 追加

class DashApp(App):
    theme = THEME

    ui = UI

    TRANSITION_SEC = 0.28  # ← 今いい感じの値に固定

    def hex_to_rgba_a(self, hex_color: str, a: float):
        r, g, b, _ = self.hex_to_rgba(hex_color)
        return (r, g, b, a)
    
    def build(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))   # ui_test/
        project_dir = os.path.dirname(base_dir)                 # car_dash/

        font_path_jp  = os.path.join(project_dir, "assets", "fonts", "NotoSansCJK-Regular.ttc")
        font_path_sym = os.path.join(project_dir, "assets", "fonts", "NotoSansSymbols2-Regular.ttf")

        LabelBase.register(name="JP",  fn_regular=font_path_jp)
        LabelBase.register(name="SYM", fn_regular=font_path_sym)

        Builder.load_string(KV)  # ★1回だけ

        Clock.schedule_interval(self._demo_speed, 0.5)

        sm = ScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(MusicScreen())
        sm.add_widget(MapFullScreen())
        return sm

    def goto(self, name: str, direction: str = "left"):
        self.root.transition = SlideTransition(direction=direction, duration=self.TRANSITION_SEC)
        self.root.current = name

    def stub(self, action: str):
        print(f"[stub] action={action}")

    def hex_to_rgba(self, hex_color: str):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b, 1)
    
    def open_system_popup(self):
        if not hasattr(self, "_system_popup") or self._system_popup is None:
            self._system_popup = Factory.SystemPopup()
        self._system_popup.open()

    def close_system_popup(self):
        if hasattr(self, "_system_popup") and self._system_popup:
            self._system_popup.dismiss()

    def quit_app(self):
        App.get_running_app().stop()

    def restart_app(self):
        # “アプリ再起動”（OS再起動じゃない）
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 直近ログを溜める（多すぎると重いので上限）
        self._log_buf = deque(maxlen=3000)

        # stdout/stderrをTeeして、printや例外も保存対象にする
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = _TeeStream(self._orig_stdout, self._log_buf)
        sys.stderr = _TeeStream(self._orig_stderr, self._log_buf, prefix="[ERR] ")
    
    def _ellipsize_middle(self, s: str, max_chars: int = 46) -> str:
        """長いパス等を中央...省略にする（UI崩れ防止）"""
        if len(s) <= max_chars:
            return s
        head = max_chars // 2 - 2
        tail = max_chars - head - 3
        return s[:head] + "..." + s[-tail:]

    def _toast(self, message: str, seconds: float = 1.6):
        # 表示幅（画面の92%）
        max_w = int(Window.width * 0.92)

        root = FloatLayout(size=Window.size)

        box = BoxLayout(
            orientation="vertical",
            padding=(dp(16), dp(12)),
            size_hint=(None, None),
            opacity=0,
        )

        with box.canvas.before:
            Color(rgba=self.hex_to_rgba(self.theme["panel"]))
            bg = RoundedRectangle(radius=[dp(14)])
            Color(rgba=self.hex_to_rgba(self.theme["stroke"]))
            border = Line(width=1)

        def _update_bg(*_):
            bg.pos = box.pos
            bg.size = box.size
            border.rounded_rectangle = (
                box.x, box.y, box.width, box.height, dp(14)
        )

        box.bind(pos=_update_bg, size=_update_bg)

        lbl = Label(
            text=message,
            font_name="JP",
            halign="left",
            valign="middle",
            color=self.hex_to_rgba(self.theme["text_main"]),
            size_hint=(None, None),
        )

        # 折り返し＋高さ自動
        lbl.text_size = (max_w - dp(32), None)
        lbl.texture_update()
        lbl.size = (lbl.text_size[0], lbl.texture_size[1])

        box.size = (max_w, lbl.height + dp(24))
        box.add_widget(lbl)

        # 画面下中央に配置
        box.pos = (
            (Window.width - box.width) / 2,
            dp(20),
        )

        root.add_widget(box)
        Window.add_widget(root)

        # アニメーション（下からふわっと）
        Animation(opacity=1, y=dp(36), d=0.18, t="out_quad").start(box)

        def _dismiss(*_):
            anim = Animation(opacity=0, y=dp(20), d=0.18, t="out_quad")
            anim.bind(on_complete=lambda *_: Window.remove_widget(root))
            anim.start(box)

        Clock.schedule_once(_dismiss, seconds)

    def save_log(self):
        try:
            # 保存先: car_dash/logs/
            base_dir = os.path.dirname(os.path.abspath(__file__))  # ui_test/
            project_dir = os.path.dirname(base_dir)                # car_dash/
            logs_dir = os.path.join(project_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)

            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(logs_dir, f"dash_{ts}.log")

            # ちょいヘッダも入れる（後から見やすい）
            header = []
            header.append(f"timestamp: {ts}\n")
            header.append(f"python: {sys.version}\n")
            header.append(f"kivy: (see runtime)\n")
            header.append(f"current_screen: {getattr(self.root, 'current', 'unknown')}\n")
            header.append("-" * 60 + "\n")

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(header)
                f.writelines(list(self._log_buf))

            rel = os.path.relpath(path, project_dir)  # 例: logs/dash_xxx.log
            self.flash_mode(f"ログ保存: {rel}", seconds=5.0)
            print(f"[log] saved: {path}")

        except Exception as e:
            # 失敗しても画面で分かるように
            self._toast(f"ログ保存に失敗: {e}", seconds=2.0)
            raise
    
    def flash_mode(self, message: str, seconds: float = 5.0):
        # 現在画面のmode_textを一時的にメッセージにする
        scr = self.root.get_screen(self.root.current)

        # 連打対策：前回の復帰タイマーをキャンセル
        if hasattr(self, "_mode_flash_ev") and self._mode_flash_ev:
            try:
                self._mode_flash_ev.cancel()
            except Exception:
                pass
            self._mode_flash_ev = None

        # 元の文字を保存（画面ごとに保持）
        if not hasattr(scr, "_mode_base"):
            scr._mode_base = scr.mode_text  # 初回だけ保存

        scr.mode_text = message

        def _restore(*_):
            scr.mode_text = scr._mode_base
            self._mode_flash_ev = None

        self._mode_flash_ev = Clock.schedule_once(_restore, seconds)

    def _demo_speed(self, dt):
        # ダミー：0→80を往復
        if not hasattr(self, "_spd"):
            self._spd = 0
            self._spd_dir = 1
        self._spd += self._spd_dir * 3
        if self._spd >= 80:
            self._spd = 80
            self._spd_dir = -1
        if self._spd <= 0:
            self._spd = 0
            self._spd_dir = 1

        spd = f"{self._spd} km/h"
        for name in ("home", "music", "map_full"):
            self.root.get_screen(name).speed_text = spd


if __name__ == "__main__":
    DashApp().run()
