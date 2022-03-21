import sqlite3
import sys
import hashlib

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QFileDialog, QLabel, \
    QHBoxLayout
from pyqt5_plugins.examplebutton import QtWidgets
from PyQt5.QtGui import QPixmap

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class NoteWindow(QWidget):  # Виджет окна редактирования / создания новой заметки
    def __init__(self, userid=None, noteid=None):
        super().__init__()
        uic.loadUi('note.ui', self)

        self.noteid = noteid
        self.userid = userid
        self.notesdb = sqlite3.connect("notesdb.db")
        self.save_button.clicked.connect(self.save)
        self.add_img_button.clicked.connect(self.add_img)
        self.del_img_button.clicked.connect(self.del_img)
        self.cancel_button.clicked.connect(self.cancel)
        self.change_img_button.clicked.connect(self.change_img)
        self.show_img_button.clicked.connect(self.show_img)
        self.image_dir = None

        if self.noteid:  # Если это редектирование существующей заметки, то загружаем ее данные
            self.note = list(self.notesdb.execute(f"SELECT * FROM notes WHERE noteid = {self.noteid}"))[0]
            self.setWindowTitle(f'{self.note[3]} - редкатирование')
            self.title_line.setText(self.note[3])
            self.note_textedit.setText(self.note[2])
            self.image_dir = self.note[4]
            if (not self.image_dir) or (self.image_dir == 'None'):
                self.image_false()
            else:
                self.image_true()
        else:
            self.image_false()

    def image_true(self):  # Показываем необходимые кнопки, если существует путь к файлу с картинкой
        self.add_img_button.hide()
        if QPixmap(self.image_dir).isNull():  # Если изображения нет в папке назначения
            self.del_img_button.show()
            self.show_img_button.hide()
            self.change_img_button.show()
            self.image_status.setText('Изображение украли')
        else:
            self.pixmap = QPixmap(self.image_dir).scaled(100, 50, aspectRatioMode=True)  # Показываем превью изображения
            self.image_status.setPixmap(self.pixmap)
            self.del_img_button.show()
            self.show_img_button.show()
            self.change_img_button.show()

    def image_false(self):  # Если изображения нет, выключаем ненужные кнопки
        self.del_img_button.hide()
        self.show_img_button.hide()
        self.change_img_button.hide()
        self.image_status.setText('Изображения нет')

    def save(self):  # сохранение заметки
        if self.title_line.text().isspace() or self.title_line.text() == '':
            QMessageBox.critical(self, "Ошибка ", "Введите название заметки", QMessageBox.Ok)
        else:
            if self.noteid:
                self.notesdb.execute(f'''UPDATE notes SET
                                        notetext = '{self.note_textedit.toPlainText()}',
                                        notetitle = '{self.title_line.text()}',
                                        img_dir = '{self.image_dir}'
                                        WHERE noteid = {self.noteid};''')
            else:
                self.notesdb.execute(f'''INSERT INTO notes (id, notetext, notetitle, img_dir)
                                Values({self.userid}, '{self.note_textedit.toPlainText()}', 
                                '{self.title_line.text()}', '{self.image_dir}')''')
            self.notesdb.commit()
            self.notesdb.close()
            self.close()
            self.mainwnd = Window(self.userid)
            self.mainwnd.show()

    def cancel(self):  # Закрываем заметку и выходим главному окну
        self.close()
        self.mainwnd = Window(self.userid)
        self.mainwnd.show()

    def closeEvent(self, event):  # Переписываем закрытие заметки крестиком, чтобы не выйти из приложения
        self.cancel()

    def add_img(self):  # Добавляем изображение
        self.image_dir = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '.', "Изображения(*.jpg *.png)")[0]
        if self.image_dir:
            self.image_true()

    def change_img(self):  # Меняем изображение
        new_img = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '.', "Изображения(*.jpg *.png)")[0]
        if new_img:
            self.image_dir = new_img
            self.pixmap = QPixmap(self.image_dir).scaled(100, 50, aspectRatioMode=True)
            self.image_status.setPixmap(self.pixmap)

    def del_img(self):  # Удаялем изображение
        self.image_dir = None
        self.del_img_button.hide()
        self.show_img_button.hide()
        self.change_img_button.hide()
        self.add_img_button.show()
        self.image_status.setText('Изображения нет')

    def show_img(self):  # Показываем изображение
        self.img_wnd = ShowImage(self.image_dir)
        self.img_wnd.show()


