import time
from assets import debugging as dev
from assets import core as downloader

while True:
    file_url = str(input("\nFile URL: "))
    downloader.download_file(file_url)

time.sleep(30)
dev.get_error_log()
dev.save_error_log('log.log')