import sqlite3
import sys
import logging

import PyQt5
from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import bwb.model
import bwb.bwbglobal
import bwb.window


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = bwb.window.WellBeingWindow()

    # System tray
    tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("icon.png"), app)
    tray_menu = QtWidgets.QMenu()
    tray_restore_action = QtWidgets.QAction("Restore")
    # noinspection PyUnresolvedReferences
    tray_restore_action.triggered.connect(main_window.show)
    tray_menu.addAction(tray_restore_action)
    tray_quit_action = QtWidgets.QAction("Quit")
    # noinspection PyUnresolvedReferences
    tray_quit_action.triggered.connect(sys.exit)
    tray_menu.addAction(tray_quit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    logging.info("===== Starting Buddhist Well-Being - " + bwb.bwbglobal.BWB_APPLICATION_VERSION_STR + " =====")
    logging.info("Python version: " + str(sys.version))
    logging.info("SQLite version: " + str(sqlite3.sqlite_version))
    logging.info("PySQLite (Python module) version: " + str(sqlite3.version))
    logging.info("Qt version: " + str(QtCore.qVersion()))
    logging.info("PyQt (Python module) version: " + str(PyQt5.Qt.PYQT_VERSION_STR))
    logging.info("Buddhist Well-Being application version: " + str(bwb.bwbglobal.BWB_APPLICATION_VERSION_STR))
    db_conn = bwb.model.DbHelperM.get_db_connection()
    logging.info("Buddhist Well-Being database schema version: " + str(bwb.model.get_schema_version(db_conn)))
    logging.info("=====")

    sys.exit(app.exec_())
