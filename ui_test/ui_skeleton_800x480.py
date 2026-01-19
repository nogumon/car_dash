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

import math

from kivy.uix.floatlayout import FloatLayout

from kivy.uix.screenmanager import SlideTransition

from kivy.properties import DictProperty, NumericProperty
from kivy.uix.button import Button

from kivy.properties import NumericProperty, BooleanProperty

from kivy.properties import DictProperty, StringProperty

from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty

from kivy.properties import BooleanProperty

from controllers.dummy import DummyController
import threading

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

THEMES = {
    "blue": {
        "bg": "#0B0F14",
        "panel": "#121925",
        "stroke": "#2A3646",
        "stroke_hi": "#3A4A60",
        "text_main": "#E6EBF2",
        "text_sub": "#A6B2C2",
        "accent": "#3A86FF",
        "accent_muted": "#5E7FBF",
        "danger": "#D32F2F",
        "danger_down": "#9A0007",
        "radius": 16,
        "panel_down": "#0E1520",
    },
    "red": {
        "bg": "#0B0F14",
        "panel": "#1A0F14",
        "stroke": "#4A2A33",
        "stroke_hi": "#6A3A47",
        "text_main": "#E6EBF2",
        "text_sub": "#A6B2C2",
        "accent": "#FF3B6B",
        "accent_muted": "#D06B86",
        "danger": "#D32F2F",
        "danger_down": "#9A0007",
        "radius": 16,
        "panel_down": "#120B10",
    },
    # retroは後で木目にする前提（今はダミーでOK）
    "retro": {
        "bg": "#0B0F14",
        "panel": "#121925",
        "stroke": "#2A3646",
        "stroke_hi": "#3A4A60",
        "text_main": "#E6EBF2",
        "text_sub": "#A6B2C2",
        "accent": "#D8A24A",
        "accent_muted": "#C09040",
        "danger": "#D32F2F",
        "danger_down": "#9A0007",
        "radius": 16,
        "panel_down": "#0E1520",
    },
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
#:import StencilView kivy.uix.stencilview.StencilView

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
                    id: title_lbl
                    text: root.title_text
                    color: app.hex_to_rgba(app.theme["accent"])
                    font_size: "26sp"
                    bold: True

                    # 1行固定＆省略
                    shorten: True
                    shorten_from: "right"
                    max_lines: 1

                    # 左詰めを確実に
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None

                    size_hint_y: None
                    height: dp(36)

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
                    padding: 0, dp(2), 0, 0   # 少し下げる。逆なら dp(-1) とかで調整
                    Label:
                        text: root.play_state_text
                        color: app.hex_to_rgba(app.theme["text_sub"])
                        font_size: "14sp"
                        halign: "left"
                        valign: "middle"
                        text_size: self.size
                    VEqualizer:
                        id: eq
                        size_hint: None, None
                        width: dp(86)
                        height: dp(26)   # ここは好み。dp(22)〜dp(30)で調整

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
                on_release: app.toggle_play()

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

<HoldDanger@LongPressButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: "18sp"
    hold_time: 0.75

    # armedになったら枠が光って、内側がさらに沈む
    canvas.before:
        # glow（armed中だけ）
        Color:
            rgba: app.hex_to_rgba_a(app.theme["accent"], 0.30) if self.armed else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.x - dp(2), self.y - dp(2)
            size: self.width + dp(4), self.height + dp(4)
            radius: [app.theme["radius"] + dp(3),]

        # outer stroke（赤枠）
        Color:
            rgba: app.hex_to_rgba(app.theme["danger"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [app.theme["radius"],]

        # fill（armed中はさらに暗く）
        Color:
            rgba: app.hex_to_rgba(app.theme["danger_down"] if self.armed else app.theme["danger"])
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

        # pressed highlight（armed中だけ）
        Color:
            rgba: (1, 1, 1, 0.12) if self.armed else (1, 1, 1, 0)
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [app.theme["radius"],]

<ThemeChoice@Button>:
    # 使うプロパティ
    theme_key: "blue"
    accent_hex: "#3A86FF"
    disabled: False

    background_normal: ""
    background_down: ""
    background_color: 0,0,0,0
    color: app.hex_to_rgba(app.theme["text_main"])
    font_size: "18sp"
    bold: True

    # 見た目
    size_hint: 1, 1

    canvas.before:
        # --- base (中身) ---
        Color:
            rgba: app.hex_to_rgba(app.theme["panel"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(app.theme["radius"]),]

        # --- 通常枠 ---
        Color:
            rgba: app.hex_to_rgba(app.theme["stroke"])
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(app.theme["radius"]))
            width: 1.0

        # --- 選択中の「発光」(疑似グロー：太い線を薄く重ねる) ---
        # ここはKVがコケやすいので式を短くしてる

        # 外側ぼんやり
        Color:
            rgba: app.hex_to_rgba_a(self.accent_hex, 0.22 if (app.theme_key == self.theme_key and self.state == "down") else (0.16 if (app.theme_key == self.theme_key) else 0.0))
        Line:
            rounded_rectangle: (self.x-dp(1), self.y-dp(1), self.width+dp(2), self.height+dp(2), dp(app.theme["radius"])+dp(1))
            width: 6.0

        # 内側くっきり
        Color:
            rgba: app.hex_to_rgba_a(self.accent_hex, 0.38 if (app.theme_key == self.theme_key and self.state == "down") else (0.28 if (app.theme_key == self.theme_key) else 0.0))
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(app.theme["radius"]))
            width: 2.2

    on_release:
        app.set_theme(self.theme_key)


<ThemePopup@Popup>:
    title: ""
    size_hint: None, None
    size: dp(520), dp(280)
    auto_dismiss: True
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    separator_height: 0
    background: ""           # ★OS/デフォ枠を消す
    background_color: 0,0,0,0

    ThemedDialog:
        orientation: "vertical"
        spacing: dp(14)
        padding: dp(16)

        Label:
            text: "Theme"
            font_size: "20sp"
            color: app.hex_to_rgba(app.theme["text_main"])
            size_hint_y: None
            height: dp(30)

        Widget:
            size_hint_y: None
            height: dp(1)
            canvas.before:
                Color:
                    rgba: app.hex_to_rgba_a(app.theme["stroke"], 0.8)
                Rectangle:
                    pos: self.pos
                    size: self.size

        GridLayout:
            cols: 2
            spacing: dp(12)
            size_hint_y: None
            height: dp(150)

            ThemeChoice:
                text: "BLUE"
                theme_key: "blue"
                accent_hex: "#3A86FF"

            ThemeChoice:
                text: "RED"
                theme_key: "red"
                accent_hex: "#FF3B6B"

            ThemeChoice:
                text: "RETRO（準備中）"
                theme_key: "retro"
                accent_hex: "#F0B44C"
                disabled: True
                color: app.hex_to_rgba(app.theme["text_sub"])
                on_release: None   # 念のため

            ThemedButton:
                text: "戻る"
                on_release: root.dismiss()

<SystemPopup>:
    title: "SYSTEM"
    size_hint: None, None
    size: dp(440), dp(250)
    auto_dismiss: True
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    background: ""
    background_color: 0, 0, 0, 0
    separator_color: 0, 0, 0, 0

    ThemedDialog:
        orientation: "vertical"
        spacing: dp(14)

        size_hint_y: None
        height: self.minimum_height
        padding: dp(16), dp(12)   # ←いらなければ消してOK

        Label:
            text: "System Menu"
            font_size: "18sp"
            color: app.hex_to_rgba(app.theme["text_main"])
            size_hint_y: None
            height: dp(28)
        
        Widget:
            size_hint_y: None
            height: dp(1)
            canvas.before:
                Color:
                    rgba: app.hex_to_rgba_a(app.theme["stroke_hi"], 0.55)
                Rectangle:
                    pos: self.pos
                    size: self.size

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

            ThemedButton:
                text: "テーマ"
                on_release:
                    root.dismiss()
                    app.open_theme_popup()

            ThemedButton:
                text: "戻る"
                on_release: root.dismiss()

        HoldDanger:
            size_hint_y: None
            height: app.ui["h_sysbtn"]
            text: "終了（長押し→離す）"
            on_hold_confirm:
                root.dismiss()
                app.request_quit()


<ThemeOption@Button>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: "18sp"

    # 外から渡す色
    accent_hex: "#3A86FF"
    panel_hex: "#121925"
    stroke_hex: "#2A3646"

    canvas.before:
        # outer
        Color:
            rgba: app.hex_to_rgba(self.stroke_hex)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16),]

        # fill（押下で少し暗く）
        Color:
            rgba: app.hex_to_rgba(self.panel_hex)
        RoundedRectangle:
            pos: self.x + dp(1), self.y + dp(1)
            size: self.width - dp(2), self.height - dp(2)
            radius: [dp(16),]

        # accent bar（左にテーマ色）
        Color:
            rgba: app.hex_to_rgba(self.accent_hex)
        RoundedRectangle:
            pos: self.x + dp(10), self.y + dp(10)
            size: dp(10), self.height - dp(20)
            radius: [dp(6),]

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

