# OSINT & Security Dashboard

A Flask-based web application designed to provide a centralized interface for running various open-source intelligence (OSINT) and cybersecurity command-line tools. This dashboard allows users to easily execute scans and investigations without needing to remember or type complex command-line arguments for each tool.

## Overview

The dashboard features a sidebar for selecting different tools and a main content area where users can input targets (usernames, emails, domains, IPs, etc.) and view the output from the selected tool. This project integrates several popular OSINT tools, making them accessible through a unified web UI.

## Features

*   **Web-based Interface:** Easy-to-use UI built with HTML, CSS, and JavaScript.
*   **Flask Backend:** Python-based backend to securely execute command-line tools.
*   **Centralized Tooling:** Access multiple OSINT tools from a single dashboard.
*   **Integrated Tools:**
    *   **Sherlock:** Hunt for social media accounts by username.
    *   **Holehe:** Check if an email is used on different sites (breaches, social media).
    *   **GHunt:** Investigate Google accounts (requires cookie setup).
    *   **IP/Domain Info:** Perform `whois` and `dig` (DNS) lookups.
    *   **TheHarvester:** Gather emails, subdomains, hosts, and open ports.
    *   **Sublist3r:** Enumerate subdomains of a website.
    *   **Metagoofil:** Extract metadata from public documents.
    *   **Nmap:** Network scanner for port scanning and service discovery.
    *   **Dnsrecon:** DNS enumeration script.
    *   **WhatWeb:** Identify technologies used on websites.
*   **Extensible:** Designed to potentially incorporate more tools in the future.

## Tech Stack

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript
*   **OSINT Tools (Command-Line):**
    *   Sherlock
    *   Holehe
    *   GHunt
    *   whois
    *   dig (or nslookup)
    *   TheHarvester
    *   Sublist3r
    *   Metagoofil
    *   Nmap
    *   Dnsrecon
    *   WhatWeb
*   **Environment Management:** Python `venv`

## Prerequisites

Before you begin, ensure you have the following installed on your Ubuntu-based Linux system:

*   Python 3.8+
*   `pip` (Python package installer)
*   `python3-venv` (for creating virtual environments)
*   `git` (for cloning repositories)
*   The following system packages:
    *   `whois`
    *   `nmap`
    *   `dnsrecon`
    *   `whatweb`
    *   `libimage-exiftool-perl` (for Metagoofil)
    *   `curl` (optional, but useful)

You can install most system prerequisites with:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git whois nmap dnsrecon whatweb libimage-exiftool-perl curl
```

## Installation and Setup

Follow these steps to set up the OSINT Dashboard on your server:

1.  **Clone the Project (or Create Project Directory):**
    If you have this README as part of a Git repository, clone it. Otherwise, create the main project directory:
    ```bash
    mkdir osint_dashboard_project
    cd osint_dashboard_project
    ```

2.  **Create and Activate Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Your terminal prompt should now start with `(venv)`.

3.  **Install Core Python Dependencies:**
    ```bash
    pip install Flask holehe theHarvester
    ```

4.  **Clone and Set Up External CLI Tools:**
    These tools will be cloned into subdirectories within your project.

    *   **Sherlock:**
        ```bash
        git clone https://github.com/sherlock-project/sherlock.git ./sherlock
        (cd sherlock && pip install -r requirements.txt)
        ```

    *   **Sublist3r:**
        ```bash
        git clone https://github.com/aboul3la/Sublist3r.git ./Sublist3r
        (cd Sublist3r && pip install -r requirements.txt)
        ```

    *   **GHunt:**
        ```bash
        git clone https://github.com/mxrch/GHunt.git ./GHunt
        (cd GHunt && pip install -r requirements.txt)
        ```
        **VERY IMPORTANT for GHunt:** You must manually configure GHunt with Google cookies.
        Navigate into the `GHunt` directory and run:
        ```bash
        cd GHunt
        python3 check_and_gen_cookies.py
        cd ..
        ```
        Follow the on-screen instructions. This step is crucial for GHunt to function. A `cookies.json` file will be created in the `GHunt` directory.

    *   **Metagoofil:**
        ```bash
        git clone https://github.com/laramies/metagoofil.git ./metagoofil
        ```
        (Metagoofil typically relies on system tools like `exiftool` rather than Python packages from `requirements.txt`.)

5.  **Place Application Files:**
    *   Copy your `app.py` (Flask backend code) into the root of the `osint_dashboard_project` directory.
    *   Create a `templates` directory in the root:
        ```bash
        mkdir templates
        ```
    *   Copy your `index.html` (frontend code) into the `templates` directory.

    Your project structure should look like:
    ```
    osint_dashboard_project/
    ├── venv/
    ├── app.py
    ├── templates/
    │   └── index.html
    ├── sherlock/
    ├── Sublist3r/
    ├── GHunt/         # Should contain cookies.json after setup
    ├── metagoofil/
    └── README.md      # This file
    ```

6.  **Verify Tool Paths in `app.py` (Optional):**
    The provided `app.py` uses relative paths which should work with the above setup. If you've placed tools elsewhere, you might need to adjust the `*_DIR` variables at the top of `app.py`.

## Running the Application

1.  **Ensure Virtual Environment is Active:**
    If you've opened a new terminal, navigate to the project directory and activate the venv:
    ```bash
    cd path/to/osint_dashboard_project
    source venv/bin/activate
    ```

2.  **Start the Flask Server:**
    ```bash
    python3 app.py
    ```
    You should see output indicating the server is running, usually on `http://0.0.0.0:5001/` or `http://127.0.0.1:5001/`.

