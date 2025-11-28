from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QListWidget, QGroupBox, QHBoxLayout,
    QDesktopWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
import json

class WelcomeWidget(QMainWindow):
    finished = pyqtSignal()  # Signal emitted when setup is finished

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.user_details = {}
        self.tradebook_files = []
        self.manual_trades_path = ""

    # Initialization and UI setup
    def init_ui(self):
        """Initialize the main UI components."""
        self.setWindowTitle("Portfolio 360")
        self.setWindowIcon(QIcon("assets/portfolio360.webp"))
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)
        self.center_on_screen()

        self.stacked_widget = QStackedWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.setup_pages()

    def center_on_screen(self):
        """Center the widget on the screen."""
        screen_geometry = QDesktopWidget().availableGeometry()
        widget_geometry = self.frameGeometry()
        widget_geometry.moveCenter(screen_geometry.center())
        self.move(widget_geometry.topLeft())

    def setup_pages(self):
        """Add all pages to the stacked widget."""
        self.stacked_widget.addWidget(self.create_welcome_page())
        self.stacked_widget.addWidget(self.create_user_details_page())
        self.stacked_widget.addWidget(self.create_tradebook_selection_page())
        self.stacked_widget.addWidget(self.create_manual_trades_selection_page())
        self.stacked_widget.addWidget(self.create_confirmation_page())

    # Navigation methods
    def next_page(self):
        """Navigate to the next page."""
        current_index = self.stacked_widget.currentIndex()
        if current_index < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(current_index + 1)

    def previous_page(self):
        """Navigate to the previous page."""
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)

    # Page creation methods
    def create_welcome_page(self):
        """Create the welcome page."""
        page = QWidget()
        layout = QVBoxLayout()

        # Welcome layout with icon and labels
        welcome_layout = QVBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("assets/portfolio360.webp").pixmap(128, 128))
        icon_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(icon_label)

        welcome_label = QLabel(
            "<div style='text-align: center;'>"
            "<span style='font-family: \"Georgia\"; font-size: 32px;'>Welcome to</span><br>"
            "<span style='font-family: \"Georgia\"; font-size: 50px; font-weight: bold;'>Portfolio 360</span>"
            "</div>"
        )
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)

        tagline_label = QLabel(
            "<div style='text-align: center;'>"
            "<span style='font-family: \"Arial\"; font-size: 18px; color: gray;'>"
            "Begin your journey towards smart investing"
            "</span>"
            "</div>"
        )
        tagline_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(tagline_label)

        layout.addStretch()
        layout.addLayout(welcome_layout)
        layout.addStretch()

        # Continue button with animation
        continue_button = QPushButton("Continue to setup >")
        continue_button.setFont(QFont("Arial", 14, QFont.Bold))
        continue_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #77dd77;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #66cc66;
            }
            QPushButton:pressed {
                background-color: #5cb85c;
            }
        """)
        continue_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(continue_button, alignment=Qt.AlignRight)

        animation_states = ["Continue to setup >  ", "Continue to setup   >", "Continue to setup     "]
        animation_index = [0]

        def animate_arrow():
            animation_index[0] = (animation_index[0] + 1) % len(animation_states)
            continue_button.setText(animation_states[animation_index[0]])

        timer = QTimer(self)
        timer.timeout.connect(animate_arrow)
        timer.start(500)

        continue_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        page.setLayout(layout)
        return page

    def create_user_details_page(self):
        """Create the user details page."""
        page = QWidget()
        layout = QVBoxLayout()

        group_box = QGroupBox("Personal Details")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #77dd77;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f0f0f0;
            }
        """)
        group_box.setFixedWidth(450)
        group_layout = QVBoxLayout()
        group_layout.setSpacing(15)

        title_label = QLabel("Please provide your details")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(title_label)

        # Name input
        name_label = QLabel("Name:")
        name_label.setFont(QFont("Arial", 12))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter your name")
        name_input.setFont(QFont("Arial", 12))
        name_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px;")
        group_layout.addWidget(name_label)
        group_layout.addWidget(name_input)

        # Email input
        email_label = QLabel("Email:")
        email_label.setFont(QFont("Arial", 12))
        email_input = QLineEdit()
        email_input.setPlaceholderText("Enter your email")
        email_input.setFont(QFont("Arial", 12))
        email_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px;")
        group_layout.addWidget(email_label)
        group_layout.addWidget(email_input)

        group_layout.addSpacing(20)

        # Back and Next buttons
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        next_button = QPushButton("Next")
        next_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #77dd77;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #66cc66;
            }
            QPushButton:pressed {
                background-color: #5cb85c;
            }
        """)
        button_layout.addWidget(next_button, alignment=Qt.AlignRight)

        group_layout.addLayout(button_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        back_button.clicked.connect(self.previous_page)
        next_button.clicked.connect(lambda: self.save_user_details(name_input, email_input))
        page.setLayout(layout)
        return page

    def save_user_details(self, name_input: str, email_input: str):
        """Save user details and navigate to the next page."""
        self.user_details['name'] = name_input.text()
        self.user_details['email'] = email_input.text()
        self.next_page()

    def create_tradebook_selection_page(self):
        """Create the tradebook selection page."""
        page = QWidget()
        layout = QVBoxLayout()

        group_box = QGroupBox("Tradebook")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #77dd77;  /* Light green border */
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f0f0f0;
            }
        """)
        group_box.setFixedWidth(450)  # Adjusted width for better alignment
        group_layout = QVBoxLayout()
        group_layout.setSpacing(15)  # Add spacing between elements

        title_label = QLabel("Upload Tradebook")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(title_label)

        # Update description label to support multiline text
        description_label = QLabel("Please upload one or more tradebook files in CSV format downloaded from Zerodha. These files may correspond to different fiscal years.")
        description_label.setFont(QFont("Arial", 10))
        description_label.setStyleSheet("color: gray;")  # Removed text-align from stylesheet
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignJustify)  # Set alignment to justify
        group_layout.addWidget(description_label)

        file_list = QListWidget()
        file_list.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
        group_layout.addWidget(file_list)

        # Add "Back", "Add Files", and "Next" buttons with updated styles
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.setIcon(QIcon("icons/back.png"))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(back_button)

        add_files_button = QPushButton("Add Files")
        add_files_button.setIcon(QIcon("icons/add.png"))
        add_files_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(add_files_button)

        next_button = QPushButton("Next")
        next_button.setIcon(QIcon("icons/next.png"))
        next_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #77dd77;  /* Light green */
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #66cc66;  /* Darker green on hover */
            }
            QPushButton:pressed {
                background-color: #5cb85c;  /* Even darker green on press */
            }
        """)
        button_layout.addWidget(next_button)

        group_layout.addLayout(button_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        def add_files():
            files, _ = QFileDialog.getOpenFileNames(self, "Select Tradebook Files")
            for file in files:
                if file not in self.tradebook_files:
                    self.tradebook_files.append(file)
                    # Extract folder and file name
                    formatted_name = "/".join(file.split("/")[-2:])
                    file_list.addItem(formatted_name)

        back_button.clicked.connect(self.previous_page)
        add_files_button.clicked.connect(add_files)
        next_button.clicked.connect(self.next_page)
        page.setLayout(layout)
        return page

    def create_manual_trades_selection_page(self):
        """Create the manual trades selection page."""
        page = QWidget()
        layout = QVBoxLayout()

        group_box = QGroupBox("Manual Trades")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #77dd77;  /* Light green border */
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f0f0f0;
            }
        """)
        group_box.setFixedWidth(450)  # Adjusted width for better alignment
        group_layout = QVBoxLayout()
        group_layout.setSpacing(15)  # Add spacing between elements

        title_label = QLabel("Upload Manual Trades")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(title_label)

        # Add description label
        description_label = QLabel("Please upload a CSV file containing your manually executed trades. This may include trades from SIPs, ESOPs, gifts, or other transactions not recorded in the tradebook.")
        description_label.setFont(QFont("Arial", 10))
        description_label.setStyleSheet("color: gray;")  # Removed text-align from stylesheet
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignJustify)  # Set alignment to justify
        group_layout.addWidget(description_label)

        path_label = QLabel("No file selected")
        path_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
        group_layout.addWidget(path_label)

        # Add "Back", "Select File", and "Next" buttons with updated styles
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.setIcon(QIcon("icons/back.png"))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(back_button)

        select_file_button = QPushButton("Select File")
        select_file_button.setIcon(QIcon("icons/select.png"))
        select_file_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(select_file_button)

        next_button = QPushButton("Next")
        next_button.setIcon(QIcon("icons/next.png"))
        next_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #77dd77;  /* Light green */
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #66cc66;  /* Darker green on hover */
            }
            QPushButton:pressed {
                background-color: #5cb85c;  /* Even darker green on press */
            }
        """)
        button_layout.addWidget(next_button)

        group_layout.addLayout(button_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        def select_file():
            path, _ = QFileDialog.getOpenFileName(self, "Select Manual Trades File")
            if path:
                self.manual_trades_path = path
                # Extract folder and file name
                formatted_name = "/".join(path.split("/")[-2:])
                path_label.setText(formatted_name)

        back_button.clicked.connect(self.previous_page)
        select_file_button.clicked.connect(select_file)
        next_button.clicked.connect(self.next_page)
        page.setLayout(layout)
        return page

    def create_confirmation_page(self):
        """Create the confirmation page."""
        page = QWidget()
        layout = QVBoxLayout()

        group_box = QGroupBox("Setup Completed")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #77dd77;  /* Light green border */
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f0f0f0;
            }
        """)
        group_box.setFixedWidth(450)  # Adjusted width for better alignment
        group_layout = QVBoxLayout()
        group_layout.setSpacing(15)  # Add spacing between elements

        title_label = QLabel("Congratulations!")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(title_label)

        message_label = QLabel("You have successfully completed the setup. Let's get started!")
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 12))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: gray;")
        group_layout.addWidget(message_label)

        # Add "Finish" button with updated styles
        button_layout = QHBoxLayout()
        finish_button = QPushButton("Finish")
        finish_button.setIcon(QIcon("icons/finish.png"))
        finish_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #77dd77;  /* Light green */
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #66cc66;  /* Darker green on hover */
            }
            QPushButton:pressed {
                background-color: #5cb85c;  /* Even darker green on press */
            }
        """)
        button_layout.addWidget(finish_button, alignment=Qt.AlignCenter)

        group_layout.addLayout(button_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        finish_button.clicked.connect(self.finish)  # Update to use the new finish method
        page.setLayout(layout)
        return page

    def save_to_json(self):
        """Save user details and file paths to a JSON file."""
        data = {
            "name": self.user_details.get("name", ""),
            "email": self.user_details.get("email", ""),
            "tradebook": self.tradebook_files,
            "manual_tradebook": self.manual_trades_path
        }
        with open("metadata/user_data.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

    def finish(self):
        """Handle finish button click."""
        self.save_to_json()
        self.finished.emit()
        self.close()