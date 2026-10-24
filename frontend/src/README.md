# Raksha SOC — Security Event Monitoring Dashboard

## Project Overview
Raksha SOC is a full-stack Security Operations Center dashboard that helps monitor security events, classify suspicious activity using machine learning, and track event status.

## Technologies Used
- **Frontend:** React, Vite, CSS
- **Backend:** Python, Flask, Flask-CORS
- **Machine Learning:** Scikit-learn, TF-IDF, Logistic Regression
- **Database:** SQLite
- **Visualization:** Recharts

## Features
- Security event monitoring dashboard
- ML-based classification into Benign, Suspicious, and Malicious
- Confidence score for predictions
- Search and filter security events
- View detailed event information
- Update event status: New, In Progress, or Resolved
- Dashboard statistics and risk distribution chart
- REST API with input validation and API-key protection for write operations
- SQLite persistence

## Project Structure
```text
raksha-soc-dashboard/
├── backend/
│   └── app.py
├── frontend/
│   └── src/
├── ml/
│   ├── training_data.csv
│   └── train_model.py
├── .venv/
└── README.md
```

## Setup and Run

### 1. Backend
Activate your Python virtual environment and install the backend dependencies.

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the packages listed in your backend requirements file, if available.

Start the Flask backend:

```powershell
python backend/app.py
```

Backend URL: `http://127.0.0.1:5000`

### 2. Frontend
Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/events` | Create and classify an event |
| GET | `/events` | List and filter events |
| GET | `/events/<id>` | Retrieve one event |
| PATCH | `/events/<id>` | Update an event's status |
| GET | `/stats` | Retrieve dashboard statistics |

Write operations require the `X-API-Key` header.

## Machine Learning
The model is trained on labeled security log examples and uses TF-IDF features with Logistic Regression to classify logs into Benign, Suspicious, or Malicious categories.

This is a lightweight demonstration model; predictions depend on the training data and should not be treated as production-grade security detection.

## Testing
- Verified backend health endpoint
- Tested event creation
- Tested event viewing and status updates
- Tested dashboard search and filters

## Future Improvements
- Add more diverse labeled security logs
- Improve model accuracy with a larger dataset
- Add user authentication and role-based access
- Add automated tests and deployment support
