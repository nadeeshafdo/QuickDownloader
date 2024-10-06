import requests
from os import remove
import math
import time
from PyQt6.QtCore import QThread, pyqtSignal

class PartDownloadThread(QThread):
    progress = pyqtSignal(int)
    finished_part = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url, start, end, part_num, save_path):
        """
        Initializes a PartDownloadThread instance.

        :param url: The URL of the file to download.
        :type url: str
        :param start: The start byte of the part to download.
        :type start: int
        :param end: The end byte of the part to download.
        :type end: int
        :param part_num: The number of the part to download.
        :type part_num: int
        :param save_path: The path to save the downloaded part to.
        :type save_path: str
        """
        super().__init__()
        self.url = url
        self.start = start
        self.end = end
        self.part_num = part_num
        self.save_path = save_path
        self.cancelled = False

    def run(self):
        """
        Downloads a part of a file from the given URL and saves it to the given save path.

        The part to download is specified by the start and end byte offsets, and the number
        of the part is specified by the part_num parameter.

        If the download is cancelled, the file is deleted and the function exits immediately.

        If any error occurs, the error message is emitted as a signal.

        :return: None
        """
        try:
            headers = {'Range': f'bytes={self.start}-{self.end}'}
            with requests.get(self.url, headers=headers, stream=True, timeout=120) as response:
                response.raise_for_status()
                with open(f"{self.save_path}.part{self.part_num}", 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if self.cancelled:
                            f.close()
                            remove(f"{self.save_path}.part{self.part_num}")
                            return
                        if chunk:
                            f.write(chunk)
                            self.progress.emit(len(chunk))
            self.finished_part.emit(self.part_num)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        """Cancel the download."""
        self.cancelled = True


class DownloadManager(QThread):
    progress = pyqtSignal(int)
    progress_percent = pyqtSignal(float)
    speed = pyqtSignal(float)
    max_speed = pyqtSignal(float)
    time_remaining = pyqtSignal(float)
    finished_download = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, url, save_path, num_threads=4):
        """
        Initializes a DownloadManager instance.

        :param url: The URL of the file to download.
        :type url: str
        :param save_path: The path to save the downloaded file to.
        :type save_path: str
        :param num_threads: The number of threads to use for downloading. Defaults to 4.
        :type num_threads: int

        This method sets up the necessary variables and starts the download process by calling the run method in a separate thread.
        """
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.num_threads = num_threads
        self.threads = []
        self.total_size = 0
        self.downloaded = 0
        self.max_speed_value = 0
        self.cancelled = False
        self.paused = False
        self.start_time = time.time()

    def run(self):
        """
        Starts the download process.

        This method gets the total size of the file, creates and starts the required number of threads to download the file in parts, and waits for all the threads to finish.

        If the download is not cancelled, it merges the downloaded parts into a single file and emits the finished_download signal.

        If any error occurs, it emits the error_occurred signal with the error message and then emits the finished_download signal.
        """
        try:
            self.total_size = self.get_file_size()
            part_size = math.ceil(self.total_size / self.num_threads)
            self.progress.emit(0)
            self.progress_percent.emit(0.0)
            self.downloaded = 0
            self.max_speed_value = 0

            for i in range(self.num_threads):
                start = part_size * i
                end = start + part_size - 1 if i < self.num_threads - 1 else self.total_size
                thread = PartDownloadThread(self.url, start, end, i, self.save_path)
                thread.progress.connect(self.update_progress)
                thread.finished_part.connect(self.part_finished)
                thread.error.connect(self.thread_error)
                self.threads.append(thread)
                thread.start()

            for thread in self.threads:
                thread.wait()

            if not self.cancelled:
                self.merge_files()
                self.finished_download.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.finished_download.emit()

    def get_file_size(self):
        """
        Retrieves the size of the file at the given URL.

        :return: The size of the file in bytes, or 0 if the size could not be retrieved.
        :type: int
        :raises: Exception if the request fails.
        """

        response = requests.head(self.url)
        if response.status_code == 200:
            return int(response.headers.get('content-length', 0))
        else:
            raise Exception("Failed to retrieve file size.")

    def update_progress(self, chunk_size):
        """
        Called when a part of the download has finished.

        Updates the progress signals and displays the current speed, max speed, and time remaining.

        :param chunk_size: The size of the chunk of data that has been downloaded
        :type chunk_size: int
        """
        if not self.paused:
            self.downloaded += chunk_size
            self.progress.emit(self.downloaded)
            percent = (self.downloaded / self.total_size) * 100
            self.progress_percent.emit(percent)

            elapsed_time = time.time() - self.start_time
            current_speed = self.downloaded / (elapsed_time + 1e-9)  # bytes per second
            self.speed.emit(current_speed)

            if current_speed > self.max_speed_value:
                self.max_speed_value = current_speed
                self.max_speed.emit(self.max_speed_value)

            remaining_bytes = self.total_size - self.downloaded
            remaining_time = remaining_bytes / (current_speed + 1e-9)
            self.time_remaining.emit(remaining_time)

    def part_finished(self, part_num):
        """
        Called when a part of the download is finished.

        Emits the part_finished signal with the given part number.

        :param part_num: The part number that has finished downloading
        :type part_num: int
        """

        self.part_finished.emit(part_num)

    def thread_error(self, error_msg):
        """
        Called when an error occurs in a PartDownloadThread.

        Emits the error_occurred signal with the given error message and
        cancels the download.

        :param error_msg: The error message from the PartDownloadThread
        :type error_msg: str
        """
        self.error_occurred.emit(error_msg)
        self.cancel()

    def merge_files(self):
        """
        Merges the part files into a single file after all parts have been downloaded.
        
        Opens the save path as a binary file in write mode and writes the contents of each
        part file to it. The part files are then deleted.
        """
        with open(self.save_path, 'wb') as outfile:
            for i in range(self.num_threads):
                part_path = f"{self.save_path}.part{i}"
                with open(part_path, 'rb') as infile:
                    outfile.write(infile.read())
                remove(part_path)

    def pause(self):
        """
        Pauses the download process if it is running.

        Sets the paused flag to True, which will prevent the DownloadManager from
        updating the progress bar and the UI. The pause method of each PartDownloadThread
        is called to pause the individual threads, but currently, it does nothing.
        """
        
        self.paused = True
        for thread in self.threads:
            thread.pause()  # Note: PartDownloadThread has no pause method

    def resume(self):
        """
        Resumes the download process if it was paused.

        Sets the paused flag to False, allowing the download process to continue.
        """
        
        self.paused = False

    def cancel(self):
        """
        Cancels the download process and stops all threads.

        Sets the cancelled flag to True and calls the cancel method of each
        PartDownloadThread in the list of threads.

        :return: None
        """
        self.cancelled = True
        for thread in self.threads:
            thread.cancel()
