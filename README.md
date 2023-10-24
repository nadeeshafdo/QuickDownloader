# Quick Downloader

A Python script for parallel file downloads in multiple parts using threads.

## Prerequisites

Make sure you have the following installed:

- Python 3
- `requests` library (can be installed via `pip install -r requirements.txt`)

## Usage

1. Clone this repository or download the `quickdownloader.py` script.

2. Open a terminal or command prompt.

3. Run the script by executing:

    ```shell
    python quickdownloader.py
    ```

4. Follow the prompts to specify the URL and the number of parts for the download.

## Example

```shell
$ python quickdownloader.py
URL: https://www.sample.com/sample.exe
Number of parts: 4
```

## How It Works

The script downloads a file in multiple parts, creating progress bars for each part. When all parts are downloaded, they are combined into a single file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---