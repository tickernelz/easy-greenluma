from datetime import datetime
from tkinter import *
from tkinter import messagebox
from pkg_resources import parse_version
import subprocess
import tkinter as tk
import os
import shutil
import distutils
import sys
import win32com.client
import time
import requests
import json

data_url = "https://raw.githubusercontent.com/tickernelz/easy-greenluma/master/data.json"
owner = "tickernelz"
repo_master = "easy-greenluma"
branch_master = "master"
version = "1.1.1"


def run_as_admin(argv=None, debug=False):
    shell = win32com.client.Dispatch("WScript.Shell")
    if argv is None and shell. statusbar("%1"):
        argv = shell.statusbar("%1").split()
    if debug:
        import sys
        sys.stderr.write("Running %r as admin\n" % (argv,))
    shell.Run(" ".join('"%s"' % arg for arg in argv), 0, True)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check_internet():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except Exception:
        return False


def load_data(id, username, checkVersion=False):
    data = requests.get(data_url, timeout=3)
    if data.status_code == 200:
        json_data = data.json()
        if checkVersion:
            return json_data.get("version")
        appid_obj = json_data['ids'].get(id)
        if appid_obj:
            return appid_obj.get(username)


def check_version():
    current_version = load_data(None, None, checkVersion=True)
    if current_version:
        if parse_version(current_version) > parse_version(version):
            return True
    return False


def load_user(data_path=resource_path("user.json")):
    if os.path.isfile(data_path):
        json_data = json.load(open(data_path))
        return json_data["username"]
    return None


def load_appid(data_path=resource_path("appid.json")):
    if os.path.isfile(data_path):
        json_data = json.load(open(data_path))
        return json_data["id"]
    return None


def check_for_updates():
    is_internet_available = check_internet()
    if is_internet_available:
        appid = load_appid()
        username = load_user()
        if appid and username:
            user_data = load_data(appid, username)
            if user_data:
                exp = datetime.fromtimestamp(user_data["exp"])
                datetime_now = datetime.now()
                version = check_version()
                if exp < datetime_now or version:
                    # Show the update message
                    mb1 = messagebox.askyesno(
                        'Update Available', 'An update is available. Do you want to update?')
                    if mb1 == True:
                        return True
    return False

def get_steam_path():
    config_json = "config.json"
    if os.path.isfile(config_json):
        json_data = json.load(open(config_json))
        return json_data["steamPath"]
    return None


def update():
    update_data = check_for_updates()
    if update_data:
        # Run update.exe inside main directory then exit
        subprocess.Popen(os.path.join(os.getcwd(), "update.exe"))
        sys.exit()


if __name__ == "__main__":

    # Check updates
    update()
    
    # Get the Steam path
    steam_path = get_steam_path()

    # Kill the steam.exe process
    subprocess.run(["taskkill", "/F", "/IM", "steam.exe"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for 5 seconds
    time.sleep(5)

    # Remove the existing Steam directories
    dirs_to_remove = [
        steam_path + "\\AppList",
        steam_path + "\\AppOwnershipTickets",
        steam_path + "\\EncryptedAppTickets"
    ]
    for dir_to_remove in dirs_to_remove:
        shutil.rmtree(dir_to_remove, ignore_errors=True)

    # Create the Steam directories
    dirs_to_create = [
        steam_path + "\\AppList",
        steam_path + "\\AppOwnershipTickets",
        steam_path + "\\EncryptedAppTickets"
    ]
    for dir_to_create in dirs_to_create:
        os.makedirs(dir_to_create, exist_ok=True)

    # Copy the folders to the Steam directories
    folders_to_copy = [
        ("bin", steam_path + "\\bin"),
        ("GreenLuma2020_Files", steam_path + "\\GreenLuma2020_Files"),
    ]

    folders_to_copy2 = [
        ("AppList", steam_path + "\\AppList"),
        ("AppOwnershipTickets", steam_path + "\\AppOwnershipTickets"),
        ("EncryptedAppTickets", steam_path + "\\EncryptedAppTickets")
    ]

    files_to_copy = [
        ("DLLInjector.exe", steam_path),
        ("DLLInjector.ini", steam_path),
        ("GreenLuma_2020_x64.dll", steam_path),
        ("GreenLuma_2020_x86.dll", steam_path),
    ]

    for src, dst in folders_to_copy:
        distutils.dir_util.copy_tree(resource_path(src), dst)

    for src, dst in folders_to_copy2:
        distutils.dir_util.copy_tree(src, dst)

    for src, dst in files_to_copy:
        shutil.copy(resource_path(src), dst)

    # Start the DLLInjector.exe process
    os.chdir(steam_path)
    subprocess.Popen(["DLLInjector.exe"], shell=True)
