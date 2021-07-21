import mmap
import time
import struct
import subprocess
import sys
import os


# Get functions from win32api
from ctypes import windll
from ctypes.wintypes import BOOL, DWORD, HANDLE, LPCWSTR, LPVOID

LPSECURITY_ATTRIBUTES = LPVOID

_CreateMutexW = windll.kernel32.CreateMutexW
_CreateMutexW.argtypes = (LPSECURITY_ATTRIBUTES, BOOL, LPCWSTR)
_CreateMutexW.restype = HANDLE

_CloseHandle = windll.kernel32.CloseHandle
_CloseHandle.argtypes = (HANDLE,)
_CloseHandle.restype = BOOL

_GetLastError = windll.kernel32.GetLastError
_GetLastError.argtypes = ()
_GetLastError.restype = DWORD

_SetLastError = windll.kernel32.SetLastError
_SetLastError.argtypes = (DWORD,)
_SetLastError.restype = None

ERROR_SUCCESS = 0
ERROR_INVALID_HANDLE = 6
ERROR_ALREADY_EXISTS = 183

def CreateMutex(name: str, initial_owner: bool = False) -> int:
    _SetLastError(ERROR_SUCCESS)
    handle = _CreateMutexW(
        None,
        BOOL(initial_owner),
        LPCWSTR(name)
    )
    error = _GetLastError()
    if error == ERROR_SUCCESS:
        return handle
    else:
        if handle != 0:
            _CloseHandle(handle)
        raise Win32ApiError(error)

def CloseHandle(handle: int) -> None:
    success = bool(_CloseHandle(handle))
    if not success:
        raise Win32ApiError(ERROR_INVALID_HANDLE)

def GetLastError() -> int:
    return _GetLastError()

def SetLastError(error: int) -> None:
    _SetLastError(error)

class Win32ApiError(OSError):
    def __init__(self, errno: int):
        super().__init__()
        self.errno = errno
    
    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.errno)
    
    def __str__(self) -> str:
        if self.errno == ERROR_SUCCESS:
            return "<Error Success>"
        elif self.errno == ERROR_ALREADY_EXISTS:
            return "<Error Already Exists>"
        elif self.errno == ERROR_INVALID_HANDLE:
            return "<Error Invalid Handle>"
        else:
            return "<Unknown Error {}>".format(self.errno)


# Configuration parameters
PYTHON_PATH = "C:\\Program Files\\Python\\pythonw.exe"
SCRIPT_PATH = "C:\\Program Files\\Flan\\converter.py"
MUMBLE_LINK_SIZE = 5460
PAGE_SIZE = 4096
OUTFILE = "Z:\\tmp\\gw2_mumble_link"
ACTIVE_SLEEP_TIME = 1/30 # 30 updates per second
INACTIVE_SLEEP_TIME = 5 # 1 update every 5 seconds
TICKS_PER_SECOND = 1/ACTIVE_SLEEP_TIME
SECONDS_UNTIL_INACTIVE = 10
TICKS_UNTIL_INACTIVE = round(TICKS_PER_SECOND * SECONDS_UNTIL_INACTIVE)


def main():
    # Daemonize
    if "-d" in sys.argv or "--daemonize" in sys.argv:
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(
                [PYTHON_PATH, SCRIPT_PATH],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=devnull, stderr=devnull, stdin=devnull
            )
        sys.exit(0)
    
    # Acquire mutex
    try:
        # The handle is discarded because it will be released when the process dies
        CreateMutex("Flan_GW2_Converter")
    except Win32ApiError as e:
        if e.errno == ERROR_ALREADY_EXISTS:
            print("error: another instance of the converter is already running")
            sys.exit(0)
        else:
            raise e

    # Open shared memory
    print("Opening gw2 mumble link")
    with mmap.mmap(fileno=-1, length=MUMBLE_LINK_SIZE, tagname="MumbleLink") as in_file:
        with open(OUTFILE, "wb") as out_file:
            # Run loop
            previous_tick = None
            missed_ticks = 0
            while True:
                # Seek both input and output to the beginning
                in_file.seek(0)
                out_file.seek(0)

                # Read the raw bytes
                data = in_file.read(PAGE_SIZE)

                # Unpack tick number
                tick = struct.unpack_from("I", data, offset=4)[0]

                # If the tick didn't change, this is a missed tick
                if tick == 0 or tick == previous_tick:
                    #print("Missed Tick: {}/{} ({})".format(missed_ticks, TICKS_UNTIL_INACTIVE, tick)) # Debug missed tick number
                    missed_ticks += 1
                else:
                    #print("Tick:", tick) # Debug tick number
                    #print(data[:32].hex()) # Debug preview of data
                    missed_ticks = 0
                    out_file.write(data)
                
                previous_tick = tick

                # If too many ticks are missed, go into inactive mode
                if missed_ticks > TICKS_UNTIL_INACTIVE:
                    time.sleep(INACTIVE_SLEEP_TIME)
                else:
                    time.sleep(ACTIVE_SLEEP_TIME)


if __name__ == "__main__":
    main()