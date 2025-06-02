# logger.py
import threading
import os

lock = threading.Lock()
log_path = os.path.join(os.path.dirname(__file__), "szavazatok.txt")

def save_vote_to_file(vote_data_str: str, file_name: str = log_path):
    with lock:
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(vote_data_str + "\n")
