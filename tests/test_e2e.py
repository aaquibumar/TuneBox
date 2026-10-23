import subprocess, uuid
from fastapi.testclient import TestClient
from tunebox.app import app

def test_end_to_end_index_play_favorite_playlist(tmp_path):
    music = tmp_path / "owned music"
    music.mkdir()
    audio = music / "Personal Test Tone.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
                    "-c:a", "pcm_s16le", str(audio)], check=True)
    client = TestClient(app)
    assert client.get("/api/health").json()["ok"] is True
    assert client.get("/").status_code == 200

    indexed = client.post("/api/index", json={"path": str(music)})
    assert indexed.status_code == 200, indexed.text
    assert indexed.json()["indexed"] == 1

    response = client.get("/api/tracks?q=Personal%20Test")
    assert response.status_code == 200
    track = response.json()[0]
    assert track["title"] == "Personal Test Tone"
    assert track["file_hash"]
    playback = client.get(f"/api/audio/{track['id']}")
    assert playback.status_code == 200
    assert playback.content[:4] == b"RIFF"

    favorite = client.patch(f"/api/tracks/{track['id']}", json={"favorite": True})
    assert favorite.status_code == 200
    assert favorite.json()["favorite"] == 1

    playlist = client.post("/api/playlists", json={"name": "E2E " + uuid.uuid4().hex[:10]})
    assert playlist.status_code == 200
    added = client.post(f"/api/playlists/{playlist.json()['id']}/tracks",
                        json={"track_id": track["id"]})
    assert added.status_code == 200
    listed = client.get(f"/api/playlists/{playlist.json()['id']}/tracks")
    assert [item["id"] for item in listed.json()] == [track["id"]]
