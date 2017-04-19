from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import bwb.model


class CompositeCalendarWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        vbox_l2 = QtWidgets.QVBoxLayout()
        hbox_l3 = QtWidgets.QHBoxLayout()
        vbox_l2.addLayout(vbox_l2)
        self.setLayout(vbox_l2)

        self.calendar_widget = QtWidgets.QCalendarWidget()
        vbox_l2.addWidget(self.calendar_widget)
        self.calendar_widget.setGridVisible(True)
        #self.calendar_widget.currentPageChanged.connect(self.on_calendar_current_page_changed)
        #self.calendar_widget.selectionChanged.connect(self.on_calendar_selection_changed)

        self.today_qpb = QtWidgets.QPushButton()
        hbox_l3.addWidget(self.today_qpb)
        self.today_qpb.clicked.connect(self.on_today_button_clicked)

    def update_gui(self):
        date_qtextcharformat = QtGui.QTextCharFormat()
        date_qtextcharformat.setFontWeight(QtGui.QFont.Bold)

        for diarym in bwb.model.DiaryM.get_all():
            qdatetime = QtCore.QDateTime.fromMSecsSinceEpoch(diarym.date_added_it * 1000)
            self.calendar_widget.setDateTextFormat(qdatetime.date(), date_qtextcharformat)

    """
    def on_calendar_selection_changed(self):
        self.update_gui()
        self.change_signal.emit()

    def on_calendar_current_page_changed(self, i_year_int, i_month_int):
        logging.debug("year: " + str(i_year_int) + " month: " + str(i_month_int))
        self.update_gui()
        self.change_signal.emit()
    """

    def on_today_button_clicked(self):
        #self.calendar_widget.setSelectedDate()
        self.calendar_widget.showToday()
        self.update_gui()

