import os
import json
import shutil
import hashlib
import time
import requests
from pathlib import Path


def file_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class WitManager:
    def __init__(self, path="."):
        self.working_path = Path(path).absolute()
        self.wit_path = self.working_path / ".wit"
        self.temp_dir = self.wit_path / "temp"
        self.commit_dir = self.wit_path / "commits"

    def init(self):
        os.makedirs(self.wit_path, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.commit_dir, exist_ok=True)
        if os.name == 'nt':
            os.system(f'attrib +h "{self.wit_path}"')
        print(f"Initialized .wit at {self.wit_path}")

    def add(self, path_str):
        ignored_items = [".wit", ".witignore"]
        os.makedirs(self.temp_dir, exist_ok=True)
        if path_str == ".":
            for item in os.listdir(self.working_path):
                if item not in ignored_items:
                    self._do_copy(self.working_path / item)
        else:
            self._do_copy(self.working_path / path_str)
        print(f"Added {path_str} to staging area.")

    def _do_copy(self, source):
        if not source.exists():
            print(f"Error: {source} not found")
            return
        destination = self.temp_dir / source.name
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)

    def commit(self, message):
        commit_id = hashlib.sha1(f"{time.time()}{message}".encode()).hexdigest()[:10]
        new_commit_path = self.commit_dir / commit_id
        last_commit_path = self.get_last_commit_path()

        if last_commit_path and self.compare_folders(last_commit_path, self.temp_dir):
            print("No changes detected since last commit.")
            return

        shutil.copytree(self.temp_dir, new_commit_path)
        with open(self.wit_path / "HEAD", "w") as f:
            f.write(commit_id)

        # Save message for 'wit log'
        log_file = self.wit_path / "commit_log.json"
        log_data = []
        if log_file.exists():
            with open(log_file) as f:
                log_data = json.load(f)
        log_data.append({
            "id": commit_id,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)

        print(f"Commit {commit_id} created successfully.")

    def log(self):
        log_file = self.wit_path / "commit_log.json"
        if not log_file.exists():
            print("No commits yet.")
            return
        with open(log_file) as f:
            log_data = json.load(f)
        for entry in reversed(log_data):
            print(f"commit {entry['id']}")
            print(f"Date:    {entry['timestamp']}")
            print(f"Message: {entry['message']}")
            print()

    def get_last_commit_path(self):
        head_file = self.wit_path / "HEAD"
        if not head_file.exists():
            return None
        with open(head_file, "r") as f:
            last_id = f.read().strip()
            return self.commit_dir / last_id

    def compare_folders(self, folder1, folder2):
        files1 = list(folder1.rglob("*"))
        files2 = list(folder2.rglob("*"))
        if len(files1) != len(files2):
            return False
        for f1 in files1:
            if f1.is_file():
                relative = f1.relative_to(folder1)
                f2 = folder2 / relative
                if not f2.exists() or file_hash(f1) != file_hash(f2):
                    return False
        return True

    def status(self):
        ignored_items = [".wit", ".witignore"]
        last_commit_path = self.get_last_commit_path()

        if not any(self.temp_dir.iterdir()) and (
                last_commit_path is None or self.compare_folders(last_commit_path, self.temp_dir)):
            return "nothing to commit, working tree clean"

        if any(self.temp_dir.iterdir()) and (
                last_commit_path is None or not self.compare_folders(last_commit_path, self.temp_dir)):
            list_files1 = [item for item in os.listdir(self.temp_dir) if item not in ignored_items]
            return f"Changes to be committed: {list_files1}"

        if not self.compare_folders(self.working_path, self.temp_dir):
            list_files2 = [item for item in os.listdir(self.working_path) if item not in ignored_items]
            return f"Changes not staged for commit: {list_files2}"

        return "No changes tracked"

    def checkout(self, commit_id):
        target_commit_path = self.commit_dir / commit_id
        if not target_commit_path.exists():
            print(f"Error: Commit {commit_id} not found.")
            return

        for item in self.working_path.iterdir():
            if item.name == ".wit": continue
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        for item in target_commit_path.iterdir():
            if item.is_file():
                shutil.copy(item, self.working_path)
            elif item.is_dir():
                shutil.copytree(item, self.working_path / item.name)

        shutil.rmtree(self.temp_dir)
        shutil.copytree(target_commit_path, self.temp_dir)
        print(f"Checked out commit {commit_id}")

    def push(self):
        last_commit_path = self.get_last_commit_path()
        if not last_commit_path or not last_commit_path.exists():
            print("Error: No commits found to push. Please commit your changes first.")
            return

        py_files = list(last_commit_path.rglob("*.py"))
        if not py_files:
            print("No Python files found in the last commit to analyze.")
            return

        print(f"CodeGuard: Analyzing {len(py_files)} files from last commit...")

        # Read all files into memory once so we can send to both endpoints
        file_contents = []
        for fp in py_files:
            with open(fp, "rb") as f:
                file_contents.append((fp.name, f.read()))

        try:
            # --- Step 1: Get alerts ---
            alerts_payload = [("files", (name, data, "text/plain")) for name, data in file_contents]
            resp = requests.post("http://127.0.0.1:8000/alerts", files=alerts_payload)
            if resp.status_code == 200:
                alerts = resp.json().get("alerts", [])
                print("\n=== Code Quality Alerts ===")
                if alerts:
                    for alert in alerts:
                        print(f"  - {alert}")
                else:
                    print("  No issues found!")
                print(f"Total: {len(alerts)} warning(s)\n")

            # --- Step 2: Get analysis graph ---
            analyze_payload = [("files", (name, data, "text/plain")) for name, data in file_contents]
            resp = requests.post("http://127.0.0.1:8000/analyze", files=analyze_payload)
            if resp.status_code == 200:
                output_graph_path = self.working_path / "code_analysis_report.png"
                with open(output_graph_path, "wb") as out_f:
                    out_f.write(resp.content)
                print(f"Push successful! Analysis report saved to: {output_graph_path}")
            else:
                print(f"Server error during push analysis. Status code: {resp.status_code}")

        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to CodeGuard server. Is your FastAPI backend running?")
