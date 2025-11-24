from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from config import Config
from utils.option_chain import OptionChainManager
from utils.openalgo_client import ExtendedOpenAlgoAPI
from utils.websocket_manager import ProfessionalWebSocketManager
import json
import time
import threading
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reduce verbosity of third-party loggers
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

app = Flask(__name__)
app.config.from_object(Config)

# Log config to verify loading
logger.info(f"Config loaded: HOST={app.config.get('OPENALGO_HOST')}, WS={app.config.get('OPENALGO_WS_URL')}")
logger.info(f"API Key present: {bool(app.config.get('OPENALGO_API_KEY'))}")

# Global instances
active_managers = {}
websocket_managers = {}
shared_websocket_manager = None

def get_api_client():
    """Create OpenAlgo API client from config"""
    return ExtendedOpenAlgoAPI(
        api_key=app.config['OPENALGO_API_KEY'],
        host=app.config['OPENALGO_HOST']
    )

def get_or_create_websocket_manager(underlying):
    """Get or create a WebSocket manager for the underlying"""
    global shared_websocket_manager
    
    # Use shared manager if available and active
    if shared_websocket_manager and shared_websocket_manager.active:
        return shared_websocket_manager
        
    # Create new manager
    ws_manager = ProfessionalWebSocketManager()
    ws_manager.connect(
        ws_url=app.config['OPENALGO_WS_URL'],
        api_key=app.config['OPENALGO_API_KEY']
    )
    
    # Wait for connection
    time.sleep(1)
    
    if ws_manager.active:
        shared_websocket_manager = ws_manager
        return ws_manager
    return None

@app.route('/')
def index():
    return redirect('/trading/option-chain')

@app.route('/trading/option-chain')
def option_chain():
    underlying = request.args.get('underlying', 'NIFTY')
    expiry = request.args.get('expiry')
    
    try:
        client = get_api_client()
        
        # Get expiry if not provided
        if not expiry:
            exchange = 'BFO' if underlying == 'SENSEX' else 'NFO'
            expiry_response = client.expiry(
                symbol=underlying,
                exchange=exchange,
                instrumenttype='options'
            )
            
            if expiry_response.get('status') == 'success':
                expiries = expiry_response.get('data', [])
                if expiries:
                    expiry = expiries[0]
        
        # Initialize option chain manager
        manager_key = f"{underlying}_{expiry}"
        
        if manager_key in active_managers:
            logger.debug(f"Reusing active manager for {manager_key}")
            manager = active_managers[manager_key]
        else:
            logger.info(f"Creating new manager for {manager_key}")
            manager = OptionChainManager(underlying, expiry)
            manager.initialize(client)

        # Get option chain data
        chain_data = manager.get_option_chain()
        logger.debug(f"Initial chain data type: {type(chain_data)}")
        logger.debug(f"Initial chain data bool: {bool(chain_data)}")
        logger.debug(f"Initial chain data keys: {chain_data.keys() if isinstance(chain_data, dict) else 'Not a dict'}")
        logger.debug(f"Initial chain data options count: {len(chain_data.get('options', [])) if isinstance(chain_data, dict) else 'N/A'}")
        
        return render_template('option_chain.html',
                             chain_data=chain_data,
                             underlying=underlying,
                             expiry=expiry,
                             available_expiries=expiries if 'expiries' in locals() else [])
                             
    except Exception as e:
        logger.error(f"Error loading option chain: {e}")
        return render_template('option_chain.html',
                             error=f"Error loading option chain: {str(e)}",
                             underlying=underlying)

@app.route('/trading/api/option-chain/expiry/<underlying>')
def get_expiry_dates(underlying):
    try:
        client = get_api_client()
        exchange = 'BFO' if underlying == 'SENSEX' else 'NFO'
        
        logger.debug(f"Fetching expiry for {underlying} ({exchange})")
        expiry_response = client.expiry(
            symbol=underlying,
            exchange=exchange,
            instrumenttype='options'
        )
        logger.debug(f"Expiry response for {underlying}: {expiry_response}")
        
        return jsonify(expiry_response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/trading/api/option-chain/stream/<underlying>')
def option_chain_stream(underlying):
    expiry = request.args.get('expiry')
    
    def generate():
        manager_key = f"{underlying}_{expiry}"
        
        # Get or create manager
        if manager_key in active_managers:
            manager = active_managers[manager_key]
        else:
            client = get_api_client()
            ws_manager = get_or_create_websocket_manager(underlying)
            
            manager = OptionChainManager(underlying, expiry, websocket_manager=ws_manager)
            manager.initialize(client)
            manager.start_monitoring()
            active_managers[manager_key] = manager
        
        while True:
            try:
                chain_data = manager.get_option_chain()
                yield f"data: {json.dumps(chain_data)}\n\n"
                time.sleep(1)
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
                
    return Response(generate(), mimetype='text/event-stream')

# Session management routes (mocked/simplified)
@app.route('/trading/api/option-chain-session/create', methods=['POST'])
def create_session():
    data = request.json
    underlying = data.get('underlying')
    expiry = data.get('expiry')
    
    # Ensure manager exists
    manager_key = f"{underlying}_{expiry}"
    if manager_key not in active_managers:
        client = get_api_client()
        ws_manager = get_or_create_websocket_manager(underlying)
        
        manager = OptionChainManager(underlying, expiry, websocket_manager=ws_manager)
        manager.initialize(client)
        manager.start_monitoring()
        active_managers[manager_key] = manager
    
    return jsonify({'status': 'success', 'session_id': 'mock-session', 'subscribed_symbols': 0})

@app.route('/trading/api/option-chain-session/heartbeat', methods=['POST'])
def session_heartbeat():
    return jsonify({'status': 'success'})

@app.route('/trading/api/option-chain-session/destroy', methods=['POST'])
def destroy_session():
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=False, port=5800)
