# Cute Budget Planner

A desktop budget planner built with Python and Tkinter. It tracks income, expenses, savings goals, recurring expenses, reports, currency settings, themes, and pet companion settings. Data is saved locally in `budget_data.json`.

## Requirements

- Windows
- Python 3.10 or newer
- `pip`

Install the build dependency:

```powershell
pip install -r requirements.txt
```

## Run the App

From this folder:

```powershell
python budget_planner.py
```

Or double-click:

```text
run_app.bat
```

## Build the EXE

The project includes `build_exe.py`, which uses PyInstaller to package the app into one Windows executable.

1. Open PowerShell in the project folder.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Build the executable:

```powershell
python build_exe.py
```

4. After the build finishes, the EXE will be here:

```text
dist\CuteBudgetPlanner.exe
```

You can double-click `CuteBudgetPlanner.exe` to run the app.

## Build Output

PyInstaller creates these folders/files:

- `dist\CuteBudgetPlanner.exe` - the final app
- `build\` - temporary build files
- `CuteBudgetPlanner.spec` - PyInstaller configuration

Only the file inside `dist` is needed to run the built app.

## Data Storage

The app stores user data in:

```text
budget_data.json
```

When running from source, this file is in the project folder. When running the EXE, the data file is created next to where the EXE is launched from.

## Troubleshooting

If `pyinstaller` is missing, run:

```powershell
pip install pyinstaller
```

If Windows blocks the EXE, right-click it, open `Properties`, check `Unblock` if shown, then run it again.

If the build fails, delete the generated `build` and `dist` folders, then run:

```powershell
python build_exe.py
```
