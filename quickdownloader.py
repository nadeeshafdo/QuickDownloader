import os
import re
import threading
import requests

# Thread-safe session
session = requests.Session()

# Create a lock
lock = threading.Lock()

def download_part(url, start, end, part, total_parts):
    headers = {'Range': f'bytes={start}-{end}'}
    response = session.get(url, headers=headers, stream=True)
    file_size = end - start + 1
    downloaded_size = 0

    with open(f'part{part}', 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
                progress_percentage = (downloaded_size / file_size) * 100

                # Acquire the lock before updating the console
                with lock:
                    # Move the cursor to the line of this part's progress bar and clear it
                    print(f'\033[{part + 2};0H\033[K', end='')
                    # Print the progress bar for this part
                    print(f"Part {part + 1}/{total_parts}: [{'█' * int(progress_percentage // 2):<50}] {progress_percentage:.2f}%")

def download_file(url, num_parts):
    response = session.head(url)
    file_size = int(response.headers['Content-Length'])

    # Get the filename from the Content-Disposition header if present
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        match = re.findall('filename="(.+)"', content_disposition)
        if match:
            filename = match[0]
    else:
        filename = 'output'  # Default filename if not provided

    part_size = file_size // num_parts

    threads = []
    for i in range(num_parts):
        start = i * part_size
        end = start + part_size - 1 if i < num_parts - 1 else file_size - 1
        threads.append(threading.Thread(target=download_part, args=(url, start, end, i, num_parts)))

    # Clear the console and print a placeholder for each progress bar
    print('\033c', end='')
    for i in range(num_parts):
        print()

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Combine all parts into one file
    with open(filename, 'wb') as output_file:
        for i in range(num_parts):
            with open(f'part{i}', 'rb') as input_file:
                output_file.write(input_file.read())
            os.remove(f'part{i}')  # Delete part files

    print(f"\nFile downloaded successfully and saved as {filename}")

# Usage
url = str(input("URL: "))
num_parts = int(input("Number of parts: "))
download_file(url, num_parts)
