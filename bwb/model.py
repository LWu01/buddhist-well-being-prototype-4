import csv
import datetime
import shutil
import sqlite3
import time
import enum

import bwb.bwbglobal

#################
#
# Model
#
# This module contains everything related to the model for the application:
# * The db schema
# * The db connection
# * Data structure classes (each of which contains functions for reading and writing to the db)
# * Database creation and setup
# * Various functions (for backing up the db etc)
#
# Notes:
# * When inserting vales, it's best to use "VALUES (?, ?)" because then the sqlite3 module will take care of
#   escaping strings for us
#
#################

# DATABASE_FILE_NAME = "bwb_database_file.db"
DATABASE_FILE_NAME = ":memory:"
SQLITE_FALSE = 0
SQLITE_TRUE = 1
TIME_NOT_SET = -1
NO_REFERENCE = -1


class QuestionSetupEnum(enum.Enum):
    gratitude = 1
    practice = 2
    livelihood = 3
    study = 4


def get_schema_version(i_db_conn):
    t_cursor = i_db_conn.execute("PRAGMA user_version")
    return t_cursor.fetchone()[0]


def set_schema_version(i_db_conn, i_version_it):
    i_db_conn.execute("PRAGMA user_version={:d}".format(i_version_it))


def initial_schema_and_setup(i_db_conn):
    """Auto-increment is not needed in our case: https://www.sqlite.org/autoinc.html
    """
    i_db_conn.execute(
        "CREATE TABLE " + DbSchemaM.QuestionTable.name + "("
        + DbSchemaM.QuestionTable.Cols.id + " INTEGER PRIMARY KEY, "
        + DbSchemaM.QuestionTable.Cols.title + " TEXT NOT NULL, "
        + DbSchemaM.QuestionTable.Cols.question + " TEXT NOT NULL DEFAULT '', "
        + DbSchemaM.QuestionTable.Cols.archived + " INTEGER DEFAULT " + str(SQLITE_FALSE)
        + ")"
    )

    i_db_conn.execute(
        "CREATE TABLE " + DbSchemaM.DiaryEntryTable.name + "("
        + DbSchemaM.DiaryEntryTable.Cols.id + " INTEGER PRIMARY KEY, "
        + DbSchemaM.DiaryEntryTable.Cols.date_added + " INTEGER, "
        + DbSchemaM.DiaryEntryTable.Cols.diary_entry + " TEXT, "
        + DbSchemaM.DiaryEntryTable.Cols.question_ref
        + " INTEGER REFERENCES " + DbSchemaM.QuestionTable.name
        + "(" + DbSchemaM.QuestionTable.Cols.id + ")"
        + " NOT NULL"
        + ")"
    )

    i_db_conn.execute(
        "CREATE TABLE " + DbSchemaM.ReminderTable.name + "("
        + DbSchemaM.ReminderTable.Cols.id + " INTEGER PRIMARY KEY, "
        + DbSchemaM.ReminderTable.Cols.title + " TEXT DEFAULT '', "
        + DbSchemaM.ReminderTable.Cols.reminder + " TEXT DEFAULT ''"
        + ")"
    )

    populate_db_with_test_data()


"""
Example of db upgrade code:
def upgrade_1_2(i_db_conn):
    backup_db_file()
    i_db_conn.execute(
        "ALTER TABLE " + DbSchemaM.ObservancesTable.name + " ADD COLUMN "
        + DbSchemaM.ObservancesTable.Cols.user_text + " TEXT DEFAULT ''"
    )
"""

upgrade_steps = {
    1: initial_schema_and_setup,
}


