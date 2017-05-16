from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import bwb.model

'''
vbox_l2 = vertical box layout level 2
hbox_l3 = horizontal box layout level 3
today_qpb = push button on calendar for date currently being viewed
'''

class CompositeCalendarWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        vbox_l2 = QtWidgets.QVBoxLayout() #creates widget vbox_l2
        #moved hbox_l3 = QtWidgets.QHBoxLayout() #creates widget hbox_l3 to line 29 where it is initialized
        vbox_l2.addLayout(vbox_l2) #add vertical layout for calendar
        self.setLayout(vbox_l2) #set vertical layout for calendar

        self.calendar_widget = QtWidgets.QCalendarWidget() #creates calendar widget
        vbox_l2.addWidget(self.calendar_widget) #holds calendar widget in the vbox_l2
        self.calendar_widget.setGridVisible(True) #sets caledar view
        #self.calendar_widget.currentPageChanged.connect(self.on_calendar_current_page_changed)
        #self.calendar_widget.selectionChanged.connect(self.on_calendar_selection_changed)

        self.today_qpb = QtWidgets.QPushButton()#creates button for each calendar day
        hbox_l3 = QtWidgets.QHBoxLayout()  # creates widget hbox_l3 for holding each day
        hbox_l3.addWidget(self.today_qpb)#buttons held in hbox_l3
        self.today_qpb.clicked.connect(self.on_today_button_clicked)#sets buttons on calendar

#for graphics part
    def update_gui(self):
        date_qtextcharformat = QtGui.QTextCharFormat()
        date_qtextcharformat.setFontWeight(QtGui.QFont.Bold)

#for entries being added to diary
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

