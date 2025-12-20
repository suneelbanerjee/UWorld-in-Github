# -*- coding: utf-8 -*-
import os
import sys
from aqt import mw
from aqt.qt import *
from aqt.utils import showText, tooltip

# ============================================================
# 0) COMPATIBILITY FIX: Qt5 vs Qt6 Enums
# ============================================================
try:
    # Qt6 / PyQt6 (Newer Anki)
    DOCK_LEFT = Qt.DockWidgetArea.LeftDockWidgetArea
    DOCK_RIGHT = Qt.DockWidgetArea.RightDockWidgetArea
except AttributeError:
    # Qt5 / PyQt5 (Older Anki)
    DOCK_LEFT = Qt.LeftDockWidgetArea
    DOCK_RIGHT = Qt.RightDockWidgetArea

# ============================================================
# 1) Chromium Flags for Speed
# ============================================================
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-background-timer-throttling "
    "--disable-renderer-backgrounding "
    "--ignore-gpu-blocklist "
    "--enable-gpu-rasterization "
    "--no-sandbox"
)

# ============================================================
# 2) WebEngine Compatibility & GLOBAL PROFILE
# ============================================================
UWORLD_GLOBAL_PROFILE = None

try:
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    try:
        from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings, QWebEngineProfile
    except ImportError:
        QWebEngineView = None
        QWebEnginePage = None
        QWebEngineProfile = None

def get_data_dir():
    """Returns the path to the user_data folder."""
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(addon_dir, "user_data")
    if not os.path.exists(data_dir):
        try: os.makedirs(data_dir)
        except: pass
    return data_dir

def get_global_profile():
    global UWORLD_GLOBAL_PROFILE
    if UWORLD_GLOBAL_PROFILE is not None:
        return UWORLD_GLOBAL_PROFILE

    if not QWebEngineProfile:
        return None

    data_dir = get_data_dir()

    UWORLD_GLOBAL_PROFILE = QWebEngineProfile("UWorld_Disk_Auth_v2", mw)
    UWORLD_GLOBAL_PROFILE.setPersistentStoragePath(data_dir)
    UWORLD_GLOBAL_PROFILE.setCachePath(data_dir)
    
    # Compat: Cache Type
    try:
        cache_type = QWebEngineProfile.HttpCacheType.DiskHttpCache
        UWORLD_GLOBAL_PROFILE.setHttpCacheType(cache_type)
    except AttributeError:
        try:
            cache_type = QWebEngineProfile.DiskHttpCache
            UWORLD_GLOBAL_PROFILE.setHttpCacheType(cache_type)
        except AttributeError: pass

    # Compat: Cookie Policy
    try:
        cookie_policy = QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        UWORLD_GLOBAL_PROFILE.setPersistentCookiesPolicy(cookie_policy)
    except AttributeError:
        try:
            cookie_policy = QWebEngineProfile.ForcePersistentCookies
            UWORLD_GLOBAL_PROFILE.setPersistentCookiesPolicy(cookie_policy)
        except AttributeError: pass

    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    UWORLD_GLOBAL_PROFILE.setHttpUserAgent(ua)
    
    s = UWORLD_GLOBAL_PROFILE.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    return UWORLD_GLOBAL_PROFILE

# ============================================================
# 3) File I/O for Correct Questions
# ============================================================
def save_correct_ids_to_file(new_ids):
    """
    Reads existing correct IDs from file, merges with new ones, 
    and saves back to 'correct_questions.txt'.
    """
    if not new_ids:
        return 0

    data_dir = get_data_dir()
    file_path = os.path.join(data_dir, "correct_questions.txt")
    
    existing_ids = set()
    
    # 1. Read existing file if it exists
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Split by commas, strip whitespace, ignore empties
                items = [x.strip() for x in content.split(",") if x.strip().isdigit()]
                existing_ids.update(items)
        except Exception as e:
            print(f"[UWorld Helper] Error reading correct IDs file: {e}")

    # 2. Add new IDs
    original_count = len(existing_ids)
    existing_ids.update(new_ids)
    added_count = len(existing_ids) - original_count
    
    # 3. Write back to file (Sorted, Comma Separated)
    try:
        sorted_list = sorted(list(existing_ids), key=lambda x: int(x))
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(", ".join(sorted_list))
        print(f"[UWorld Helper] Saved {len(sorted_list)} correct IDs to {file_path}")
    except Exception as e:
        print(f"[UWorld Helper] Error writing correct IDs file: {e}")
        
    return added_count

# ============================================================
# 4) Result Dialog
# ============================================================
class ScanResultDialog(QDialog):
    def __init__(self, ids, parent=None):
        super().__init__(parent)
        self.setWindowTitle("UWorld Missed Questions")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Found <b>{len(ids)}</b> Missed Question IDs:"))
        
        self.text_area = QTextEdit()
        sorted_ids = sorted(list(ids), key=lambda x: int(x) if x.isdigit() else 0)
        self.text_area.setPlainText(", ".join(sorted_ids))
        layout.addWidget(self.text_area)
        
        btn_layout = QHBoxLayout()
        btn_copy = QPushButton("Copy to Clipboard")
        btn_copy.clicked.connect(lambda: [mw.app.clipboard().setText(self.text_area.toPlainText()), tooltip("Copied!")])
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_copy)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

