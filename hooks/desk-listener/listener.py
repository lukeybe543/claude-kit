#!/usr/bin/env python3
"""Play a sound on the desktop you sit at when a remote notify.py hook asks.

The notify.py hooks run on the dev box (a headless droplet), which has no audio.
This runs on your own machine and plays the bundled sound plus a desktop popup
when the dev box POSTs to it. Two ways for the dev box to reach it:

  * over a tailnet -- bind 0.0.0.0 here (NOTIFY_LISTEN_ADDR=0.0.0.0) and point
    the dev box at http://<this-machine-tailscale-ip>:19191; works whenever this
    machine is up.
  * over a reverse SSH forward -- keep the default loopback bind and add
    `RemoteForward 127.0.0.1:19191 127.0.0.1:19191` to ~/.ssh/config for the dev
    box; works only while you are connected.

Either way, set `"local"` in the dev box's .claude/hooks/notify.local.json to
the matching URL. See README.md.

Sounds come from ../sounds/ (the claude-kit / project checkout this file lives
in). If they are missing, only the desktop popup fires -- it never falls back to
a system sound.
"""

import json
import os
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = 19191
LISTEN_ADDR = os.environ.get("NOTIFY_LISTEN_ADDR", "127.0.0.1")
BUNDLED = Path(__file__).resolve().parent.parent / "sounds"
_QUIET = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}


def _player():
    for name in ("paplay", "pw-play", "aplay"):
        found = shutil.which(name)
        if found:
            return [found]
    canberra = shutil.which("canberra-gtk-play")
    return [canberra, "-f"] if canberra else None


def _sound(event):
    wav = BUNDLED / (event + ".wav")
    return wav if wav.is_file() else None


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
    HTTPServer((LISTEN_ADDR, PORT), Handler).serve_forever()
