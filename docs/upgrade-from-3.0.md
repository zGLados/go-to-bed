# Upgrading from 3.0.0 to 3.1

Version 3.0.0 cannot update itself, so you install 3.1 **once by hand**. It takes about a minute, you don't need to quit anything first, and your settings and statistics are kept. From 3.1 on, every update is installed automatically.

## Steps

1. **Download** `GotoBed.exe` from the [3.1.0 release](https://github.com/zGLados/go-to-bed/releases/tag/v3.1.0) (or the [latest release](https://github.com/zGLados/go-to-bed/releases/latest)).
2. **Double-click** the downloaded file. Your 3.0.0 may keep running – that's fine.
   - If Windows SmartScreen shows *"Windows protected your PC"*: click **More info → Run anyway** (the exe is not code-signed).
3. **Wait a few seconds.** Go-to-Bed now:
   - stops the running 3.0.0 (its tray icon disappears),
   - installs itself to `%LOCALAPPDATA%\Programs\GotoBed`,
   - starts the new version (new tray icon) and shows the notification **"Go-to-Bed installed – The old version was replaced"**,
   - deletes your old `GotoBed.exe` and puts a **Go-to-Bed shortcut** in the same place (e.g. on your Desktop),
   - moves *Start with Windows* to the new version and adds **Go-to-Bed** to the Start menu and to *Settings → Apps*.
4. **Done.** You can delete the downloaded file (e.g. from your Downloads folder).

## Check that it worked

- Right-click the tray icon → the last entry says **Quit (v3.1.0)**.
- Tray → **Settings** → the new **Updates** section shows *Installed version: 3.1.0*. Your bedtime, days and other settings are the same as before.
- *Task Manager → Startup apps* lists **GotoBed** (enabled, if *Start with Windows* is on).

## If something is different

| What you see | What to do |
|---|---|
| *"The same or a newer version of Go-to-Bed is already running"* | 3.1 (or newer) is already installed and running – nothing to do. |
| The old tray icon is still there and a second one appeared | Right-click the old icon → **Quit**. Then start the new version from the Start menu. |
| The old `GotoBed.exe` is still there (no shortcut) | It could not be deleted, e.g. because it is in a protected folder or on a USB stick. Delete it by hand; the installed version in the Start menu is the one to use. |
| Nothing happens at all | Look in the hidden tray icons (**^** in the taskbar). Otherwise check `%APPDATA%\GotoBed\gotobed.log` and [open an issue](https://github.com/zGLados/go-to-bed/issues). |

### Manual way (always works)

1. Right-click the Go-to-Bed tray icon → **Quit**.
2. Start the downloaded 3.1 `GotoBed.exe` once.
3. Delete the old `GotoBed.exe`.

Settings and statistics live in `%APPDATA%\GotoBed` and are not touched by any of this.
