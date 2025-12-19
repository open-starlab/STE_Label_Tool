import os
import cv2
import pandas as pd

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QStyle, QSlider,
    QHBoxLayout, QVBoxLayout, QFileDialog, QLabel,
    QStackedLayout
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QRect, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage, QPixmap

import numpy as np


class CustomVideoWidget(QVideoWidget):
    """
    Video widget that emits clicked coordinates in *frame pixel* space (x,y),
    accounting for letterboxing/pillarboxing inside the widget.
    """
    frame_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_width = 0
        self.video_height = 0

    def set_video_size(self, width: int, height: int):
        self.video_width = int(width) if width else 0
        self.video_height = int(height) if height else 0

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            widget_pos = event.pos()
            frame_pos = self.widget_to_frame_pos(widget_pos)
            if frame_pos is not None:
                x, y = frame_pos.x(), frame_pos.y()
                print(f"Clicked frame coordinates: ({x}, {y})")
                self.frame_clicked.emit(x, y)

        super().mousePressEvent(event)

    def widget_to_frame_pos(self, widget_pos: QPoint):
        # If we don't know video dimensions yet, we can't map coordinates.
        if self.video_width <= 0 or self.video_height <= 0:
            return None

        video_rect = self.get_video_rect()
        if not video_rect.isValid() or video_rect.width() <= 0 or video_rect.height() <= 0:
            return None

        if not video_rect.contains(widget_pos):
            return None  # click outside the actual video area

        # Relative position inside displayed video rectangle
        relative_x = (widget_pos.x() - video_rect.left()) / video_rect.width()
        relative_y = (widget_pos.y() - video_rect.top()) / video_rect.height()

        # Convert to original frame pixel coordinates
        frame_x = int(relative_x * self.video_width)
        frame_y = int(relative_y * self.video_height)

        # Clamp to valid range
        frame_x = max(0, min(self.video_width - 1, frame_x))
        frame_y = max(0, min(self.video_height - 1, frame_y))

        return QPoint(frame_x, frame_y)

    def get_video_rect(self) -> QRect:
        """
        Return the QRect of the actual displayed video area within the widget,
        assuming aspect-ratio-preserving fit.
        """
        if self.video_width <= 0 or self.video_height <= 0:
            return QRect()

        widget_size = self.size()
        vw, vh = self.video_width, self.video_height

        # Scale to fit while preserving aspect ratio
        scale_w = widget_size.width() / vw if vw else 0
        scale_h = widget_size.height() / vh if vh else 0
        scale = min(scale_w, scale_h) if scale_w and scale_h else 0

        if scale <= 0:
            return QRect()

        disp_w = int(vw * scale)
        disp_h = int(vh * scale)

        # Center within widget
        x = (widget_size.width() - disp_w) // 2
        y = (widget_size.height() - disp_h) // 2

        return QRect(x, y, disp_w, disp_h)


