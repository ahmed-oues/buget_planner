"""
Build script to create executable from budget planner
Run this script to generate the .exe file
"""

import PyInstaller.__main__
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
app_file = os.path.join(current_dir, 'budget_planner.py')

print("🚀 Building Budget Planner executable...")
print("This may take a few minutes...")

PyInstaller.__main__.run([
    app_file,
    '--onefile',                    # Create a single executable file
    '--windowed',                   # Don't show console window (GUI app)
    '--name=CuteBudgetPlanner',     # Name of the executable
    '--icon=NONE',                  # No icon (you can add one later)
    '--clean',                      # Clean PyInstaller cache
    '--noconfirm',                  # Replace output directory without asking
])

print("\n✨ Build complete! ✨")
print(f"📁 Your executable is in the 'dist' folder:")
print(f"   {os.path.join(current_dir, 'dist', 'CuteBudgetPlanner.exe')}")
print("\n💡 You can now run the .exe file from the dist folder!")

