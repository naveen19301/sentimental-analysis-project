# Sentiment Analysis Project (Zoho Desk + Excel)

Modular Python tool for fetching Zoho Desk ticket threads and performing rule-based sentiment analysis.

## Features
- Fetches inbound and outbound threads from Zoho Desk API.
- Advanced Rule-Based Sentiment Analysis.
- Processes local Excel files (`.xlsx`).
- Secure credential management via `config.json`.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Credentials**:
   Edit `config.json` with your Zoho API details:
   - `CLIENT_ID`
   - `CLIENT_SECRET`
   - `REFRESH_TOKEN`
   - `ORG_ID`

3. **Prepare Input File**:
   Place your input Excel file (default: `tickets.xlsx`) in the project directory. Ensure it has a `Ticket ID` (or `TicketNumber`) column.

4. **Run the Script**:
   ```bash
   python main.py
   ```

## Project Structure
- `main.py`: Entry point, handles Excel reading/writing.
- `zoho_client.py`: Handles Zoho Desk API authentication and data fetching.
- `sentiment_engine.py`: Contains the logic for sentiment and category classification.
- `utils.py`: Text cleaning and helper functions.
- `config.json`: Store your sensitive API keys here (ignored by git).
