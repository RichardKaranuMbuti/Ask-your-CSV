# Ask-your-CSV

The CSV/Excel Chatbot is an AI-powered application that enables users to upload CSV and Excel files, ask questions related to the data in those files, and receive comprehensive responses, including results, graphs, charts, and summaries.

# How to Run

## Prerequisites

Before running the application, make sure you have the following installed:

- Python (version 3.6 or later)
- pip (Python package installer)

## Setting up the Environment

1. Clone the repository: `git clone https://github.com/your-username/csv-excel-chatbot.git`
2. Navigate to the project directory: `cd csv-excel-chatbot`
3. Create a virtual environment (optional but recommended): `python -m venv env`
   - Activate the virtual environment:
     - On Windows: `env\Scripts\activate`
     - On Unix or macOS: `source env/bin/activate`
4. Install the required packages: `pip install -r requirements.txt`

## Configuration

1. Create a `.env` file in the project root directory and add your API keys (if required).
2. Apply any necessary database migrations: `python manage.py migrate`

## Running the Application

1. Start the development server: `python manage.py runserver`
2. Open your web browser and navigate to `http://localhost:8000` to access the CSV/Excel Chatbot application.

## Usage

1. Upload CSV or Excel files by clicking the "Upload Files" button on the homepage.
2. Once files are uploaded, you can start asking questions related to the data in those files by typing your queries in the input field.
3. The chatbot will execute code to process the data, generate results, graphs, charts, and summaries based on your queries.
4. The responses will be displayed in the chat interface, including any generated visuals or summaries.

## Contributing

If you'd like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## License

This project is licensed under the [MIT License](LICENSE).
