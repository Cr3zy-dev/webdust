
# WebDust

**WebDust** is a fast, smart and colorful web application reconnaissance tool.  
It crawls, analyzes, and highlights potential vulnerabilities in web endpoints.  
Perfect for bug bounty hunters, red teamers, and security researchers.

---

## 🚀 Features

- 🔍 Smart crawling with customizable depth
- 📦 Detects parameters, forms, uploads, and JS files
- 🧠 Identifies potential vuln vectors (XSS, SQLi, IDOR, etc.)
- 🎨 Colorful terminal output (Windows & Linux)
- 💾 Optional output to file
- 🧪 Designed for speed, clarity, and real-world use

---

## 📦 Installation

### Linux

```bash
git clone https://github.com/Cr3zy-dev/webdust.git
cd webdust
pip3 install -r requirements.txt --break-system-packages
python3 webdust.py -u https://example.com
```

### Windows (PowerShell)

```powershell
git clone https://github.com/Cr3zy-dev/webdust.git
cd webdust
pip install -r requirements.txt
python webdust.py -u https://example.com
```

---

## 🛠 Usage

```bash
python webdust.py -u https://example.com [options]
```

### ⚙️ Options

| Flag                  | Description                                                 |
|---------------------- |------------------------------------------------------------ |
| `-u, --url`           | Target URL to scan                                          |
| `-d, --depth`         | Crawl depth (default: 2)                                    |
| `-o, --output`        | Save results to a file                                      |
| `-v, --verbose`       | Enable verbose/debug output                                 |
| `--no-color`          | Disable colored terminal output                             |
| `-w, --wordlist`      | Configure custom wordlist paths for detection               |
| `-s, --show`          | Display currently configured custom wordlist file paths     |

---

### 📂 `wordlists/` Directory

The `wordlists/` folder included in this repository is provided as a **template**.  
⚠️ **It is not used by default in the scanning process, unless you have configured the paths.**

WebDust uses **internally hardcoded parameter keywords** for vulnerability detection (such as `id`, `file`, `query`, etc.).  
The files in `wordlists/` are meant for **reference** but **I recommend to use them**.

---

### 🔧 Custom Wordlists

To use your own wordlists, run:

```bash
python webdust.py -w
```

This will prompt you to enter the paths to individual wordlist files (for XSS, SQLi, etc.).   

✅ WebDust will save your configured paths into a JSON file (webdust/wordlist_config.json) and automatically load them during future scans.   

❗ You don’t need to use -w every time unless you want to reconfigure.

To change the paths later, simply rerun:
```bash
python webdust.py -w
```
and provide new paths or press Enter to use the hardcoded ones.

**I do recommend to use wordlists, but it is not necessary.**

---

## 📸 Screenshots

![image](https://github.com/user-attachments/assets/6d6afe37-82f6-4df5-918c-09eafa0d0cd5)
![image](https://github.com/user-attachments/assets/2c0a1dc5-6e95-4672-82d5-0d7ddf9c46e1)

---


## 📜 License

GNU GPLv3, see [LICENSE](LICENSE)

---

## 🎯 Author

Created by [Cr3zy](https://github.com/Cr3zy-dev) - WebDust Copyright (C) 2025  Cr3zy
