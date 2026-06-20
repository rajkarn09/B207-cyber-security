# PhishGuard — Phishing Email Detection System

**B207 Cyber Security | Gisma University of Applied Sciences**

A machine learning-based command-line tool that classifies emails as **Phishing** or **Legitimate** using Logistic Regression and TF-IDF text vectorization, with persistent SQLite storage of all analysis results.

---

## Project Structure

```
phishguard/
├── phish_detector.py       # Main application (ML + CLI + database)
├── phishing_dataset.xlsx   # Training dataset (Kaggle)
├── requirements.txt        # Python dependencies
├── setup.sh                # One-command setup script
├── model/
│   └── classifier.pkl      # Saved trained model (auto-generated)
├── db/
│   └── phishing_analysis.db  # SQLite database (auto-generated)
└── README.md
```

---

## Requirements

- Python 3.10 or higher
- The dataset file (`phishing_dataset.xlsx`) placed in the project root

---

## Quick Start (Recommended)

Run the one-command setup script. It installs all dependencies, trains the model, and initialises the database automatically.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/phishguard-b207.git
cd phishguard-b207

# 2. Make the setup script executable
chmod +x setup.sh

# 3. Run setup (pass your dataset file as an argument)
./setup.sh phishing_dataset.xlsx

# 4. Activate the virtual environment
source venv/bin/activate

# 5. Launch PhishGuard
python3 phish_detector.py
```

---

## Manual Setup (Alternative)

If you prefer not to use the setup script:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 phish_detector.py
```

The application will automatically train the model on first run if no saved model is found.

---

## Usage

When launched, PhishGuard presents a menu:

```
=============================================
   PHISHGUARD — EMAIL DETECTION SYSTEM
=============================================
  1. Analyse New Email
  2. View Detection History
  3. Retrain Model
  4. Exit
---------------------------------------------
Select an option (1-4):
```

### Option 1 — Analyse an Email

Enter the subject, sender, and body text of the email. The system will:
- Extract any URLs present
- Check for urgency keywords
- Run the ML classifier
- Display the verdict with confidence score
- Log the result to the database

**Example:**
```
Subject : Verify Your Account Immediately
Sender  : security@bank-alerts.com
Body    > Your account has been suspended. Click here to verify:
          http://phish-site.com/login

ANALYSIS RESULT
---------------------------------------------
  Verdict     : ⚠ PHISHING
  Confidence  : 98.4%
  URL Found   : http://phish-site.com/login
  Urgency     : YES — suspicious keywords detected
  [✓] Logged to database.
```

### Option 2 — View Detection History

Displays all previously scanned emails from the SQLite database, including a summary of total scans, threats detected, and threat rate.

### Option 3 — Retrain Model

Retrains the classifier from the dataset. Useful if you update the dataset with new records. You can specify a different dataset path when prompted.

### Option 4 — Exit

Closes the database connection and shuts down the application.

---

## How It Works

1. **Preprocessing** — Email text is lowercased and stripped of punctuation
2. **Feature Extraction** — TF-IDF vectorizer converts text to numerical features; `has_link` and `urgency_flag` are extracted as binary features
3. **Classification** — A Logistic Regression model (trained on 640 labelled emails) predicts phishing probability
4. **Storage** — Every scan is logged to `db/phishing_analysis.db` with metadata, extracted features, prediction, confidence, and timestamp

---

## Dataset

**Source:** [Phishing Email Dataset — Kaggle](https://www.kaggle.com/datasets/tommyf1/phishing-email-dataset)

- 800 labelled emails (414 phishing, 386 legitimate)
- Features used: `email_text`, `has_link`, `urgency_flag`
- 80/20 train-test split

---

## Model Performance

| Metric    | Legitimate | Phishing |
|-----------|-----------|---------|
| Precision | 1.00      | 1.00    |
| Recall    | 1.00      | 1.00    |
| F1-Score  | 1.00      | 1.00    |
| **Accuracy** | **100%** | |

---

## Dependencies

| Library | Version | Purpose |
|---|---|---|
| pandas | ≥2.0.0 | Data loading and manipulation |
| openpyxl | ≥3.1.0 | Reading Excel dataset |
| scikit-learn | ≥1.3.0 | TF-IDF, Logistic Regression, metrics |
| joblib | ≥1.3.0 | Saving and loading the trained model |

---

## Academic Notes

- This project was developed as an individual submission for B207 Cyber Security at Gisma University of Applied Sciences (Spring 2025)
- The use of external libraries is limited to those that support the implementation; no library that accomplishes the detection task directly was used
- All design decisions are documented in the accompanying report
