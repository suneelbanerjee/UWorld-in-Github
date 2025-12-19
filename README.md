UWorld Helper for Anki
UWorld Helper is an Anki add-on that embeds the UWorld QBank directly into an Anki sidebar. Its primary feature is a "Missed Question Scanner" that automatically detects incorrect answers on your test results page and extracts the Question IDs (QIDs) for easy card retrieval.

🚀 Features
Embedded Browser: Browse UWorld without leaving Anki.

Smart Missed Question Scan: Automatically scans the current page for "Incorrect" markers (Red 'X' icons) and extracts the specific Question IDs.

Logic: It identifies the Index - QID pattern (e.g., 2 - 92) and captures only the QID (92), ignoring the index.

Persistent Login: Keeps you logged in across Anki restarts by storing cookies in a dedicated local profile (user_data folder).

Clipboard Export: Generates a clean, comma-separated list of IDs ready to be pasted into the Anki Browser (e.g., cid:123,456 or tag:123).

📥 Installation
Download the repository (or the __init__.py file).

Open Anki and go to Tools -> Add-ons -> View Files.

Create a new folder (e.g., UWorld_Helper).

Paste the __init__.py file into that folder.

Restart Anki.

🛠️ Usage
1. Opening the Sidebar
Go to Tools -> UWorld Helper -> Toggle Sidebar.

Note: The sidebar will wait ~1.5 seconds before loading the login page. This is intentional to ensure Anki's UI is fully ready and to prevent freezing.

2. Logging In
Log in to your UWorld account inside the sidebar.

Check the "Remember Me" box if available.

Once logged in, the add-on will save your session to a local folder inside the add-on directory. You should not need to log in again after restarting Anki.

3. Scanning for Missed Questions
Navigate to your Test Results page (the table showing correct/incorrect answers).

Go to Tools -> UWorld Helper -> Scan for Missed Questions.

A popup will appear listing all found Question IDs.

Click Copy to Clipboard.

Paste the IDs into your Anki Browser to find the relevant cards.

🔧 Troubleshooting
"Session Expired" on startup? Occasionally, UWorld may require a fresh login if the session token expires. If the sidebar loads the login page instead of the dashboard, simply log in again. The new token will be saved automatically.

Scan says "No 'Incorrect' markers found"?

Ensure you are on the Test Results page (the list view of questions).

Ensure the rows have the "Red X" icon visible.

The scanner looks for the pattern Index - QID (e.g., 5 - 10542). If the column format changes, the scanner may need updating.

Anki hangs when opening the sidebar? The add-on uses a 1.5-second delay to prevent this. If it persists, try closing other heavy add-ons or waiting a moment after Anki launches before opening the sidebar.

⚖️ Disclaimer
This is a third-party tool and is not affiliated with, endorsed by, or connected to UWorld or Anki in any way. Use it responsibly and in accordance with UWorld's Terms of Service.
