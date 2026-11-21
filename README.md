# Mekace's Deck

A desktop AI assistant built with PySide6. Mekace's Deck is built around **free-tier AI APIs**, combining models from six providers in one local interface so you can switch models or providers whenever you hit a rate limit.

## Features

* **Free-first multi-provider routing.** Switch between Google Gemini, OpenRouter, Groq, Cerebras, SambaNova Cloud, and NVIDIA NIM from the top bar.
* **Local file context.** Browse any project folder in the collapsible sidebar and double-click a file to attach its contents to your prompt.
* **Model management with tooltips.** Enable or disable specific models per provider in Settings, with inline info badges describing what each model is best suited for.
* **Thinking budget control.** Choose between 5 reasoning levels (Off, Low 1K, Medium 4K, High 8K, Max 24K) on supported models.
* **Centralized configuration.** Manage API keys, system prompt, max output tokens, and UI language (English / Turkish) in one window.
* **Markdown and code blocks.** Renders formatted responses with syntax-labeled code blocks and one-click copy buttons.

## Supported providers

All six providers offer free API tiers or free model endpoints:

* Google Gemini
* OpenRouter (`:free` models)
* Groq
* Cerebras
* SambaNova Cloud
* NVIDIA NIM (Serverless free endpoints)

## Known limitations & roadmap

All active provider endpoints are listed in the model selector, including non-chat models such as speech-to-text (`whisper`), text-to-speech (`orpheus`), image generation, and embedding models.

* **Current limitation.** The chat interface sends requests to standard text completion endpoints, so audio, image, and embedding models currently return API errors if called directly.
* **Planned updates.** Dedicated routing and UI controls for audio transcription (Whisper), text-to-speech playback, and image generation are planned for upcoming releases.

## Project structure

```text
mekace-deck/
├── main.py
├── requirements.txt
├── LICENSE
├── assets/
├── core/
│   ├── config.py
│   ├── providers.py
│   ├── translations.py
│   └── worker.py
└── ui/
    ├── main_window.py
    ├── settings_dialog.py
    ├── theme.py
    └── widgets.py
```

## Installation

### Prerequisites

* Python 3.10 or newer
* Git

---

### Windows

1. Install [Python 3.10+](https://www.python.org/downloads/) (check **Add python.exe to PATH** during setup) and [Git](https://git-scm.com/).
2. Open PowerShell or Command Prompt and run:
   ```powershell
   git clone [https://github.com/Mekace/mekace-deck.git](https://github.com/Mekace/mekace-deck.git)
   cd mekace-deck
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

---

### macOS

1. Install Python and Git via [Homebrew](https://brew.sh/):
   ```bash
   brew install python git
   ```
2. Clone and run:
   ```bash
   git clone [https://github.com/Mekace/mekace-deck.git](https://github.com/Mekace/mekace-deck.git)
   cd mekace-deck
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

---

### Linux

#### Ubuntu / Debian / Linux Mint

PySide6 requires `libxcb-cursor0` and `python3-venv` on Debian-based distributions.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git libxcb-cursor0 libegl1

git clone [https://github.com/Mekace/mekace-deck.git](https://github.com/Mekace/mekace-deck.git)
cd mekace-deck
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### Arch Linux / CachyOS / Manjaro

```bash
sudo pacman -S --needed python git

git clone [https://github.com/Mekace/mekace-deck.git](https://github.com/Mekace/mekace-deck.git)
cd mekace-deck
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

*(For Fish shell, activate the virtual environment with `source venv/bin/activate.fish`.)*

#### Fedora

```bash
sudo dnf install -y python3 python3-pip git

git clone [https://github.com/Mekace/mekace-deck.git](https://github.com/Mekace/mekace-deck.git)
cd mekace-deck
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Usage

1. Launch the app and click **Settings** in the top bar.
2. Open the **API Keys** tab and enter keys for the providers you want to use.
3. Open the **Models** tab to enable or disable models. Hover over the `i` icon next to any model to see its primary use case.
4. Select a provider, model, and thinking level from the top-right menus.
5. Use the top-left `☰` button to toggle the file explorer, click **Open Folder** to load a directory, and double-click any file to attach it to your prompt.

## Security

API keys and preferences are stored locally in `config.json`. This file is listed in `.gitignore` and is never tracked or pushed to GitHub.

## License

This project is licensed for **non-commercial use only**. You are free to use, modify, and fork the project for personal or educational purposes with attribution. Commercial use requires written permission. See the [LICENSE](LICENSE) file for details.