class LongPressButton(Button):
    """
    押す → hold_time経過で「armed=True」「見た目をdown」にする
    離す → armedなら on_hold_confirm を発火（＝離した瞬間に確定）
    """
    __events__ = ("on_hold_confirm",)

    hold_time = NumericProperty(0.75)
    armed = BooleanProperty(False)

    _ev = None

    def on_press(self):
        self.armed = False
        # 長押しタイマー開始
        if self._ev:
            self._ev.cancel()
        self._ev = Clock.schedule_once(self._arm, self.hold_time)

    def _arm(self, *_):
        self._ev = None
        self.armed = True
        # 見た目を「押し込み」に固定（離すまで down）
        self.state = "down"

    def on_release(self):
        # タイマーキャンセル
        if self._ev:
            self._ev.cancel()
            self._ev = None

        # armed なら離した瞬間に確定
        if self.armed:
            self.dispatch("on_hold_confirm")

        # 状態リセット
        self.armed = False
        self.state = "normal"

    def on_hold_confirm(self, *args):
        pass


class SystemPopup(Popup):
    # フェード時間
    fade_sec = NumericProperty(0.16)

    def on_open(self):
        # content全体をフェードイン
        if self.content:
            self.content.opacity = 0
            Animation(opacity=1, d=self.fade_sec, t="out_quad").start(self.content)

    def dismiss(self, *largs, **kwargs):
        # フェードアウトしてから閉じる
        if self.content:
            anim = Animation(opacity=0, d=self.fade_sec, t="out_quad")
            anim.bind(on_complete=lambda *_: super(SystemPopup, self).dismiss(*largs, **kwargs))
            anim.start(self.content)
            return
        return super().dismiss(*largs, **kwargs)

