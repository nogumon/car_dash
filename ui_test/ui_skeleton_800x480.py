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


THEME = {
    "bg": "#0B0F14",          # 少し深く
    "panel": "#121925",       # 少し青寄り
    "stroke": "#2A3646",      # 枠線を明るく（見やすさUP）
    "stroke_hi": "#3A4A60",   # ハイライト用（うっすら）
    "text_main": "#E6EBF2",
    "text_sub": "#A6B2C2",    # 少しだけ明るく
    "accent": "#3A86FF",
    "accent_muted": "#5E7FBF",
    "danger": "#FF6B6B",
    "radius": 16,
    "panel_down": "#0E1520",
}

KV = """

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
            radius: [app.theme["radius"],]

        # outer stroke
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, app.theme["radius"])
            width: 1.35

        # inner highlight (top-ish)
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke_hi"])
        Line:
            rounded_rectangle: (self.x+dp(1), self.y+dp(1), self.width-dp(2), self.height-dp(2), app.theme["radius"])
            width: 1.0

        # inner shadow (bottom-ish) : 下側に“沈み”を作る
        Color:
            rgba: 0, 0, 0, 0.35
        Line:
            rounded_rectangle: (self.x+dp(2), self.y+dp(2), self.width-dp(4), self.height-dp(4), app.theme["radius"])
            width: 1.0

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
            radius: [dp(18),]
        
        # stroke (枠線) 
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(18))
            width: 1.0

<ThemedButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: app.hex_to_rgba(app.theme["text_main"])
    font_size: "18sp"
    canvas.before:
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]
        Color:
            rgba: app.hex_to_rgba(app.theme["panel_down"] if self.state=="down" else app.theme["panel"])
        RoundedRectangle:
            pos: self.x+dp(1), self.y+dp(1)
            size: self.width-dp(2), self.height-dp(2)
            radius: [app.theme["radius"],]

    on_press:
        self.color = app.hex_to_rgba(app.theme["accent"])
    on_release:
        self.color = app.hex_to_rgba(app.theme["text_main"])

<IconButton@Button>:
    font_name: "SYM"
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: app.hex_to_rgba(app.theme["text_main"])
    font_size: "20sp"
    bold: True
    canvas.before:
        # outer stroke
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]
        # inner fill
        Color:
            rgba: app.hex_to_rgba(app.theme["panel"])
        RoundedRectangle:
            pos: self.x+dp(1), self.y+dp(1)
            size: self.width-dp(2), self.height-dp(2)
            radius: [app.theme["radius"],]
    disabled_color: app.hex_to_rgba(app.theme["text_sub"])

<IconButton@ThemedButton>:
    font_size: "20sp"

<StatusBar@BoxLayout>:
    size_hint_y: None
    height: dp(40)
    padding: dp(10), dp(6)
    spacing: dp(8)
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
                width: dp(220)
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
                    height: dp(46)
                    on_release: app.goto("music")

            # Right: Mini map
            ThemedPanel:
                orientation: "vertical"
                padding: dp(10)
                spacing: dp(8)
                size_hint_x: None
                width: dp(250)

                # Mini map box (dummy) : 余った高さをここが全部使う
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

                # Location + Temp under map（そのまま）
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

                # MAPボタン（そのまま）
                ThemedButton:
                    text: "MAP (Full)"
                    size_hint_y: None
                    height: dp(46)
                    on_release: app.goto("map_full")

        BoxLayout:
            size_hint_y: None
            height: dp(66)
            padding: dp(10), dp(8)
            spacing: dp(10)
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
            height: dp(66)
            padding: dp(10), dp(8)
            spacing: dp(10)
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
                on_release: app.goto("home")

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
            height: dp(66)
            padding: dp(10), dp(8)
            spacing: dp(10)
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
                on_release: app.goto("home")
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

<DangerButton@ThemedButton>:
    canvas.before:
        Color:
            rgba: app.hex_to_rgba(app.theme["danger"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]
        Color:
            rgba: 0, 0, 0, 0

#:import dp kivy.metrics.dp

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

            # ★ここが重要：高さを中身に追従させる
            size_hint_y: None
            height: self.minimum_height

            # 2行分のボタン高さを固定して“揃える”
            row_force_default: True
            row_default_height: dp(52)

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

    def goto(self, name: str):
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
