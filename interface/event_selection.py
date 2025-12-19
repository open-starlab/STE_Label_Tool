from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
from utils.event_class import Event, ms_to_time
from interface.txt_opener import TextFileOpener

class EventSelectionWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Defining some variables of the window
        self.title_window = "Event Selection"
        self.setWindowTitle(self.title_window)

        self.palette_main_window = self.palette()
        self.palette_main_window.setColor(QPalette.Window, Qt.black)

        self.x_coord  = -1
        self.y_coord = -1

        # Initiate the sub-widgets
        self.init_window()

    def init_window(self):
        # Initialize widgets
        self.list_widget = QListWidget()
        self.list_widget.clicked.connect(self.clicked)

        self.list_widget_second = QListWidget()
        self.list_widget_second.clicked.connect(self.clicked)

        # Add the "Config" button
        self.config_button = QPushButton("Config")
        self.config_button.clicked.connect(self.open_config_window)
        self.config_button.clicked.connect(
            self.main_window.media_player.hide_frame_overlay
        )

        #Add the coordinates display label 
        self.coord_label = QLabel("Coordinates")
        self.coord_label_x = QLabel("X: ")
        self.coord_label_y = QLabel("Y: ")
        self.coord_label_x_value = QLabel(str(self.x_coord))
        self.coord_label_y_value = QLabel(str(self.y_coord))

        # Create a horizontal layout for coordinate labels
        coord_layout = QHBoxLayout()
        # coord_layout.addWidget(self.coord_label)
        coord_layout.addWidget(self.coord_label_x)
        coord_layout.addWidget(self.coord_label_x_value)
        coord_layout.addWidget(self.coord_label_y)
        coord_layout.addWidget(self.coord_label_y_value)

        # Add the Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_event)
        self.save_button.clicked.connect(
            self.main_window.media_player.hide_frame_overlay
        )

        # Create labels for the text areas
        self.label_event = QLabel("Event")
        self.label_team = QLabel("Team")

        # Layout the different widgets
        final_layout = QVBoxLayout()
        final_layout.addWidget(self.config_button)
        final_layout.addWidget(self.label_event)
        final_layout.addWidget(self.list_widget)
        final_layout.addWidget(self.coord_label)
        final_layout.addLayout(coord_layout)
        final_layout.addWidget(self.label_team)
        final_layout.addWidget(self.list_widget_second)
        final_layout.addWidget(self.save_button)
        self.setLayout(final_layout)

        self.first_label = None
        self.second_label = None

        # Now call get_label() to populate the list widgets
        self.get_label()

    def get_label(self):
        """Read labels from configuration files."""
        self.labels = self.read_labels('./config/event_classes.txt')
        self.second_labels = self.read_labels('./config/team_classes.txt')

        # Update the list widgets with the new labels
        self.populate_list_widget(self.list_widget, self.labels)
        self.populate_list_widget(self.list_widget_second, self.second_labels)

    def update_coordinates(self, x, y):
        """Update the displayed coordinates."""
        self.x_coord = x
        self.y_coord = y
        self.coord_label_x_value.setText(str(self.x_coord))
        self.coord_label_y_value.setText(str(self.y_coord))

    def populate_list_widget(self, list_widget, items):
        """Populate the specified QListWidget with items."""
        list_widget.clear()  # Clear existing items
        for item in items:
            list_widget.addItem(item)

    def read_labels(self, file_path):
        """Read labels from a given file."""
        labels = []
        with open(file_path) as file:
            for line in file:
                labels.append(line.rstrip())
        return labels

    def clicked(self, qmodelindex):
        """Handle list widget item click event."""
        self.main_window.media_player.hide_frame_overlay()
        print("clicked")

    def keyPressEvent(self, event):
        """Handle key press events for saving or cancelling selection."""
        if event.key() == Qt.Key_Return:
            self.save_event()  # Call the save_event function when Enter key is pressed
        elif event.key() == Qt.Key_Escape:
            self.reset_selection()  # Reset selection on Escape key

    def reset_selection(self):
        """Reset the selection in the list widgets."""
        self.first_label = None
        self.second_label = None
        self.list_widget.setCurrentRow(-1)
        self.list_widget_second.setCurrentRow(-1)
        self.main_window.setFocus()

    def save_event(self):
        """Save the selected event."""
        self.first_label = self.list_widget.currentItem()
        self.second_label = self.list_widget_second.currentItem()
        if self.first_label is None or self.second_label is None:
            return

        self.first_label = self.list_widget.currentItem().text() #event
        self.second_label = self.list_widget_second.currentItem().text() #team
        position = self.main_window.media_player.media_player.position()
        frame = int(position / 1000 * self.main_window.media_player.frame_rate)
        # self.x_coord = -1
        # self.y_coord = -1
        self.main_window.list_manager.add_event(Event(frame, self.second_label, self.first_label, ms_to_time(position)[0], ms_to_time(position)[1], self.x_coord, self.y_coord, position))
        self.main_window.list_display.display_list(self.main_window.list_manager.create_text_list())

        # Reset label variables and save to file
        self.first_label = None
        self.second_label = None
        path_label = self.main_window.media_player.path_label
        self.main_window.list_manager.save_file(path_label, self.main_window.half)

        # Clear selections and reset focus
        self.list_widget.setCurrentRow(-1)
        self.list_widget_second.setCurrentRow(-1)
        self.main_window.setFocus()

        # Reset coordinates to 0
        self.update_coordinates(-1, -1)

    def open_config_window(self):
        """Open the configuration editor window."""
        self.config_window = TextFileOpener(self.main_window)
        self.config_window.setWindowTitle("Configuration Editor")
        self.config_window.resize(600, 400)  # Set the window size
        self.config_window.closed.connect(self.get_label)  # Connect the closed signal to get_label method
        self.config_window.show()
