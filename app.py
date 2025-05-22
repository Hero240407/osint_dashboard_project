from flask import Flask, render_template, request, jsonify
import subprocess
import shlex
import os

app = Flask(__name__)

# --- Configuration: Paths to Tool Scripts (if not in global PATH) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SHERLOCK_DIR is no longer strictly needed for the command itself if installed globally in venv,
# but can be kept for organizational purposes or if other files from its dir were needed.
SHERLOCK_DIR = os.path.join(BASE_DIR, "sherlock")
SUBLIST3R_DIR = os.path.join(BASE_DIR, "Sublist3r")
GHUNT_DIR = os.path.join(BASE_DIR, "GHunt")

# ... (Keep your existing run_command function and other routes) ...

# --- Tool Routes ---
@app.route('/run/sherlock', methods=['POST'])
def run_sherlock():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # CORRECTED WAY TO CALL SHERLOCK:
    # Assumes 'sherlock' is now in the PATH of your virtual environment
    # after 'pip install .' in the sherlock directory.
    command = f"sherlock {shlex.quote(username)} --no-color --timeout 10 --print-found"
    
    # We no longer need to specify the sherlock_script path directly.
    # Also, cwd=SHERLOCK_DIR is likely not needed anymore as the installed command
    # should be self-contained. If issues arise, you can try adding cwd=SHERLOCK_DIR back.
    output = run_command(command) # Removed cwd argument
    
    # Check if Sherlock still outputs the "outdated method" error even with the direct command
    # This might happen if the environment PATH isn't picking up the venv's bin correctly,
    # or if the old script is somehow still being preferred.
    if "outdated method" in output.lower() or "did you run sherlock with `python3 sherlock/sherlock.py" in output.lower():
        additional_info = (
            "\n\n[INFO] Still seeing 'outdated method' error? "
            "Ensure Sherlock was installed correctly in your virtual environment using 'pip install .' in its directory, "
            "and that the venv is active. The command being run now is: " + command
        )
        output += additional_info

    return jsonify({'output': output})

# ... (Rest of your app.py: other routes, if __name__ == '__main__':, etc.) ...
# Ensure the run_command function and other routes are the same as the last fully working version.

# --- Helper Function to Run Commands (ensure this is the robust version) ---
def run_command(command, timeout=300, cwd=None):
    try:
        app.logger.info(f"Running command: {command} in {cwd or os.getcwd()}")
        if not isinstance(command, str):
            app.logger.error(f"Command is not a string: {command}")
            return "Error: Internal server error, command format invalid."

        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd, errors='replace')
        stdout, stderr = process.communicate(timeout=timeout)
        
        if process.returncode != 0:
            app.logger.error(f"Command failed with code {process.returncode} for '{command}'. Stderr: {stderr}. Stdout: {stdout}")
            error_message = f"Error (Code {process.returncode})"
            if stderr: # Primary error output
                error_message += f"\nStderr:\n{stderr}"
            if stdout: # Sometimes errors or important info also on stdout
                error_message += f"\nStdout:\n{stdout}" # Changed to append if stderr was also present
            return error_message.strip()
        return stdout
    except subprocess.TimeoutExpired:
        app.logger.error(f"Command timed out: {command}")
        if 'process' in locals() and process.poll() is None:
            try:
                process.kill()
                process.communicate()
            except Exception as e_kill:
                app.logger.error(f"Error killing timed-out process: {e_kill}")
        return f"Error: Command '{command.split()[0]}' timed out after {timeout} seconds."
    except FileNotFoundError:
        app.logger.error(f"Command not found: {command.split()[0]}")
        return f"Error: The command '{command.split()[0]}' was not found. Ensure it's installed and in your virtual environment's PATH."
    except Exception as e:
        app.logger.error(f"Unexpected error running command {command}: {str(e)}")
        return f"An unexpected error occurred while trying to run '{command.split()[0]}': {str(e)}"


