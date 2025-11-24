"""
Professional WebSocket Manager
Handles real-time data streaming
Adapted for standalone use (no DB dependencies)
"""

import json
import threading
import time
import logging
import websocket

logger = logging.getLogger(__name__)

class ProfessionalWebSocketManager:
    """
    WebSocket Connection Management
    """
    
    def __init__(self):
        self.ws = None
        self.ws_thread = None
        self.active = False
        self.authenticated = False
        self.subscriptions = set()
        self.ws_url = None
        self.api_key = None
        
        # Data handlers
        self.quote_handlers = []
        self.depth_handlers = []
        self.ltp_handlers = []
    
    def connect(self, ws_url, api_key):
        """Establish WebSocket connection"""
        try:
            self.ws_url = ws_url
            self.api_key = api_key
            self.authenticated = False
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Start WebSocket in separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Wait for connection to establish
            time.sleep(2)
            
            self.active = True
            logger.info("WebSocket connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            return False
    
    def on_open(self, ws):
        """WebSocket opened callback"""
        logger.info("WebSocket connection opened")
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with WebSocket server"""
        if self.ws:
            auth_msg = {
                "action": "authenticate",
                "api_key": self.api_key
            }
            logger.debug(f"Authenticating...")
            self.ws.send(json.dumps(auth_msg))
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Handle authentication response
            if data.get("type") == "auth":
                if data.get("status") == "success":
                    self.authenticated = True
                    logger.info("Authentication successful!")
                    if self.subscriptions:
                        self.resubscribe_all()
                else:
                    logger.error(f"Authentication failed: {data}")
                return
            
            # Handle market data
            if data.get("type") == "market_data" or data.get("ltp") is not None:
                self.process_market_data(data)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def process_market_data(self, data):
        """Process market data and route to handlers"""
        # Extract actual data if nested
        market_data = data.get('data', data)
        
        # Determine mode
        mode = 'ltp'
        if 'depth' in market_data or 'bids' in market_data:
            mode = 'depth'
        elif 'open' in market_data:
            mode = 'quote'
            
        # Route to handlers
        if mode == 'depth':
            for handler in self.depth_handlers:
                try:
                    handler(market_data)
                except Exception as e:
                    logger.error(f"Error in depth handler: {e}")
        elif mode == 'quote':
            for handler in self.quote_handlers:
                try:
                    handler(market_data)
                except Exception as e:
                    logger.error(f"Error in quote handler: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        logger.warning("WebSocket connection closed")
        self.active = False
        
    def subscribe(self, subscription):
        """Subscribe to symbol"""
        if not self.ws or not self.authenticated:
            logger.warning("WebSocket not ready for subscription")
            return False
            
        symbol = subscription.get('symbol')
        exchange = subscription.get('exchange')
        mode = subscription.get('mode', 'ltp')
        
        # Map mode to number
        mode_map = {'ltp': 1, 'quote': 2, 'depth': 3}
        mode_num = mode_map.get(mode, 1)
        
        message = {
            'action': 'subscribe',
            'symbol': symbol,
            'exchange': exchange,
            'mode': mode_num,
            'depth': 5
        }
        
        self.ws.send(json.dumps(message))
        self.subscriptions.add(json.dumps(subscription))
        time.sleep(0.05)
        return True
        
    def subscribe_batch(self, instruments, mode='ltp'):
        """Batch subscribe"""
        for inst in instruments:
            self.subscribe({
                'symbol': inst.get('symbol'),
                'exchange': inst.get('exchange'),
                'mode': mode
            })
            
    def resubscribe_all(self):
        """Resubscribe all symbols"""
        for sub_str in self.subscriptions:
            self.subscribe(json.loads(sub_str))
            
    def register_handler(self, mode, handler):
        """Register data handler"""
        if mode == 'quote':
            self.quote_handlers.append(handler)
        elif mode == 'depth':
            self.depth_handlers.append(handler)
        elif mode == 'ltp':
            self.ltp_handlers.append(handler)
