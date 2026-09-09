# desk-listener — hear the dev box on your own machine

`notify.py` runs on the dev box (a headless droplet), which has no audio. This
is the other half: a tiny listener on **your** machine that plays the bundled
sound and pops a desktop notification when the dev box POSTs to it.

```
dev box (droplet)                          your machine
  notify.py hook  ── POST ──>  :19191  ──>  listener.py  ──>  paplay + notify-send
```

Two transports — pick one and set the dev box's `notify.local.json` `"local"`
URL to match.

## Over a tailnet (recommended for a fixed workstation)

The listener binds `0.0.0.0` and the dev box reaches it at the workstation's
tailnet address. Works whenever the workstation is up — no SSH session needed.

1. Install the service (it sets `NOTIFY_LISTEN_ADDR=0.0.0.0`):

   ```
   mkdir -p ~/.config/systemd/user
   cp desk-listener.service ~/.config/systemd/user/
   # confirm ExecStart points at this file's real path
   systemctl --user daemon-reload
   systemctl --user enable --now desk-listener
   loginctl enable-linger "$USER"
   ```

2. Allow the port on the tailnet zone (firewalld):

   ```
   sudo firewall-cmd --permanent --zone=trusted --add-port=19191/tcp
   sudo firewall-cmd --reload
   ```

   (Tailscale usually puts `tailscale0` in the `trusted` zone. Check with
   `firewall-cmd --get-zone-of-interface=tailscale0`.)

3. On the dev box, `.claude/hooks/notify.local.json`:

   ```json
   { "local": "http://<workstation-tailnet-ip>:19191" }
   ```

## Over a reverse SSH forward (laptop, or no tailnet)

Only makes noise while you are connected. Set `NOTIFY_LISTEN_ADDR=127.0.0.1` (or
drop the `Environment=` line), and in `~/.ssh/config` for the dev box:

```
Host <dev-box>
    RemoteForward 127.0.0.1:19191 127.0.0.1:19191
```

Zed and VS Code remote connections use `~/.ssh/config`. A second concurrent
connection logs `remote port forwarding failed` and carries on — harmless.
Dev box `notify.local.json`: `{ "local": "http://127.0.0.1:19191" }`.

## Requirements & check

Needs `paplay` (or `pw-play` / `aplay` / `canberra-gtk-play`) and `notify-send`
(`libnotify`) — standard on a Fedora workstation. Sounds are read from
`../sounds/`; if they are missing only the popup fires, never a system sound.

From the dev box:

```
curl -sX POST <the same URL> -d '{"event":"needs-you","title":"test","body":"hi"}'
```

You should hear the bell and see a popup. `systemctl --user status
desk-listener` and `journalctl --user -u desk-listener -f` if not.
