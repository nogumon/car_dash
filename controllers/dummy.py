# controllers/dummy.py
class DummyController:
    """
    UIから呼ばれる“窓口”。いまは何もしないダミー。
    後で RealController に差し替えるだけで UI を触らず統合できる。
    """
    def play_pause(self):
        print("[ctrl] play_pause")
        # True/False を返して UI の is_playing を更新できるようにする
        return None

    def next_track(self):
        print("[ctrl] next_track")
        return True

    def prev_track(self):
        print("[ctrl] prev_track")
        return True

    def restart_app(self):
        print("[ctrl] restart_app")
        return True

    def request_quit(self):
        print("[ctrl] request_quit")
        return True

    def save_log(self):
        print("[ctrl] save_log")
        return True