from flask import Flask, request, send_file, jsonify
import yt_dlp
import tempfile
import os

app = Flask(__name__)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Downloader</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #f1f1f5;
    background: linear-gradient(135deg, #1a1033, #3b1d5a 50%, #7a2e6b);
    padding: 20px;
  }
  .card {
    width: 100%;
    max-width: 520px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 32px 28px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
  }
  h1 { margin: 0 0 6px; font-size: 26px; }
  .sub { margin: 0 0 24px; color: #c9c3d9; font-size: 14px; }
  .row { display: flex; gap: 8px; }
  input {
    flex: 1;
    min-width: 0;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.3);
    color: #fff;
    font-size: 15px;
    outline: none;
  }
  input:focus { border-color: #ff6bb5; }
  button {
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 600;
    transition: transform 0.1s, opacity 0.2s;
  }
  button:active { transform: scale(0.97); }
  select {
    width: 100%;
    margin-top: 12px;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.3);
    color: #fff;
    font-size: 15px;
    outline: none;
    cursor: pointer;
  }
  select option { color: #000; }
  .paste {
    padding: 0 16px;
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
  }
  .go {
    width: 100%;
    margin-top: 12px;
    padding: 14px;
    color: #fff;
    background: linear-gradient(90deg, #ff6bb5, #ff9a5a);
  }
  .go:disabled { opacity: 0.6; cursor: wait; }
  #msg {
    margin-top: 16px;
    min-height: 22px;
    font-size: 14px;
    text-align: center;
  }
  .err { color: #ff8a8a; }
  .ok { color: #8affb5; }
  .spin {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    vertical-align: -2px;
    margin-right: 6px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .foot { margin-top: 20px; font-size: 12px; color: #9d96b3; text-align: center; }
</style>
</head>
<body>
  <div class="card">
    <h1>⬇️ My Downloader</h1>
    <p class="sub">Paste a link, pick a format, and hit download.</p>

    <div class="row">
      <input id="url" type="text" placeholder="Paste an Instagram or YouTube link..." autocomplete="off">
      <button class="paste" id="pasteBtn" type="button">Paste</button>
    </div>
    <select id="format">
      <option value="best">Video - Best quality</option>
      <option value="1080">Video - 1080p</option>
      <option value="720">Video - 720p</option>
      <option value="480">Video - 480p</option>
      <option value="mp3">Audio only - MP3</option>
    </select>
    <button class="go" id="goBtn" type="button">Download</button>

    <div id="msg"></div>
    <div class="foot">For personal use only. Respect creators' rights.</div>
  </div>

<script>
  const urlInput = document.getElementById("url");
  const goBtn = document.getElementById("goBtn");
  const pasteBtn = document.getElementById("pasteBtn");
  const msg = document.getElementById("msg");

  function show(text, cls) {
    msg.className = cls || "";
    msg.innerHTML = text;
  }

  pasteBtn.onclick = async () => {
    try {
      urlInput.value = await navigator.clipboard.readText();
    } catch (e) {
      show("Couldn't read clipboard. Paste manually with Ctrl+V.", "err");
    }
  };

  urlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") goBtn.click();
  });

  goBtn.onclick = async () => {
    const link = urlInput.value.trim();
    if (!link) { show("Please paste a link first.", "err"); return; }

    goBtn.disabled = true;
    show('<span class="spin"></span>Downloading, please wait...');

    try {
      const fmt = document.getElementById("format").value;
      const body = new URLSearchParams({ url: link, format: fmt });
      const res = await fetch("/download", { method: "POST", body });

      if (!res.ok) {
        const data = await res.json();
        show(data.error || "Something went wrong.", "err");
      } else {
        const blob = await res.blob();
        const disp = res.headers.get("Content-Disposition") || "";
        const match = disp.match(/filename="?([^";]+)"?/);
        const name = match ? match[1] : "video.mp4";

        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = name;
        a.click();
        URL.revokeObjectURL(a.href);

        show("Done! Check your Downloads folder ✅", "ok");
        urlInput.value = "";
      }
    } catch (e) {
      show("Could not reach the server. Is app.py still running?", "err");
    }
    goBtn.disabled = false;
  };
</script>
</body>
</html>
"""


FORMATS = {
    "best": "bv*+ba/b",
    "1080": "bv*[height<=1080]+ba/b[height<=1080]/b",
    "720": "bv*[height<=720]+ba/b[height<=720]/b",
    "480": "bv*[height<=480]+ba/b[height<=480]/b",
}


@app.route("/")
def home():
    return PAGE


@app.route("/download", methods=["POST"])
def download():
    url = (request.form.get("url") or "").strip()
    if not url.startswith("http"):
        return jsonify(error="That doesn't look like a valid link."), 400

    choice = request.form.get("format", "best")

    tmp = tempfile.mkdtemp()
    opts = {
        "outtmpl": os.path.join(tmp, "%(title).80s [%(id)s].%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": True,
    }

    if choice == "mp3":
        # Needs ffmpeg installed
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        opts["format"] = FORMATS.get(choice, FORMATS["best"])
        opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloads = info.get("requested_downloads")
            if downloads and downloads[0].get("filepath"):
                path = downloads[0]["filepath"]
            else:
                path = ydl.prepare_filename(info)
    except Exception as e:
        print("Download error:", e)
        return jsonify(
            error="Couldn't download that link. It may be private, deleted, or the site blocked it. "
                  "For MP3 or HD merging, make sure ffmpeg is installed. "
                  "Also try updating with: pip install -U yt-dlp"
        ), 400

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(port=5000, debug=False)