class MediaPlayer(QWidget):
    """
    MediaPlayer widget:
    - Uses Qt for playback/display (QMediaPlayer + QVideoWidget)
    - Uses OpenCV to reliably extract video width/height/FPS (instead of Qt metadata)
    - Maintains frame stepping based on FPS
    - Creates/loads Labels.csv in the video folder
    """

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.video_path = None

        # Qt Media Player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Video display widget
        # self.video_widget = CustomVideoWidget()

        self.video_container = QWidget(self)

        self.stack = QStackedLayout(self.video_container)
        self.stack.setStackingMode(QStackedLayout.StackAll)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.video_widget = CustomVideoWidget(self.video_container)
        self.stack.addWidget(self.video_widget)

        # UI controls
        self.open_file_button = QPushButton("Open video")
        self.open_file_button.clicked.connect(self.open_file)

        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_video)

        self.prev_frame_button = QPushButton("Previous Frame")
        self.prev_frame_button.setEnabled(False)
        self.prev_frame_button.clicked.connect(self.previous_frame)

        self.next_frame_button = QPushButton("Next Frame")
        self.next_frame_button.setEnabled(False)
        self.next_frame_button.clicked.connect(self.next_frame)

        self.frame_label = QLabel("Frame: 0")
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Layout
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.open_file_button)
        hbox.addWidget(self.play_button)
        hbox.addWidget(self.prev_frame_button)
        hbox.addWidget(self.next_frame_button)
        hbox.addWidget(self.frame_label)
        hbox.addWidget(self.slider)

        self.layout = QVBoxLayout()
        # self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.video_container)
        self.layout.addLayout(hbox)

        # Attach video output
        self.media_player.setVideoOutput(self.video_widget)

        # Signals
        self.media_player.stateChanged.connect(self.mediastate_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        # State
        self.path_label = None
        self.video_path = None

        self.frame_rate = 30.0  # default fallback
        self.is_media_loaded = False

        self.frame_overlay_label = QLabel(self.video_container)
        self.frame_overlay_label.setScaledContents(True)
        self.frame_overlay_label.hide()
        self.frame_overlay_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.frame_overlay_label.raise_()

        self.connect_hide_overlay_on_click(self.open_file_button)
        self.connect_hide_overlay_on_click(self.play_button)
        self.connect_hide_overlay_on_click(self.prev_frame_button)
        self.connect_hide_overlay_on_click(self.next_frame_button)
        self.slider.sliderPressed.connect(self.hide_frame_overlay)
        self.slider.sliderMoved.connect(self.hide_frame_overlay)

        # self.play_button.clicked.connect(self.hide_frame_overlay)
        # self.prev_frame_button.clicked.connect(self.hide_frame_overlay)
        # self.next_frame_button.clicked.connect(self.hide_frame_overlay)
        # self.slider.sliderPressed.connect(self.hide_frame_overlay)
        # self.slider.sliderMoved.connect(lambda _: self.hide_frame_overlay())
        # self.video_widget.frame_clicked.connect(lambda *_: self.hide_frame_overlay())

    # -------------------------
    # File / metadata (OpenCV)
    # -------------------------
    def _probe_video_with_cv2(self, filename: str):
        """
        Returns (width, height, fps) using OpenCV, or (None, None, None) on failure.
        """
        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            cap.release()
            return None, None, None

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        cap.release()

        if width <= 0 or height <= 0:
            width, height = None, None

        # Some files return 0.0 or NaN fps
        try:
            fps_val = float(fps)
        except Exception:
            fps_val = None

        if fps_val is None or fps_val <= 1.0 or fps_val != fps_val:  # fps!=fps catches NaN
            fps_val = None

        return width, height, fps_val

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename != '':
            self.video_path = filename
        if not filename:
            return

        # Probe with OpenCV FIRST (avoids Windows file-handle weirdness)
        width, height, fps = self._probe_video_with_cv2(filename)

        if width is not None and height is not None:
            self.video_widget.set_video_size(width, height)
            print(f"[cv2] Video size: {width} x {height}")
        else:
            print("[cv2] Could not read video size (click mapping may not work).")

        if fps is not None:
            self.frame_rate = fps
            print(f"[cv2] FPS: {fps}")
        else:
            print(f"[cv2] FPS unavailable/invalid; using default: {self.frame_rate}")

        # Load into Qt player
        self.video_path = filename
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))

        self.play_button.setEnabled(True)
        self.prev_frame_button.setEnabled(True)
        self.next_frame_button.setEnabled(True)
        self.is_media_loaded = True

        # Labels.csv in same directory
        self.path_label = os.path.join(os.path.dirname(filename), os.path.basename(filename).split('.')[0] + '.csv')
        if not os.path.isfile(self.path_label):
            tmp_df = pd.DataFrame(
                columns=["frame", "team", "event", "minute", "second", "x_coord", "y_coord", "video_ms"]
            )
            tmp_df.to_csv(self.path_label, index=False)

        # Refresh list UI from CSV
        self.main_window.list_manager.create_list_from_csv(self.path_label)
        self.main_window.list_display.display_list(self.main_window.list_manager.create_text_list())

    # -------------------------
    # Playback controls
    # -------------------------
    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediastate_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position: int):
        """
        position is in milliseconds.
        """
        self.slider.setValue(position)

        # Guard FPS
        fps = self.frame_rate if self.frame_rate and self.frame_rate > 1.0 else 30.0
        frame = int(position / (1000.0 / fps))
        self.frame_label.setText(f"Frame: {frame}")

    def duration_changed(self, duration: int):
        self.slider.setRange(0, duration)

    def set_position(self, position: int):
        self.media_player.setPosition(position)

    # -------------------------
    # Frame stepping
    # -------------------------
    def _frame_duration_ms(self) -> float:
        fps = self.frame_rate if self.frame_rate and self.frame_rate > 1.0 else 30.0
        return 1000.0 / fps

    def previous_frame(self):
        if not self.is_media_loaded:
            return
        current = float(self.media_player.position())
        step = self._frame_duration_ms()
        new_pos = max(current - step, 0.0)
        self.media_player.setPosition(int(new_pos))

    def next_frame(self):
        if not self.is_media_loaded:
            return
        current = float(self.media_player.position())
        step = self._frame_duration_ms()
        dur = float(self.media_player.duration())
        new_pos = min(current + step, dur)
        self.media_player.setPosition(int(new_pos))

    # -------------------------
    # Optional: debug click on container widget
    # (Clicks you care about should be on CustomVideoWidget)
    # -------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            print(f"[MediaPlayer widget] Clicked pixel coordinates: ({event.x()}, {event.y()})")
        super().mousePressEvent(event)

    # If you had get_last_label_file elsewhere, keep it.
    # (MainWindow uses self.media_player.get_last_label_file() on Ctrl+S in your code.)
    def get_last_label_file(self):
        return self.path_label

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # match the overlay label to the video widget area
        self.frame_overlay_label.setGeometry(self.video_widget.geometry())

    def hide_frame_overlay(self):
        label = getattr(self, "frame_overlay_label", None)
        if label is None:
            return
        label.hide()
        label.clear()

    def connect_hide_overlay_on_click(self, widget):
        """
        Connect any clickable widget to hide the frame overlay.
        """
        if hasattr(widget, "clicked"):
            widget.clicked.connect(self.hide_frame_overlay)

    def show_painted_frame_overlay(self, position_ms: int, frame_x: int, frame_y: int):
        """
        position_ms : video time in ms
        frame_x, frame_y : coordinates in *frame pixel coordinates*
        """

        if not self.video_path:
            return

        # --- OpenCV: read frame at position ---
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("OpenCV failed to open video for overlay")
            return

        cap.set(cv2.CAP_PROP_POS_MSEC, float(position_ms))
        ok, frame = cap.read()
        cap.release()

        if not ok or frame is None:
            print("OpenCV failed to read frame for overlay")
            return

        # --- Draw cross in FRAME coordinates (BGR) ---
        h, w = frame.shape[:2]
        x = int(frame_x)
        y = int(frame_y)

        if 0 <= x < w and 0 <= y < h:
            size = 5
            thickness = 1
            color = (0, 0, 255)  # red (BGR)

            cv2.line(frame, (x - size, y), (x + size, y), color, thickness)
            cv2.line(frame, (x, y - size), (x, y + size), color, thickness)

        # --- Convert BGR -> RGB ---
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # --- MATCH QVideoWidget (KeepAspectRatio + centering) ---
        video_widget = self.video_widget
        widget_w = video_widget.width()
        widget_h = video_widget.height()

        fh, fw = frame_rgb.shape[:2]

        scale = min(widget_w / fw, widget_h / fh)
        scaled_w = int(fw * scale)
        scaled_h = int(fh * scale)

        resized = cv2.resize(frame_rgb, (scaled_w, scaled_h), interpolation=cv2.INTER_LINEAR)

        # Black padded canvas (black bars)
        canvas = np.zeros((widget_h, widget_w, 3), dtype=np.uint8)

        x0 = (widget_w - scaled_w) // 2
        y0 = (widget_h - scaled_h) // 2

        canvas[y0:y0 + scaled_h, x0:x0 + scaled_w] = resized

        # --- Convert to QPixmap ---
        bytes_per_line = 3 * widget_w
        qimg = QImage(
            canvas.data,
            widget_w,
            widget_h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pix = QPixmap.fromImage(qimg)

        # --- Show overlay exactly on top of the video ---
        self.frame_overlay_label.setGeometry(video_widget.geometry())
        self.frame_overlay_label.setPixmap(pix)
        self.frame_overlay_label.show()
        self.frame_overlay_label.raise_()
