import enum
import sys
import logging

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import bwb.calendar
import bwb.central
import bwb.model
import bwb.questions
import bwb.wisdom
import bwb.bwbglobal


class EventSource(enum.Enum):
    undefined = -1
    obs_selection_changed = 1
    obs_current_row_changed = 2
    practice_details = 3


class WellBeingWindow(QtWidgets.QMainWindow):
    """
    The main window of the application
    Suffix explanation:
    _w: widget
    _l: layout
    _# (number): The level in the layout stack
    """
    # noinspection PyArgumentList,PyUnresolvedReferences
    def __init__(self):
        super().__init__()

        # Initializing window
        self.setGeometry(40, 30, 1100, 700)
        self.showMaximized()
        self.setWindowTitle("Buddhist Practice Diary [" + bwb.bwbglobal.BWB_APPLICATION_VERSION_STR + "]")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setStyleSheet("selection-background-color:#579e44")

        # Setup of widgets..
        # ..calendar
        calendar_dock_qdw2 = QtWidgets.QDockWidget("Calendar", self)
        calendar_dock_qdw2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        calendar_dock_qdw2.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.custom_calendar_w3 = bwb.calendar.CompositeCalendarWidget()
        self.custom_calendar_w3.setFixedHeight(200)
        self.custom_calendar_w3.calendar_widget.selectionChanged.connect(self.on_calendar_selection_changed)
        self.custom_calendar_w3.calendar_widget.currentPageChanged.connect(self.on_calendar_page_changed)
        calendar_dock_qdw2.setWidget(self.custom_calendar_w3)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, calendar_dock_qdw2)
        # ..reminders
        self.reminders_dock_qw2 = QtWidgets.QDockWidget("Journal Reminders", self)
        self.reminders_dock_qw2.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable)
        self.reminders_composite_w3 = bwb.questions.PracticeCompositeWidget()
        self.reminders_composite_w3.item_selection_changed_signal.connect(self.on_practice_item_selection_changed)
        self.reminders_composite_w3.current_row_changed_signal.connect(self.on_practice_current_row_changed)
        self.reminders_dock_qw2.setWidget(self.reminders_composite_w3)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.reminders_dock_qw2)
        # ..central widget (which **holds the diary** etc)
        self.central_widget_w3 = bwb.central.CompositeCentralWidget()
        self.setCentralWidget(self.central_widget_w3)
        self.central_widget_w3.journal_button_toggled_signal.connect(self.update_gui)
        # ..wisdom
        wisdom_dock_qw2 = QtWidgets.QDockWidget("Wisdom", self)
        self.wisdom_composite_w3 = bwb.wisdom.WisdomCompositeWidget()
        wisdom_dock_qw2.setWidget(self.wisdom_composite_w3)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, wisdom_dock_qw2)
        wisdom_dock_qw2.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

        # Creating the menu bar..
        # ..setup of actions
        export_qaction = QtWidgets.QAction("Export", self)
        export_qaction.triggered.connect(bwb.model.export_all)
        exit_qaction = QtWidgets.QAction("Exit", self)
        exit_qaction.triggered.connect(lambda x: sys.exit())
        redraw_qaction = QtWidgets.QAction("Redraw", self)
        redraw_qaction.triggered.connect(self.update_gui)
        about_qaction = QtWidgets.QAction("About", self)
        about_qaction.triggered.connect(self.show_about_box)
        manual_qaction = QtWidgets.QAction("Manual", self)
        ###inline_help_qaction = QtWidgets.QAction("Inline help", self)
        backup_qaction = QtWidgets.QAction("Backup db", self)
        backup_qaction.triggered.connect(bwb.model.backup_db_file)
        dear_buddha_qaction = QtWidgets.QAction("Prepend diary entries with \"Dear Buddha\"", self)
        dear_buddha_qaction.triggered.connect(self.toggle_dear_buddha_text)
        wisdom_window_qaction = wisdom_dock_qw2.toggleViewAction()
        # ..adding menu items
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("&File")
        debug_menu = self.menu_bar.addMenu("Debu&g")
        tools_menu = self.menu_bar.addMenu("&Tools")
        help_menu = self.menu_bar.addMenu("&Help")
        window_menu = self.menu_bar.addMenu("&Window")
        file_menu.addAction(export_qaction)
        file_menu.addAction(exit_qaction)
        debug_menu.addAction(redraw_qaction)
        debug_menu.addAction(backup_qaction)
        tools_menu.addAction(dear_buddha_qaction)
        help_menu.addAction(about_qaction)
        help_menu.addAction(manual_qaction)
        window_menu.addAction(wisdom_window_qaction)

        self.update_gui()

        """
        # ..practice details
        practice_details_dock_qw2 = QtWidgets.QDockWidget("Journal Details", self)
        self.practice_details_composite_w3 = bwb_practice_details.PracticeCompositeWidget()
        practice_details_dock_qw2.setWidget(self.practice_details_composite_w3)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, practice_details_dock_qw2)
        self.practice_details_composite_w3.time_of_day_state_changed_signal.connect(
            self.on_practice_details_time_of_day_state_changed)
        """
        # ..quotes
        # TODO: A stackedwidget, perhaps with two arrows above for going back and fwd (or just one to switch randomly)
        """
        # ..help
        help_dock_qw2 = QtWidgets.QDockWidget("Help", self)
        self.help_composite_w3 = bwb_help.HelpCompositeWidget()
        help_dock_qw2.setWidget(self.help_composite_w3)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, help_dock_qw2)
        """
        """
        # ..image
        image_qll = QtWidgets.QLabel()
        image_qll.setPixmap(QtGui.QPixmap("Gerald-G-Yoga-Poses-stylized-1-300px-CC0.png"))
        image_dock_qw2 = QtWidgets.QDockWidget("Image", self)
        image_dock_qw2.setWidget(image_qll)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, image_dock_qw2)
        """

    def toggle_dear_buddha_text(self):
        old_text_str = self.central_widget_w3.adding_text_to_diary_textedit_w6.toPlainText()
        new_text_str = "Dear Buddha, "
        if old_text_str.startswith(new_text_str):
            new_text_str_length_int = len(new_text_str)
            new_text_str = old_text_str[new_text_str_length_int:]
        self.central_widget_w3.adding_text_to_diary_textedit_w6.setText(new_text_str)

    def on_calendar_selection_changed(self):
        logging.debug("Selected date: " + str(self.custom_calendar_w3.calendar_widget.selectedDate()))
        bwb.bwbglobal.active_date_qdate = self.custom_calendar_w3.calendar_widget.selectedDate()
        self.update_gui()

    def on_calendar_page_changed(self):
        bwb.bwbglobal.shown_month_1to12_it = self.custom_calendar_w3.calendar_widget.monthShown()
        bwb.bwbglobal.shown_year_it = self.custom_calendar_w3.calendar_widget.yearShown()
        self.update_gui()

    def on_practice_details_time_of_day_state_changed(self):
        self.update_gui(EventSource.practice_details)

    def on_practice_current_row_changed(self, i_current_practice_row_it):
        current_practice_qlistitem = self.reminders_composite_w3.list_widget.item(i_current_practice_row_it)
        question_id_it = current_practice_qlistitem.data(QtCore.Qt.UserRole)
        bwb.bwbglobal.active_question_id_it = question_id_it
        question = bwb.model.QuestionM.get(question_id_it)
        self.central_widget_w3.question_label.setText(question.question_str)


        self.update_gui(EventSource.obs_current_row_changed)

    def on_practice_item_selection_changed(self):
        pass
        ###self.update_gui(EventSource.obs_selection_changed)  # Showing habits for practice etc

    def show_about_box(self):
        message_box = QtWidgets.QMessageBox.about(
            self, "About Buddhist Well-Being",
            ("Concept and programming by _____\n"
            'Photography (for icons) by Torgny Dellsén - <a href="torgnydellsen.zenfolio.com">asdf</a><br>'
            "Software License: GPLv3\n"
            "Photo license: CC BY-SA 4.0"
            "Art license: CC PD")
        )

    def update_gui(self, i_event_source = EventSource.undefined):
        if i_event_source == EventSource.practice_details:
            return

        self.central_widget_w3.update_gui()

        self.custom_calendar_w3.update_gui()

        if i_event_source != EventSource.obs_current_row_changed:
            self.reminders_composite_w3.update_gui()

        self.reminders_dock_qw2.setWindowTitle("Daily questions / rememberances")