class VEqualizer(Widget):
    """
    縦バーの簡易イコライザー（ダミー）
    - bars本数
    - vals: 0.0〜1.0
    """
    bars = NumericProperty(12)
    vals = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._phase = 0.0
        self._rects = []
        self._bg_rects = []

        with self.canvas:
            # 背景バー（薄く）
            self._bg_color = Color(1, 1, 1, 0.10)
            # 実バー（アクセント色、rgbaは後で更新）
            self._fg_color = Color(1, 1, 1, 0.90)

        self.bind(pos=self._rebuild, size=self._rebuild)
        self._rebuild()

    def _rebuild(self, *_):
        # バーを作り直し
        self.canvas.clear()
        self._rects = []
        self._bg_rects = []

        with self.canvas:
            # 背景バー色
            #self._bg_color = Color(1, 1, 1, 0.10)
            # 実バー色（あとで theme の accent で更新する）
            self._fg_color = Color(1, 1, 1, 0.90)

            n = int(self.bars)
            if n <= 0:
                return

            gap = dp(3)
            bar_w = dp(4)
            total_w = n * bar_w + (n - 1) * gap
            start_x = self.x + (self.width - total_w) / 2.0

            # vals初期化
            if len(self.vals) != n:
                self.vals = [0.3] * n

            # 実バー（高さは update() で変える）
            for i in range(n):
                x = start_x + i * (bar_w + gap)
                rr = RoundedRectangle(pos=(x, self.y), size=(bar_w, dp(2)), radius=[dp(2)])
                self._rects.append(rr)

        self._apply_theme_color()
        self._apply_vals()

    def _apply_theme_color(self):
        app = App.get_running_app()
        if not app:
            return
        r, g, b, _ = app.hex_to_rgba(app.theme["accent"])
        self._fg_color.rgba = (r, g, b, 0.90)
        # 背景バーは stroke 由来にしても良い（好み）
        sr, sg, sb, _ = app.hex_to_rgba(app.theme["stroke_hi"])
        self._bg_color.rgba = (sr, sg, sb, 0.22)

    def _apply_vals(self):
        if not self._rects:
            return
        n = len(self._rects)
        for i in range(n):
            v = self.vals[i] if i < len(self.vals) else 0.2
            v = max(0.05, min(1.0, float(v)))
            h = self.height * v
            rect = self._rects[i]
            rect.size = (rect.size[0], h)
            rect.pos = (rect.pos[0], self.y)

    def update(self, dt):
        app = App.get_running_app()
        n = int(self.bars) if hasattr(self, "bars") else 10

        min_idle = 0.10   # 停止中の「ちょこっと」
        if not app or not getattr(app, "is_playing", False):
            if not hasattr(self, "vals") or len(self.vals) != n:
                self.vals = [min_idle] * n
            else:
                self.vals = [max(min_idle, v * 0.85) for v in self.vals]
            self._apply_vals()
            return

        n = int(self.bars)
        if n <= 0:
            return

        self._phase += dt * 3.2

        vals = []
        for i in range(n):
            a = 0.55 + 0.45 * math.sin(self._phase + i * 0.55)
            b = 0.25 + 0.25 * math.sin(self._phase * 1.9 + i * 0.9)
            v = 0.18 + 0.72 * max(0.0, a) + b
            v = max(0.06, min(1.0, v))
            vals.append(v)

        self.vals = vals
        self._apply_theme_color()
        self._apply_vals()

