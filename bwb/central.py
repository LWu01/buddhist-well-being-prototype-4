import logging
import bwb.diary
import bwb.model
from PyQt5 import QtCore
from PyQt5 import QtWidgets

import bwb.bwbglobal

ADD_NEW_HEIGHT_IT = 80
JOURNAL_BUTTON_GROUP_ID_INT = 1


class CompositeCentralWidget(QtWidgets.QWidget):

    journal_button_toggled_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        journalm_list = bwb.model.QuestionM.get_all()

        self.vbox_l2 = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox_l2)

        hbox_l3 = QtWidgets.QHBoxLayout()
        self.vbox_l2.addLayout(hbox_l3)
        self.diary_label = QtWidgets.QLabel()
        hbox_l3.addWidget(self.diary_label)

        hbox_l3.addStretch()
        self.view_radio_qbuttongroup = QtWidgets.QButtonGroup(self)
        # noinspection PyUnresolvedReferences
        self.view_radio_qbuttongroup.buttonToggled.connect(self.on_view_radio_button_toggled)
        self.day_view_qrb = QtWidgets.QRadioButton("Daily overview")
        self.day_view_qrb.setChecked(True)
        self.view_radio_qbuttongroup.addButton(self.day_view_qrb, bwb.bwbglobal.ViewEnum.diary_daily_overview.value)
        hbox_l3.addWidget(self.day_view_qrb)
        self.filter_view_qrb = QtWidgets.QRadioButton("Monthly question view")
        hbox_l3.addWidget(self.filter_view_qrb)
        self.lock_view_qpb = QtWidgets.QPushButton("Lock view")
        self.lock_view_qpb.setCheckable(True)
        self.view_radio_qbuttongroup.addButton(self.filter_view_qrb, bwb.bwbglobal.ViewEnum.journal_monthly_view.value)
        hbox_l3.addWidget(self.lock_view_qpb)

        # **Adding the diary**
        self.diary_widget = bwb.diary.DiaryListCompositeWidget()
        ##diary_widget.add_text_to_diary_button_pressed_signal.connect(self.on_diary_add_entry_button_pressed)
        self.diary_widget.context_menu_change_date_signal.connect(self.on_diary_context_menu_change_date)
        self.diary_widget.context_menu_delete_signal.connect(self.on_diary_context_menu_delete)
        self.vbox_l2.addWidget(self.diary_widget)

        # Adding new diary entry..
        adding_area_hbox_l3 = QtWidgets.QHBoxLayout()
        # ..question
        self.question_label = QtWidgets.QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setFixedWidth(200)
        adding_area_hbox_l3.addWidget(self.question_label)
        # ..text input area
        self.adding_text_to_diary_textedit_w6 = QtWidgets.QTextEdit()
        ###self.adding_text_to_diary_textedit_w6.setText("<i>New diary entry</i>")
        self.adding_text_to_diary_textedit_w6.setFixedHeight(ADD_NEW_HEIGHT_IT)
        adding_area_hbox_l3.addWidget(self.adding_text_to_diary_textedit_w6)
        # .."add new buttons"
        edit_diary_entry_vbox_l4 = QtWidgets.QVBoxLayout()
        ###diary_entry_label = QtWidgets.QLabel("<h4>New diary entry </h4>")
        ###edit_diary_entry_vbox_l4.addWidget(diary_entry_label)
        self.add_bn_w3 = QtWidgets.QPushButton("Add new diary entry")
        self.add_bn_w3.setFixedHeight(50)
        edit_diary_entry_vbox_l4.addWidget(self.add_bn_w3)
        # noinspection PyUnresolvedReferences
        self.add_bn_w3.clicked.connect(self.on_add_text_to_diary_button_clicked)
        self.add_and_next_qbn_w3 = QtWidgets.QPushButton("Add and Next")
        edit_diary_entry_vbox_l4.addWidget(self.add_and_next_qbn_w3)
        adding_area_hbox_l3.addLayout(edit_diary_entry_vbox_l4)

        self.vbox_l2.addLayout(adding_area_hbox_l3)

        self.update_gui()

    """
    def update_gui_journal_buttons(self):
        journalm_list = bwb_model.JournalM.get_all()
    """

    def on_view_radio_button_toggled(self):
        bwb.bwbglobal.active_view_viewenum = bwb.bwbglobal.ViewEnum(self.view_radio_qbuttongroup.checkedId())
        self.update_gui()

    def on_journal_button_toggled(self):
        bwb.bwbglobal.active_question_id_it = self.journal_qbuttongroup.checkedId()
        self.update_gui()
        self.journal_button_toggled_signal.emit()

    def update_gui(self):
        if bwb.bwbglobal.active_view_viewenum == bwb.bwbglobal.ViewEnum.journal_monthly_view:
            active_journalm = bwb.model.QuestionM.get(bwb.bwbglobal.active_question_id_it)
            self.diary_label.setText("<h3>" + active_journalm.title_sg + "</h3>")
        else:
            self.diary_label.setText("<h3>Daily Overview</h3>")
        self.diary_widget.update_gui()

    def on_diary_context_menu_change_date(self):
        self.update_gui()

    def on_diary_context_menu_delete(self):
        self.update_gui()

    def on_add_text_to_diary_button_clicked(self):
        notes_sg = self.adding_text_to_diary_textedit_w6.toPlainText().strip()
        if bwb.bwbglobal.active_date_qdate == QtCore.QDate.currentDate():
            time_qdatetime = QtCore.QDateTime.currentDateTime()
            unix_time_it = time_qdatetime.toMSecsSinceEpoch() // 1000
        else:
            unix_time_it = bwb.bwbglobal.qdate_to_unixtime(bwb.bwbglobal.active_date_qdate)

        logging.debug("t_unix_time_it = " + str(unix_time_it))

        bwb.model.DiaryM.add(unix_time_it, notes_sg, bwb.bwbglobal.active_question_id_it)
        # -TODO: Change from currentIndex
        self.adding_text_to_diary_textedit_w6.clear()
        self.update_gui()


"""
class CustomPushButton(QtWidgets.QWidget):
    def __init__(self, i_journal_name_str, i_journal_id_int):
        super.__init__(self, i_journal_name_str)
        self.journal_id_it = i_journal_id_int
"""
