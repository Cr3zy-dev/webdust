
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

### Options

| Flag              | Description                          |
|-------------------|--------------------------------------|
| `-u, --url`        | Target URL (required)               |
| `-d, --depth`      | Crawl depth (default: 2)            |
| `-o, --output`     | Save results to file                |
| `-v, --verbose`    | Verbose mode                        |
| `--no-color`       | Disable colored output              |

---

## 📸 Screenshot

![image](https://github.com/user-attachments/assets/882a3b0d-8827-4bd2-a6af-fa725435aad8)
![image](https://github.com/user-attachments/assets/02811178-0c8a-479a-98bd-f1103063be7e)

---

## 📜 License

GNU GPLv3, see [LICENSE](LICENSE)

---

## 🎯 Author

Created by [Cr3zy](https://github.com/Cr3zy-dev)
WebDust Copyright (C) 2025  Cr3zy