# ============================================================
# 5) The UWorld Dock
# ============================================================
class UWorldDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("UWorld", parent)
        self.setObjectName("UWorldDock")
        self.setAllowedAreas(DOCK_LEFT | DOCK_RIGHT)
        self.setMinimumWidth(450)
        
        container = QWidget()
        self.setWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        nav = QHBoxLayout()
        b_back = QPushButton("◀"); b_back.setMaximumWidth(30)
        b_refresh = QPushButton("⟳"); b_refresh.setMaximumWidth(30)
        b_home = QPushButton("🏠"); b_home.setMaximumWidth(30)
        nav.addWidget(b_back); nav.addWidget(b_refresh); nav.addWidget(b_home); nav.addStretch()
        layout.addLayout(nav)

        if QWebEngineView:
            self.web_view = QWebEngineView()
            self.profile = get_global_profile()
            self.page = UWorldPage(self.profile, self.web_view)
            self.web_view.setPage(self.page)
            
            QTimer.singleShot(1500, self.load_initial_url)
            
            b_back.clicked.connect(self.web_view.back)
            b_refresh.clicked.connect(self.web_view.reload)
            b_home.clicked.connect(self.load_initial_url)

            layout.addWidget(self.web_view)
        else:
            layout.addWidget(QLabel("Error: WebEngine not found."))

    def load_initial_url(self):
        url = QUrl("https://www.uworld.com/app/index.html#/login")
        self.web_view.setUrl(url)

    def run_scan(self):
        # Scans for both Incorrect (.fa-times) and Correct (.fa-check)
        js_code = r"""
        (function() {
            let result = { missed: [], correct: [] };

            function getIDs(selector) {
                let ids = [];
                document.querySelectorAll(selector).forEach(icon => {
                    let row = icon.closest('tr') || icon.closest('.mat-row') || icon.closest('[role="row"]');
                    if (row) {
                        let text = row.innerText;
                        // Regex: Capture digits after the dash (e.g. "2 - 92" -> "92")
                        let match = text.match(/\d+\s*[-–—]\s*(\d+)/);
                        if (match && match[1]) {
                             ids.push(match[1]);
                        }
                    }
                });
                return [...new Set(ids)];
            }

            // 1. Get Incorrect (Red X)
            result.missed = getIDs('.fa-times');
            
            // 2. Get Correct (Green Check)
            result.correct = getIDs('.fa-check');

            return result;
        })();
        """
        self.web_view.page().runJavaScript(js_code, self.process_results)

    def process_results(self, data):
        if not data:
            tooltip("Scan complete. No data found.")
            return

        missed = data.get('missed', [])
        correct = data.get('correct', [])

        # PERSIST CORRECT IDs TO FILE
        added = save_correct_ids_to_file(correct)
        
        # Determine tooltip message
        msg = []
        if missed:
            msg.append(f"Found {len(missed)} missed.")
        else:
            msg.append("No missed questions.")
            
        if correct:
            msg.append(f"Saved {len(correct)} correct ({added} new).")
        
        # Show tooltip with summary
        tooltip("\n".join(msg))

        # Only show the Copy Dialog if there are missed questions
        if missed:
            ScanResultDialog(missed, mw).exec()

class UWorldPage(QWebEnginePage):
    def acceptNavigationRequest(self, u, t, m): return True
    def createWindow(self, t): return self

# ============================================================
# 6) Menu & Init
# ============================================================
uworld_dock = None
def toggle_sidebar():
    global uworld_dock
    if not uworld_dock:
        uworld_dock = UWorldDock(mw)
        mw.addDockWidget(DOCK_RIGHT, uworld_dock)
        uworld_dock.setFloating(False)
    
    # Simple toggle logic
    if uworld_dock.isVisible():
        uworld_dock.hide()
    else:
        uworld_dock.show()

def perform_scan():
    if uworld_dock and uworld_dock.isVisible():
        uworld_dock.run_scan()
    else:
        tooltip("Open sidebar first.")

uw_menu = None
for action in mw.form.menuTools.actions():
    if action.text() == "UWorld Helper": uw_menu = action.menu(); break
if not uw_menu: uw_menu = mw.form.menuTools.addMenu("UWorld Helper")

uw_menu.clear()

# 1. Toggle Sidebar
action_toggle = QAction("Toggle Sidebar", mw)
action_toggle.triggered.connect(toggle_sidebar)
uw_menu.addAction(action_toggle)

uw_menu.addSeparator()

# 2. Scan Test Results (Renamed + Shortcut)
action_scan = QAction("Scan Test Results", mw)
# Qt automatically maps "Ctrl" to "Command" on macOS
action_scan.setShortcut(QKeySequence("Ctrl+Shift+S"))
action_scan.triggered.connect(perform_scan)
uw_menu.addAction(action_scan)