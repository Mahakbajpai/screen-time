from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSystemTrayIcon, QMenu, QDialog, QSpinBox, QLabel, QDialogButtonBox
from PySide6.QtGui import QIcon
import sys, os
from PySide6.QtCore import QThread
from st_tracker.worker import TrackerWorker
from threading import Thread
from backend.api import run_api
from backend.database import init_db
from st_tracker import helper
import webbrowser


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "catto.ico")


class ThresholdDialog(QDialog):
    def __init__(self, current_value, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Idle Threshold")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        label_top = QLabel("Idle Threshold (seconds):")
        layout.addWidget(label_top)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(5, 3600) # Min 5s, Max 1hr
        self.spin_box.setValue(current_value)
        layout.addWidget(self.spin_box)

        self.label_note = QLabel("Note: This is the time the app waits before it considers you 'Away (AFK)'.\n"
            "If you don't move your mouse for this long, tracking stops.\n"
            "Min: 5s Max: 3600s (1hr)")
        self.label_note.setWordWrap(True)
        self.label_note.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.label_note)

        # 5. Add OK/Cancel Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_value(self):
        return self.spin_box.value()

class ButtonHolder(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Screen Time")
        self.setFixedSize(300, 200)

        saved_val = helper.read()

        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.handle_reset)

        btn_viewStats = QPushButton("View Stats")
        btn_viewStats.clicked.connect(self.handle_viewStats)

        btn_pause = QPushButton("Pause Tracking")
        btn_pause.clicked.connect(self.handle_pause)

        btn_resume = QPushButton("Resume Tracking")
        btn_resume.clicked.connect(self.handle_resume)

        btn_start = QPushButton("Start Tracking Again")
        btn_start.clicked.connect(self.handle_start)

        # Create the button
        btn_settings = QPushButton("Change Threshold Time")
        btn_settings.clicked.connect(self.handle_threshold)


        layout = QVBoxLayout()
        layout.addWidget(btn_pause)
        layout.addWidget(btn_resume)
        layout.addWidget(btn_start)
        layout.addWidget(btn_reset)
        layout.addWidget(btn_viewStats)
        layout.addWidget(btn_settings)
        

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.tray = QSystemTrayIcon(QIcon(ICON_PATH), self)
        self.tray.setToolTip("Screen Time Tracker")

        menu = QMenu()
        open_action = menu.addAction("Open")
        open_action.triggered.connect(self.show)

        reset_action = menu.addAction("Reset")
        reset_action.triggered.connect(self.handle_reset)

        vewiStats_action = menu.addAction("View Stats")
        vewiStats_action.triggered.connect(self.handle_viewStats)

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_app)


        self.tray.activated.connect(self.on_tray_activated)

        self.tray.setContextMenu(menu)
        self.tray.show()


        #Thread
        self.thread = QThread()
        self.worker = TrackerWorker(saved_val)

        #starting FastAPI
        self.api_thread = Thread(target=run_api, daemon=True)
        self.api_thread.start()
        print("FastAPI server started.")


        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def handle_pause(self):
        self.worker.pause()
        print("Tracking paused.")

    def handle_resume(self):
        self.worker.resume()
        print("Tracking resumed.")

    def handle_start(self):
        self.worker.reset()
        self.worker.resume()
        print("Tracking started fresh!")

    def handle_reset(self):
        self.worker.reset()
        print("Data reset!")

    def handle_viewStats(self):
        webbrowser.open("http://127.0.0.1:8000")

    def exit_app(self):
        self.worker.running = False
        self.tray.hide()
        QApplication.quit()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def handle_threshold(self):
        dialog = ThresholdDialog(self.worker.idle_threshold, self)
        
        if dialog.exec() == QDialog.Accepted:
            new_val = dialog.get_value()
            
            self.worker.idle_threshold = new_val
            helper.write(new_val)
            print(f"Threshold updated to {new_val}s")



app = QApplication(sys.argv)

window = ButtonHolder()
window.show()

app.exec()
