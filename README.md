# Personal Video Downloader

A small local web app built with Flask and [yt-dlp](https://github.com/yt-dlp/yt-dlp). Paste a link, pick a format, and save the file to your computer. It runs only on your own machine.

## Features

- Simple, clean web page (dark theme)
- Paste button and Enter-to-download
- Choose quality: Best, 1080p, 720p, 480p
- Audio-only MP3 option
- Loading indicator and friendly error messages
- Works with any site supported by yt-dlp

## Requirements

- [Python 3.9+](https://www.python.org/downloads/) (tick "Add Python to PATH" on Windows)
- [ffmpeg](https://ffmpeg.org/) (needed for MP3 and for merging HD video and audio)

Install ffmpeg on Windows:

```
winget install ffmpeg
```

## Installation

```
git clone https://github.com/YOUR-USERNAME/personal-video-downloader.git
cd personal-video-downloader
pip install -r requirements.txt
```

## Usage

```
python app.py
```

Then open **http://localhost:5000** in your browser, paste a link, choose a format, and click **Download**.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Downloads suddenly stop working | Update yt-dlp: `pip install -U yt-dlp` |
| MP3 fails or HD video has no sound | Make sure ffmpeg is installed (`ffmpeg -version`) |
| "Sign in to confirm you're not a bot" | Wait a while and try again, or use browser cookies with yt-dlp |
| Private or deleted content fails | Only public content works by default |

## Disclaimer

This project is for **personal and educational use only**. Downloading content may violate the terms of service of some websites. You are responsible for how you use this tool. Only download content you own or have permission to save, and respect creators' copyright. This project is not affiliated with or endorsed by any website or platform.

Please do not deploy this as a public service for other people.

## Credits

Built on top of [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [Flask](https://flask.palletsprojects.com/).

## License

MIT License. Add a `LICENSE` file if you want to publish it (GitHub can generate one for you when you create the repo).
