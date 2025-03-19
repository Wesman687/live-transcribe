from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="live-transcribe",  # Package name for pip install
    version="0.1.0",  # Start with 0.1.0
    author="Paul Miracle",
    author_email="Wesman687@gmail.com",
    description="A real-time live transcription tool using Whisper AI",
    long_description=long_description,  # ✅ Ensuring UTF-8 encoding
    long_description_content_type="text/markdown",
    url="https://github.com/wesman687/live-transcribe",  # Update with your repo
    packages=find_packages(include=["lt_app", "lt_app.*"]),
    include_package_data=True,
    install_requires=[
        "faster-whisper",  # Whisper AI
        "numpy",
        "pynput",
        "sounddevice",
        "asyncio",
        "pyyaml",
        "setuptools",
    ],
    extras_require={
        "cuda": ["torchaudio @ https://download.pytorch.org/whl/cu118/torchaudio-2.1.0%2Bcu118-cp310-cp310-linux_x86_64.whl"],
    },
    python_requires=">=3.8",  # Ensure Python 3.8+
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "live-transcribe=lt_app.transcriber:main"  # Allows running `live-transcribe`
        ]
    },
)