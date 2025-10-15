
PRIVATE ACCESS — Sully's Bot
============================
This build is password-gated. Set the environment variable SULLY_APP_PASSWORD
and only users with the password can see the app.

Quick Start (Windows, local network)
------------------------------------
1) Open Command Prompt in this folder.
2) Set a password for this session:
   set SULLY_APP_PASSWORD=YourSecretHere
3) Run the helper:
   private_helpers\install_and_run_private.bat
4) On your phone (same Wi‑Fi), open: http://<your-pc-ip>:8501
   You'll be asked for the password.

Public Private Link (ngrok)
---------------------------
1) Install ngrok and run 'ngrok config add-authtoken <YOUR_TOKEN>' once.
2) Set the same password:
   set SULLY_APP_PASSWORD=YourSecretHere
3) Run:
   private_helpers\ngrok_private_link.bat
4) ngrok prints a https://... URL protected with basic auth:
   - username: sully
   - password: <YourSecretHere>
