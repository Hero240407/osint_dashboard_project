import os
import json
import threading
from threading import RLock
import traceback
from flask import Flask, send_from_directory, abort, request, jsonify
from flask_cors import CORS

print("--- Basic Imports Done ---", flush=True)

try:
    # --- Configuration ---
    HOST_IP = '0.0.0.0'
    PORT = 5124
    MAIN_HTML_FILE = 'index.html' # Assuming you still have a main index
    CREDIT_DATA_FILE = 'credit_data.json'
    STOCK_REPLENISH_DATA_FILE = 'stock_replenish_data.json'
    STOCK_VALUE_DATA_FILE = 'stock_value_data.json' # NEW data file for stock value tool
    print("--- Configuration Done ---", flush=True)

    # --- Flask App Setup ---
    app = Flask(__name__, static_folder='.', static_url_path='')
    print("--- Flask(__name__) OK ---", flush=True)
    CORS(app)
    print("--- CORS(app) OK ---", flush=True)

    # --- Data Storage & Synchronization ---
    credit_data_lock = threading.RLock()
    stock_replenish_data_lock = threading.RLock() # Renamed for clarity from stock_data_lock
    stock_value_data_lock = threading.RLock() # NEW lock for stock value tool data
    print("--- Data Locks Initialized ---", flush=True)

    # --- Default Empty State for Stock Replenishment Tool ---
    DEFAULT_STOCK_REPLENISH_TOOL_STATE = {
        "allLoadedProducts": [],
        "selectedCategories": ["all"],
        "sortOrder": "default",
        "budget": "",
        "distributor": "",
        "isShowingAllProducts": False,
        "isCompareMode": False,
        "appVersion": "1.13" # Assuming original tool is at 1.13
    }
    print("--- Default Stock Replenish Tool State Defined ---", flush=True)

    # --- Default Empty State for Stock Value Tool ---
    DEFAULT_STOCK_VALUE_TOOL_STATE = {
        "allLoadedProducts": [],
        "selectedCategories": ["all"],
        "sortOrder": "default",
        "distributor": "",
        "isCompareMode": False,
        "appVersion": "1.0" # Version for the new stock value tool
    }
    print("--- Default Stock Value Tool State Defined ---", flush=True)


    # --- Function Definitions for Credit Data ---
    def load_credit_data():
        print("--- Entering load_credit_data ---", flush=True)
        with credit_data_lock:
            try:
                if os.path.exists(CREDIT_DATA_FILE):
                    with open(CREDIT_DATA_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return data if isinstance(data, list) else []
                return []
            except Exception as e:
                print(f"--- ERROR loading {CREDIT_DATA_FILE}: {e} ---", flush=True)
                return []

    def save_credit_data(data):
        print("--- Entering save_credit_data ---", flush=True)
        if not isinstance(data, list): return False
        with credit_data_lock:
            try:
                with open(CREDIT_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"--- ERROR saving {CREDIT_DATA_FILE}: {e} ---", flush=True)
                return False

    # --- Function Definitions for Stock Replenishment Tool Data ---
    def load_stock_replenish_data():
        print("--- Entering load_stock_replenish_data ---", flush=True)
        with stock_replenish_data_lock:
            try:
                if os.path.exists(STOCK_REPLENISH_DATA_FILE):
                    with open(STOCK_REPLENISH_DATA_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            loaded_data = {**DEFAULT_STOCK_REPLENISH_TOOL_STATE, **data}
                            if not isinstance(loaded_data.get("allLoadedProducts"), list):
                                loaded_data["allLoadedProducts"] = []
                            return loaded_data
                        return DEFAULT_STOCK_REPLENISH_TOOL_STATE.copy()
                return DEFAULT_STOCK_REPLENISH_TOOL_STATE.copy()
            except Exception as e:
                print(f"--- ERROR loading {STOCK_REPLENISH_DATA_FILE}: {e} ---", flush=True)
                return DEFAULT_STOCK_REPLENISH_TOOL_STATE.copy()

    def save_stock_replenish_data(data):
        print("--- Entering save_stock_replenish_data ---", flush=True)
        if not isinstance(data, dict): return False
        with stock_replenish_data_lock:
            try:
                with open(STOCK_REPLENISH_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"--- ERROR saving {STOCK_REPLENISH_DATA_FILE}: {e} ---", flush=True)
                return False

    # --- Function Definitions for Stock Value Tool Data ---
    def load_stock_value_data():
        """Loads stock value tool data from its JSON file."""
        print("--- Entering load_stock_value_data ---", flush=True)
        with stock_value_data_lock:
            try:
                if os.path.exists(STOCK_VALUE_DATA_FILE):
                    with open(STOCK_VALUE_DATA_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            # Merge with defaults to ensure all keys are present
                            loaded_data = {**DEFAULT_STOCK_VALUE_TOOL_STATE, **data}
                            if not isinstance(loaded_data.get("allLoadedProducts"), list):
                                print(f"--- WARNING: 'allLoadedProducts' in {STOCK_VALUE_DATA_FILE} is not a list. Resetting it. ---", flush=True)
                                loaded_data["allLoadedProducts"] = []
                            return loaded_data
                        else:
                            print(f"--- ERROR: {STOCK_VALUE_DATA_FILE} does not contain a JSON object. Returning default. ---", flush=True)
                            return DEFAULT_STOCK_VALUE_TOOL_STATE.copy()
                else:
                    print(f"--- {STOCK_VALUE_DATA_FILE} does not exist. Returning default. ---", flush=True)
                    return DEFAULT_STOCK_VALUE_TOOL_STATE.copy()
            except Exception as e:
                print(f"--- ERROR loading {STOCK_VALUE_DATA_FILE}: {e} ---", flush=True)
                traceback.print_exc()
                return DEFAULT_STOCK_VALUE_TOOL_STATE.copy()

    def save_stock_value_data(data):
        """Saves the provided stock value tool state object to its JSON file."""
        print("--- Entering save_stock_value_data ---", flush=True)
        if not isinstance(data, dict):
             print(f"--- ERROR: Stock value data to save is not an object (dict) for {STOCK_VALUE_DATA_FILE}. Aborting. ---", flush=True)
             return False
        with stock_value_data_lock:
            try:
                with open(STOCK_VALUE_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"--- Stock value data saved successfully to {STOCK_VALUE_DATA_FILE} ---", flush=True)
                return True
            except Exception as e:
                print(f"--- ERROR saving stock value data to {STOCK_VALUE_DATA_FILE}: {e} ---", flush=True)
                traceback.print_exc()
                return False

    # --- API Endpoints ---

    # Credit Data Endpoints
    @app.route('/api/creditdata', methods=['GET', 'POST'])
    def creditdata_handler():
        if request.method == 'GET':
            print("--- GET /api/creditdata ---", flush=True)
            return jsonify(load_credit_data())
        elif request.method == 'POST':
            print("--- POST /api/creditdata ---", flush=True)
            new_data = request.get_json()
            if not isinstance(new_data, list):
                return jsonify({"error": "Invalid data: Expected list"}), 400
            if save_credit_data(new_data):
                return jsonify({"message": "Credit data updated"}), 200
            return jsonify({"error": "Failed to save credit data"}), 500

    # Stock Replenishment Tool Data Endpoints (Original stock tool)
    @app.route('/api/stockdata', methods=['GET', 'POST']) # Original endpoint for replenishment tool
    def stockdata_replenish_handler():
        if request.method == 'GET':
            print("--- GET /api/stockdata (Replenish Tool) ---", flush=True)
            return jsonify(load_stock_replenish_data())
        elif request.method == 'POST':
            print("--- POST /api/stockdata (Replenish Tool) ---", flush=True)
            new_data = request.get_json()
            if not isinstance(new_data, dict):
                return jsonify({"error": "Invalid data: Expected object"}), 400
            if "allLoadedProducts" not in new_data or not isinstance(new_data["allLoadedProducts"], list):
                 return jsonify({"error": "Invalid data: 'allLoadedProducts' missing or not a list"}), 400
            if save_stock_replenish_data(new_data):
                return jsonify({"message": "Stock replenish data updated"}), 200
            return jsonify({"error": "Failed to save stock replenish data"}), 500

    # Stock Value Tool Data Endpoints (NEW)
    @app.route('/api/stockvaluedata', methods=['GET', 'POST']) # NEW endpoint
    def stockvaluedata_handler():
        if request.method == 'GET':
            print("--- GET /api/stockvaluedata (Value Tool) ---", flush=True)
            return jsonify(load_stock_value_data())
        elif request.method == 'POST':
            print("--- POST /api/stockvaluedata (Value Tool) ---", flush=True)
            new_data = request.get_json()
            if not isinstance(new_data, dict):
                return jsonify({"error": "Invalid data: Expected object"}), 400
            if "allLoadedProducts" not in new_data or not isinstance(new_data["allLoadedProducts"], list):
                 return jsonify({"error": "Invalid data: 'allLoadedProducts' missing or not a list"}), 400
            if save_stock_value_data(new_data):
                return jsonify({"message": "Stock value data updated"}), 200
            return jsonify({"error": "Failed to save stock value data"}), 500

    # Routes for serving HTML files
    @app.route('/')
    def serve_index():
        print(f"--- GET / request received. Serving {MAIN_HTML_FILE} ---", flush=True)
        # If MAIN_HTML_FILE doesn't exist, you might want to serve one of the tools,
        # or a simple page linking to them. For now, it tries to serve MAIN_HTML_FILE.
        if os.path.exists(MAIN_HTML_FILE):
            return send_from_directory('.', MAIN_HTML_FILE)
        # Fallback if index.html is not present (e.g. serve one of the tools)
        elif os.path.exists('excelProcessorL-4.html'): # Check for original tool
             print(f"--- {MAIN_HTML_FILE} not found, serving excelProcessorL-4.html as fallback ---", flush=True)
             return send_from_directory('.', 'excelProcessorL-4.html')
        print(f"--- ERROR: {MAIN_HTML_FILE} and fallbacks not found ---", flush=True)
        abort(404)


    @app.route('/<path:filename>')
    def serve_other_html(filename):
        print(f"--- GET /{filename} request received ---", flush=True)
        # Allow common static files and our specific HTML tool files
        allowed_extensions = ('.html', '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.json')
        if not filename.lower().endswith(allowed_extensions):
             print(f"--- Forbidden: Request for disallowed file type: {filename} ---", flush=True)
             abort(403)
        if '..' in filename or filename.startswith('/'):
             print(f"--- Forbidden: Invalid path: {filename} ---", flush=True)
             abort(403)
        try:
            return send_from_directory('.', filename)
        except FileNotFoundError:
            print(f"--- ERROR: {filename} not found ---", flush=True)
            abort(404, description=f"Resource not found: {filename}")
        except Exception as e:
            print(f"--- ERROR serving {filename}: {e} ---", flush=True)
            abort(500)

    print("--- Route Definitions Parsed ---", flush=True)

except ImportError as e:
    print(f"--- !!! IMPORT ERROR: {e} !!! ---", flush=True)
    print("--- Please run: pip install Flask Flask-Cors ---", flush=True)
    exit()
except Exception as e:
    print(f"--- !!! ERROR during initial setup: {e} !!! ---", flush=True)
    traceback.print_exc()
    exit()

# --- Server Execution ---
if __name__ == '__main__':
    print("--- Entered __main__ block ---", flush=True)
    try:
        print("--- Initial load of credit data ---", flush=True)
        load_credit_data()
        print("--- Initial load of stock replenish tool data ---", flush=True)
        load_stock_replenish_data()
        print("--- Initial load of stock value tool data ---", flush=True)
        load_stock_value_data() # Initialize new data file if not exists

        print(f"Server will listen on http://{HOST_IP}:{PORT}", flush=True)
        print(f"Serving files from directory: {os.path.abspath('.')}", flush=True)
        print(f"Credit data file: {os.path.abspath(CREDIT_DATA_FILE)}", flush=True)
        print(f"Stock Replenish data file: {os.path.abspath(STOCK_REPLENISH_DATA_FILE)}", flush=True)
        print(f"Stock Value data file: {os.path.abspath(STOCK_VALUE_DATA_FILE)}", flush=True) # New file
        print("Press CTRL+C to stop the server.", flush=True)

        app.run(host=HOST_IP, port=PORT, debug=True) # debug=False for production
        print("--- app.run() finished ---", flush=True)

    except Exception as e:
        print(f"--- !!! ERROR within __main__ block: {e} !!! ---", flush=True)
        traceback.print_exc()