# UW Helper for Anki

**UW Helper** is an Anki add-on that embeds the UW QBank directly into an Anki sidebar. It streamlines your workflow by keeping you logged in and providing a powerful scanner that extracts Question IDs (QIDs) from your test results.

## 🚀 Features

* **Embedded Browser:** Browse UW, take tests, and review explanations without leaving Anki.
* **Smart Result Scanner:** Automatically detects **Missed** (Red X) and **Correct** (Green Check) questions on your results page.
    * **Missed Questions:** Pop up in a dialog for you to copy/paste into the Anki Browser (to find cards you need to review).
    * **Correct Questions:** Are silently saved to a local "Mastery List" (`correct_questions.txt`). This allows other tools (like the *History Fetcher*) to automatically filter out questions you already know.
* **Persistent Login:** Keeps you logged in across Anki restarts by storing cookies in a dedicated, isolated local profile.
* **Keyboard Shortcuts:** Trigger a scan instantly with `Cmd+Shift+S` (Mac) or `Ctrl+Shift+S` (Windows).
* **Smart Logic:** Identifies the `Index - QID` pattern (e.g., `2 - 92`) and extracts only the unique ID (`92`).

## 📥 Installation

1.  **Download** this repository (Code -> Download ZIP).
2.  Open Anki and go to **Tools** -> **Add-ons** -> **View Files**.
3.  Extract the zip to the add-ons directory.
4.  **Restart Anki**.

## 🛠️ Usage

### 1. Opening the Sidebar
* Go to **Tools** -> **UW Helper** -> **Toggle Sidebar**.
* *Note:* The sidebar waits ~1.5 seconds before loading the login page to ensure Anki is responsive.

### 2. Logging In
* Log in to your UW account inside the sidebar.
* Check "Remember Me" if available.
* Your session is saved to a persistent local profile. You typically won't need to log in again unless you are inactive for >24 hours (UW's server limit).

### 3. Scanning Test Results
When you finish a test block or view a previous test:
1.  Navigate to the **Test Results** page (the table view showing questions with Red/Green icons).
2.  Press **`Cmd+Shift+S`** (Mac) or **`Ctrl+Shift+S`** (Windows).
    * *Alternative:* Go to **Tools** -> **UW Helper** -> **Scan Test Results**.
3.  **What happens next:**
    * **Missed Questions:** A popup appears with a list of IDs. Click **Copy** and paste them into the Anki Browser (`tag:123`, `cid:123`, etc.) to find your cards.
    * **Correct Questions:** These are automatically saved to `user_data/correct_questions.txt` in the background. You won't be bothered with them, but they are recorded so you don't study them again unnecessarily.

## 🔧 Troubleshooting

**"Session Expired" on startup?**
UW's servers force a logout after ~24 hours of inactivity. This is security behavior from their side. Simply log in again; the add-on will save the new token.

**Scan says "No data found"?**
* Ensure you are on the **list view** of the results page.
* Ensure the "Red X" or "Green Check" icons are visible in the table rows.

**Anki hangs when opening the sidebar?**
The add-on uses a slight delay on launch to prevent this. If it persists, try closing other resource-heavy add-ons.

## ⚖️ Disclaimer
This is a third-party tool and is not affiliated with, endorsed by, or connected to UW or Anki in any way. Use it responsibly and in accordance with UW's Terms of Service.
