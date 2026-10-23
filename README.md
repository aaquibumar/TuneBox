# TuneBox

TuneBox is a local-first personal music library and playback app: a practical, deliberately limited substitute for the *personal-library* parts of a music player—not a replica of Apple Music's catalog or service.

## Scope and rights

TuneBox organizes, indexes, analyzes, and plays local files that you own or are authorized to use. It does **not** provide music, licensing, distribution, or royalty collection. It does not acquire copyrighted catalogs, share tracks, circumvent streaming services, calculate royalties, distribute to labels, or provide global content delivery. It does not reproduce proprietary catalog data, network liquidity, regulated access, or frontier infrastructure. You are responsible for the rights and permissions applicable to files you import and exports you create.

## Requirements

- Python 3.12
- `ffmpeg` and `ffprobe` installed and available on `PATH` (ffprobe is useful for diagnostics; analysis requires ffmpeg)
- macOS, Linux, or Windows with a supported Python installation

## First run

From the project directory, one documented command installs dependencies and starts the server:

```bash
python3.12 -m pip install -r requirements.txt && python3.12 -m uvicorn tunebox.app:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. On first launch, enter a folder path visible to the machine running TuneBox, then click **Index selected folder**. Folder access is not recursive outside the folder you chose. Indexing reads tags, calculates SHA-256 hashes, and attempts loudness/waveform analysis. Original source files are never modified. A large library can take time because audio analysis is performed during indexing.

To use a `.env` file, copy `.env.example` to `.env` and adjust values. Keep `.env` private; it is git-ignored. Environment variables can also override data directory, host, and port. The one-command default is intentionally bound to `127.0.0.1`, not exposed to the network.

## Private network use

For a trusted home network only, set `TUNEBOX_HOST=0.0.0.0` and start with `python3.12 -m uvicorn tunebox.app:app --host 0.0.0.0 --port 8000`; then open `http://<server-LAN-IP>:8000` from a device on the same trusted network. This app has **no accounts or authentication**. Do not expose it to the public internet, port-forward it, or use an untrusted network. Restrict access with your operating system firewall and trusted LAN configuration. Network mode is an opt-in deployment choice, not the default.

## Features

- Selected-folder indexing, tag metadata, album/artist views, text search
- SHA-256 exact duplicate detection (same bytes; not acoustic/fuzzy matching)
- Loudness/true-peak analysis where ffmpeg supports it; compact waveform summaries
- Local playback, favorite toggles, queue, playlists, and periodically saved playback position
- Track-level rights/source fields and rights sidecars for generated exports
- Trim and loudness-normalized new MP3 exports; optional local Demucs stem splitting
- SQLite backup and JSON library manifest export

Album artwork presence is detected from common embedded tag formats; this starter UI does not extract or display artwork images. Creator transforms create new files and never overwrite the imported source. Demucs is optional, does not download weights automatically, and may require separate model installation and compatible hardware.

## Data location and permissions

Default data location is `./data` relative to the project directory (override with `TUNEBOX_DATA_DIR`). It contains `library.sqlite3` and generated `exports/`. Source audio stays at its original path and is not copied into the database. The server process needs read access to selected audio files and write access to the data directory. The browser cannot select a server folder directly; enter a path on the machine running the server. Folder paths are stored locally in SQLite.

`.env` is for local configuration/secrets and is never committed. This starter does not require any API keys or external services. The stylesheet uses a system font fallback; no third-party API is required for playback or analysis.

## Backup and export

1. Use **Download SQLite backup** for a consistent database backup.
2. Use **Export library manifest** for a portable JSON record of tags, paths, hashes, rights notes, favorites, and playback positions.
3. Back up the `data/` directory, including `exports/`, separately if you want generated files and sidecars.
4. Back up original music folders separately. TuneBox references the originals and does not include their audio bytes in the SQLite backup.
5. Keep backups encrypted and in a location you control; a manifest contains local file paths and rights notes.

## Architecture

- `tunebox/core.py`: safe filenames, file hashes, Mutagen metadata, ffmpeg analysis/transforms, SQLite schema and library operations
- `tunebox/app.py`: FastAPI routes, validation, local audio responses, export endpoints
- `static/`: local web interface
- `tests/`: focused core tests and HTTP happy-path test

SQLite is local and uses foreign keys. File operations are allowlisted by audio extension; API inputs are validated with Pydantic; export filenames are sanitized. Exact duplicates are grouped by SHA-256. Failures for unsupported formats or missing optional tools are surfaced as recoverable errors where possible.

## Development and tests

```bash
python3.12 -m pip install -r requirements.txt
python3.12 -m pytest -q
```

The tests cover filename safety, transform argument validation, folder/manifest persistence, and an HTTP happy path. Audio transform integration tests need a working ffmpeg binary and valid audio fixtures.
