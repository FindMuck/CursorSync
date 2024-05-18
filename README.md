<div align="center">
<a href="assets/images" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/FindMuck/CursorSync/main/assets/images/dark_transparentBG.png" width="50%">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/FindMuck/CursorSync/main/assets/images/light_and_other_lightgrayBG.png" width="50%">
    <img alt="" src="https://raw.githubusercontent.com/FindMuck/CursorSync/main/assets/images/light_and_other_lightgrayBG.png" width="50%">
  </picture>
</a>
  <h1>CursorSync — <em>Cursor Synchronizer</em>
</br>
<a href="https://github.com/FindMuck/CursorSync/releases/download/1.0/CursorSync.exe" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/Windows-33.3MB-lightgray?logo=Windows&labelColor=0078D4"></a>
</br>
<a href="https://github.com/FindMuck/CursorSync/releases/latest" target="_blank"><img alt="Downloads" src="https://img.shields.io/github/downloads/FindMuck/CursorSync/total?label=Downloads"></a>
<a href="https://github.com/FindMuck/CursorSync/tree/main/LICENSE" target="_blank"><img alt="License" src="https://img.shields.io/github/license/FindMuck/CursorSync?label=License"></a>
<a href="https://github.com/FindMuck/CursorSync/releases/latest" target="_blank"><img alt="App Version" src="https://img.shields.io/github/v/release/FindMuck/CursorSync?label=App%20Version"></a>
</h1>
</div>
</br>

> **_CursorSync_** is a simple yet useful solution for users who need to perform synchronized cursor click actions across multiple PCs at the very same time. Whether you're collaborating on a project or playing games, _CursorSync_ ensures that everyone is literally on the same  **_point_**.
</br>

### Here's how it works ✨🖱️
1. **[RadminVPN](https://radmin-vpn.com)**: _CursorSync_ uses [RadminVPN](https://radmin-vpn.com), a free and easy-to-use software product that creates a virtual local networks, making it possible to work as if you were on the same local network. Users need to install [RadminVPN](https://radmin-vpn.com) and join the same network to ensure seamless connectivity between all PCs.

2. **_CursorSync_ App**: Once [RadminVPN](https://radmin-vpn.com) is set up and all PCs are on the same network, users need to [download](https://github.com/FindMuck/CursorSync/releases/download/1.0/CursorSync.exe) and run the _CursorSync_ application. This application establishes a seamless connection between all PCs in the local network with the help of [RadminVPN](https://radmin-vpn.com).

3. **Locating Coordinates**: Users can manually specify the X and Y coordinates of the pixel where they want the cursor to click. Alternatively, they can click the "Locate coordinates" button, which will display a crosshair for users to choose the required pixel.

4. **Synchronizing Clicks**: After the coordinates have been set, users can click the "Go!" button. This action will move the cursor to the specified coordinates and perform a click. The same action will be mirrored on all other connected PCs, thus synchronizing the cursor clicks and positions.

5. **Enjoying _CursorSync_ App?** If you find _CursorSync_ helpful, consider giving it a
<a href="https://github.com/FindMuck/CursorSync" target="_blank"><img alt="Star" src="https://img.shields.io/github/stars/FindMuck/CursorSync?label=Star"></a>
on GitHub. Your support helps more people discover _CursorSync_ project and motivates continuous improvements. Thanks! 🌟
</br>
</br>

<details>
  <summary><b>OS compatibility of an executable ⚙️</b></summary>
  <dl><dd><dl><dt></dt><dd>

  The original _CursorSync_ executable was built on **Intel x64 Windows 10** using PyInstaller with [UPX](https://upx.github.io) packer. It was also tested using only this architecture. If you want to build your own version of the _CursorSync_ executable for your OS, use the [instructions below](https://github.com/FindMuck/CursorSync/tree/main?tab=readme-ov-file#build-your-own-cursorsync-executabe-for-advanced-users-man_technologistneckbeard). Test it, and if it's working, contact me and proudly share it with others! :shipit:
</dd></dl></dd></dl>
</details>


</br>
</br>

> [!WARNING]
> **This software is distributed under the [MIT License](https://github.com/FindMuck/CursorSync/tree/main/LICENSE)**.
> 
> Please note that the software is provided "[AS IS](https://github.com/FindMuck/CursorSync/tree/main/LICENSE#L15C27-L15C32)", **without** warranty of any kind.
<hr>

### Build your own _CursorSync_ executabe! (for _Advanced_ users) :man_technologist::neckbeard:
<details>
  <summary><b>Step-by-Step Guide 👷🛠️</b></summary>

1. **Clone or download the _CursorSync_ GitHub Repo**: You can do this by visiting this [link](https://github.com/FindMuck/CursorSync.git).

2. **Navigate to the ```src``` directory in your terminal**.

3. **Create and activate a new virtual environment** (This step is not necessary but is _recommended_ as it can reduce the final size of your executable).

4. **Install the necessary packages**. Run the following command in your terminal:
   ```bash
   pip install pyinstaller pyautogui PyQt5
   ```

5. **Download the latest version of [UPX](https://upx.github.io)**: UPX is a free, portable, extendable, high-performance executable packer for several executable formats.

6. **Build your own _CursorSync_ executable!** Run the ```pyinstaller``` command as shown below. Make sure to replace ```UPX``` in ```--upx-dir=UPX``` with the actual path to the root directory of UPX.
   > 📝 **Note**:
   >  
   > ```"icon.ico;."``` portion in the ```--add-data``` option can vary depending on the OS you’re using to build the executable. The ```;``` symbol is used as a separator in Windows. However, for Unix-based systems (Linux, macOS, etc.), you should use the ```:``` symbol instead.
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico --version-file=CursorSync_VERSIONINFO.txt --add-data "icon.ico;." --upx-dir=UPX CursorSync.py
   ```
</details>
