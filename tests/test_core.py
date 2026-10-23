from pathlib import Path
import pytest
from tunebox.core import safe_filename, trim_audio, normalize_audio, Library

def test_safe_filename_blocks_paths_and_invalid_chars():
    assert safe_filename("../../hello:world?.mp3") == "hello_world_.mp3"
    assert safe_filename("   ") == "track"

def test_transform_validation_happens_before_ffmpeg(tmp_path):
    with pytest.raises(ValueError):
        trim_audio(tmp_path/"missing.wav", tmp_path/"out.mp3", 3, 2)
    with pytest.raises(ValueError):
        normalize_audio(tmp_path/"missing.wav", tmp_path/"out.mp3", -50)

def test_library_persists_folder_and_manifest(tmp_path):
    lib=Library(tmp_path/"db.sqlite3",tmp_path)
    folder=tmp_path/"music"; folder.mkdir()
    result=lib.add_folder(str(folder))
    assert result["indexed"] == 0
    with lib.connect() as c:
        assert c.execute("SELECT COUNT(*) FROM folders").fetchone()[0] == 1
    out=lib.export_manifest(tmp_path/"manifest.json")
    assert '"tunebox-manifest-v1"' in out.read_text()
