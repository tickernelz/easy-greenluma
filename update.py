import shutil
import zipfile
import requests
import os


class Update:

    def __init__(self, owner, repo, branch):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        self.files = [
            'Hogwarts Legacy.exe'
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
            with zipfile(f"{self.repo}-{self.branch}.zip", "r") as zipObj:
                zipObj.extractall()
        except Exception as e:
            print(f"Error extracting zip file: {e}")
            return False
        return True
                
    def delete_zip(self):
        try:
            os.remove(f"{self.repo}-{self.branch}.zip")
        except Exception as e:
            print(f"Error deleting zip file: {e}")
            return False
        return True
        
    def delete_old_files(self):
        try:
            for file in self.files:
                if os.path.isfile(file):
                    os.remove(file)
            for folder in self.folders:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
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
        delete_old = self.delete_old_files()
        print("Deleting zip file...")
        delete_zip = self.delete_zip()
        if download and extract and delete_old and delete_zip:
            print("Update complete!")
            return True
        return False
       
