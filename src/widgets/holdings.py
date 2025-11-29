from typing import List
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QFormLayout, QTextEdit, QFrame, QGroupBox, QGridLayout, QHeaderView, QStyledItemDelegate, QTabWidget, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont, QPainter

from src.models.holding import Holding
from src.widgets.price_bar import PriceBarWidget  # Import the PriceBarWidget
from src.widgets.profit_bar_chart import ProfitBarChart  # Import the ProfitBarChart widget

class ProfitLossDelegate(QStyledItemDelegate):
    """
    Custom delegate to handle coloring of profit/loss cells.
    """
    def paint(self, painter, option, index):
        value = index.data()  # Get the cell value
        if value is not None and isinstance(value, str):
            try:
                numeric_value = float(value)
                if numeric_value > 0:
                    option.palette.setColor(option.palette.Text, QColor(0, 128, 0))  # Dark green
                elif numeric_value < 0:
                    option.palette.setColor(option.palette.Text, QColor(255, 0, 0))  # Red
            except ValueError:
                pass  # Ignore non-numeric values
        super().paint(painter, option, index)

class HoldingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize stock_info_widgets dictionary
        self.stock_info_widgets = {}

        # Initialize the ProfitBarChart widget
        self.profit_bar_chart = ProfitBarChart([])

        # Main layout with QSplitter for adjustable widths
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # Left: Two tables for holdings (current and past)
        left_pane = QVBoxLayout()

        # Label for Current Holdings Table
        current_holdings_label = QLabel("Current Holdings")
        current_holdings_label.setStyleSheet("""
            QLabel {
                font-size: 22px; /* Increased font size */
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 5px;
            }
        """)
        left_pane.addWidget(current_holdings_label)

        # Current Holdings Table
        self.current_holdings_table = QTableWidget()
        self.current_holdings_table.setColumnCount(5)  # Updated to 5 columns
        self.current_holdings_table.setHorizontalHeaderLabels([
            "Symbol", "Quantity", "Price Average", "Invested Value", "Unrealized Profit"
        ])
        self.current_holdings_table.cellClicked.connect(lambda row, col: self.display_details(row, col, "current"))
        self.current_holdings_table.setSortingEnabled(True)
        self._customize_table(self.current_holdings_table)
        left_pane.addWidget(self.current_holdings_table)

        # Label for Past Holdings Table
        past_holdings_label = QLabel("Past Holdings")
        past_holdings_label.setStyleSheet("""
            QLabel {
                font-size: 22px; /* Increased font size */
                font-weight: bold;
                color: #4CAF50;
                margin-top: 10px;
                margin-bottom: 5px;
            }
        """)
        left_pane.addWidget(past_holdings_label)

        # Past Holdings Table
        self.past_holdings_table = QTableWidget()
        self.past_holdings_table.setColumnCount(5)  # Updated to 5 columns
        self.past_holdings_table.setHorizontalHeaderLabels([
            "Symbol", "Dividend Earned", "Profitable Trades", "Loss Trades", "Realized Profit"
        ])
        self.past_holdings_table.cellClicked.connect(lambda row, col: self.display_details(row, col, "past"))
        self.past_holdings_table.setSortingEnabled(True)
        self._customize_table(self.past_holdings_table)
        left_pane.addWidget(self.past_holdings_table)

        # Add left pane to splitter
        left_widget = QWidget()
        left_widget.setLayout(left_pane)
        splitter.addWidget(left_widget)

        # Right: Detailed description pane with a grid layout inside a group box
        self.details_group = QGroupBox("Holding Details")
        self.details_group.setStyleSheet("""
            QGroupBox {
                font: bold 12px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #4CAF50;
            }
        """)

        # Create a vertical layout for the details group
        self.details_layout = QVBoxLayout()
        self.details_group.setLayout(self.details_layout)  # Explicitly set the layout

        # Top section: Symbol
        self.top_section = QVBoxLayout()

        # Symbol label (top, center-aligned)
        self.symbol_label = QLabel()
        self.symbol_label.setStyleSheet("""
            QLabel {
                font-size: 60px; /* Increased font size */
                font-weight: bold;
                color: #333;
            }
        """)
        self.top_section.addWidget(self.symbol_label, alignment=Qt.AlignCenter)  # Changed alignment to center

        # Details section (below the symbol)
        self.details_below_symbol = QGridLayout()
        self.details_below_symbol.setHorizontalSpacing(20)
        self.details_below_symbol.setVerticalSpacing(10)

        # Add placeholders for details (except description)
        self.details_widgets = {
            "Industry Type": QLabel(),
            "Sector Type": QLabel(),
            "Market Cap": QLabel(),
            "Risk-Free Return": QLabel(),
            "Index Returns": QLabel(),
            "Total Investment": QLabel()
        }
        for row, (label, widget) in enumerate(self.details_widgets.items()):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; color: #333;")
            self.details_below_symbol.addWidget(label_widget, row, 0, alignment=Qt.AlignRight)
            self.details_below_symbol.addWidget(widget, row, 1, alignment=Qt.AlignLeft)

        self.top_section.addLayout(self.details_below_symbol)

        # Profit section (right side)
        self.profit_section = QVBoxLayout()

        # Realized and Unrealized Profit (side by side)
        self.profit_row_layout = QHBoxLayout()

        # Realized Profit
        self.realized_profit_layout = QVBoxLayout()
        self.realized_profit_value = QLabel()
        self.realized_profit_label = QLabel("Realized Profit")
        self.realized_profit_value.setStyleSheet("""
            QLabel {
                font-size: 40px; /* Increased font size */
                font-weight: bold;
            }
        """)
        self.realized_profit_label.setStyleSheet("""
            QLabel {
                font-size: 12px; /* Label font size */
                color: #666;
            }
        """)
        self.realized_profit_layout.addWidget(self.realized_profit_value, alignment=Qt.AlignCenter)
        self.realized_profit_layout.addWidget(self.realized_profit_label, alignment=Qt.AlignCenter)

        # Unrealized Profit
        self.unrealized_profit_layout = QVBoxLayout()
        self.unrealized_profit_value = QLabel()
        self.unrealized_profit_label = QLabel("Unrealized Profit")
        self.unrealized_profit_value.setStyleSheet("""
            QLabel {
                font-size: 40px; /* Increased font size */
                font-weight: bold;
            }
        """)
        self.unrealized_profit_label.setStyleSheet("""
            QLabel {
                font-size: 12px; /* Label font size */
                color: #666;
            }
        """)
        self.unrealized_profit_layout.addWidget(self.unrealized_profit_value, alignment=Qt.AlignCenter)
        self.unrealized_profit_layout.addWidget(self.unrealized_profit_label, alignment=Qt.AlignCenter)

        # Add Realized and Unrealized Profit to the row layout
        self.profit_row_layout.addLayout(self.realized_profit_layout)
        self.profit_row_layout.addLayout(self.unrealized_profit_layout)

        # Invested Amount (below Realized and Unrealized Profit)
        self.invested_amount_layout = QVBoxLayout()
        self.invested_amount_value = QLabel()
        self.invested_amount_label = QLabel("Invested Amount")
        self.invested_amount_value.setStyleSheet("""
            QLabel {
                font-size: 40px; /* Increased font size */
                font-weight: bold;
            }
        """)
        self.invested_amount_label.setStyleSheet("""
            QLabel {
                font-size: 12px; /* Label font size */
                color: #666;
            }
        """)
        self.invested_amount_layout.addWidget(self.invested_amount_value, alignment=Qt.AlignCenter)
        self.invested_amount_layout.addWidget(self.invested_amount_label, alignment=Qt.AlignCenter)

        # Add the profit row and invested amount to the profit section
        self.profit_section.addLayout(self.profit_row_layout)
        self.profit_section.addLayout(self.invested_amount_layout)

        # Combine the symbol and profit sections
        self.symbol_and_profit_layout = QHBoxLayout()
        self.symbol_and_profit_layout.addLayout(self.top_section, stretch=1)
        self.symbol_and_profit_layout.addLayout(self.profit_section, stretch=1)

        # Add the price bar widget to the rightmost corner
        self.price_bar_widget = PriceBarWidget()
        self.symbol_and_profit_layout.addWidget(self.price_bar_widget, stretch=1)

        # Replace the details layout with a tabbed structure
        self.details_tabs = QTabWidget()
        self.details_layout.addWidget(self.details_tabs)

        # Tab 1: Existing details
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)
        tab1_layout.addLayout(self.symbol_and_profit_layout)
        tab1_layout.addWidget(self.profit_bar_chart)  # Use the initialized widget
        self.details_tabs.addTab(tab1_widget, "Overview")

        # Tab 2: StockInfo details
        tab2_widget = QWidget()
        tab2_layout = QVBoxLayout(tab2_widget)

        # Add a scrollable area for StockInfo details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Helper function to create cluster sections
        def create_cluster_section(title, attributes):
            section_widget = QWidget()
            section_layout = QVBoxLayout(section_widget)
            section_layout.setSpacing(10)

            # Add section title
            title_label = QLabel(f"<b>{title}</b>")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #4CAF50;
                    margin-bottom: 10px;
                }
            """)
            section_layout.addWidget(title_label)

            # Add attributes in a multi-column grid layout
            grid_layout = QGridLayout()
            grid_layout.setHorizontalSpacing(20)
            grid_layout.setVerticalSpacing(10)

            for row, attr in enumerate(attributes):
                label = QLabel(attr.replace("_", " ").title() + ":")
                label.setStyleSheet("font-weight: bold; color: #333;")
                value_label = QLabel()
                value_label.setStyleSheet("color: #666;")
                grid_layout.addWidget(label, row // 2, (row % 2) * 2, alignment=Qt.AlignRight)
                grid_layout.addWidget(value_label, row // 2, (row % 2) * 2 + 1, alignment=Qt.AlignLeft)
                self.stock_info_widgets[attr] = value_label

            section_layout.addLayout(grid_layout)
            return section_widget

        # Populate StockInfo details in clusters
        scroll_layout.addWidget(create_cluster_section("Basic Information", [
            "symbol", "symbol_yf", "name", "city", "industry", "sector"
        ]))
        scroll_layout.addWidget(create_cluster_section("Price and Volume", [
            "previous_close", "volume", "average_volume_10days", "average_volume_3months",
            "fifty_two_week_low", "fifty_two_week_high", "fifty_two_week_change"
        ]))
        scroll_layout.addWidget(create_cluster_section("Valuation Metrics", [
            "market_cap", "book_value", "price_to_sales_trailing_12_months", "price_to_book",
            "trailing_pe", "forward_pe", "trailing_eps", "forward_eps", "price_eps_current_year"
        ]))
        scroll_layout.addWidget(create_cluster_section("Moving Averages", [
            "fifty_day_average", "two_hundred_day_average"
        ]))
        scroll_layout.addWidget(create_cluster_section("Financial Ratios", [
            "beta", "debt_to_equity", "enterprise_to_revenue", "enterprise_to_ebitda"
        ]))
        scroll_layout.addWidget(create_cluster_section("Financial Performance", [
            "ebitda", "total_debt", "total_revenue", "revenue_per_share", "gross_profit",
            "revenue_growth", "gross_margins", "ebitda_margins", "operating_margins",
            "eps_trailing_12months", "eps_forward", "eps_current_year"
        ]))
        scroll_layout.addWidget(create_cluster_section("Price Targets", [
            "target_high_price", "target_low_price", "target_mean_price"
        ]))
        scroll_layout.addWidget(create_cluster_section("Dividends", [
            "dividend_yield", "five_year_average_dividend_yield"
        ]))

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        tab2_layout.addWidget(scroll_area)
        self.details_tabs.addTab(tab2_widget, "Stock Info")

        # Tab 3: Running Info
        tab3_widget = QWidget()
        tab3_layout = QVBoxLayout(tab3_widget)

        # Running LTCG and STCG section
        running_info_layout = QHBoxLayout()
        
        # Running LTCG
        self.running_ltcg_layout = QVBoxLayout()
        self.running_ltcg_value = QLabel("0.00")
        self.running_ltcg_label = QLabel("Current Running LTCG")
        self.running_ltcg_value.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        """)
        self.running_ltcg_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
            }
        """)
        self.running_ltcg_layout.addWidget(self.running_ltcg_value, alignment=Qt.AlignCenter)
        self.running_ltcg_layout.addWidget(self.running_ltcg_label, alignment=Qt.AlignCenter)

        # Running STCG
        self.running_stcg_layout = QVBoxLayout()
        self.running_stcg_value = QLabel("0.00")
        self.running_stcg_label = QLabel("Current Running STCG")
        self.running_stcg_value.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        """)
        self.running_stcg_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
            }
        """)
        self.running_stcg_layout.addWidget(self.running_stcg_value, alignment=Qt.AlignCenter)
        self.running_stcg_layout.addWidget(self.running_stcg_label, alignment=Qt.AlignCenter)

        running_info_layout.addLayout(self.running_ltcg_layout)
        running_info_layout.addLayout(self.running_stcg_layout)
        tab3_layout.addLayout(running_info_layout)

        # Running Trades Table
        running_trades_label = QLabel("Running Trades")
        running_trades_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        tab3_layout.addWidget(running_trades_label)

        self.running_trades_table = QTableWidget()
        self.running_trades_table.setColumnCount(7)
        self.running_trades_table.setHorizontalHeaderLabels([
            "Order ID", "Symbol", "Quantity", "Price", "Type", "Timestamp", "Current Profit"
        ])
        self._customize_trades_table(self.running_trades_table)
        tab3_layout.addWidget(self.running_trades_table)

        # All Trades Table
        all_trades_label = QLabel("All Trades")
        all_trades_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        tab3_layout.addWidget(all_trades_label)

        self.all_trades_table = QTableWidget()
        self.all_trades_table.setColumnCount(7)
        self.all_trades_table.setHorizontalHeaderLabels([
            "Order ID", "Symbol", "Quantity", "Price", "Type", "Timestamp", "Remarks"
        ])
        self._customize_trades_table(self.all_trades_table)
        tab3_layout.addWidget(self.all_trades_table)

        self.details_tabs.addTab(tab3_widget, "Running Info")

        splitter.addWidget(self.details_group)

        # Set initial splitter sizes (50% for left, 50% for right)
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.current_holdings = []  # Store current holdings
        self.past_holdings = []     # Store past holdings

    def _customize_table(self, table):
        """
        Apply common customizations to the tables.
        """
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
            }
            QTableWidget::item {
                border-bottom: 1px solid #dcdcdc;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff; /* Highlight entire row */
                color: #000000;
            }
        """)
        table.setSelectionBehavior(table.SelectRows)  # Highlight entire row on selection
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)
        header = table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: 1px solid #dcdcdc;
                padding: 5px;
            }
        """)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(QHeaderView.Stretch)  # Make all columns expand equally
        table.verticalHeader().setDefaultSectionSize(35)
        table.verticalHeader().setVisible(False)

        # Apply delegate to the correct columns
        if table == self.current_holdings_table:
            table.setItemDelegateForColumn(4, ProfitLossDelegate())  # Unrealized Profit column
        elif table == self.past_holdings_table:
            table.setItemDelegateForColumn(4, ProfitLossDelegate())  # Realized Profit column

    def _customize_trades_table(self, table):
        """
        Apply customizations specific to trades tables.
        """
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
            }
            QTableWidget::item {
                border-bottom: 1px solid #dcdcdc;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: #000000;
            }
        """)
        table.setSelectionBehavior(table.SelectRows)
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)
        header = table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: 1px solid #dcdcdc;
                padding: 5px;
            }
        """)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setDefaultSectionSize(30)
        table.verticalHeader().setVisible(False)
        table.setSortingEnabled(True)

    def set_holdings(self, current_holdings: List[Holding], past_holdings: List[Holding]):
        """
        Populate the tables with current and past holdings data.
        :param current_holdings: List of current holdings.
        :param past_holdings: List of past holdings.
        """
        self.current_holdings = current_holdings  # Store current holdings
        self.past_holdings = past_holdings        # Store past holdings

        self._populate_table(self.current_holdings_table, current_holdings, "current")
        self._populate_table(self.past_holdings_table, past_holdings, "past")

        # Automatically select the first row in the current holdings table
        if len(current_holdings) > 0:
            self.current_holdings_table.selectRow(0)
            self.display_details(0, 0, "current")

    def _populate_table(self, table, holdings: List[Holding], table_type: str):
        """
        Populate a given table with holdings data.
        """
        table.setRowCount(len(holdings))
        for row, holding in enumerate(holdings):
            if table_type == "current":
                # Populate Current Holdings Table
                item = QTableWidgetItem(holding.symbol)
                item.setData(Qt.UserRole, holding)  # Store the holding object
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(str(abs(holding.quantity))))
                table.setItem(row, 2, QTableWidgetItem(str(round(holding.buy_average, 2))))
                table.setItem(row, 3, QTableWidgetItem(str(round(holding.investment, 2))))

                # Unrealized Profit with numeric data for sorting and text color
                unrealized_profit_item = QTableWidgetItem()
                unrealized_profit_item.setData(Qt.DisplayRole, round(holding.unrealized_profit, 2))
                color = QColor(0, 128, 0) if holding.unrealized_profit >= 0 else QColor(255, 0, 0)
                unrealized_profit_item.setForeground(QBrush(color))
                table.setItem(row, 4, unrealized_profit_item)

            elif table_type == "past":
                # Populate Past Holdings Table
                item = QTableWidgetItem(holding.symbol)
                item.setData(Qt.UserRole, holding)  # Store the holding object
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(str(round(holding.dividend_income, 2))))
                table.setItem(row, 2, QTableWidgetItem(str(sum(1 for profit in holding.realized_profit_history if profit[1] > 0))))
                table.setItem(row, 3, QTableWidgetItem(str(sum(1 for profit in holding.realized_profit_history if profit[1] <= 0))))

                # Realized Profit with numeric data for sorting and text color
                realized_profit_item = QTableWidgetItem()
                realized_profit_item.setData(Qt.DisplayRole, round(holding.realized_profit, 2))
                color = QColor(0, 128, 0) if holding.realized_profit >= 0 else QColor(255, 0, 0)
                realized_profit_item.setForeground(QBrush(color))
                table.setItem(row, 4, realized_profit_item)

    def display_details(self, row, column, table_type):
        """
        Display details of the selected holding in the right pane.
        :param row: Row index of the selected holding.
        :param column: Column index of the selected holding.
        :param table_type: Type of table ("current" or "past").
        """
        # Fetch the table based on the type
        table = self.current_holdings_table if table_type == "current" else self.past_holdings_table

        # Retrieve the holding object from the selected row using Qt.UserRole
        holding: Holding = table.item(row, 0).data(Qt.UserRole)  # Type hint added

        # Update the description pane with the selected holding's details
        self.symbol_label.setText(holding.symbol)
        self.realized_profit_value.setText(f"{holding.realized_profit:,.2f}")
        self.realized_profit_value.setStyleSheet(f"""
            QLabel {{
                font-size: 40px;
                font-weight: bold;
                color: {"green" if holding.realized_profit > 0 else "red"};
            }}
        """)

        self.unrealized_profit_value.setText(f"{holding.unrealized_profit:,.2f}")
        self.unrealized_profit_value.setStyleSheet(f"""
            QLabel {{
                font-size: 40px;
                font-weight: bold;
                color: {"green" if holding.unrealized_profit > 0 else "red"};
            }}
        """)

        self.invested_amount_value.setText(f"{holding.investment:,.2f}")
        self.invested_amount_value.setStyleSheet("""
            QLabel {
                font-size: 40px;
                font-weight: bold;
                color: #333;
            }
        """)

        # Update other details
        details = {
            "Industry Type": holding.stock_info.industry,
            "Sector Type": holding.stock_info.sector,
            "Market Cap": holding.stock_info.market_cap,
            "Risk-Free Return": round(holding.risk_free_return_trend[-1][1], 2),
            "Index Returns": round(holding.nifty50_return_trend[-1][1], 2),
            "Total Investment": f"{holding.investment:,.2f}"
        }
        for key, value in details.items():
            if key in self.details_widgets:
                self.details_widgets[key].setText(str(value))

        # Update the price bar with actual data from the holding variable
        self.price_bar_widget.set_prices(
            high_52_week = holding.stock_info.fifty_two_week_high,
            low_52_week = holding.stock_info.fifty_two_week_low,
            current_price = holding.current_price,
            buy_average = holding.buy_average,
            trade_prices = holding.trades
        )

        self.profit_bar_chart.update_data(holding.realized_profit_history)

        # Update Tab 2 with StockInfo details
        stock_info = holding.stock_info
        for attr, widget in self.stock_info_widgets.items():
            value = getattr(stock_info, attr, "N/A")
            widget.setText(str(value))

        # Update Tab 3 with Running Info details
        self._update_running_info_tab(holding)

    def _add_stock_info_row(self, layout, attr):
        """
        Helper method to add a row for a StockInfo attribute.
        """
        label = QLabel(attr.replace("_", " ").title() + ":")
        label.setStyleSheet("font-weight: bold; color: #333;")
        value_label = QLabel()
        layout.addRow(label, value_label)
        self.stock_info_widgets[attr] = value_label

    def _update_running_info_tab(self, holding):
        """
        Update the Running Info tab with the selected holding's running information.
        """
        # Update running LTCG and STCG values
        self.running_ltcg_value.setText(f"{holding.running_ltcg:,.2f}")
        self.running_ltcg_value.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {"green" if holding.running_ltcg > 0 else "red" if holding.running_ltcg < 0 else "#333"};
            }}
        """)

        self.running_stcg_value.setText(f"{holding.running_stcg:,.2f}")
        self.running_stcg_value.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {"green" if holding.running_stcg > 0 else "red" if holding.running_stcg < 0 else "#333"};
            }}
        """)

        # Populate running trades table
        self._populate_trades_table(self.running_trades_table, holding.running_trades, include_remarks=False, current_price=holding.current_price)

        # Populate all trades table
        self._populate_trades_table(self.all_trades_table, holding.trades, include_remarks=True)

    def _populate_trades_table(self, table, trades, include_remarks=True, current_price=None):
        """
        Populate a trades table with trade data.
        """
        # Sort trades by timestamp in descending order (latest first)
        sorted_trades = sorted(trades, key=lambda trade: trade.timestamp, reverse=True)
        
        table.setRowCount(len(sorted_trades))
        for row, trade in enumerate(sorted_trades):
            table.setItem(row, 0, QTableWidgetItem(str(trade.order_id)))
            table.setItem(row, 1, QTableWidgetItem(trade.symbol))
            
            # Color code quantity based on buy/sell
            quantity_item = QTableWidgetItem(str(trade.quantity))
            if trade.typ.upper() == "BUY":
                quantity_item.setForeground(QBrush(QColor(0, 128, 0)))  # Green for buy
            elif trade.typ.upper() == "SELL":
                quantity_item.setForeground(QBrush(QColor(255, 0, 0)))  # Red for sell
            table.setItem(row, 2, quantity_item)
            
            table.setItem(row, 3, QTableWidgetItem(f"{trade.price:.2f}"))
            table.setItem(row, 4, QTableWidgetItem(trade.typ.upper()))
            table.setItem(row, 5, QTableWidgetItem(trade.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            
            # Add current profit column for running trades (when current_price is provided)
            if current_price is not None:
                if trade.typ.upper() == "BUY":
                    current_profit = (current_price - trade.price) * abs(trade.quantity)
                else:  # SELL
                    current_profit = (trade.price - current_price) * abs(trade.quantity)
                
                profit_item = QTableWidgetItem(f"{current_profit:.2f}")
                color = QColor(0, 128, 0) if current_profit >= 0 else QColor(255, 0, 0)
                profit_item.setForeground(QBrush(color))
                table.setItem(row, 6, profit_item)
                
                # Shift remarks column if needed
                if include_remarks:
                    table.setItem(row, 7, QTableWidgetItem(trade.remarks or ""))
            elif include_remarks:
                table.setItem(row, 6, QTableWidgetItem(trade.remarks or ""))