# Ensure the rest of your Flask app is present below (other routes, main block)
# For example:
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run/holehe', methods=['POST'])
def run_holehe():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    # Ensure holehe is installed in your venv and callable
    command = f"holehe {shlex.quote(email)} --no-color"
    output = run_command(command) # run_command is your helper function
    return jsonify({'output': output})

@app.route('/run/ghunt', methods=['POST'])
def run_ghunt():
    data = request.get_json()
    email_or_gaia = data.get('email')
    if not email_or_gaia:
        return jsonify({'error': 'Email or Gaia ID is required'}), 400
    
    ghunt_script = os.path.join(GHUNT_DIR, "main.py")
    check_cookies_script = os.path.join(GHUNT_DIR, "check_and_gen_cookies.py")

    if not os.path.exists(ghunt_script):
         return jsonify({'error': f"GHunt script not found at {ghunt_script}. Please check GHUNT_DIR and ensure it's cloned and set up."}), 500

    # This is a simplified call. GHunt heavily depends on cookies.json being present and valid in its directory.
    # You MUST run `python3 check_and_gen_cookies.py` inside the GHUNT_DIR on the server first.
    # The command might be `python3 ghunt.py email <email>` or `python3 ghunt.py gaia <id>`
    # For simplicity, assuming email for now.
    command = f"python3 {ghunt_script} email {shlex.quote(email_or_gaia)}"
    
    # GHunt needs to run from its own directory to find cookies.json etc.
    pre_output = "Attempting to run GHunt. Ensure cookies are configured on the server by running check_and_gen_cookies.py in the GHunt directory.\n\n"
    ghunt_execution_output = run_command(command, cwd=GHUNT_DIR)
    return jsonify({'output': pre_output + ghunt_execution_output})


@app.route('/run/ipdomain', methods=['POST'])
def run_ipdomain():
    data = request.get_json()
    target = data.get('target')
    if not target:
        return jsonify({'error': 'Target IP or Domain is required'}), 400
    sanitized_target = shlex.quote(target)
    output_whois = f"--- WHOIS for {target} ---\n" + run_command(f"whois {sanitized_target}")
    # Using 'dig' for more detailed DNS info on Linux
    output_dns = f"\n--- DIG (DNS Lookup) for {target} ---\n" + run_command(f"dig {sanitized_target} ANY +noall +answer")
    return jsonify({'output': f"{output_whois}\n{output_dns}"})

# --- New Tool Routes ---
@app.route('/run/theharvester', methods=['POST'])
def run_theharvester():
    data = request.get_json()
    domain = data.get('domain')
    source = data.get('source', 'google,bing') # Default source
    if not domain:
        return jsonify({'error': 'Domain is required for TheHarvester'}), 400
    # TheHarvester can be slow, especially with 'all' sources. Timeout is important.
    command = f"theHarvester -d {shlex.quote(domain)} -b {shlex.quote(source)} -l 200 --screenshot /tmp" # Limit results, define screenshot dir
    output = run_command(command, timeout=300) # 5 minute timeout
    return jsonify({'output': output})

@app.route('/run/sublist3r', methods=['POST'])
def run_sublist3r():
    data = request.get_json()
    domain = data.get('domain')
    if not domain:
        return jsonify({'error': 'Domain is required for Sublist3r'}), 400
    
    sublist3r_script = os.path.join(SUBLIST3R_DIR, "sublist3r.py")
    if not os.path.exists(sublist3r_script):
        return jsonify({'error': f"Sublist3r script not found at {sublist3r_script}. Please check SUBLIST3R_DIR in app.py."}), 500
    
    command = f"python3 {sublist3r_script} -d {shlex.quote(domain)} -n" # -n for no color
    output = run_command(command, cwd=SUBLIST3R_DIR, timeout=180) # 3 minute timeout
    return jsonify({'output': output})

