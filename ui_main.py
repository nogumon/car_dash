# ui_main.py
from ui_test.ui_skeleton_800x480 import DashApp
from controllers.real_playerctl import PlayerctlController

if __name__ == "__main__":
    DashApp(controller=PlayerctlController()).run()