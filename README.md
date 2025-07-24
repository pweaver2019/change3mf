# 🛠️ change3mf

A command-line tool to **view and modify `Metadata/project_settings.config`** in `.3mf` 3D printing project files.

**I cheated on this one**; I have been using MAP2MODEL a lot lately and it creates .3mf files specifically for Bamboo printers. I have an Anycubic Kobra S1 with the ACE Pro 1. Every time I opened the .3mf created by MAP2MODEL I needed to change the printer name, and settings ID. This was getting annoying and I was in a hurry so I asked ChatGPT to write the code to change these using python. This is the code ChatGPT came up with. **Not my code, ChatGPT created this, and even created the initial README.md file.**

Supports:
- 🔧 Modifying any key in `project_settings.config`
- 📋 Reading values from a JSON config file
- 🔍 Displaying current config or specific keys
- 🛡️ Automatic backup of original file
- 📜 Logging changes made

---

## 🚀 Features

- Modify any key in `project_settings.config`
- Use either command-line arguments or JSON config file
- Optional change logging with `--log`
- Automatic `.bak` backup (can be disabled with `--nobackup`)
- Overwrites original `.3mf` file

---

## 🧰 Usage

### Basic Syntax

```bash
python change3mf.py <file.3mf> [options]
````

---

### 🔍 View Config

#### Show entire config:

```bash
python change3mf.py model.3mf --show
```

#### Show a specific key:

```bash
python change3mf.py model.3mf --show --element printer_model
```

---

### 🛠️ Modify from Command Line

#### Change a string:

```bash
python change3mf.py model.3mf --modifications "printer_model=Anycubic Kobra S1 0.4 nozzle"
```

---

### 📁 Modify from JSON File

ChatGPT suggested this modification and this is what I use now.
Open your slicer, create a new project and get all your settings the way you want them.
Save the project as a my_config.3mf.
Then extract the project_settings.config using this tool.
That gave me a json file with 1133 lines in it.
Use that extracted json data as your import to modified the downloaded 3mf.

#### `my_config.json`

```json
{
  "printer_model": "Anycubic Kobra S1 0.4 nozzle",
  "printer_settings_id": "0.20mm Standard @AC KS1",
  "filament_settings_id": ["Anycubic PLA","Anycubic PLA","Anycubic PLA","Anycubic PLA"],
  "sparse_infill_density": "10%"
}
```

#### Usage:

```bash
python change3mf.py model.3mf --config-from-file my_config.json
```

#### The way I use this:

```bash
python change3mf.py my_config.3mf --show > my_config.json
rm myconfig.3mf
python change3mf.py downloaded.3mf --config-from-file my_config.json
```

---

## 💾 Backup & Overwrite Behavior

* By default, the tool saves a backup: `model.3mf.bak`
* Modified file replaces the original `.3mf`
* Disable backup with:

```bash
--nobackup
```

---

## 📝 Logging

Use `--log` to show a summary of changes:

```bash
python change3mf.py model.3mf --show --element printer_model
printer_model: OldPrinter
python change3mf.py model.3mf --modifications "printer_model=Test" --log
🔧 Changes made:
 - printer_model: OldPrinter → Test
```

---

## 🔧 Installation as CLI Tool (Optional)

To run `change3mf` from anywhere:

### Windows

1. Save `change3mf.py` to a folder like `C:\Users\<you>\.local\bin\`
2. Create a batch file `change3mf.bat` in a folder on your PATH:

```bat
@echo off
python "C:\Users\<you>\.local\bin\change3mf.py" %*
```

Now you can run:

```bash
change3mf model.3mf --show
```

---

### Unix / macOS

1. Save script as `change3mf.py`
2. Make it executable:

```bash
chmod +x change3mf.py
mv change3mf.py /usr/local/bin/change3mf
```

Then run:

```bash
change3mf model.3mf --show
```

---


## 📂 Supported Fields

Any key under `Metadata/project_settings.config` can be modified, including:

* `printer_model`
* `printer_settings_id`
* `filament_settings_id`
* `printable_height`
* … and many others

---

## 🤝 License

MIT License – Free to use, modify, and distribute.
