import sys
import requests
import pandas as pd
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox


def fetch_card_details(api_url):
    response = requests.get(api_url)
    return response.json()


def integrate_aspects(card_data, collection_df):
    aspects_dict = {card['CardNumber']: card['Aspects'] for card in card_data}
    collection_df['Aspects'] = collection_df['CardNumber'].map(aspects_dict)
    return collection_df


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Star Wars Collection Integrator')
        self.setGeometry(100, 100, 300, 100)
        
        self.layout = QVBoxLayout()
        
        self.btn_load_csv = QPushButton('Select Collection CSV File')
        self.btn_load_csv.clicked.connect(self.load_csv)
        self.layout.addWidget(self.btn_load_csv)
        
        self.btn_save_json = QPushButton('Save Integrated JSON File')
        self.btn_save_json.clicked.connect(self.save_json)
        self.layout.addWidget(self.btn_save_json)
        
        self.setLayout(self.layout)
        
        self.collection_df = pd.DataFrame()
        self.card_data = fetch_card_details('https://api.swu-db.com/cards/sor')

    def load_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select your collection CSV file", "", "CSV files (*.csv)", options=options)
        if file_path:
            self.collection_df = pd.read_csv(file_path)
            QMessageBox.information(self, 'File Loaded', 'CSV File Loaded Successfully', QMessageBox.Ok)

    def save_json(self):
        if not self.collection_df.empty:
            integrated_collection = integrate_aspects(self.card_data, self.collection_df)
            
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(self, "Save the integrated JSON file", "", "JSON files (*.json)", options=options)
            if save_path:
                integrated_collection.to_json(save_path, orient='records', indent=4)
                QMessageBox.information(self, 'File Saved', 'Integrated JSON File Saved Successfully', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'No CSV Loaded', 'Please load a CSV file first.', QMessageBox.Ok)


def main():
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()