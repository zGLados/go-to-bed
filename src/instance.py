"""Single-instance lock and a "please quit" signal between Go-to-Bed processes (Windows).

The running app holds a named mutex. Other processes (the uninstaller) can
ask it to quit by setting a named event that the app waits on.
On other platforms these are no-ops so the app can run there for development.
"""
import sys
import threading
import time
from typing import Callable

from config import APP_NAME

MUTEX_NAME = f'Local\\{APP_NAME}SingleInstance'
QUIT_EVENT_NAME = f'Local\\{APP_NAME}Quit'
ERROR_ALREADY_EXISTS = 183

if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    _kernel32.CreateMutexW.restype = wintypes.HANDLE
    _kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.CreateEventW.restype = wintypes.HANDLE
    _kernel32.CreateEventW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.OpenEventW.restype = wintypes.HANDLE
    _kernel32.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.SetEvent.argtypes = [wintypes.HANDLE]
    _kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def acquire_lock(wait_seconds: float = 0):
    """Return a lock handle, or None if another instance holds it (after waiting up to `wait_seconds`)."""
    if sys.platform != 'win32':
        return True
    deadline = time.monotonic() + wait_seconds
    while True:
        handle = _kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.get_last_error() != ERROR_ALREADY_EXISTS:
            return handle
        _kernel32.CloseHandle(handle)
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.5)


def release_lock(handle) -> None:
    """Release a lock from acquire_lock() so another instance can start."""
    if sys.platform == 'win32' and handle:
        _kernel32.CloseHandle(handle)


def watch_quit_signal(on_quit: Callable[[], None]) -> None:
    """Call `on_quit` (from a background thread) when another process requests a quit."""
    if sys.platform != 'win32':
        return
    event = _kernel32.CreateEventW(None, True, False, QUIT_EVENT_NAME)

    def wait():
        if _kernel32.WaitForSingleObject(event, 0xFFFFFFFF) == 0:  # INFINITE, WAIT_OBJECT_0
            on_quit()

    threading.Thread(target=wait, name='quit-signal', daemon=True).start()


def request_quit() -> bool:
    """Ask a running instance to quit. Returns whether one was listening."""
    if sys.platform != 'win32':
        return False
    event = _kernel32.OpenEventW(0x0002, False, QUIT_EVENT_NAME)  # EVENT_MODIFY_STATE
    if not event:
        return False
    _kernel32.SetEvent(event)
    _kernel32.CloseHandle(event)
    return True
