"""
Extended OpenAlgo API client with additional methods
"""
from openalgo import api

class ExtendedOpenAlgoAPI(api):
    """Extended OpenAlgo API client with ping method"""
    
    def ping(self):
        """
        Test connectivity and validate API key authentication
        """
        payload = {"apikey": self.api_key}
        return self._make_request("ping", payload)
