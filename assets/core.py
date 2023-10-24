import requests
import re

def progress_bar(iterable, total, length=50):
    for i, item in enumerate(iterable):
        percent = (i + 1) / total
        arrow = "=" * int(length * percent)
        spaces = " " * (length - len(arrow))
        print(f"\r[{arrow}{spaces}] {int(percent * 100)}%", end="")
        yield item

def download_file(url):
    try:
        # Send a GET request to the URL to download the file and wait for 60 seconds before timing out.
        response = requests.get(url, stream=True, timeout=60)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            chunk_size = 1024  # 1 KB
            # Get the total file size in bytes from the response headers
            total_size = int(response.headers.get('content-length', 0))
            print("File Size: ", total_size / chunk_size, "KB")

            # Extract the filename from the 'content-disposition' header if it exists
            d = response.headers.get('content-disposition')
            if d is not None:
                save_path = re.findall("filename=(.+)", d)[0]
                # Remove any double quotation marks from the filename
                save_path = save_path.replace('"', '')
            else:
                save_path = url.split('/')[-1]

            print("Filename: ", save_path)

            # Create a progress bar
            for _ in progress_bar(range(total_size), total_size):
                pass

            # Open the file for writing in binary mode
            with open(save_path, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    # Write the data to the file
                    file.write(data)

            print("\nDownload complete!")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    except Exception as err:
        print(f"Error:\n{err}")
    except KeyboardInterrupt as err:
        print(f"\nTerminated by the user")
