from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="livekit/turn-detector",
    revision="v1.2.1",
    local_dir="models/turn-detector",
    local_dir_use_symlinks=False
)