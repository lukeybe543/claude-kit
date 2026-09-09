#!/usr/bin/env python3
"""Play a sound on the desktop you sit at when a remote notify.py hook asks.

The notify.py hooks run on the dev box (a headless droplet), which has no audio.
This runs on your own machine and listens on a loopback port; the dev box
reaches it through a reverse SSH forward of that same port. When the forward is
down -- you are not connected -- the hook's POST just fails, silently, which is
what you want.

    # ~/.ssh/config, for the dev box:
    #   Host <dev-box>
    #       RemoteForward 127.0.0.1:19191 127.0.0.1:19191
    #
    # then, on this machine (systemd --user, see desk-listener.service):
    python3 listener.py

    # and on the dev box, in .claude/hooks/notify.local.json:
    #   { "local": "http://127.0.0.1:19191" }

Sounds come from ../sounds/ if this repo is checked out here, else the
freedesktop theme, else nothing but a desktop popup.
"""

import json
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = 19191

BUNDLED = Path(__file__).resolve().parent.parent / "sounds"
FREEDESKTOP = Path("/usr/share/sounds/freedesktop/stereo")
_THEME = {
    "needs-you": "phone-incoming-call.oga", "pass": "complete.oga",
    "fail": "dialog-error.oga", "done": "message.oga",
    "compacting": "dialog-warning.oga",
}
_QUIET = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}


def _player():
    for name in ("paplay", "pw-play", "aplay"):
        found = shutil.which(name)
        if found:
            return [found]
    canberra = shutil.which("canberra-gtk-play")
    return [canberra, "-f"] if canberra else None


def _sound(event):
    bundled = BUNDLED / (event + ".wav")
    if bundled.is_file():
        return bundled
    theme = FREEDESKTOP / _THEME.get(event, "")
    return theme if theme.is_file() else None


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            payload = {}
        self.send_response(204)
        self.end_headers()

        player = _player()
        sound = _sound(payload.get("event") or "needs-you")
        if player and sound:
            subprocess.Popen([*player, str(sound)], **_QUIET)
        if shutil.which("notify-send"):
            subprocess.Popen(
                ["notify-send", "-a", "Claude Code",
                 payload.get("title") or "Claude", payload.get("body") or ""],
                **_QUIET)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
