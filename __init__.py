# -*- coding: utf-8 -*-
import os
import sys
from aqt import mw
from aqt.qt import *
from aqt.utils import showText, tooltip

# ============================================================
# 0) COMPATIBILITY FIX: Qt5 vs Qt6 Enums
#    (Fixes 'Qt' has no attribute 'LeftDockWidgetArea' error)
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

def get_global_profile():
    """
    Creates a SINGLE persistent profile enforced with Disk Caching.
    This ensures login cookies are saved and loaded correctly every time.
    """
    global UWORLD_GLOBAL_PROFILE
    if UWORLD_GLOBAL_PROFILE is not None:
        return UWORLD_GLOBAL_PROFILE

    if not QWebEngineProfile:
        return None

    # 1. Storage Path: Inside the Add-on folder (cleaner & reliable)
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(addon_dir, "user_data")
    if not os.path.exists(data_dir):
        try: os.makedirs(data_dir)
        except: pass

    # 2. Create Profile attached to MW
    UWORLD_GLOBAL_PROFILE = QWebEngineProfile("UWorld_Disk_Auth", mw)
    
    # 3. FORCE DISK PERSISTENCE
    UWORLD_GLOBAL_PROFILE.setPersistentStoragePath(data_dir)
    UWORLD_GLOBAL_PROFILE.setCachePath(data_dir)
    
    if hasattr(QWebEngineProfile.HttpCacheType, "DiskHttpCache"):
        UWORLD_GLOBAL_PROFILE.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    
    if hasattr(QWebEngineProfile.PersistentCookiesPolicy, "ForcePersistentCookies"):
        UWORLD_GLOBAL_PROFILE.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

    # 4. User Agent & Settings
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    UWORLD_GLOBAL_PROFILE.setHttpUserAgent(ua)
    
    s = UWORLD_GLOBAL_PROFILE.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    return UWORLD_GLOBAL_PROFILE

# ============================================================
# 3) Result Dialog
# ============================================================
class ScanResultDialog(QDialog):
    def __init__(self, ids, parent=None):
        super().__init__(parent)
        self.setWindowTitle("UWorld Missed Questions")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Found <b>{len(ids)}</b> Missed Question IDs:"))
        
        self.text_area = QTextEdit()
        # Sort numerically
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
# 4) The UWorld Dock
# ============================================================
class UWorldDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("UWorld", parent)
        self.setObjectName("UWorldDock")
        # [FIX] Use the compatibility variables we defined at the top
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
            
            # 1. Get Global Profile
            self.profile = get_global_profile()
            self.page = UWorldPage(self.profile, self.web_view)
            self.web_view.setPage(self.page)
            
            # 2. DELAYED START: Wait 1.5s, then load Login
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
        # NEW STRATEGY: Look specifically for the "Index - QID" pattern (e.g. "2 - 92")
        # and capture ONLY the number after the dash.
        js_code = r"""
        (function() {
            let missedIDs = [];
            // 1. Find the "Red X" icons
            let icons = document.querySelectorAll('.fa-times');
            
            icons.forEach(icon => {
                // 2. Find the row
                let row = icon.closest('tr') || icon.closest('.mat-row') || icon.closest('[role="row"]');
                if (row) {
                    let text = row.innerText;
                    
                    // 3. REGEX TARGETING:
                    // Look for: [Digits] [Space] [Dash] [Space] [Digits]
                    // Capturing group (parentheses) around the SECOND number.
                    let match = text.match(/\d+\s*[-–—]\s*(\d+)/);
                    
                    if (match && match[1]) {
                         // match[1] is the QID (the part after the dash)
                         missedIDs.push(match[1]);
                    }
                }
            });
            return [...new Set(missedIDs)];
        })();
        """
        self.web_view.page().runJavaScript(js_code, self.process_results)

    def process_results(self, ids):
        if not ids:
            tooltip("Scan complete. No 'Incorrect' markers found.")
            return
        ScanResultDialog(ids, mw).exec()

class UWorldPage(QWebEnginePage):
    def acceptNavigationRequest(self, u, t, m): return True
    def createWindow(self, t): return self

# ============================================================
# 5) Menu & Init
# ============================================================
uworld_dock = None
def toggle_sidebar():
    global uworld_dock
    if not uworld_dock:
        uworld_dock = UWorldDock(mw)
        # [FIX] Use DOCK_RIGHT compatibility variable
        mw.addDockWidget(DOCK_RIGHT, uworld_dock)
        uworld_dock.setFloating(False)
    uworld_dock.setVisible(not uworld_dock.isVisible())

def perform_scan():
    if uworld_dock and uworld_dock.isVisible(): uworld_dock.run_scan()
    else: tooltip("Open sidebar first.")

uw_menu = None
for action in mw.form.menuTools.actions():
    if action.text() == "UWorld Helper": uw_menu = action.menu(); break
if not uw_menu: uw_menu = mw.form.menuTools.addMenu("UWorld Helper")

uw_menu.clear()
uw_menu.addAction(QAction("Toggle Sidebar", mw, triggered=toggle_sidebar))
uw_menu.addSeparator()
uw_menu.addAction(QAction("Scan for Missed Questions", mw, triggered=perform_scan))