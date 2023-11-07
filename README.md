# Faculty Examination Schedule Explorer

## The Challenge
Effective communication between faculty and the student body is crucial for fostering a thriving educational environment. One critical area where communication is of utmost importance is the dissemination of examination schedules. Students require a reliable platform to receive updates about their schedules to prevent missing exams.

## Our Approach
We've developed an interactive service using Flask to address this challenge. This platform empowers faculty members to easily communicate examination schedules with their students, ensuring seamless information flow.

## Getting Started
1. Clone this repository.
2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a secret token:
    ```python
    import secrets
    print(secrets.token_hex(32))
    ```
5. Export the secret token:
    - On Linux systems:
        ```bash
        export SECRET_KEY=paste-your-secret-key-here
        ```
    - On Windows (or if the previous command doesn't work):
        - Create a `.env` file in the root directory of the project and paste the following lines:
        ```bash
        SECRET_KEY=paste-your-secret-key-here
        ```
6. In your terminal, run:
    ```bash
    flask run
    ```
7. The app will be hosted on `127.0.0.1:5000` if it's available.

## Usage
To edit the Timetable details, modify the [database.db](instance/database.db) file to your liking. Make sure to keep the same format.

## How to Contribute
Open a pull request with your suggested changes, and a maintainer will review and take further actions. You can reach the creator [here](https://www.linkedin.com/in/ali-osman-ml/).