3.  **Access the Dashboard:**
    Open your web browser and navigate to `http://YOUR_SERVER_IP:5001` (replace `YOUR_SERVER_IP` with your server's actual IP address, or use `localhost` if running locally).

4.  **Firewall Configuration (If Needed):**
    If you have a firewall like `ufw` enabled, allow traffic on port 5001:
    ```bash
    sudo ufw allow 5001/tcp
    sudo ufw reload
    ```

## Usage

*   Use the sidebar on the left to select the desired OSINT tool.
*   The corresponding panel for the selected tool will appear in the main content area.
*   Enter the required input (e.g., username, email, domain) into the input field(s).
*   Click the "Run", "Search", or "Scan" button for that tool.
*   The results from the command-line tool will be displayed in the textarea below the input fields.
*   Please be patient, as some tools (like TheHarvester with 'all' sources, or Nmap full port scans) can take several minutes to complete.

## Important Notes & Considerations

*   **GHunt `cookies.json`:** The GHunt tool relies heavily on a valid `cookies.json` file obtained by authenticating a Google account. If GHunt fails, this is the most likely cause. You may need to periodically refresh these cookies by re-running `check_and_gen_cookies.py` within the `GHunt` directory.
*   **Tool Execution Time:** Some tools can take a significant amount of time to run. The application has a timeout for commands, but long-running tasks might still make the UI unresponsive during execution in this simple setup.
*   **Output Parsing:** The current implementation displays the raw or slightly processed output from the tools. More sophisticated parsing could be added for better presentation.
*   **Security:**
    *   The Flask development server is **not for production use**. For deployment, use a production-grade WSGI server like Gunicorn or uWSGI, preferably behind a reverse proxy like Nginx.
    *   Input sanitization is implemented using `shlex.quote()`, but always be cautious when building web interfaces that execute shell commands.
*   **Ethical Use:** These tools are powerful. Always use them responsibly and ethically, ensuring you have permission to scan or investigate any target. Comply with all applicable laws and regulations.

## Troubleshooting

*   **"Command not found" errors:**
    *   Ensure the tool (e.g., `nmap`, `whois`) is installed globally on the system (via `apt`).
    *   For cloned tools (Sherlock, Sublist3r, etc.), verify the paths in `app.py` (`*_DIR` variables) are correct and the tool's executable script exists at that path.
    *   Ensure you are running the Flask app from within the activated virtual environment.
*   **GHunt not working:** Almost always due to missing or invalid `GHunt/cookies.json`. Re-run `python3 GHunt/check_and_gen_cookies.py`.
*   **Permission denied:** Some tools or operations (like Nmap's SYN scans or Metagoofil writing to certain directories) might require elevated privileges if not handled carefully. The current setup aims to use user-level permissions where possible.
*   **Flask app doesn't start:** Check for Python syntax errors in `app.py` or issues with installed dependencies.

## Future Enhancements (To-Do)

*   Integrate more OSINT tools.
*   Implement asynchronous task execution (e.g., using Celery & Redis) to prevent UI blocking for long-running tools.
*   Improve UI/UX, including better formatting of tool outputs.
*   Add user authentication and authorization.
*   More robust error handling and reporting.
*   Allow users to configure tool-specific options (e.g., Nmap scan types more dynamically).
*   Implement a results storage/history feature.
*   Security hardening for production deployment.

## Disclaimer

This project is for educational and research purposes only. The developers assume no liability and are not responsible for any misuse or damage caused by this program. Use at your own risk and ensure you comply with all applicable laws.
