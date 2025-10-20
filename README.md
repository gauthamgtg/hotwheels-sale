# Hot Wheels Sale Tracker

A Streamlit application for tracking Hot Wheels sales with user authentication.

## Features

- 🔐 Password-based authentication
- 📊 Personalized sales data display
- 📈 Summary statistics
- 📱 Responsive design
- 🔗 Google Sheets CSV integration (no API setup required!)

## Setup Instructions

### 1. Google Sheets Setup

1. Make sure your Google Sheets are publicly accessible for CSV export
2. The app uses these specific sheet URLs:
   - Sales Data
   - Users Data

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### 3. Usage

1. Open the application in your browser
2. Enter your unique password in the sidebar
3. View your personalized sales data
4. Use the "Refresh Data" button to get the latest data from Google Sheets
