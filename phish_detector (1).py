import pandas as pd
import sqlite3
import re
import os
from datetime import datetime

# Machine Learning Imports
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# ==========================================
# 1. DATABASE INTEGRATION (SQLite)
# ==========================================
def init_db():
    """Initializes the SQLite database and creates the table."""
    conn = sqlite3.connect('phishing_analysis.db')
    cursor = conn.cursor()
    # Stores email details and SPECIFIC extracted features (like the URL)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            sender TEXT,
            extracted_url TEXT,    -- Requirement: Save actual feature for reference
            urgency_flag INTEGER,   -- Requirement: Save actual feature for reference
            prediction TEXT,        -- Requirement: Store analysis result
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn

# ==========================================
# 2. MACHINE LEARNING SYSTEM
# ==========================================
class PhishingDetector:
    def __init__(self):
        self.pipeline = None
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

    def preprocess_text(self, text):
        """Cleans text for the ML model."""
        if not isinstance(text, str): return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def train_model(self, file_path):
        """Trains the ML model using the Excel dataset."""
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found!")
            return False

        print(f"[*] Training model using {file_path}...")
        df = pd.read_excel(file_path)
        
        # Prepare data
        df['email_text'] = df['email_text'].apply(self.preprocess_text)
        X = df[['email_text', 'has_link', 'urgency_flag']]
        y = df['label'].map({'legitimate': 0, 'phishing': 1})

        # Define processing for Text vs Numeric columns
        preprocessor = ColumnTransformer(
            transformers=[
                ('text', self.vectorizer, 'email_text'),
                ('stats', 'passthrough', ['has_link', 'urgency_flag'])
            ])

        self.pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression())
        ])

        # Train and Validate
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.pipeline.fit(X_train, y_train)
        
        acc = accuracy_score(y_test, self.pipeline.predict(X_test))
        print(f"[+] Model Accuracy: {acc:.2%}")
        return True

    def analyze_email(self, text):
        """Extracts actual features and predicts phishing status."""
        
        # 1. Feature Extraction: Find actual URLs
        url_pattern = r'(https?://\S+|www\.\S+)'
        links_found = re.findall(url_pattern, text)
        # We save the first link found to the database for "future reference"
        actual_url_text = links_found[0] if links_found else "None"
        
        # 2. Feature Extraction: Check for Urgency keywords
        urgency_words = ['urgent', 'immediately', 'action', 'suspended', 'verify', 'password']
        urgency_flag = 1 if any(word in text.lower() for word in urgency_words) else 0
        
        # 3. ML Prediction
        # The ML model needs a number (1 or 0) for the 'has_link' column
        has_link_numeric = 1 if links_found else 0
        processed_text = self.preprocess_text(text)
        
        input_df = pd.DataFrame([[processed_text, has_link_numeric, urgency_flag]], 
                                 columns=['email_text', 'has_link', 'urgency_flag'])
        
        prediction_num = self.pipeline.predict(input_df)[0]
        result = "Phishing" if prediction_num == 1 else "Legitimate"
        
        return result, actual_url_text, urgency_flag

# ==========================================
# 3. COMMAND LINE INTERFACE (CLI)
# ==========================================
def main():
    db_conn = init_db()
    detector = PhishingDetector()
    
    # Train on startup using your dataset
    if not detector.train_model('phishing_dataset (1).xlsx'):
        return

    while True:
        print("\n" + "="*40)
        print("  PHISHING EMAIL DETECTION SYSTEM  ")
        print("="*40)
        print("1. Analyze New Email")
        print("2. View Scan History (Database Report)")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ")

        if choice == '1':
            print("\n--- New Email Scan ---")
            subj = input("Subject: ")
            sndr = input("Sender: ")
            print("Enter/Paste Email Body (Press Enter when done):")
            body = input("> ")

            # Run Analysis
            res, extracted_url, urg_feat = detector.analyze_email(body)
            
            print(f"\n[!] ANALYSIS COMPLETE")
            print(f"Prediction: {res.upper()}")
            print(f"Extracted URL: {extracted_url}")
            print(f"Urgency Detected: {'Yes' if urg_feat == 1 else 'No'}")

            # Save to Database (Fulfills all Storage requirements)
            cursor = db_conn.cursor()
            cursor.execute('''
                INSERT INTO scan_history (subject, sender, extracted_url, urgency_flag, prediction, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (subj, sndr, extracted_url, urg_feat, res, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            db_conn.commit()
            print("\n[v] Data logged to SQLite database.")

        elif choice == '2':
            print("\n" + "-"*60)
            print("         DATABASE LOGS / HISTORY REPORT")
            print("-"*60)
            history_df = pd.read_sql_query("SELECT * FROM scan_history", db_conn)
            
            if history_df.empty:
                print("No records found.")
            else:
                # Display the data
                print(history_df.to_string(index=False))
                
                # Tracking statistics
                total = len(history_df)
                phish = len(history_df[history_df['prediction'] == 'Phishing'])
                print(f"\n[SUMMARY] Scans: {total} | Threats Tracked: {phish} | Safe: {total-phish}")

        elif choice == '3':
            print("System shutting down...")
            db_conn.close()
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main()