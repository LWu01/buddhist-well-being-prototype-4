
"""
Module comments:
Global vars are used for storing some of the global application states. Please don't use global vars for
storing other types of values
"""

import enum

from PyQt5 import QtCore


class ViewEnum(enum.Enum):
    diary_daily_overview = 0
    journal_monthly_view = 1


BWB_APPLICATION_VERSION_STR = "prototype 4"

active_view_viewenum = ViewEnum.diary_daily_overview
active_date_qdate = QtCore.QDate.currentDate()
active_question_id_it = 1  # -TODO: Change this
shown_month_1to12_it = QtCore.QDate.currentDate().month()
shown_year_it = QtCore.QDate.currentDate().year()


def qdate_to_unixtime(i_qdate: QtCore.QDate) -> int:
    qdatetime = QtCore.QDateTime(i_qdate)
    unixtime_it = qdatetime.toMSecsSinceEpoch() // 1000
    return unixtime_it


"""
def get_active_date():
    global active_date
    return active_date
def set_active_date(i_qdate):
    global active_date
    active_date = i_qdate
"""
