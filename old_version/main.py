import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from pyqt5_plugins.examplebutton import QtWidgets
from new_user_window import Ui_new_user_window
from main_window import Ui_MainWindow
from welcome_window import Ui_Welcome_window
from note import Ui_Form


class NoteWindow(QWidget, Ui_Form):
    def __init__(self, userid=None, noteid=None):
        super().__init__()
        self.setupUi(self)

        self.noteid = noteid
        self.userid = userid
        self.notesdb = sqlite3.connect("notesdb.db")
        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.cancel)

        if self.noteid:
            self.note = list(self.notesdb.execute(f"SELECT * FROM notes WHERE noteid = {self.noteid}"))[0]
            print(self.note)
            self.setWindowTitle(f'{self.note[3]} - редкатирование')
            self.title_line.setText(self.note[3])
            self.note_textedit.setText(self.note[2])

    def save(self):
        if self.noteid:
            self.notesdb.execute(f'''UPDATE notes SET
                                    notetext = '{self.note_textedit.toPlainText()}',
                                    notetitle = '{self.title_line.text()}'
                                    WHERE noteid = {self.noteid};''')
        else:
            self.notesdb.execute(f'''INSERT INTO notes (id, notetext, notetitle)
                            Values({self.userid}, '{self.note_textedit.toPlainText()}', '{self.title_line.text()}');''')
        self.notesdb.commit()
        self.notesdb.close()
        self.close()
        self.mainwnd = Window(self.userid)
        self.mainwnd.show()

    def cancel(self):
        self.close()
        self.mainwnd = Window(self.userid)
        self.mainwnd.show()


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, userid=-1):
        super(Window, self).__init__()
        self.setupUi(self)

        self.userid = userid
        self.notesdb = sqlite3.connect("notesdb.db")
        self.notes = list(self.notesdb.execute(f"SELECT * FROM notes WHERE id = {self.userid}"))
        self.notes_list.addItems([i[3] for i in self.notes])

        self.user_change_button.clicked.connect(self.user_change)
        self.export_button.clicked.connect(self.data_export)
        self.new_note_button.clicked.connect(self.new_note)
        self.edit_note_button.clicked.connect(self.edit_note)
        self.delete_note_button.clicked.connect(self.delete_note)
        self.search_button.clicked.connect(self.search)
        self.discharge_button.clicked.connect(self.refresh)

        if not self.notes:
            self.edit_note_button.setEnabled(False)
            self.edit_note_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.discharge_button.setEnabled(False)
            self.delete_note_button.setEnabled(False)
            self.export_button.setEnabled(False)

    def user_change(self):
        self.close()
        self.wcwnd = WelcomeWindow()
        self.wcwnd.show()

    def data_export(self):
        self.new_file = QtWidgets.QFileDialog.getSaveFileName(self,
                                    "Сохранить файл",
                                    ".",
                                    "TXT(*.txt)")
        try:
            self.export_file = open(self.new_file[0], 'w')
            self.file_text = [self.notes[i][3] + '\n' + self.notes[i][2] + '\n' for i in range(len(self.notes))]
            self.export_file.write('------\n'.join(self.file_text))
            self.export_file.close()
        except:
            pass

    def new_note(self):
        self.nnwnd = NoteWindow(self.userid)
        self.nnwnd.show()
        self.close()

    def edit_note(self):
        self.nnwnd = NoteWindow(self.userid, self.notes[self.notes_list.currentRow()][0])
        self.nnwnd.show()
        self.close()

    def delete_note(self):
        self.notesdb.execute(f"""DELETE FROM notes where noteid = '{self.notes[self.notes_list.currentRow()][0]}'""")
        self.notesdb.commit()
        self.refresh()

    def search(self):
        self.request = self.search_line.text()
        self.req = list(self.notesdb.execute(f"SELECT * FROM notes WHERE id = {self.userid} "
                                             f"AND notetext LIKE '%{self.request}%'"))
        self.notes_list.clear()
        self.notes_list.addItems([i[3] for i in self.req])

    def refresh(self):
        self.close()
        self.wcwnd = Window(self.userid)
        self.wcwnd.show()


class WelcomeWindow(QWidget, Ui_Welcome_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.notesdb = sqlite3.connect("notesdb.db")
        self.usernames = dict(self.notesdb.execute("SELECT * FROM users"))
        self.usernames_box.addItems(list(map(str, self.usernames.values())))
        self.start_button.clicked.connect(self.start)
        self.new_user_button.clicked.connect(self.new_user)
        self.delete_user_button.clicked.connect(self.delete_user)
        if not self.usernames:
            self.start_button.setEnabled(False)
            self.delete_user_button.setEnabled(False)
            self.usernames_box.setEnabled(False)

    def start(self):
        self.close()
        self.mainwnd = Window(self.iddetect(self.usernames_box.currentText()))
        self.mainwnd.show()

    def new_user(self):
        self.dialog = NewUserWindow()
        self.dialog.show()
        self.close()

    def delete_user(self):
        self.notesdb.execute(f"""DELETE FROM users where username = '{self.usernames_box.currentText()}'""")
        self.notesdb.execute(f"""DELETE FROM notes where id = '{self.iddetect(self.usernames_box.currentText())}'""")
        self.notesdb.commit()
        self.refresh()

    def refresh(self):
        self.close()
        self.wcwnd = WelcomeWindow()
        self.wcwnd.show()

    def iddetect(self, user):
        for id, search_user in self.usernames.items():
            if search_user == user:
                return id


class NewUserWindow(QWidget, Ui_new_user_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.notesdb = sqlite3.connect("notesdb.db")
        self.usernames = dict(self.notesdb.execute("SELECT * FROM users"))
        self.buttonBox.accepted.connect(self.new_user)
        self.buttonBox.rejected.connect(self.cancel)
        self.wcwnd = WelcomeWindow()

    def new_user(self):
        if self.new_user_name.text() == '':
            self.error_message.setText('Введите имя пользователя')

        elif self.new_user_name.text() in self.usernames.values():
            self.error_message.setText('Такой пользователь уже существует')
        else:
            self.notesdb.execute(f'''INSERT INTO users (Username)
                                                Values('{self.new_user_name.text()}');''')
            self.notesdb.commit()
            self.notesdb.close()
            self.close()
            self.wcwnd = WelcomeWindow()
            self.wcwnd.show()

    def cancel(self):
        self.notesdb.close()
        self.close()
        self.wcwnd.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wcwnd = WelcomeWindow()
    wcwnd.show()
    sys.exit(app.exec())
