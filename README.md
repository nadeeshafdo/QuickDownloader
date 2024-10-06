# Quick Downloader

A command line-based GUI tool for downloading large files quickly and efficiently.

## About

The Quick Downloader is a Python-based tool that uses multi-threading to download large files quickly and efficiently. It splits the download into multiple parts and downloads them concurrently, significantly reducing the total download time.

The tool utilizes Python's threading capabilities and the `requests` library for handling HTTP requests. It also provides a simple and intuitive command line interface for easy use.

## Features

* Multi-threaded downloading for fast and efficient downloads
* Supports HTTP and HTTPS downloads
* Supports large file downloads (> 2GB)
* Supports resumable downloads (if server supports it)
* Supports custom number of threads for download
* Supports custom download speed limit
* Supports logging of download progress and errors
* Supports pause and resume of downloads
* Supports cancellation of downloads

## Screenshots

![Screenshot of the tool](./docs/screenshot.png)
Test downloading [this file](https://github.com/nadeeshafdo/SeismicDataWorldwide/raw/refs/heads/main/query_M2.5+_2000-2024.csv.7z).

## Installation

1. Click on this link to download this repository.
2. Unzip the downloaded ZIP file and open `quickdownloader-main` directory with your terminal.
3. Execute the following command to install necessary libraries:
    

