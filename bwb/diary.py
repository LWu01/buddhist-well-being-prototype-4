import datetime
import time
import logging

import bwb.date_time_dialog
import bwb.model
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from bwb import bwbglobal

MY_WIDGET_NAME_STR = "test-name"
BACKGROUND_IMAGE_PATH_STR = "Gerald-G-Yoga-Poses-stylized-1-300px-CC0.png"
NO_ENTRY_CLICKED_INT = -1


# noinspection PyArgumentList
class DiaryListCompositeWidget(QtWidgets.QWidget):
    """
    Inspiration for this class:
    http://stackoverflow.com/questions/20041385/python-pyqt-setting-scroll-area
    """

    context_menu_change_date_signal = QtCore.pyqtSignal()
    context_menu_delete_signal = QtCore.pyqtSignal()

    last_entry_clicked_id_it = NO_ENTRY_CLICKED_INT

    def __init__(self):
        super().__init__()

        self.vbox_l2 = QtWidgets.QVBoxLayout()
        self.scroll_area_w3 = QtWidgets.QScrollArea()
        self.scroll_area_w3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area_w3.setWidgetResizable(True)
        self.scroll_list_widget_w4 = QtWidgets.QWidget()
        self.scroll_list_widget_w4.setObjectName(MY_WIDGET_NAME_STR)
        self.scroll_list_widget_w4.setStyleSheet("#" + MY_WIDGET_NAME_STR
             + "{" + "background-image:url(\"" + BACKGROUND_IMAGE_PATH_STR
             + "\"); background-position:center; background-repeat:no-repeat" + "}")
        self.scroll_list_vbox_l5 = QtWidgets.QVBoxLayout()

        self.scroll_list_widget_w4.setLayout(self.scroll_list_vbox_l5)
        self.scroll_area_w3.setWidget(self.scroll_list_widget_w4)
        self.vbox_l2.addWidget(self.scroll_area_w3)
        self.setLayout(self.vbox_l2)

    # The same function is used for all the "rows"
    def on_custom_label_mouse_pressed(self, i_qmouseevent, i_diary_id_it):
        logging.debug("button clicked: " + str(i_qmouseevent.button()))
        logging.debug("diary id: " + str(i_diary_id_it))
        self.last_entry_clicked_id_it = i_diary_id_it

    # noinspection PyUnresolvedReferences
    def contextMenuEvent(self, i_qcontextmenuevent):
        """
        Overridden
        Docs: http://doc.qt.io/qt-5/qwidget.html#contextMenuEvent
        """
        self.right_click_menu = QtWidgets.QMenu()
        rename_action = QtWidgets.QAction("Rename")
        rename_action.triggered.connect(self.on_context_menu_rename)
        self.right_click_menu.addAction(rename_action)
        delete_action = QtWidgets.QAction("Delete")
        delete_action.triggered.connect(self.on_context_menu_delete)
        self.right_click_menu.addAction(delete_action)
        change_date_action = QtWidgets.QAction("Change date")
        change_date_action.triggered.connect(self.on_context_menu_change_date)
        self.right_click_menu.addAction(change_date_action)
        self.right_click_menu.exec_(QtGui.QCursor.pos())

    def on_context_menu_delete(self):
        message_box_reply = QtWidgets.QMessageBox.question(
            self, "Remove diary entry?", "Are you sure that you want to remove this diary entry?"
        )
        if message_box_reply == QtWidgets.QMessageBox.Yes:
            bwb.model.DiaryM.remove(int(self.last_entry_clicked_id_it))
            self.update_gui()
            self.context_menu_delete_signal.emit()
        else:
            pass  # -do nothing

    def on_context_menu_rename(self):
        """
        Docs: http://doc.qt.io/qt-5/qinputdialog.html#getText
        """
        last_clicked_row_dbkey_it = int(self.last_entry_clicked_id_it)
        diary_entry = bwb.model.DiaryM.get(last_clicked_row_dbkey_it)
        text_input_dialog = QtWidgets.QInputDialog()
        new_text_qstring = text_input_dialog.getText(
            self, "Rename dialog", "New name: ", text=diary_entry.diary_text)
        if new_text_qstring[0]:
            logging.debug("new_text_qstring = " + str(new_text_qstring))
            bwb.model.DiaryM.update_note(last_clicked_row_dbkey_it, new_text_qstring[0])
            self.update_gui()
        else:
            pass  # -do nothing

    def on_context_menu_change_date(self):
        last_clicked_row_dbkey_it = int(self.last_entry_clicked_id_it)
        diary_item = bwb.model.DiaryM.get(last_clicked_row_dbkey_it)
        updated_time_unix_time_it = bwb.date_time_dialog.DateTimeDialog.get_date_time_dialog(diary_item.date_added_it)
        if updated_time_unix_time_it != -1:
            bwb.model.DiaryM.update_date(diary_item.id, updated_time_unix_time_it)
            self.update_gui()
            self.context_menu_change_date_signal.emit()
        else:
            pass  # -do nothing

    def update_gui(self):
        clear_widget_and_layout_children(self.scroll_list_vbox_l5)
        qdate = QtCore.QDate(bwbglobal.shown_year_it, bwbglobal.shown_month_1to12_it, 1)
        qdatetime = QtCore.QDateTime(qdate)
        start_of_month_as_unix_time_it = qdatetime.toMSecsSinceEpoch() // 1000

        diarym_list = []
        if bwbglobal.active_view_viewenum == bwbglobal.ViewEnum.journal_monthly_view:
            diarym_list = bwb.model.DiaryM.get_all_for_question_and_month(
                bwbglobal.active_question_id_it, start_of_month_as_unix_time_it, qdate.daysInMonth())
        elif bwbglobal.active_view_viewenum == bwbglobal.ViewEnum.diary_daily_overview:
            diarym_list = bwb.model.DiaryM.get_all_for_active_day()
        else:
            pass

        old_date_str = ""
        for diary_entry in diarym_list:
            label_text_sg = diary_entry.diary_text.strip()

            hbox_l6 = QtWidgets.QHBoxLayout()
            self.scroll_list_vbox_l5.addLayout(hbox_l6)

            date_string_format_str = "%A"  # -weekday
            if diary_entry.date_added_it < time.time() - 60 * 60 * 24 * 7:
                date_string_format_str = "%-d %b"  # -weekday

            left_qlabel = QtWidgets.QLabel("")
            if bwbglobal.active_view_viewenum == bwbglobal.ViewEnum.journal_monthly_view:
                date_str = datetime.datetime.fromtimestamp(diary_entry.date_added_it).strftime(
                    date_string_format_str)
                if old_date_str == date_str:
                    left_qlabel.setText("")
                elif is_same_day(diary_entry.date_added_it, time.time()):
                    left_qlabel.setText("Today")
                else:
                    left_qlabel.setText(date_str)
                old_date_str = date_str
            elif bwbglobal.active_view_viewenum == bwbglobal.ViewEnum.diary_daily_overview:
                journalm = bwb.model.QuestionM.get(diary_entry.question_ref_it)
                journal_sg = str(journalm.title_sg)
                left_qlabel = QtWidgets.QLabel(journal_sg)
            else:
                pass

            hbox_l6.addWidget(left_qlabel, stretch=1)

            listitem_cqll = CustomQLabel(label_text_sg, diary_entry.id)
            listitem_cqll.setWordWrap(True)
            listitem_cqll.mouse_pressed_signal.connect(self.on_custom_label_mouse_pressed)

            hbox_l6.addWidget(listitem_cqll, stretch=5)

            hbox_l6.addWidget(QtWidgets.QLabel("tags here"), stretch=1)

        self.scroll_list_vbox_l5.addStretch()

        # TODO: Scroll to bottom


