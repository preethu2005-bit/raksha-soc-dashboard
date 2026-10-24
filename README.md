# Raksha SOC Dashboard

## Overview

Raksha SOC Dashboard is a web-based Security Operations Center (SOC) application for viewing, filtering, and managing security events. It uses a Flask REST API, a React frontend, SQLite for data persistence, and a machine-learning pipeline to classify security logs as Benign, Suspicious, or Malicious.

## Features

- View security events and event details.
- Search, filter, and sort events.
- Filter by risk level, source, and status.
- View event statistics and risk distribution.
- Update event statuses.
- Store events in SQLite.
- Classify log messages using TF-IDF and Logistic Regression.
- Protect write operations with API-key authentication.

## Technology Stack

**Frontend:** React, Vite, JavaScript, CSS

**Backend:** Python, Flask, Flask-CORS, SQLite

**Machine learning:** pandas, scikit-learn, joblib

## Project Structure

```text
raksha-soc-dashboard/
├── README.md
├── .gitignore
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── model.joblib
├── frontend/
│   ├── src/
│   └── package.json
└── ml/
    ├── train_model.py
    └── training_data.csv
```

## Prerequisites

- Python
- Node.js and npm
- Visual Studio Code (recommended)

## Getting Started

### 1. Set up and run the backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set the API key for the current PowerShell session:

```powershell
$env:RAKSHA_API_KEY = "dev-secret-change-me"
```

Start the Flask server:

```powershell
python app.py
```

The backend runs at `http://127.0.0.1:5000`.

Keep this terminal open. The API key above is for local development only; use a strong private value in other environments.

### 2. Set up and run the frontend

Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL shown by Vite in the terminal, commonly `http://localhost:5173`.

Keep both servers running while using the dashboard.

### 3. Train the machine-learning model

From a terminal at the project root, activate the Python environment used for the backend and run:

```powershell
python ml\train_model.py
```

The training script reads `ml/training_data.csv`, splits the labeled data into training and test sets, trains a TF-IDF and Logistic Regression pipeline, prints evaluation metrics, and saves the final model to `backend/model.joblib`.

## Machine-Learning Evaluation

Evaluation from the current training run:

| Metric | Result |
|---|---:|
| Labeled examples | 36 |
| Training examples | 28 |
| Testing examples | 8 |
| Accuracy | 62.5% |
| Macro F1-score | 0.5833 |
| Weighted F1-score | 0.5938 |

The evaluation uses a held-out test set of eight examples. These metrics are an initial baseline and may vary if the dataset or training configuration changes. A larger, representative labeled dataset is recommended for more reliable performance estimates.

## API Endpoints

The Flask backend provides the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/events` | Retrieve events; supports filters and pagination implemented by the backend |
| POST | `/events` | Create or submit security events |
| GET | `/events/<id>` | Retrieve a specific event |
| PATCH | `/events/<id>` | Update an event's status |
| GET | `/stats` | Retrieve event statistics |

The events endpoint supports filters such as risk level, status, source, and date range, as implemented by the backend.

### API-key authentication

Write operations require the `X-API-Key` request header. For local development, the key is configured using the `RAKSHA_API_KEY` environment variable.

Example PowerShell request to update an event:

```powershell
$headers = @{ "X-API-Key" = "dev-secret-change-me" }
$body = @{ status = "Reviewed" } | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/events/1" `
  -Method Patch `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Use a valid status supported by the application. Do not commit real API keys or other secrets to version control.

## Usage

1. Start the Flask backend.
2. Start the React frontend.
3. Open the frontend URL shown by Vite.
4. Review events and their risk levels.
5. Search, filter, and sort the event list.
6. Open an event to inspect its details.
7. Update its status as needed.

## Security and Generated Files

- Do not commit passwords, private API keys, or access tokens.
- Keep virtual environments, `node_modules`, build output, and local database files out of version control when appropriate.
- Review `.gitignore` before pushing the project to GitHub.

## Future Improvements

- Expand the labeled training dataset.
- Improve and further validate classification performance.
- Add automated API and frontend tests.
- Document complete request and response schemas.
- Add deployment and production configuration instructions.

## License

Created for educational and assignment purposes. Add a license if required by your intended use.