class DbHelperM(object):
    __db_connection = None  # "Static"

    # noinspection PyTypeChecker
    @staticmethod
    def get_db_connection():
        if DbHelperM.__db_connection is None:
            DbHelperM.__db_connection = sqlite3.connect(DATABASE_FILE_NAME)

            # Upgrading the database
            # Very good upgrade explanation:
            # http://stackoverflow.com/questions/19331550/database-change-with-software-update
            # More info here: https://www.sqlite.org/pragma.html#pragma_schema_version
            current_db_ver_it = get_schema_version(DbHelperM.__db_connection)
            target_db_ver_it = max(upgrade_steps)
            for upgrade_step_it in range(current_db_ver_it + 1, target_db_ver_it + 1):
                if upgrade_step_it in upgrade_steps:
                    upgrade_steps[upgrade_step_it](DbHelperM.__db_connection)
                    set_schema_version(DbHelperM.__db_connection, upgrade_step_it)
            DbHelperM.__db_connection.commit()

            # TODO: Where do we close the db connection? (Do we need to close it?)
            # http://stackoverflow.com/questions/3850261/doing-something-before-program-exit

        return DbHelperM.__db_connection


class DbSchemaM:
    class QuestionTable:
        name = "question"

        class Cols:
            id = "id"  # key
            title = "title"
            question = "question"
            archived = "archived"

    class DiaryEntryTable:
        name = "diary_entry"

        class Cols:
            id = "id"  # key
            date_added = "date_added"
            diary_entry = "diary_entry"
            question_ref = "question_ref"

    class ReminderTable:
        name = "reminder"

        class Cols:
            id = "id"  # key
            title = "title"
            reminder = "reminder"


class QuestionM:
    def __init__(self, i_id: int, i_title: str, i_question: str, i_archived: bool=False) -> None:
        self.id_int = i_id
        self.title_str = i_title
        self.question_str = i_question
        self.archived_bl = i_archived

    @staticmethod
    def add(i_title_str: str, i_question_str: str) -> None:
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.QuestionTable.name + "("
            + DbSchemaM.QuestionTable.Cols.title + ", "
            + DbSchemaM.QuestionTable.Cols.question
            + ") VALUES (?, ?)", (i_title_str, i_question_str)
        )
        db_connection.commit()

    @staticmethod
    def get(i_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.QuestionTable.name
            + " WHERE " + DbSchemaM.QuestionTable.Cols.id + "=" + str(i_id_it)
        )
        journal_db_te = db_cursor_result.fetchone()
        db_connection.commit()

        return QuestionM(*journal_db_te)

    @staticmethod
    def get_all():
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.QuestionTable.name
        )
        journal_db_te_list = db_cursor_result.fetchall()
        db_connection.commit()

        return [QuestionM(*journal_db_te) for journal_db_te in journal_db_te_list]


