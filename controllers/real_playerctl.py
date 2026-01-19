# controllers/real_playerctl.py
import subprocess


class PlayerctlController:
    def _run(self, *args):
        try:
            cp = subprocess.run(
                ["playerctl", *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True, (cp.stdout or "").strip()
        except subprocess.CalledProcessError as e:
            return False, (e.stderr or "").strip()
        except FileNotFoundError:
            return False, "playerctl not found"

    def get_status(self):
        # 戻り値: True/False/None（Noneは不明）
        ok, out = self._run("status")
        if not ok:
            return None
        s = out.lower()
        if "playing" in s:
            return True
        if "paused" in s or "stopped" in s:
            return False
        return None

    def play_pause(self):
        print("[ctrl] play_pause (real)")
        ok, _ = self._run("play-pause")
        # 叩いたあと実状態を読む（同期のキモ）
        if not ok:
            return None
        return self.get_status()

    def next_track(self):
        print("[ctrl] next_track (real)")
        ok, _ = self._run("next")
        return ok

    def prev_track(self):
        print("[ctrl] prev_track (real)")
        ok, _ = self._run("previous")
        return ok
    
    def get_metadata(self):
        """
        戻り値: {"title": str, "artist": str} / None
        """
        # title
        ok_t, title = self._run("metadata", "--format", "{{title}}")
        # artist（複数になることある）
        ok_a, artist = self._run("metadata", "--format", "{{artist}}")

        if not ok_t and not ok_a:
            return None

        title = (title or "").strip()
        artist = (artist or "").strip()

        # どっちも空なら未取得扱い
        if not title and not artist:
            return None

        return {"title": title, "artist": artist}