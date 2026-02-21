from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
import os
import random

# ==========================================
# 🎨 ส่วนที่ 1: Kivy Design (UI & Layouts)
# ==========================================
KV = '''
ScreenManager:
    transition: app.fade_transition()
    MenuScreen:

<MenuScreen>:
    name: 'menu'
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 30
        Label:
            text: '[b]TIME-ATTACK QUIZ[/b]\\nSurvive the Bomb!'
            markup: True
            halign: 'center'
            font_size: 45
            color: 1, 0.4, 0.1, 1
            size_hint_y: 0.4
'''
