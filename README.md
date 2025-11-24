# OpenAlgo Option Chain

A standalone Flask application for visualizing real-time option chain data built on top of OpenAlgo API and WebSockets.

![Option Chain Screenshot](https://github.com/marketcalls/option-chain/blob/master/static/images/Chain.png?raw=true)

## Features

- **Real-time Data**: Live option chain updates via Server-Sent Events (SSE).
- **Market Depth**: View Bid/Ask quantities and spreads.
- **Dynamic Expiries**: Automatically fetches and caches expiry dates for NIFTY, BANKNIFTY, and SENSEX.
- **Calculated Metrics**: Real-time PCR (Put-Call Ratio) and Volume analysis.
- **Responsive UI**: Modern interface built with DaisyUI and Tailwind CSS.

## Prerequisites

- Python 3.10+
- OpenAlgo API Key (and running OpenAlgo instance)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/marketcalls/option-chain
    cd option-chain
    ```

2.  **Create a virtual environment**:
    
    **Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

    **macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install uv (recommended)**:
    ```bash
    pip install uv
    ```

3.  **Install dependencies**:
    **Method 1: Using uv (Recommended)**
    Dependencies will be automatically installed when running the app.

    **Method 2: Using requirements.txt**
    ```bash
    pip install -r requirements.txt
    ```

    **Method 3: Using pyproject.toml**
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

1.  **Start the application using uv**:
    ```bash
    uv run app.py
    ```

2.  **Or using standard python**:
    ```bash
    python app.py
    ```

3.  **Access the Option Chain**:
    Open your browser and navigate to `http://127.0.0.1:5800`.

## Project Structure

- `app.py`: Main Flask application entry point.
- `utils/`: Helper modules for API interaction, WebSocket management, and option chain logic.
- `templates/`: HTML templates (Jinja2).
- `static/`: Static assets (CSS, JS).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
