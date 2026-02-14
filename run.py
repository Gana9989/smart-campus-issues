"""Run the Smart Campus Issue Reporting System."""
from app import app

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
