# Spatial-Temporal Event (STE) label Tool

[![ArXiv](https://img.shields.io/badge/ArXiv-2502.02785-b31b1b?logo=arxiv)](https://arxiv.org/abs/2502.02785)

The **STE Label Tool** is designed to assist in annotating event data, which can then be used for event modeling with the [openstarlab-preprocessing](https://github.com/open-starlab/PreProcessing) and [openstarlab-event](https://github.com/open-starlab/Event) packages. Depending on the specific video footage, some additional manual preprocessing of the event data may be required to ensure compatibility.

![Event Data LabelTool](https://github.com/open-starlab/Event_Data_LabelTool/blob/main/example.png) <!-- Replace with your image path -->

## Installation

### Prerequisites

- **Recommended Python version:** 3.7

### Steps

1. Install the required packages:

   ```bash
   pip install pyqt5 pandas
   ```

2. Launch the GUI:

   ```bash
   python main.py
   ```

## How to Use

### Annotation

1. Click the **"Open Video"** button to select the video to annotate.
2. Ensure that a **"Label.csv"** file for previous annotations exists in the same directory as the video. For new videos, a **"Label.csv"** file will be created automatically.
3. Use the video player to identify the frame you want to annotate.
4. Select the **Event**, **Coordinate** (click on the frame to auto-update the value), and **Team**.
5. Save the annotation by clicking the **"Save"** button.

### Edit Annotation

1. Select a row on the left side. Double-click it to locate the video at the same frame as the annotation.
2. Delete the selected row by pressing the **"Delete"** key.

### Configure Events and Teams

1. Click the **"Config"** button.
2. To edit name of the option, modify the text directly in the respective field.
3. To add or remove options, insert a new row or delete an existing row directly.
4. Press the **"Save and Exit"** button to apply changes.

## Additional Notes

- Ensure that the video format is supported and that your system meets any necessary requirements for optimal performance.
- For troubleshooting and support, please refer to the issues section of the respective GitHub repositories or create a new issue if needed.

### Windows 11 note (MP4 playback)

On some Windows 11 environments, MP4 videos may fail to render in the PyQt5/Qt video player (e.g., blank/white video area or DirectShow-related errors), even though the same MP4 plays correctly in Windows default players.

**Workarounds**
- If MP4 does not show in the tool, try converting the video to **AVI** or **WMV** and open that file instead. (In our tests, AVI/WMV playback worked reliably when MP4 did not.)
- Alternatively, installing DirectShow codecs/filters (e.g., **LAV Filters** / codec packs) may resolve MP4 playback issues, depending on your system policy.

If you encounter this issue, please include your OS version (Windows 10/11), video format, and any console logs when opening an issue.
This tool is developed based on the SoccerNet action annotation tool. For more information, visit the [SoccerNetv2-DevKit Annotation](https://github.com/SilvioGiancola/SoccerNetv2-DevKit/tree/main/Annotation/actions) repository.

## Developer
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
<!-- [![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-) -->
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/calvinyeungck"><img src="https://github.com/calvinyeungck.png" width="100px;" alt="Calvin Yeung"/><br /><sub><b>Calvin Yeung</b></sub></a><br /><a href="#Developer-CalvinYeung" title="Lead Developer">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/keisuke198619"><img src="https://github.com/keisuke198619.png" width="100px;" alt="Keisuke Fujii"/><br /><sub><b>Keisuke Fujii</b></sub></a><br /><a href="#lead-KeisukeFujii" title="Team Leader">🧑‍💻</a></td>
    </tr>
  </tbody>
</table>
