import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QPushButton
from PyQt5.QtGui import QIcon
from src.widgets.piechart import PieChartWidget
from src.widgets.chatbox import ChatboxWidget
from src.widgets.tradebook_table import TradeBookTable
from src.widgets.welcome import WelcomeWidget
from src.lib.controller import Controller
from src.widgets.holdings import HoldingsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portfolio 360")
        self.setGeometry(100, 100, 1920, 1080)
        self.setWindowIcon(QIcon("assets/portfolio360.webp"))  # Set application icon

        self.controller = Controller()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add navigation buttons
        nav_layout = QHBoxLayout()
        holdings_button = QPushButton("Holdings")
        holdings_button.clicked.connect(self.show_holdings_page)
        dashboard_button = QPushButton("Dashboard")
        dashboard_button.clicked.connect(self.show_dashboard_page)
        nav_layout.addWidget(holdings_button)
        nav_layout.addWidget(dashboard_button)
        main_layout.addLayout(nav_layout)

        # Stacked widget for pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Page 1: HoldingsWidget
        self.holdings_widget = HoldingsWidget()
        self.holdings_widget.set_holdings(self.controller.current_holdings, self.controller.past_holdings)
        self.pages.addWidget(self.holdings_widget)

        # Page 2: Dashboard (existing widgets)
        dashboard_page = QWidget()
        dashboard_layout = QHBoxLayout(dashboard_page)

        # Left layout for PieChartWidget and ChatboxWidget
        left_layout = QVBoxLayout()
        dashboard_layout.addLayout(left_layout)

        data1 = (
            ['Stocks', 'Bonds', 'Real Estate', 'Cash', 'Mutual Funds', 'ETFs', 'Options', 'Futures', 
             'Private Equity', 'Hedge Funds', 'Currencies', 'Commodities', 'Derivatives', 'REITs', 'Savings'],
            [10, 8, 7, 5, 6, 5, 4, 4, 3, 3, 2, 2, 2, 2, 1]
        )
        pie_chart1 = PieChartWidget(*data1)
        left_layout.addWidget(pie_chart1)

        chatbox = ChatboxWidget()
        left_layout.addWidget(chatbox)

        # Right layout for TradeBookTable and PriceBarWidget
        right_layout = QHBoxLayout()
        dashboard_layout.addLayout(right_layout)

        # Add TradeBookTable
        self.tradebook_table = TradeBookTable()
        sample_trades = self.controller.adjusted_tradebook
        self.tradebook_table.populateTable(sample_trades)
        right_layout.addWidget(self.tradebook_table)

        self.pages.addWidget(dashboard_page)

        # Show HoldingsWidget by default
        self.pages.setCurrentWidget(self.holdings_widget)

    def show_holdings_page(self):
        self.pages.setCurrentWidget(self.holdings_widget)

    def show_dashboard_page(self):
        self.pages.setCurrentIndex(1)  # Dashboard is the second page


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set Centra No.2 font globally
    app.setStyleSheet("""
        * {
            font-family: "Centra No.2";
        }
    """)

    if os.path.exists("metadata/user_data.json"):
        # If user_data.json exists, directly open the main application
        app.main_window = MainWindow()  # Keep MainWindow as an attribute of the app
        app.main_window.show()
    else:
        # Launch WelcomeWidget first
        welcome_widget = WelcomeWidget()

        def on_welcome_finished():
            welcome_widget.close()
            app.main_window = MainWindow()
            app.main_window.show()

        welcome_widget.finished.connect(on_welcome_finished)  # Connect the finished signal
        welcome_widget.show()

    sys.exit(app.exec_())