@app.route('/run/metagoofil', methods=['POST'])
def run_metagoofil():
    data = request.get_json()
    domain = data.get('domain')
    filetypes = data.get('filetypes', 'pdf,doc,xls')
    limit = data.get('limit', '50')
    if not domain:
        return jsonify({'error': 'Domain is required for Metagoofil'}), 400
    
    # Metagoofil often downloads files. The output here will be the console output.
    # For a real app, you'd handle file management if you want to store/show them.
    # Creating a temporary output directory for metagoofil's files
    metagoofil_output_dir = os.path.join(BASE_DIR, "metagoofil_output", shlex.quote(domain).replace('.', '_'))
    os.makedirs(metagoofil_output_dir, exist_ok=True)

    command = (f"metagoofil -d {shlex.quote(domain)} -t {shlex.quote(filetypes)} "
               f"-l {shlex.quote(limit)} -n {shlex.quote(limit)} -o {metagoofil_output_dir} -f metagoofil_results.html")
    # Note: -o specifies output directory, -f specifies a report file. The stdout will show progress.
    
    console_output = run_command(command, timeout=300) # 5 min timeout
    result_message = (f"Metagoofil console output:\n{console_output}\n\n"
                      f"Files (if any) were attempted to be saved in the server directory: {metagoofil_output_dir}\n"
                      f"Report (if generated): {os.path.join(metagoofil_output_dir, 'metagoofil_results.html')}")
    return jsonify({'output': result_message})


@app.route('/run/nmap', methods=['POST'])
def run_nmap():
    data = request.get_json()
    target = data.get('target')
    scan_type = data.get('scan_type', '-F') # Default to Fast Scan
    if not target:
        return jsonify({'error': 'Target IP or Hostname is required for Nmap'}), 400
    
    # Basic sanitization for scan type - ensure it's one of the expected options
    allowed_scan_types = {"-F": True, "-sV -T4": True, "-A -T4": True, "-p- -T4": True, "--script vuln":True}
    if scan_type not in allowed_scan_types:
        return jsonify({'error': 'Invalid Nmap scan type selected'}), 400
        
    command = f"nmap {scan_type} {shlex.quote(target)}"
    # Nmap might require sudo for some scan types (e.g., -sS).
    # For simplicity, using types that often work without sudo, but this can be a limitation.
    # If running Flask as root (not recommended) or with sudo for nmap, be extremely careful.
    output = run_command(command, timeout=600) # 10 min timeout for potentially long scans
    return jsonify({'output': output})

@app.route('/run/dnsrecon', methods=['POST'])
def run_dnsrecon():
    data = request.get_json()
    domain = data.get('domain')
    recon_type = data.get('type', 'std')
    if not domain:
        return jsonify({'error': 'Domain is required for Dnsrecon'}), 400
    
    # Add more type checks if necessary
    command_parts = ["dnsrecon", "-d", shlex.quote(domain), "-n"] # -n for no ANSI
    if recon_type == "std":
        command_parts.append("-t std")
    elif recon_type == "brt":
        # Note: Default wordlist path for dnsrecon might vary.
        # This assumes a common path or that dnsrecon finds it.
        # You might need to specify -w /path/to/wordlist if it fails.
        command_parts.extend(["-t brt"])
    elif recon_type == "axfr":
        command_parts.append("-t axfr")
    else:
        return jsonify({'error': 'Invalid Dnsrecon type'}), 400

    command = " ".join(command_parts)
    output = run_command(command, timeout=300)
    return jsonify({'output': output})

@app.route('/run/whatweb', methods=['POST'])
def run_whatweb():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required for WhatWeb'}), 400
    
    # WhatWeb might need --no-errors for cleaner output in scripts
    command = f"whatweb --no-color --color never {shlex.quote(url)}"
    output = run_command(command, timeout=180)
    return jsonify({'output': output})

if __name__ == '__main__':
    os.makedirs(os.path.join(BASE_DIR, "metagoofil_output_default_domain"), exist_ok=True)
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host='0.0.0.0', port=5001)