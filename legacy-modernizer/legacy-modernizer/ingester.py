import os
import requests
import zipfile
import io

class CodeIngester:

    def __init__(self, source):
        self.source = source
        self.files = {}

    def load(self):
        self.files = {}   # ✅ RESET HERE

        if self.source.startswith("http"):
            return self._load_github_repo()
        else:
            return self._load_local_repo()

    def _load_local_repo(self):
        for root, _, files in os.walk(self.source):
            for file in files:
                if file.endswith((".java", ".cbl")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            self.files[path] = f.read()
                    except:
                        pass
        return self.files

    def _load_github_repo(self):
        branches = ["main", "master"]

        for branch in branches:
            try:
                url = f"{self.source}/archive/refs/heads/{branch}.zip"
                r = requests.get(url)

                if r.status_code != 200:
                    continue

                z = zipfile.ZipFile(io.BytesIO(r.content))

                for file in z.namelist():
                    if file.endswith((".java", ".cbl")):
                        try:
                            self.files[file] = z.read(file).decode("utf-8", errors="ignore")
                        except:
                            pass

                print(f"Loaded from branch: {branch}")
                return self.files

            except:
                continue

        raise Exception("Failed to load GitHub repo")