class DiaryM:
    def __init__(self, i_id, i_date_added_it, i_diary_text, i_question_ref_it):
        self.id = i_id
        self.date_added_it = i_date_added_it
        self.diary_text = i_diary_text
        self.question_ref_it = i_question_ref_it

    @staticmethod
    def add(i_date_added_it, i_diary_text, i_journal_ref_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.DiaryEntryTable.name + "("
            + DbSchemaM.DiaryEntryTable.Cols.date_added + ", "
            + DbSchemaM.DiaryEntryTable.Cols.diary_entry + ", "
            + DbSchemaM.DiaryEntryTable.Cols.question_ref
            + ") VALUES (?, ?, ?)",
            (i_date_added_it, i_diary_text, i_journal_ref_it)
        )
        db_connection.commit()

        # t_diary_id = db_cursor.lastrowid

    @staticmethod
    def update_note(i_id_it, i_new_text_sg):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE " + DbSchemaM.DiaryEntryTable.name
            + " SET " + DbSchemaM.DiaryEntryTable.Cols.diary_entry + " = ?"
            + " WHERE " + DbSchemaM.DiaryEntryTable.Cols.id + " = ?",
            (i_new_text_sg, str(i_id_it))
        )
        db_connection.commit()

    @staticmethod
    def update_date(i_id_it, i_new_time_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE " + DbSchemaM.DiaryEntryTable.name
            + " SET " + DbSchemaM.DiaryEntryTable.Cols.date_added + " = ?"
            + " WHERE " + DbSchemaM.DiaryEntryTable.Cols.id + " = ?",
            (str(i_new_time_it), str(i_id_it))
        )
        db_connection.commit()

    @staticmethod
    def remove(i_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "DELETE FROM " + DbSchemaM.DiaryEntryTable.name
            + " WHERE " + DbSchemaM.DiaryEntryTable.Cols.id + "=" + str(i_id_it)
        )
        db_connection.commit()

    @staticmethod
    def get(i_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryEntryTable.name + " WHERE "
            + DbSchemaM.DiaryEntryTable.Cols.id + "=" + str(i_id_it)
        )
        diary_db_te = db_cursor_result.fetchone()
        db_connection.commit()

        return DiaryM(*diary_db_te)

    @staticmethod
    def get_all(i_reverse_bl = False):  # -TODO: Change to for just one month
        t_direction_sg = "ASC"
        if i_reverse_bl:
            t_direction_sg = "DESC"
        ret_diary_list = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryEntryTable.name
            + " ORDER BY " + DbSchemaM.DiaryEntryTable.Cols.date_added + " " + t_direction_sg
        )
        diary_db_te_list = db_cursor_result.fetchall()
        for diary_db_te in diary_db_te_list:
            ret_diary_list.append(DiaryM(*diary_db_te))
        db_connection.commit()
        return ret_diary_list

    @staticmethod
    def get_all_for_question_and_month(i_question_id_it, i_start_of_month_as_unix_time_it,
                                       i_number_of_days_in_month_it, i_reverse_bl=True):
        ret_diary_list = []
        t_direction_sg = "DESC"
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryEntryTable.name
            + " WHERE " + DbSchemaM.DiaryEntryTable.Cols.date_added + ">=" + str(i_start_of_month_as_unix_time_it)
            + " AND " + DbSchemaM.DiaryEntryTable.Cols.date_added + "<"
            + str(i_start_of_month_as_unix_time_it + 24 * 3600 * i_number_of_days_in_month_it)
            + " AND " + DbSchemaM.DiaryEntryTable.Cols.question_ref + "=" + str(i_question_id_it)
            + " ORDER BY " + DbSchemaM.DiaryEntryTable.Cols.date_added + " " + t_direction_sg
        )
        diary_db_te_list = db_cursor_result.fetchall()
        for diary_db_te in diary_db_te_list:
            ret_diary_list.append(DiaryM(*diary_db_te))
        db_connection.commit()

        if i_reverse_bl:
            ret_diary_list.reverse()
        return ret_diary_list

    @staticmethod
    def get_all_for_active_day(i_reverse_bl=True):
        start_of_day_datetime = datetime.datetime(
            year=bwb.bwbglobal.active_date_qdate.year(),
            month=bwb.bwbglobal.active_date_qdate.month(),
            day=bwb.bwbglobal.active_date_qdate.day()
        )
        start_of_day_unixtime_it = int(start_of_day_datetime.timestamp())

        ret_diary_list = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryEntryTable.name
            + " WHERE " + DbSchemaM.DiaryEntryTable.Cols.date_added + ">=" + str(start_of_day_unixtime_it)
            + " AND " + DbSchemaM.DiaryEntryTable.Cols.date_added + "<" + str(start_of_day_unixtime_it + 24 * 3600)
        )
        diary_db_te_list = db_cursor_result.fetchall()
        for diary_db_te in diary_db_te_list:
            ret_diary_list.append(DiaryM(*diary_db_te))
        db_connection.commit()

        if i_reverse_bl:
            ret_diary_list.reverse()
        return ret_diary_list


