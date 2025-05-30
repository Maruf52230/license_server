# License Key Manager

## Overview

The License Key Manager is a Python application that provides a simple interface for managing license keys using Firebase Firestore as the backend. This application allows users to create, check, and delete license keys through a RESTful API built with Flask.

## Features

- Create license keys with expiration dates.
- Check the validity of license keys.
- Deactivate (delete) license keys.

## Prerequisites

- Python 3.x
- A Firebase project with Firestore enabled
- Firebase Web API Key and Project ID

## Project Structure

```
license-key-manager/
├── src/
│   ├── app.py               # Main application file
│   ├── firebase_config.py    # Firebase configuration
│   └── utils.py             # Utility functions
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Setup

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Update the `firebase_config.py` file with your Firebase API key and project ID.

## Usage

To run the application, execute the following command:

```
python src/app.py
```

The server will start, and you can access the API at `http://localhost:5000`.

## API Endpoints

- **Create License Key**: `POST /create`
  - Request Body: `{ "expires_in_days": <number> }`
  - Response: `{ "license_key": "<key>", "expiresAt": "<expiration_date>" }`

- **Check License Key**: `GET /check/<license_key>`
  - Response: `{ "valid": <boolean>, "message": "<message>", "expiresAt": "<expiration_date>" }`

- **Delete License Key**: `DELETE /delete/<license_key>`
  - Response: `{ "success": <boolean>, "message": "<message>" }`

## Notes

- Ensure that your Firestore security rules allow access via your API key or implement authentication as needed.
- For production use, secure your API keys and set appropriate Firestore security rules.