class Window(QMainWindow):  # главное окно программы / список заметок пользователя с userid
    def __init__(self, userid=-1):
        super(Window, self).__init__()
        uic.loadUi('main_window.ui', self)

        self.userid = userid
        self.notesdb = sqlite3.connect("notesdb.db")
        self.refresh()

        self.user_change_button.clicked.connect(self.user_change)
        self.export_button.clicked.connect(self.data_export)
        self.new_note_button.clicked.connect(self.new_note)
        self.edit_note_button.clicked.connect(self.edit_note)
        self.delete_note_button.clicked.connect(self.delete_note)
        self.search_button.clicked.connect(self.search)
        self.discharge_button.clicked.connect(self.refresh)
        self.notes_list.itemDoubleClicked.connect(self.edit_note)
        self.change_user_action.triggered.connect(self.user_change)
        self.exit_action.triggered.connect(self.close)

    def user_change(self):  # Смена пользователя
        self.close()
        self.wcwnd = WelcomeWindow()
        self.wcwnd.show()

    def data_export(self):  # Сохраняем все заметки в текстовый файл
        new_file = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         "Сохранить файл",
                                                         ".",
                                                         "txt(*.txt)")
        try:
            export_file = open(new_file[0], 'w')
            file_text = [self.notes[i][3] + '\n' + self.notes[i][2] + '\n' for i in range(len(self.notes))]
            export_file.write('------\n'.join(file_text))
            export_file.close()
        except OSError:
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
        self.notesdb.execute(f"""DELETE FROM notes WHERE noteid = '{self.notes[self.notes_list.currentRow()][0]}'""")
        self.notesdb.commit()
        self.refresh()

    def search(self):
        self.request = self.search_line.text()
        self.req = list(
            self.notesdb.execute(f"SELECT * FROM notes WHERE id = {self.userid} AND notetext LIKE '%{self.request}%'"))
        self.notes_list.clear()
        if not self.req:
            self.notes_list.addItems(['Ничего не найдено'])
            self.notes_list.blockSignals(True)
        else:
            self.notes_list.blockSignals(False)
            self.notes_list.addItems([i[3] for i in self.req])

    def refresh(self):
        self.notes = list(self.notesdb.execute(f"SELECT * FROM notes WHERE id = {self.userid}"))
        self.notes_list.clear()
        self.notes_list.blockSignals(False)
        self.notes_list.addItems([i[3] for i in self.notes])

        if not self.notes:
            self.edit_note_button.setEnabled(False)
            self.edit_note_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.discharge_button.setEnabled(False)
            self.delete_note_button.setEnabled(False)
            self.export_button.setEnabled(False)


class WelcomeWindow(QWidget):  # окно выбора пользователя
    def __init__(self):
        super().__init__()
        uic.loadUi('welcome_window.ui', self)

        self.notesdb = sqlite3.connect("notesdb.db")
        self.refresh()

        self.start_button.clicked.connect(self.start)
        self.new_user_button.clicked.connect(self.new_user)
        self.delete_user_button.clicked.connect(self.delete_user)

    def start(self):  # Проверяем пароль
        self.close()
        self.psw_check = PasswordCheck(self.iddetect(self.usernames_box.currentText()))
        self.psw_check.show()

    def new_user(self):  # Создаем нового пользователя
        self.dialog = NewUserWindow()
        self.dialog.show()
        self.close()

    def delete_user(self):  # Удаляем пользователя и все его заметки из БД
        self.notesdb.execute(f"""DELETE FROM users where username = '{self.usernames_box.currentText()}'""")
        self.notesdb.execute(f"""DELETE FROM notes where id = '{self.iddetect(self.usernames_box.currentText())}'""")
        self.notesdb.commit()
        self.refresh()

    def refresh(self):  # Перерисовываем виджет, если были внесены изменения
        self.usernames = list(self.notesdb.execute("SELECT * FROM users"))
        self.usernames_box.clear()
        self.usernames_box.addItems([self.usernames[i][1] for i in range(len(self.usernames))])
        if not self.usernames:
            self.start_button.setEnabled(False)
            self.delete_user_button.setEnabled(False)
            self.usernames_box.setEnabled(False)

    def iddetect(self, searching_user):
        for user in self.usernames:
            if user[1] == searching_user:
                return user[0]


class NewUserWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('new_user_window.ui', self)
        self.notesdb = sqlite3.connect("notesdb.db")
        self.usernames = list(self.notesdb.execute("SELECT * FROM users"))
        self.buttonBox.accepted.connect(self.new_user)
        self.buttonBox.rejected.connect(self.cancel)
        self.wcwnd = WelcomeWindow()

    def new_user(self):
        self.new_user_name.setStyleSheet("")
        self.psw1_input.setStyleSheet("")
        self.psw2_input.setStyleSheet("")
        if self.new_user_name.text() == '':
            self.error_message.setText('Введите имя пользователя')
            self.new_user_name.setStyleSheet("border: 1px solid red")
        elif self.new_user_name.text() in [self.usernames[i][1] for i in range(len(self.usernames))]:
            self.new_user_name.setStyleSheet("border: 1px solid red")
            self.error_message.setText('Такой пользователь уже существует')
        elif self.psw1_input.text() != self.psw2_input.text():
            self.psw1_input.setStyleSheet("border: 1px solid red")
            self.psw2_input.setStyleSheet("border: 1px solid red")
            self.error_message.setText('Пароли не совпадают')
        elif self.psw1_input.text() == self.psw2_input.text() == '':
            self.psw1_input.setStyleSheet("border: 1px solid red")
            self.psw2_input.setStyleSheet("border: 1px solid red")
            self.error_message.setText('Введите пароль')
        elif len(self.psw1_input.text()) < 4:
            self.psw1_input.setStyleSheet("border: 1px solid red")
            self.psw2_input.setStyleSheet("border: 1px solid red")
            self.error_message.setText('Пароль слишком короткий')
        else:
            self.psw_hash = hashlib.sha256(bytes(self.psw1_input.text(), encoding='utf-8')).hexdigest()
            self.notesdb.execute(f'''INSERT INTO users (Username, psw_hash)
                                                Values('{self.new_user_name.text()}', 
                                                '{self.psw_hash}');''')
            self.notesdb.commit()
            self.notesdb.close()
            self.close()
            self.wcwnd = WelcomeWindow()
            self.wcwnd.show()

    def cancel(self):
        self.notesdb.close()
        self.close()
        self.wcwnd.show()

    def closeEvent(self, event):
        self.close()
        self.wcwnd.show()


class ShowImage(QWidget):
    def __init__(self, img_dir=None):
        super().__init__()
        self.img_dir = img_dir
        self.initUI()

    def initUI(self):
        self.pixmap = QPixmap(self.img_dir).scaled(500, 500, aspectRatioMode=True)
        self.setWindowTitle('Изображение ')
        self.image = QLabel(self)
        self.hbox = QHBoxLayout(self)
        self.image.setPixmap(self.pixmap)
        self.image.setScaledContents(True)
        self.hbox.addWidget(self.image)
        self.setLayout(self.hbox)
        self.image.setPixmap(self.pixmap)


class PasswordCheck(QWidget):  # Окно проверки пароля
    def __init__(self, userid=-1):
        super(PasswordCheck, self).__init__()
        uic.loadUi('psw_check.ui', self)

        self.userid = userid
        self.notesdb = sqlite3.connect("notesdb.db")
        self.psw_hash = list(self.notesdb.execute(f"""SELECT psw_hash
                                                FROM users
                                                WHERE id = {self.userid}"""))[0][0]
        self.enter_btn_box.accepted.connect(self.vreify)
        self.enter_btn_box.rejected.connect(self.cancel)

    def vreify(self):  # сравниваем хэш введенного пароля с хэшом выбранного пользователя
        if self.psw_hash == hashlib.sha256(bytes(self.psw_input.text(), encoding='utf-8')).hexdigest():
            self.mainwnd = Window(self.userid)
            self.mainwnd.show()
            self.close()
        else:
            self.psw_input.setStyleSheet("border: 1px solid red")
            self.error_message.setText('Неверный пароль')

    def cancel(self):
        self.close()
        self.wcwnd = WelcomeWindow()
        self.wcwnd.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wcwnd = WelcomeWindow()
    wcwnd.show()
    sys.exit(app.exec())
