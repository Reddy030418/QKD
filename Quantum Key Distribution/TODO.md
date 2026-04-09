# Tasks to Fix Dashboard Data Display Issue

## 1. Run Sample Data Script to Populate Database

The backend database needs sample QKD session data for the dashboard to display meaningful statistics.

Run the following script to populate the database with sample data:

```bash
cd "Quantum Key Distribution/backend"
python populate_sample_data_working.py
```

This will create 25 sample QKD sessions with realistic parameters, including status and security status.

## 2. Verify User Login and Token

Ensure you are logged in to the frontend application so that the authentication token is set.

- The token is stored in localStorage under the key `token`.
- The Dashboard component uses this token to fetch statistics from the backend.
- If not logged in, the dashboard will show a message: "Please log in to view dashboard statistics."

## 3. Verify API URL Configuration

Make sure the frontend environment variable `REACT_APP_API_URL` is set correctly to point to your backend API URL.

If not set, it defaults to `http://localhost:8000`.

## 4. Testing the Dashboard

- After running the sample data script and logging in, reload the dashboard page.
- The dashboard should display updated statistics and charts based on the sample data.

## 5. Optional Improvements

- You can improve the login flow or add UI feedback for token expiration or unauthorized access.
- Add more detailed error handling in the Dashboard component if needed.

---

If you need assistance with any of these steps or want me to help improve the login flow or error handling, please let me know.
