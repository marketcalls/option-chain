# OpenAlgo Option Chain

A standalone Flask application for visualizing real-time option chain data with market depth, built on the OpenAlgo API.

## Features

- **Real-time Data**: Live option chain updates via Server-Sent Events (SSE).
- **Market Depth**: View Bid/Ask quantities and spreads.
- **Dynamic Expiries**: Automatically fetches and caches expiry dates for NIFTY, BANKNIFTY, and SENSEX.
- **Calculated Metrics**: Real-time PCR (Put-Call Ratio) and Volume analysis.
- **Responsive UI**: Modern interface built with DaisyUI and Tailwind CSS.

## Prerequisites

- Python 3.8+
- OpenAlgo API Key (and running OpenAlgo instance)

## Installation

1.  **Clone the repository** (or navigate to the directory):
    ```bash
    cd option-chain
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    **Method 1: Using requirements.txt**
    ```bash
    pip install -r requirements.txt
    ```

    **Method 2: Using pyproject.toml**
    ```bash
    pip install .
    ```

## Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Edit `.env` and configure your settings:
    ```ini
    SECRET_KEY=your_secret_key_here
    OPENALGO_API_KEY=your_openalgo_api_key
    OPENALGO_HOST=http://127.0.0.1:5000
    OPENALGO_WS_URL=ws://127.0.0.1:8765
    ```

## Usage

1.  **Start the application**:
    ```bash
    python app.py
    ```

2.  **Access the Option Chain**:
    Open your browser and navigate to `http://127.0.0.1:5800`.

## Project Structure

- `app.py`: Main Flask application entry point.
- `utils/`: Helper modules for API interaction, WebSocket management, and option chain logic.
- `templates/`: HTML templates (Jinja2).
- `static/`: Static assets (CSS, JS).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
