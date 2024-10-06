import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QProgressBar, QFileDialog, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt
from core import DownloadManager


class Downloader(QMainWindow):
    def __init__(self):
        """
        Initializes the main window of the application.

        Sets the window title, size, initializes the UI components, and
        sets the download manager and max speed to None and 0, respectively.

        :return: None
        """
        super().__init__()
        self.setWindowTitle("Quick Downloader v2")
        self.setFixedSize(600, 350)
        self.init_ui()
        self.download_manager = None
        self.max_speed = 0

    def init_ui(self):
        """
        Initializes the UI components of the main window.

        This method creates all the UI components, including labels, line edits, buttons, and a progress bar, and adds them to a grid layout. It also sets up the properties of the UI components and connects the signals of the buttons to the corresponding slots of this class.

        The method also sets the initial text of the max speed label to 0.00 bytes/second.

        The method does not return any value.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout()
        central_widget.setLayout(layout)

        # URL Label and Entry
        self.url_label = QLabel("URL:")
        layout.addWidget(self.url_label, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter the URL to download")
        layout.addWidget(self.url_entry, 0, 1, 1, 3)

        # Download Button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button, 1, 0)

        # Cancel Button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button, 1, 1)

        # Pause/Resume Button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_download)
        self.pause_button.setEnabled(False)
        layout.addWidget(self.pause_button, 1, 2)

        # Number of Threads
        self.threads_label = QLabel("Threads:")
        layout.addWidget(self.threads_label, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.threads_entry = QLineEdit("4")
        self.threads_entry.setFixedWidth(50)
        layout.addWidget(self.threads_entry, 2, 1)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar, 3, 0, 1, 4)

        # Progress Label
        self.progress_label = QLabel("Downloaded: 0.00%")
        layout.addWidget(self.progress_label, 4, 0, 1, 4)

        # Time Remaining Label
        self.time_label = QLabel("Estimated time remaining: 0.00 seconds")
        layout.addWidget(self.time_label, 5, 0, 1, 4)

        # Current Speed Label
        self.speed_label = QLabel("Current speed: 0.00 bytes/second")
        layout.addWidget(self.speed_label, 6, 0, 1, 4)

        # Max Speed Label
        self.max_speed_label = QLabel("Max speed: 0.00 bytes/second")
        layout.addWidget(self.max_speed_label, 7, 0, 1, 4)

    def start_download(self):
        """
        Starts the download process based on the user's input.

        This method gets the URL and number of threads from the user interface, prompts the user to select a save location, and starts the download process using the DownloadManager class.

        If the user enters invalid input, a warning message box will pop up and the method will return without starting the download.

        If the user cancels the save dialog, the method will return without starting the download.

        The method disables the Download button, enables the Cancel button, and enables the Pause button when the download starts.

        The method also sets the initial text of the max speed label to 0.00 bytes/second.

        The method connects the signals of the DownloadManager instance to the corresponding slots of this class.

        Finally, the method starts the DownloadManager instance and begins the download process.
        """
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid URL.")
            return

        try:
            num_threads = int(self.threads_entry.text())
            if num_threads < 1:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number of threads.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)")
        if not save_path:
            return  # User cancelled the save dialog

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.pause_button.setText("Pause")
        self.max_speed = 0
        self.max_speed_label.setText("Max speed: 0.00 bytes/second")

        self.download_manager = DownloadManager(url, save_path, num_threads)
        self.download_manager.progress.connect(self.update_progress)
        self.download_manager.progress_percent.connect(self.update_progress_percent)
        self.download_manager.speed.connect(self.update_speed)
        self.download_manager.max_speed.connect(self.update_max_speed)
        self.download_manager.time_remaining.connect(self.update_time_remaining)
        self.download_manager.finished_download.connect(self.download_finished)
        self.download_manager.error_occurred.connect(self.download_error)
        self.download_manager.start()

    def cancel_download(self):
        """
        Slot function that is connected to the Cancel button's clicked signal.

        When the button is clicked, it prompts the user to confirm whether they want
        to cancel the download. If the user confirms, it sends a cancel signal to the
        DownloadManager and closes the window. If the user cancels, the function does
        nothing.

        If the download is not running, the function closes the window without
        prompting the user.
        """
        if self.download_manager and self.download_manager.isRunning():
            reply = QMessageBox.question(
                self, 'Cancel Download',
                "Are you sure you want to cancel the download?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.download_manager.cancel()
        else:
            self.close()

    def pause_download(self):
        """
        Slot function that is connected to the Pause/Resume button's clicked signal.

        When the button is clicked, it toggles the download's state between paused and
        resumed. If the download is paused, it sends a pause signal to the
        DownloadManager and changes the button's text to "Resume". If the download is
        resumed, it sends a resume signal to the DownloadManager and changes the
        button's text to "Pause".

        If the download is not running, the function does nothing.
        """
        if self.download_manager and self.download_manager.isRunning():
            if self.pause_button.text() == "Pause":
                self.download_manager.pause()
                self.pause_button.setText("Resume")
            else:
                self.download_manager.resume()
                self.pause_button.setText("Pause")

    def update_progress(self, downloaded):
        """
        Slot function that is called when the number of bytes downloaded is updated.

        :param downloaded: The number of bytes downloaded so far.
        :type downloaded: int
        """
        percent = (downloaded / self.download_manager.total_size) * 100
        self.progress_bar.setValue(percent)

    def update_progress_percent(self, percent):
        """
        Slot function that is called when the percentage of the file downloaded is updated.

        :param percent: The percentage of the file downloaded, from 0 to 100.
        :type percent: float
        """

        self.progress_bar.setValue(int(percent))
        self.progress_label.setText(f"Downloaded: {percent:.2f}%")

    def update_speed(self, speed):
        """
        Slot function that is called when the current download speed is updated.

        :param speed: The current download speed in bytes per second.
        :type speed: float
        """
        self.speed_label.setText(f"Current speed: {speed:.2f} bytes/second")

    def update_max_speed(self, max_speed):
        """
        Slot function that is called when the maximum download speed is updated.

        :param max_speed: The maximum download speed in bytes per second.
        :type max_speed: float
        """
        self.max_speed_label.setText(f"Max speed: {max_speed:.2f} bytes/second")

    def update_time_remaining(self, time_remaining):
        """
        Slot function that is called when the estimated time remaining to complete the download is updated.

        :param time_remaining: The estimated time remaining to complete the download in seconds.
        :type time_remaining: float
        """
        self.time_label.setText(f"Estimated time remaining: {time_remaining:.2f} seconds")

    def download_finished(self):
        """
        Slot function that is called when the download is finished or cancelled.

        It pops up a message box to inform the user that the download is finished or cancelled.
        It also resets the UI to its initial state.
        """

        QMessageBox.information(self, "Download", "Download completed or cancelled.")
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.progress_bar.setValue(0)
        self.progress_label.setText("Downloaded: 0.00%")
        self.time_label.setText("Estimated time remaining: 0.00 seconds")
        self.speed_label.setText("Current speed: 0.00 bytes/second")
        self.max_speed_label.setText(f"Max speed: {self.max_speed:.2f} bytes/second")
        self.download_manager = None

    def download_error(self, error_msg):
        """
        Displays an error message to the user if an error occurs during the download,
        then cancels the download.

        :param error_msg: The error message to display to the user
        :return: None
        """
        QMessageBox.critical(self, "Download Error", f"An error occurred: {error_msg}")
        self.download_manager.cancel()

def main():
    """
    Creates a QApplication instance, initializes a Downloader object, shows it and executes the application's main loop.

    :return: None
    """
    app = QApplication(sys.argv)
    downloader = Downloader()
    downloader.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
