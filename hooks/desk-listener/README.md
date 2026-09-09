# desk-listener — hear the dev box on your own machine

`notify.py` runs on the droplet, which has no audio. This is the other half:
a tiny listener on **your** machine that plays the sound, reached over a reverse
SSH forward. It only makes noise while you are connected — the rest of the time
the hook's POST just fails silently.

```
dev box (droplet)                     your machine (Fedora)
  notify.py hook  ── POST ──>  127.0.0.1:19191  ──>  listener.py  ──>  paplay + notify-send
                  (reverse-forwarded over your SSH session)
```

## Setup on your machine

1. **Forward the port on every connection to the dev box.** In `~/.ssh/config`:

   ```
   Host <dev-box>
       RemoteForward 127.0.0.1:19191 127.0.0.1:19191
   ```

   Zed's remote connections use this file, so nothing else is needed there. A
   second concurrent connection will log `remote port forwarding failed` and
   carry on — harmless, the first connection owns the port.

2. **Run the listener**, as a user service so it survives logout:

   ```
   mkdir -p ~/.config/systemd/user
   cp desk-listener.service ~/.config/systemd/user/
   # edit ExecStart in that copy to this repo's real path
   systemctl --user daemon-reload
   systemctl --user enable --now desk-listener
   loginctl enable-linger "$USER"
   ```

   Needs `paplay` (or `pw-play` / `aplay` / `canberra-gtk-play`) and, for the
   popup, `notify-send` (`libnotify`). All standard on a Fedora workstation.

## Setup on the dev box

`.claude/hooks/notify.local.json` (gitignored):

```json
{ "local": "http://127.0.0.1:19191" }
```

## Check it

With the SSH session up and the listener running, from the dev box:

```
curl -sX POST 127.0.0.1:19191 -d '{"event":"needs-you","title":"test","body":"hi"}'
```

You should hear the arpeggio and see a popup on your machine. `systemctl --user
status desk-listener` and `journalctl --user -u desk-listener` if not.
