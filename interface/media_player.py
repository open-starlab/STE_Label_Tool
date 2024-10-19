import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QStyle, QSlider, 
                             QHBoxLayout, QVBoxLayout, QFileDialog, QLabel)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QRect, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QMouseEvent
import pandas as pd

class CustomVideoWidget(QVideoWidget):

    frame_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_width = 0
        self.video_height = 0

    def set_video_size(self, width, height):
        self.video_width = width
        self.video_height = height

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            widget_pos = event.pos()
            frame_pos = self.widget_to_frame_pos(widget_pos)
            if frame_pos:
                print(f"Clicked frame coordinates: ({frame_pos.x()}, {frame_pos.y()})")
                self.frame_clicked.emit(frame_pos.x(), frame_pos.y())
        
        super().mousePressEvent(event)

    def widget_to_frame_pos(self, widget_pos):
        if self.video_width == 0 or self.video_height == 0:
            return None

        # Get the rectangle of the actual video within the widget
        video_rect = self.get_video_rect()

        if not video_rect.contains(widget_pos):
            return None  # Click was outside the actual video area

        # Calculate the relative position within the video rectangle
        relative_x = (widget_pos.x() - video_rect.left()) / video_rect.width()
        relative_y = (widget_pos.y() - video_rect.top()) / video_rect.height()

        # Convert to frame coordinates
        frame_x = int(relative_x * self.video_width)
        frame_y = int(relative_y * self.video_height)

        return QPoint(frame_x, frame_y)

    def get_video_rect(self):
        widget_size = self.size()
        video_size = QSize(self.video_width, self.video_height)

        # Calculate the scaling factor to fit the video in the widget
        scale_w = widget_size.width() / video_size.width()
        scale_h = widget_size.height() / video_size.height()
        scale = min(scale_w, scale_h)

        # Calculate the size of the video within the widget
        video_width = int(video_size.width() * scale)
        video_height = int(video_size.height() * scale)

        # Calculate the position to center the video in the widget
        x = (widget_size.width() - video_width) // 2
        y = (widget_size.height() - video_height) // 2

        return QRect(x, y, video_width, video_height)

class MediaPlayer(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Media Player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Video Widget
        self.video_widget = CustomVideoWidget()

        # Button to open a new file
        self.open_file_button = QPushButton('Open video')
        self.open_file_button.clicked.connect(self.open_file)

        # Button for playing the video
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_video)

        # Slider for video position
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Previous and Next Frame Buttons
        self.prev_frame_button = QPushButton("Previous Frame")
        self.prev_frame_button.setEnabled(False)  # Initially disabled
        self.prev_frame_button.clicked.connect(self.previous_frame)

        self.next_frame_button = QPushButton("Next Frame")
        self.next_frame_button.setEnabled(False)  # Initially disabled
        self.next_frame_button.clicked.connect(self.next_frame)

        # Label to display the current frame number
        self.frame_label = QLabel("Frame: 0")
        self.frame_label.setAlignment(Qt.AlignCenter)

        # Create hbox layout for buttons, slider, and frame label
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)
        
        # Set widgets to the hbox layout
        hboxLayout.addWidget(self.open_file_button)
        hboxLayout.addWidget(self.play_button)
        hboxLayout.addWidget(self.prev_frame_button)  # Add previous frame button
        hboxLayout.addWidget(self.next_frame_button) 
        hboxLayout.addWidget(self.frame_label)  # Add next frame button
        hboxLayout.addWidget(self.slider)
        # hboxLayout.addWidget(self.frame_label)  # Add the frame label to the same row

        # Create vbox layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_widget)
        self.layout.addLayout(hboxLayout)  # Add the button and slider layout

        self.media_player.setVideoOutput(self.video_widget)

        # Media player signals
        self.media_player.stateChanged.connect(self.mediastate_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        self.media_player.mediaStatusChanged.connect(self.update_video_size)

        self.path_label = None
        self.frame_rate = 30  # Default frame rate
        self.is_media_loaded = False

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.play_button.setEnabled(True)
            filepath = os.path.basename(filename)

            self.path_label = os.path.dirname(filename) + "/Labels.csv"
            if not os.path.isfile(self.path_label):
                tmp_df = pd.DataFrame(columns=['team', 'event', 'minute', 'second', 'x_coord', 'y_coord', 'video_ms'])
                tmp_df.to_csv(self.path_label, index=False)
            self.main_window.list_manager.create_list_from_csv(self.path_label)
            self.main_window.list_display.display_list(self.main_window.list_manager.create_text_list())
            self.is_media_loaded = True
            self.prev_frame_button.setEnabled(True)
            self.next_frame_button.setEnabled(True)

    def media_status_changed(self, status):
        # Check if the media has been successfully loaded
        if status == QMediaPlayer.LoadedMedia:
            self.extract_frame_rate()

    def extract_frame_rate(self):
        # Get the frame rate from the media player's metadata
        frame_rate = self.media_player.metaData(QMediaMetaData.VideoFrameRate)
        if frame_rate is not None:
            self.frame_rate = frame_rate
            print("Frame rate extracted:", self.frame_rate)
        else:
            print("Frame rate metadata not available, using default:", self.frame_rate)

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediastate_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.slider.setValue(position)
        current_frame = int(position / (1000 / self.frame_rate))  # Calculate current frame
        self.frame_label.setText(f"Frame: {current_frame}")  # Update frame label

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_errors(self):
        self.play_button.setEnabled(False)
        print("Error: " + self.media_player.errorString())

    def previous_frame(self):
        if not self.is_media_loaded:
            return
        current_position = self.media_player.position()
        frame_duration = 1000 / self.frame_rate  # duration of one frame in milliseconds
        new_position = max(current_position - frame_duration, 0)
        self.media_player.setPosition(new_position)

    def next_frame(self):
        if not self.is_media_loaded:
            return
        current_position = self.media_player.position()
        frame_duration = 1000 / self.frame_rate  # duration of one frame in milliseconds
        new_position = min(current_position + frame_duration, self.media_player.duration())
        self.media_player.setPosition(new_position)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:  # Check if the left mouse button was clicked
            x = event.x()  # Get the x-coordinate
            y = event.y()  # Get the y-coordinate
            print(f"Clicked pixel coordinates: ({x}, {y})")
        super().mousePressEvent(event)

    def update_video_size(self, status):
        if status == QMediaPlayer.LoadedMedia:
            # Get video dimensions
            video_size = self.media_player.metaData(QMediaMetaData.Resolution)
            if video_size.isValid():
                width = video_size.width()
                height = video_size.height()
                self.video_widget.set_video_size(width, height)
                print(f"Video dimensions: {width}x{height}")