class HomeScreen(Screen):
    time_text = StringProperty("12:34")
    mode_text = StringProperty("HOME")   # 追加
    speed_text = StringProperty("0 km/h")  # 追加
    title_text = StringProperty("Ocean Waves")
    artist_text = StringProperty("Chillout Lounge")
    play_state_text = StringProperty("Playing")
    location_text = StringProperty("埼玉県 草加市")
    temp_text = StringProperty("14℃")
    _scroll_x = NumericProperty(0.0)
    _scroll_active = BooleanProperty(False)


class MusicScreen(Screen):
    time_text = StringProperty("12:34")
    mode_text = StringProperty("MUSIC")  # 追加
    speed_text = StringProperty("0 km/h")  # 追加

class MapFullScreen(Screen):
    time_text = StringProperty("12:34")
    mode_text = StringProperty("MAP")    # 追加
    speed_text = StringProperty("0 km/h")  # 追加

class DashApp(App):
    # 追加：テーマは DictProperty にする（KVが追従しやすい）
    theme = DictProperty(THEMES["blue"])
    theme_key = StringProperty("blue")
    ui = UI

    TRANSITION_SEC = 0.28
    _theme_order = ["blue", "red", "retro"]
    _theme_i = 0

    is_playing = BooleanProperty(True)  # 仮でTrue

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)

        # Controller差し替え口（無指定ならダミー）
        self.controller = controller or DummyController()

        # 直近ログを溜める（多すぎると重いので上限）
        self._log_buf = deque(maxlen=3000)

        # stdout/stderrをTeeして、printや例外も保存対象にする
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = _TeeStream(self._orig_stdout, self._log_buf)
        sys.stderr = _TeeStream(self._orig_stderr, self._log_buf, prefix="[ERR] ")

    def set_theme(self, key: str):
        # ★安全：未知キーは無視
        if key not in THEMES:
            return

        # DictPropertyは「新しいdict」を代入するとKV側が反応しやすい
        self.theme = dict(THEMES[key])
        self.theme_key = key

        # 切替フィードバック
        self._toast(f"Theme: {key.upper()}", seconds=2.0)

        # 選んだら少しだけ見せて閉じる
        if hasattr(self, "_theme_popup") and self._theme_popup:
            Clock.schedule_once(lambda *_: self._theme_popup.dismiss(), 0.15)

    def cycle_theme(self):
        self._theme_i = (self._theme_i + 1) % len(self._theme_order)
        self.set_theme(self._theme_order[self._theme_i])

    def hex_to_rgba(self, hex_color: str):
        # 防御：Noneや変な文字混入でも落とさない
        if hex_color is None:
            return (0, 0, 0, 1)

        s = str(hex_color).strip()

        # よくある「□#xxxxxx」みたいな混入対策
        s = s.replace("□", "").replace("\ufeff", "").strip()

        # 先頭の#を外す
        if s.startswith("#"):
            s = s[1:]

        # 長さチェック
        if len(s) < 6:
            return (0, 0, 0, 1)

        try:
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b, 1)
        except Exception:
            return (0, 0, 0, 1)

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

        Factory.register("VEqualizer", cls=VEqualizer)

        Clock.schedule_interval(self._demo_speed, 0.5)

        Clock.schedule_interval(self._tick_eq, 1/30)  # 30fps くらい

        Clock.schedule_interval(self._tick_title_scroll, 1/30)  # 30fps

        sm = ScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(MusicScreen())
        sm.add_widget(MapFullScreen())
        # 起動直後に実状態と同期
        Clock.schedule_once(lambda *_: self.sync_play_state(), 0.2)
        # 起動直後1回同期
        Clock.schedule_once(lambda *_: self.sync_now_playing(), 0.3)

        # 以降は定期的に同期（重くない）
        Clock.schedule_interval(lambda dt: self.sync_now_playing(), 1.0)

        return sm

    def goto(self, name: str, direction: str = "left"):
        self.root.transition = SlideTransition(direction=direction, duration=self.TRANSITION_SEC)
        self.root.current = name

    def toggle_play(self):
        def _done(res):
            # resがTrue/Falseなら実状態として採用
            if isinstance(res, bool):
                self.is_playing = res
            else:
                # 実状態が取れない時だけトグル（保険）
                self.is_playing = not self.is_playing

            state = "Playing" if self.is_playing else "Paused"
            for name in ("home", "music", "map_full"):
                scr = self.root.get_screen(name)
                if hasattr(scr, "play_state_text"):
                    scr.play_state_text = state

        self.call_async(self.controller.play_pause, on_done=_done)

    def stub(self, action: str):
        if action == "play_pause":
            self.toggle_play()
            return

        if action == "next":
            self.call_async(self.controller.next_track)
            return

        if action == "prev":
            self.call_async(self.controller.prev_track)
            return

        print(f"[stub] action={action}")

    def open_system_popup(self):
        if not hasattr(self, "_system_popup") or self._system_popup is None:
            self._system_popup = Factory.SystemPopup()
        self._system_popup.open()

    def close_system_popup(self):
        if hasattr(self, "_system_popup") and self._system_popup:
            self._system_popup.dismiss()

    def quit_app(self):
        App.get_running_app().stop()

    def request_quit(self):
        self._toast("See you later", seconds=2.0)
        # 見える時間を確保してから終了
        Clock.schedule_once(lambda *_: self.quit_app(), 1.2)

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def open_theme_popup(self):
        if not hasattr(self, "_theme_popup") or self._theme_popup is None:
            self._theme_popup = Factory.ThemePopup()
        self._theme_popup.open()

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
            bg = RoundedRectangle(radius=[dp(self.ui.get("r_toast", 14))])
            Color(rgba=self.hex_to_rgba(self.theme["stroke"]))
            border = Line(width=1)

        def _update_bg(*_):
            bg.pos = box.pos
            bg.size = box.size
            border.rounded_rectangle = (box.x, box.y, box.width, box.height, dp(self.ui.get("r_toast", 14)))

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
        box.pos = ((Window.width - box.width) / 2, dp(20))

        root.add_widget(box)
        Window.add_widget(root)

        # アニメーション（下からふわっと）
        Animation(opacity=1, y=dp(36), d=0.18, t="out_quad").start(box)

        def _dismiss(*_):
            anim = Animation(opacity=0, y=dp(20), d=0.18, t="out_quad")
            anim.bind(on_complete=lambda *_: Window.remove_widget(root))
            anim.start(box)

        Clock.schedule_once(_dismiss, seconds)

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

    def save_log(self):
        try:
            # 保存先: car_dash/logs/
            base_dir = os.path.dirname(os.path.abspath(__file__))  # ui_test/
            project_dir = os.path.dirname(base_dir)                # car_dash/
            logs_dir = os.path.join(project_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)

            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(logs_dir, f"dash_{ts}.log")

            header = []
            header.append(f"timestamp: {ts}\n")
            header.append(f"python: {sys.version}\n")
            header.append(f"current_screen: {getattr(self.root, 'current', 'unknown')}\n")
            header.append("-" * 60 + "\n")

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(header)
                f.writelines(list(self._log_buf))

            rel = os.path.relpath(path, project_dir)  # 例: logs/dash_xxx.log
            self.flash_mode(f"ログ保存: {rel}", seconds=5.0)
            print(f"[log] saved: {path}")

        except Exception as e:
            self._toast(f"ログ保存に失敗: {e}", seconds=2.0)
            raise

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

    def _tick_eq(self, dt):
        # 画面にいるイコライザー全部更新（いれば）
        try:
            for scr_name in ("home", "music", "map_full"):
                scr = self.root.get_screen(scr_name)
                # idで取る or walkで探す。まずは id を推奨
                w = getattr(scr, "ids", {}).get("eq", None)
                if w:
                    w.update(dt)
        except Exception:
            pass

    def call_async(self, fn, on_done=None):
        """
        OS操作/playerctlは固まることがあるのでUIスレッドから切り離す。
        on_done(result) はUIスレッドで呼ぶ。
        """
        def _run():
            try:
                res = fn()
            except Exception as e:
                res = e
            if on_done:
                Clock.schedule_once(lambda *_: on_done(res), 0)

        threading.Thread(target=_run, daemon=True).start()

    def sync_play_state(self):
        def _done(res):
            if isinstance(res, bool):
                self.is_playing = res
                state = "Playing" if self.is_playing else "Paused"
                for name in ("home", "music", "map_full"):
                    scr = self.root.get_screen(name)
                    if hasattr(scr, "play_state_text"):
                        scr.play_state_text = state

        self.call_async(self.controller.get_status, on_done=_done)

    def _apply_now_playing(self, meta: dict):
        # 空なら更新しない
        if not meta:
            return

        title = meta.get("title") or ""
        artist = meta.get("artist") or ""

        # ここで表示用のfallback
        if not title:
            title = "（タイトル不明）"
        if not artist:
            artist = ""

        # Homeの表示を更新
        try:
            home = self.root.get_screen("home")
            home.title_text = title
            home.artist_text = artist
        except Exception:
            pass

    def sync_now_playing(self):
        def _done(res):
            if isinstance(res, dict):
                self._apply_now_playing(res)

        self.call_async(self.controller.get_metadata, on_done=_done)

    def _tick_title_scroll(self, dt):
        # Home画面のタイトルだけスクロール（まずはここだけ）
        try:
            home = self.root.get_screen("home")
            lbl = home.ids.get("title_lbl")
            if not lbl:
                return

            # ラベルの実表示幅と、文字の幅
            lbl.texture_update()
            text_w = lbl.texture_size[0]
            box_w = lbl.width

            # 収まってるなら止める
            if text_w <= box_w + dp(2):
                home._scroll_active = False
                home._scroll_x = 0.0
                lbl.x = lbl.parent.x + dp(0)
                return

            # スクロールする
            if not home._scroll_active:
                home._scroll_active = True
                home._scroll_x = 0.0

            speed = dp(40)  # 1秒あたり40pxくらい（好みで）
            home._scroll_x += speed * dt

            # ループ：末尾が完全に抜けたら先頭に戻す（チカチカしない方式）
            loop_len = text_w - box_w + dp(30)  # 余白30
            if home._scroll_x > loop_len:
                home._scroll_x = 0.0

            # Labelを左にずらす（clipは親で行われる）
            base_x = lbl.parent.x
            lbl.x = base_x - home._scroll_x

        except Exception:
            pass

if __name__ == "__main__":
    DashApp().run()
