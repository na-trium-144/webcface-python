import ctypes
import platform
import os

if platform.system() == "Windows":
    lib_name = "webcface12.dll"
elif platform.system() == "Linux":
    lib_name = "libwebcface.12.so"
elif platform.system() == "Darwin":
    lib_name = "libwebcface.12.dylib"
else:
    raise ImportError("Unsupported platform: " + platform.system())
if "WEBCFACE_LIBRARY_PATH" in os.environ:
    lib_name = os.path.join(os.environ["WEBCFACE_LIBRARY_PATH"], lib_name)
try:
    wcf = ctypes.cdll.LoadLibrary(lib_name)
except OSError as e:
    raise ImportError(
        f"Could not find WebCFace Library {lib_name}\n\tOriginal error: {str(e)}"
    )

wcfInitW = wcf.wcfInitW
wcfInitW.restype = ctypes.c_void_p
wcfInitW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int]
wcfStart = wcf.wcfStart
wcfStart.argtypes = [ctypes.c_void_p]
wcfSync = wcf.wcfSync
wcfSync.argtypes = [ctypes.c_void_p]
wcfClose = wcf.wcfClose
wcfClose.argtypes = [ctypes.c_void_p]

wcfValueGetVecDW = wcf.wcfValueGetVecDW
wcfValueGetVecDW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_wchar_p,
    ctypes.c_wchar_p,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
]
wcfValueSetVecDW = wcf.wcfValueSetVecDW
wcfValueSetVecDW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_wchar_p,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_int,
]

WCF_OK = 0
WCF_BAD_WCLI = 1
WCF_BAD_HANDLE = 2
WCF_INVALID_ARGUMENT = 3
WCF_NOT_FOUND = 4
WCF_EXCEPTION = 5
WCF_NOT_CALLED = 6
WCF_NOT_RETURNED = 7

WCF_VAL_NONE = 0
WCF_VAL_STRING = 1
WCF_VAL_BOOL = 2
WCF_VAL_INT = 3
WCF_VAL_FLOAT = 4
