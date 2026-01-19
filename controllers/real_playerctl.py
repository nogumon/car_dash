# controllers/real_playerctl.py
import subprocess


class PlayerctlController:
    """
    playerctl を使って実際の音楽プレイヤーを操作する Controller
    （YouTube Music / Chromium / Spotify 等）
    """

    def _run(self, *args) -> bool:
        try:
            subprocess.run(
                ["playerctl", *args],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            # playerctl が無い
            return False

    def play_pause(self):
        print("[ctrl] play_pause (real)")
        ok = self._run("play-pause")
        # 状態はUI側でトグルするので None を返す
        return None if ok else False

    def next_track(self):
        print("[ctrl] next_track (real)")
        return self._run("next")

    def prev_track(self):
        print("[ctrl] prev_track (real)")
        return self._run("previous")