class ReminderM:
    def __init__(self, i_id_int: int, i_title_str: str, i_reminder_str: str) -> None:
        self.id_int = i_id_int
        self.title_str = i_title_str
        self.reminder_str = i_reminder_str

    @staticmethod
    def add(i_title_str: str, i_reminder_str: str) -> None:
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.ReminderTable.name + "("
            + DbSchemaM.ReminderTable.Cols.title + ", "
            + DbSchemaM.ReminderTable.Cols.reminder
            + ") VALUES (?, ?)", (i_title_str, i_reminder_str)
        )

        db_connection.commit()

    @staticmethod
    def get(i_id_int: int):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.ReminderTable.name
            + " WHERE " + DbSchemaM.ReminderTable.Cols.id + "=" + str(i_id_int)
        )
        reminder_db_te = db_cursor_result.fetchone()
        db_connection.commit()

        return ReminderM(*reminder_db_te)

    @staticmethod
    def get_all():
        ret_reminder_list = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.ReminderTable.name
        )
        reminder_db_te_list = db_cursor_result.fetchall()
        for diary_db_te in reminder_db_te_list:
            ret_reminder_list.append(ReminderM(*diary_db_te))
        db_connection.commit()
        return ret_reminder_list

    @staticmethod
    def remove(i_id_int):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "DELETE FROM " + DbSchemaM.ReminderTable.name
            + " WHERE " + DbSchemaM.ReminderTable.Cols.id + "=" + str(i_id_int)
        )
        db_connection.commit()


def export_all():
    csv_writer = csv.writer(open("exported.csv", "w"))
    for diary_item in DiaryM.get_all():
        time_datetime = datetime.date.fromtimestamp(diary_item.date_added_it)
        date_str = time_datetime.strftime("%Y-%m-%d")
        csv_writer.writerow((date_str, diary_item.diary_text))


def backup_db_file():
    date_sg = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_file_name_sg = DATABASE_FILE_NAME + "_" + date_sg
    shutil.copyfile(DATABASE_FILE_NAME, new_file_name_sg)
    return


def populate_db_with_test_data():
    delta_day_it = 24 * 60 * 60

    QuestionM.add(
        QuestionSetupEnum.gratitude.name.capitalize(),
        "What posivite things came my way today? What did i do to water the seeds of joy in myself today?")
    QuestionM.add(
        QuestionSetupEnum.practice.name.capitalize(),
        "What practices did i do today? Sitting meditation? Walking meditation? Gathas?")
    QuestionM.add(
        QuestionSetupEnum.livelihood.name.capitalize(),
        "How did i contribute today to the well-being on others? On a personal plane? In a long-term way?")
    QuestionM.add(
        QuestionSetupEnum.study.name.capitalize(),
        "What did i read and listen to today and learn? Professionally? Dharma?")

    DiaryM.add(
        time.time(),
        "Dear Buddha, today i was practicing sitting meditation before meeting a friend of mine to be able to be more present during our meeting",
        QuestionSetupEnum.practice.value)
    DiaryM.add(
        time.time(),
        "Dear Buddha, i'm grateful for being able to breathe!",
        QuestionSetupEnum.gratitude.value)
    DiaryM.add(time.time() - delta_day_it,
        "Most difficult today was my negative thinking, practicing with this by changing the peg from negative thoughts to positive thinking",
        QuestionSetupEnum.practice.value)
    DiaryM.add(
        time.time() - 7 * delta_day_it,
        "Grateful for having a place to live, a roof over my head, food to eat, and people to care for",
        QuestionSetupEnum.gratitude.value)
    DiaryM.add(
        time.time() - 7 * delta_day_it,
        "Grateful for the blue sky and the white clouds",
        QuestionSetupEnum.gratitude.value)
    DiaryM.add(
        time.time() - 3 * delta_day_it,
        "Dear Buddha, today i read about the four foundations of mindfulness. Some important parts: 1. Body 2. Feelings 3. Mind 4. Objects of mind",
        QuestionSetupEnum.study.value)
    DiaryM.add(
        time.time() - 4 * delta_day_it,
        "Programming and working on the application. Using Python and Qt",
        QuestionSetupEnum.livelihood.value)
    DiaryM.add(
        time.time(),
        "Lecture by Tara Brach - Namaste. Soul recognition: Seeing (1) the vulnerability in ourselves and others, (2) the goodness, and (3) the conciousness. The Story of Sir Gawain and ____",
        QuestionSetupEnum.practice.value)

    ReminderM.add("Inter-being",
        "All things in the universe inter-are, our suffering and happiness inter-is with the suffernig and happiness of others")
    ReminderM.add("No Mud, no lotus",
        "A lotus flower cannot grow on marble!")

