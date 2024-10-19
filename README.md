# Event Data LabelTool

The **Event Data LabelTool** is designed to assist in annotating event data, which can then be used for event modeling with the [openstarlab-preprocessing](https://github.com/open-starlab/PreProcessing) and [openstarlab-event](https://github.com/open-starlab/Event) packages. Depending on the specific video footage, some additional manual preprocessing of the event data may be required to ensure compatibility.

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

