import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit, QLabel, QDateEdit, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt5.QtCore import QDate
import sqlite3
import datetime

class ContractManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check_reminders()  # Check reminders on startup

    def initUI(self):
        self.setWindowTitle('Contract Management and Reminder System')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.name_label = QLabel('Contract Name:')
        layout.addWidget(self.name_label)
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.description_label = QLabel('Contract Description:')
        layout.addWidget(self.description_label)
        self.description_input = QTextEdit()
        layout.addWidget(self.description_input)

        self.date_label = QLabel('End Date:')
        layout.addWidget(self.date_label)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)

        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton('Add Contract')
        self.add_button.clicked.connect(self.add_contract)
        button_layout.addWidget(self.add_button)

        self.reminder_button = QPushButton('Check Reminders')
        self.reminder_button.clicked.connect(self.check_reminders)
        button_layout.addWidget(self.reminder_button)
        
        layout.addLayout(button_layout)

        self.contract_table = QTableWidget()
        self.contract_table.setColumnCount(6)
        self.contract_table.setHorizontalHeaderLabels(['ID', 'Name', 'Description', 'End Date', 'Edit', 'Delete'])
        layout.addWidget(self.contract_table)

        self.load_contracts()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_contract(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        end_date = self.date_input.date().toString('yyyy-MM-dd')

        conn = sqlite3.connect('contracts.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO contracts (name, description, end_date) VALUES (?, ?, ?)', (name, description, end_date))
        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Success', 'Contract added successfully!')
        self.name_input.clear()
        self.description_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.load_contracts()

    def check_reminders(self):
        today = datetime.date.today()
        conn = sqlite3.connect('contracts.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, end_date FROM contracts WHERE end_date <= ?', (today,))
        reminders = cursor.fetchall()
        conn.close()

        if reminders:
            reminder_text = '\n'.join([f'Contract: {name}, End Date: {end_date}' for name, end_date in reminders])
            QMessageBox.warning(self, 'Reminders', reminder_text)
        else:
            QMessageBox.information(self, 'No Reminders', 'There are no contracts ending today or earlier.')

    def load_contracts(self):
        conn = sqlite3.connect('contracts.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contracts')
        contracts = cursor.fetchall()
        conn.close()

        self.contract_table.setRowCount(0)
        for row_number, row_data in enumerate(contracts):
            self.contract_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.contract_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
            edit_button = QPushButton('Edit')
            edit_button.clicked.connect(lambda ch, row_number=row_number: self.edit_contract(row_number))
            self.contract_table.setCellWidget(row_number, 4, edit_button)
            delete_button = QPushButton('Delete')
            delete_button.clicked.connect(lambda ch, row_number=row_number: self.delete_contract(row_number))
            self.contract_table.setCellWidget(row_number, 5, delete_button)

    def edit_contract(self, row_number):
        contract_id = self.contract_table.item(row_number, 0).text()
        name = self.contract_table.item(row_number, 1).text()
        description = self.contract_table.item(row_number, 2).text()
        end_date = self.contract_table.item(row_number, 3).text()

        self.name_input.setText(name)
        self.description_input.setText(description)
        self.date_input.setDate(QDate.fromString(end_date, 'yyyy-MM-dd'))
        self.add_button.setText('Update Contract')
        self.add_button.clicked.disconnect()
        self.add_button.clicked.connect(lambda: self.update_contract(contract_id))

    def update_contract(self, contract_id):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        end_date = self.date_input.date().toString('yyyy-MM-dd')

        conn = sqlite3.connect('contracts.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE contracts SET name = ?, description = ?, end_date = ? WHERE id = ?', (name, description, end_date, contract_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Success', 'Contract updated successfully!')
        self.name_input.clear()
        self.description_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.add_button.setText('Add Contract')
        self.add_button.clicked.disconnect()
        self.add_button.clicked.connect(self.add_contract)
        self.load_contracts()

    def delete_contract(self, row_number):
        contract_id = self.contract_table.item(row_number, 0).text()

        conn = sqlite3.connect('contracts.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Success', 'Contract deleted successfully!')
        self.load_contracts()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ContractManager()
    ex.show()
    sys.exit(app.exec_())
