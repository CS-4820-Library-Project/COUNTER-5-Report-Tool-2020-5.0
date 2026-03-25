March 25, 2026 
Message from Melissa Belvadi

Some providers like Ingenta Connect are no longer allowing connections from apps using older certificate settings. I don't have the capacity to update the executables to make the required changes.

However, if you are willing to do a fresh install and use the command line python command, you can follow these instructions to create a new installation of this 5.0 Harvester that will work.

Be sure you fully backup your entire all_data folder to somewhere safe. And you will at minimum need to copy the vendors.dat file that is in all_data/vendor_manager to the new installation location
after you complete these steps.

```md
# Windows 10/11 — Run the legacy COUNTER-5 Report Tool from source (no executable)

These steps install the project into an isolated Python virtual environment and run it from the command line. This avoids a common misconception: updating packages system-wide (or tweaking User-Agent / throttling) will **not** fix TLS certificate verification errors. TLS happens before HTTP headers are sent, and frozen executables often carry their own dependency/certificate bundle.

## 1) Install Python

1. Install Python 3 from python.org (recommended: Python 3.11+ or 3.12+).
2. During install, enable **Add Python to PATH**.

Verify in **Command Prompt**:

```bat
py -V
```

## 2) Get the source code


1. Download ZIP from GitHub: https://github.com/CS-4820-Library-Project/COUNTER-5-Report-Tool-2020-5.0/archive/refs/heads/master.zip
2. Plan and create the new folder/location where you want everything to go - make it different from your previous installation, for instance Desktop\COUNTER50
3. Move the zip file to that folder
4. Right-click ZIP → Extract All.
5. Open Command Prompt and go into the extracted folder and into where the Harvester files actually are within that:

```bat
cd C:\Users\YourUserName\Desktop\COUNTER50\COUNTER-5-Report-Tool-master
```
Modify the end of that path to whatever it's actually called for you. The rest of these instructions assume that path to the harvester (what is called the "repo root")

## 3) Create and activate a virtual environment

From the repo root   \Users\YourUserName\Desktop\COUNTER50\COUNTER-5-Report-Tool-master :

```bat
py -m venv .venv
.venv\Scripts\activate
python -V
```

Sanity-check that `python` is coming from `.venv`:

```bat
python -c "import sys; print(sys.executable)"
```

## 4) Install dependencies

Upgrade packaging tools:

```bat
python -m pip install -U pip setuptools wheel
```

Install project dependencies:

```bat
python -m pip install -r requirements_2026.txt
```

If `pip install` fails, the project’s dependency pins may be too old for your Python version (common with legacy PyQt). In that case you need either:
- a Python version compatible with the pinned GUI stack, or
- updated dependency pins (preferred if you’re fixing TLS/cert issues).

## 5) Install vendors.dat before running the program

Assuming you are still in \Users\YourUserName\Desktop\COUNTER50\COUNTER-5-Report-Tool-master

```bat
mkdir all_data\vendor_manager
```
Then use your File Manager to copy your old vendors.dat into that vendor_manager folder.

## 6) Run the program

Important: run from the **repo root**  so relative paths resolve correctly.

Make sure you are still in the "venv" activation. if you got out of that, do this step again now in the command line window:

```bat
cd \Users\YourUserName\Desktop\COUNTER50\COUNTER-5-Report-Tool-master
.venv\Scripts\activate
```
Either way, the CD command will make sure you are in the right place, but the actual command to start the Harvester is the python command below.
```bat
cd \Users\YourUserName\Desktop\COUNTER50\COUNTER-5-Report-Tool-master
python MainDriver.py
```

## Techie Stuff if you have a python expert around to help and you're having problems

### 7) Optional TLS sanity check (useful when debugging)

```bat
python -c "import requests,certifi,ssl; print('requests',requests.__version__); print('certifi',certifi.__version__); print('openssl',ssl.OPENSSL_VERSION)"
python -c "import requests; r=requests.get('https://www.ingentaconnect.com/',timeout=30); print('status',r.status_code)"
```

If you see `certificate verify failed`, it is **not** throttling and **not** User-Agent. It’s certificate trust (usually solved by updating `requests/urllib3/certifi` or dealing with corporate TLS inspection).

## 8) Clean reset (start over)

```bat
deactivate
rmdir /s /q .venv
```

Then repeat from step 3.


# Linux (Ubuntu/Debian) — Run the legacy COUNTER-5 Report Tool from source (no executable)

These steps install the project into an isolated Python virtual environment and run it from the command line.

## 1) Install prerequisites

```bash
sudo apt update
sudo apt install -y python3 python3-venv
```

If you encounter Qt/PyQt runtime errors about missing XCB/Xinerama libs (varies by distro/desktop), this often fixes it:

```bash
sudo apt install -y libxcb-xinerama0
```

## 2) Get the source code

**Option A: Git (recommended for people comfortable with git)**

```bash
git clone <YOUR_REPO_URL>
cd <REPO_DIR>
```

**Option B: GitHub ZIP**

Use your web browser to download: https://github.com/CS-4820-Library-Project/COUNTER-5-Report-Tool-2020-5.0/archive/refs/heads/master.zip
and put it somewhere that you plan to install the whole harvester.

```bash
unzip <REPO_ZIP_NAME>.zip
cd <UNZIPPED_REPO_DIR>
```
The "repo root" will be the folder created from that unzip, the one you just CD'd into.

## 3) Create and activate a virtual environment

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -V
```

Sanity-check that `python` is coming from `.venv`:

```bash
python -c "import sys; print(sys.executable)"
```

## 4) Install dependencies

Upgrade packaging tools:

```bash
python -m pip install -U pip setuptools wheel
```

Install project dependencies:

```bash
python -m pip install -r requirements_2026.txt
```

If `pip install` fails, the project’s dependency pins may be too old for your Python version (common with legacy PyQt). In that case you need either:
- a Python version compatible with the pinned GUI stack, or
- updated dependency pins (preferred if you’re fixing TLS/cert issues).

## 5) Find `vendors.dat` (if needed)

If you’re not sure where `vendors.dat` is, search your home directory and print both an `ls -l` line and the full path:

```bash
find ~ -type f -name 'vendors.dat' -exec ls -l {} \; -print
```

If your home directory is huge, limit search depth:

```bash
find ~ -maxdepth 6 -type f -name 'vendors.dat' -exec ls -l {} \; -print
```

## 6) Run the program

Important: run from the **repo root** so relative paths resolve correctly.

```bash
python MainDriver.py
```

## 7) Optional TLS sanity check (useful when debugging)

```bash
python -c "import requests,certifi,ssl; print('requests',requests.__version__); print('certifi',certifi.__version__); print('openssl',ssl.OPENSSL_VERSION); import certifi as c; print('cacert',c.where())"
python - <<'PY'
import requests
r = requests.get("https://www.ingentaconnect.com/", timeout=30)
print("status:", r.status_code)
PY
```

If you see `certificate verify failed`, it is **not** throttling and **not** User-Agent. It’s certificate trust (usually solved by updating `requests/urllib3/certifi` or dealing with corporate TLS inspection).

## 8) Clean reset (start over)

```bash
deactivate 2>/dev/null
rm -rf .venv
```

Then repeat from step 3.
```
