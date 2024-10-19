from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import pyqtSignal

class TextFileOpener(QWidget):

    closed = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Set up the text areas for both files
        self.text_edit_class = QTextEdit()  # Editable text area for event_classes.txt
        self.text_edit_team = QTextEdit()  # Editable text area for team_classes.txt

        # Set up the save button
        self.save_button = QPushButton("Save and Exit")
        self.save_button.clicked.connect(self.save_and_exit)

        # Create labels for the text areas
        self.label_event = QLabel("Event")
        self.label_team = QLabel("Team")

        # Set up the layout for text areas side by side
        text_layout = QHBoxLayout()
        
        # Create vertical layouts for each text area and its label
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.label_event)  # Add Event label
        left_layout.addWidget(self.text_edit_class)  # Add event text area

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.label_team)  # Add Team label
        right_layout.addWidget(self.text_edit_team)  # Add team text area

        # Add the left and right layouts to the main text layout
        text_layout.addLayout(left_layout)
        text_layout.addLayout(right_layout)

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addLayout(text_layout)  # Add text areas layout
        layout.addWidget(self.save_button)  # Save button at the bottom

        self.setLayout(layout)

        # Variables to store the file paths
        self.class_file = './config/event_classes.txt'
        self.team_file = './config/team_classes.txt'
        
        # Auto open both text files
        self.open_files()

    def open_files(self):
        # Open and read the content of the class file
        with open(self.class_file, 'r') as file:
            class_content = file.read()
        self.text_edit_class.setText(class_content)

        # Open and read the content of the team file
        with open(self.team_file, 'r') as file:
            team_content = file.read()
        self.text_edit_team.setText(team_content)

    def save_and_exit(self):
        # Get the edited content from the text areas
        edited_class_content = self.text_edit_class.toPlainText()
        edited_team_content = self.text_edit_team.toPlainText()

        # Write the edited content back to the respective files
        with open(self.class_file, 'w') as file:
            file.write(edited_class_content)

        with open(self.team_file, 'w') as file:
            file.write(edited_team_content)

        print(f"Files saved: {self.class_file}, {self.team_file}")

        # Close the window after saving
        self.close()
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


# To test this in a PyQt5 application
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = TextFileOpener(None)
    window.setWindowTitle("Text File Editor")
    window.resize(800, 400)  # Set the window size
    window.show()
    sys.exit(app.exec_())
