from zipfile import ZipFile
from tkinter import *
from tkinter import messagebox
import shutil
import tkinter as tk
import requests
import os
import sys
import json


class Update:

    def __init__(self):
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)
        
        def load_user(data_path="config.json"):
            if os.path.isfile(data_path):
                json_data = json.load(open(data_path))
                return json_data
            return None
        
        self.owner = load_user("config.json").get("owner")
        self.repo = load_user("config.json").get("repo")
        self.branch = load_user("config.json").get("branch")
        self.url = f"https://api.github.com/repos/{self.owner}/{self.repo}/zipball/{self.branch}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        self.files = [
            'Hogwarts Legacy.exe',
            'config.json',
        ]
        self.folders = [
            'AppList',
            'AppOwnershipTickets',
            'EncryptedAppTickets'
        ]

    def download(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                with open(f"{self.repo}-{self.branch}.zip", "wb") as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Error downloading zip file: {e}")
            return False
        return True

    def extract(self):
        try:
            with ZipFile(f"{self.repo}-{self.branch}.zip", "r") as zipObj:
                zipObj.extractall()
        except Exception as e:
            print(f"Error extracting zip file: {e}")
            return False
        return True

    def get_folder_name(self):
        for folder in os.listdir():
            if folder.startswith(f"{self.owner}-{self.repo}"):
                return folder
        return None

    def get_app_path(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
            running_mode = 'Frozen/executable'
        else:
            try:
                app_full_path = os.path.realpath(__file__)
                application_path = os.path.dirname(app_full_path)
                running_mode = "Non-interactive (e.g. 'python myapp.py')"
            except NameError:
                application_path = os.getcwd()
                running_mode = 'Interactive'
        return {
            "path": application_path,
            "mode": running_mode
        }

    def move_files(self):
        # Move files inside extracted folder to main folder
        folder_name = self.get_folder_name()
        for file in self.files:
            try:
                # check if config.json exists
                if file == "config.json":
                    if os.path.isfile(f"{self.get_app_path().get('path')}/{file}"):
                        continue
                shutil.move(f"{folder_name}/{file}", f"{self.get_app_path().get('path')}/{file}")
            except Exception as e:
                print(f"Error moving file: {e}")
                return False
        # Move folders inside extracted folder to main folder
        for folder in self.folders:
            try:
                shutil.move(f"{folder_name}/{folder}", f"{self.get_app_path().get('path')}/{folder}")
            except Exception as e:
                print(f"Error moving folder: {e}")
                return False
        return True

    def delete_zip(self):
        try:
            os.remove(f"{self.repo}-{self.branch}.zip")
        except Exception as e:
            print(f"Error deleting zip file: {e}")
            return False
        return True
    
    def delete_extracted_folder(self):
        try:
            folder_name = self.get_folder_name()
            shutil.rmtree(f"{folder_name}", ignore_errors=True)
        except Exception as e:
            print(f"Error deleting extracted folder: {e}")
            return False
        return True

    def delete_old_app_path(self):
        try:
            app_path = self.get_app_path().get("path")
            # Delete files
            for file in self.files:
                shutil.rmtree(f"{app_path}/{file}", ignore_errors=True)
            # Delete folders
            for folder in self.folders:
                shutil.rmtree(f"{app_path}/{folder}", ignore_errors=True)
        except Exception as e:
            print(f"Error deleting old files: {e}")
            return False
        return True

    def update(self):
        print("Downloading latest version...")
        download = self.download()
        print("Extracting latest version...")
        extract = self.extract()
        print("Deleting old files...")
        delete_old = self.delete_old_app_path()
        print("Moving files...")
        move = self.move_files()
        print("Deleting zip file...")
        delete_zip = self.delete_zip()
        print("Deleting extracted folder...")
        delete_extracted_folder = self.delete_extracted_folder()
        if download and extract and delete_old and move and delete_zip and delete_extracted_folder:
            messagebox.showinfo("Update", "Update successful!")
            return True
        messagebox.showerror("Update", "Update failed!")
        return False

if __name__ == "__main__":
    update = Update()
    update.update()
