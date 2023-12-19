import requests
from os import path
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import time

class Downloader(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding="10")
        self.grid(sticky=(tk.W, tk.E, tk.N, tk.S))
        self.create_widgets()
        self.max_speed = 0
        self.cancelled = False
        self.paused = False
        self.downloading = False

    def create_widgets(self):
        self.url_label = ttk.Label(self, text="URL:")
        self.url_label.grid(row=0, column=0, sticky=tk.W)

        self.url_entry = ttk.Entry(self, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        self.download_button = ttk.Button(self, text="Download", command=self.start_download)
        self.download_button.grid(row=1, column=0)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel_download)
        self.cancel_button.grid(row=1, column=1)

        self.pause_button = ttk.Button(self, text="Pause", command=self.pause_download)
        self.pause_button.grid(row=1, column=2)

        self.progress = ttk.Progressbar(self, length=400)
        self.progress.grid(row=2, column=0, columnspan=3, pady=10)

        self.progress_label = ttk.Label(self, text="")
        self.progress_label.grid(row=3, column=0, columnspan=3)

        self.time_label = ttk.Label(self, text="")
        self.time_label.grid(row=4, column=0, columnspan=3)

        self.speed_label = ttk.Label(self, text="")
        self.speed_label.grid(row=5, column=0, columnspan=3)

        self.max_speed_label = ttk.Label(self, text="")
        self.max_speed_label.grid(row=6, column=0, columnspan=3)

    def start_download(self):
        self.cancelled = False
        self.paused = False
        self.downloading = True
        self.download_thread = Thread(target=self.download_file, args=(self.url_entry.get(),))
        self.download_thread.start()

    def cancel_download(self):
        if self.downloading:
            self.cancelled = True
        else:
            self.master.destroy()

    def pause_download(self):
        self.paused = not self.paused
        self.pause_button["text"] = "Resume" if self.paused else "Pause"

    def download_file(self, url):
        url_parse = urlparse(url)
        filename = path.basename(url_parse.path)
        save_path = filedialog.askdirectory()
        filename = path.join(save_path, filename)
        response = requests.get(url, stream=True, timeout=60)  # Increase timeout to 60 seconds
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        self.progress["maximum"] = total_size_in_bytes

        start_time = time.time()
        try:
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    while self.paused:
                        time.sleep(1)
                    if self.cancelled:
                        break
                    fd.write(chunk)
                    downloaded = self.progress["value"] = self.progress["value"] + len(chunk)
                    percentage = downloaded / (total_size_in_bytes + 1e-9) * 100
                    self.progress_label["text"] = f"Downloaded: {percentage:.2f}%"

                    elapsed_time = time.time() - start_time
                    speed = downloaded / (elapsed_time + 1e-9)  # Add a small value to prevent division by zero
                    self.speed_label["text"] = f"Current speed: {speed:.2f} bytes/second"
                    self.max_speed = max(self.max_speed, speed)
                    self.max_speed_label["text"] = f"Max speed: {self.max_speed:.2f} bytes/second"

                    remaining_time = (total_size_in_bytes - downloaded) / speed
                    self.time_label["text"] = f"Estimated time remaining: {remaining_time:.2f} seconds"
        finally:
            # Reset the displayed values after the download is completed or cancelled
            self.progress["value"] = 0
            self.progress_label["text"] = ""
            self.time_label["text"] = ""
            self.speed_label["text"] = ""
            self.max_speed_label["text"] = ""
            self.max_speed = 0
            self.pause_button["text"] = "Pause"
            self.downloading = False

def main():
    root = tk.Tk()
    root.title("Quick Downloader")
    root.geometry("500x200")  # Set the window size
    root.resizable(False, False)  # Disable resizing
    app = Downloader(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
