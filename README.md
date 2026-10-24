# Raksha SOC Dashboard

## Overview

Raksha SOC Dashboard is a web-based Security Operations Center (SOC) dashboard designed to display and manage security events. It provides an interface for viewing security alerts, searching and filtering events, viewing event details, and updating event statuses.

## Features

- **Security Event Dashboard:** View security events in a centralized interface.
- **Event Details:** Open an event to view its details.
- **Search:** Search for security events.
- **Filtering:** Filter events based on available criteria.
- **Status Management:** Update the status of security events.
- **Backend API:** Use a Flask-based backend to handle event requests.
- **Data Persistence:** Store event data using SQLite.
- **Machine Learning Components:** Includes a machine-learning-related project component.

## Technology Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- Flask
- Flask-CORS
- SQLite

### Machine Learning
- Python
- scikit-learn
- joblib
- pandas

## Project Structure

```text
raksha-soc-dashboard/
├── README.md
├── .gitignore
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── ml/
```

## Prerequisites

Install the following before running the project:

- Python
- Node.js and npm
- Visual Studio Code (recommended)

## Getting Started

### 1. Start the Backend

Open a terminal in Visual Studio Code.

Navigate to the backend folder:

```bash
cd backend
```

Create and activate a Python virtual environment if you have not already created one.

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask application:

```bash
python app.py
```

The backend should be available at:

`http://127.0.0.1:5000`

### 2. Start the Frontend

Open a **second terminal** in Visual Studio Code.

Navigate to the frontend folder from the project root:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in the terminal. It is typically:

`http://localhost:5173`

Keep both terminals running while using the dashboard.

## Usage

1. Start the backend and frontend.
2. Open the dashboard in your browser.
3. View the security events displayed on the dashboard.
4. Use the search and filter controls to find events.
5. Open an event to inspect its details.
6. Update an event's status using the available controls.

## API

The backend provides API functionality for managing security events.

Known endpoints include:

- `GET /events` — Retrieve security events.
- `POST /events` — Submit a security event.

The exact request fields and response formats depend on the implementation in `backend/app.py`.

## Security and Configuration

- Do not commit passwords, API keys, access tokens, or other secrets.
- Keep local environment files and generated database files out of version control.
- Use the root `.gitignore` file to exclude local and generated files.

## Future Improvements

Potential improvements include:

- More advanced event analytics and visualizations.
- Improved alert classification and prioritization.
- Additional automated tests.
- More detailed documentation of API request and response formats.

## License

This project was created for educational and assignment purposes. Add a license if one is required for your intended use.
