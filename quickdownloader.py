import time as tm
import requests
from tqdm import tqdm
import re
import traceback

try:
    def download_file(url):
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
            else:
                save_path = url.split('/')[-1]

            print("Filename: ", save_path)

            # Create a progress bar using tqdm
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)

            # Open the file for writing in binary mode
            with open(save_path, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    # Write the data to the file
                    file.write(data)
                    # Update the progress bar
                    progress_bar.update(len(data))

            # Close the progress bar
            progress_bar.close()

            print("Download complete!")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    if __name__ == "__main__":

        while True:
            file_url = str(input("\nFile URL: "))
            
            download_file(file_url)
except Exception as err:
    print(f"Error:\n{err}")
    traceback.print_exc()
except KeyboardInterrupt as err:
    print(f"\nTerminated by the user.")
tm.sleep(30)
