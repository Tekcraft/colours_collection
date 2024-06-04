import sys
import requests
import pandas as pd
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox

def fetch_card_details(card_number):
    url = f'https://api.swu-db.com/cards/sor/{card_number}'
    response = requests.get(url)
    try:
        card_data = response.json()
        return card_data
    except json.JSONDecodeError:
        print(f"Error decoding JSON from API response for card number {card_number}.")
        return {}

def format_card_number(card_number):
    """Ensure that the card number has three digits with leading zeros if necessary."""
    card_number_str = str(card_number)
    if len(card_number_str) == 1:
        return '00' + card_number_str
    elif len(card_number_str) == 2:
        return '0' + card_number_str
    else:
        return card_number_str

def integrate_aspects(collection_df):
    # Format the card numbers in the CSV to have three digits
    collection_df['CardNumber'] = collection_df['CardNumber'].apply(format_card_number)

    # Create a column for Aspects or Traits
    collection_df['Aspects'] = None

    for index, row in collection_df.iterrows():
        card_number = row['CardNumber']
        card_data = fetch_card_details(card_number)
        
        if 'Aspects' in card_data:
            aspects = ", ".join(card_data['Aspects'])
            collection_df.at[index, 'Aspects'] = aspects
        elif 'Traits' in card_data:
            traits = ", ".join(card_data['Traits'])
            collection_df.at[index, 'Aspects'] = traits
        else:
            print(f"Warning: card number {card_number} has neither Aspects nor Traits in the API data.")
    
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
        
        self.btn_save_csv = QPushButton('Save Integrated CSV File')  # Cambiato qui
        self.btn_save_csv.clicked.connect(self.save_csv)  # Cambiato qui
        self.btn_save_csv.setVisible(False)  # Cambiato qui
        self.layout.addWidget(self.btn_save_csv)  # Cambiato qui
        
        self.setLayout(self.layout)
        
        self.collection_df = pd.DataFrame()

    def load_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select your collection CSV file", "", "CSV Files (*.csv)", options=options)
        if file_path:
            self.collection_df = pd.read_csv(file_path)
            QMessageBox.information(self, 'File Loaded', 'CSV File Loaded Successfully', QMessageBox.Ok)
            self.btn_save_csv.setVisible(True)  # Cambiato qui

    def save_csv(self):  # Cambiato qui
        if not self.collection_df.empty:
            integrated_collection = integrate_aspects(self.collection_df)
            
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(self, "Save the Integrated CSV File", "", "CSV Files (*.csv)", options=options)  # Cambiato qui
            if save_path:
                integrated_collection.to_csv(save_path, index=False)  # Cambiato qui
                QMessageBox.information(self, 'File Saved', 'Integrated CSV File Saved Successfully', QMessageBox.Ok)  # Cambiato qui
        else:
            QMessageBox.warning(self, 'No CSV Loaded', 'Please load a CSV file first.', QMessageBox.Ok)

def main():
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