def is_same_day(i_first_date_it, i_second_date_it):
    first_date = datetime.datetime.fromtimestamp(i_first_date_it)
    second_date = datetime.datetime.fromtimestamp(i_second_date_it)
    return first_date.date() == second_date.date()  # - == operator works for "datetime" type


def clear_widget_and_layout_children(qlayout_or_qwidget):
    if qlayout_or_qwidget.widget():
        qlayout_or_qwidget.widget().deleteLater()
    elif qlayout_or_qwidget.layout():
        while qlayout_or_qwidget.layout().count():
            child_qlayoutitem = qlayout_or_qwidget.takeAt(0)
            clear_widget_and_layout_children(child_qlayoutitem)  # Recursive call


class CustomQLabel(QtWidgets.QLabel):
    NO_DIARY_ENTRY_SELECTED = -1
    diary_entry_id = NO_DIARY_ENTRY_SELECTED
    mouse_pressed_signal = QtCore.pyqtSignal(QtGui.QMouseEvent, int)

    def __init__(self, i_text_sg, i_diary_entry_id=NO_DIARY_ENTRY_SELECTED):
        super().__init__(i_text_sg)
        self.diary_entry_id = i_diary_entry_id

    # Overridden
    # Please note that this is the event handler (not an event!)
    def mousePressEvent(self, i_qmouseevent):
        ### super(CustomQLabel, self).mousePressEvent(i_qmouseevent)
        self.mouse_pressed_signal.emit(i_qmouseevent, self.diary_entry_id)
