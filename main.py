import sys
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta

class CustomButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(CustomButton, self).__init__(*args, **kwargs)

    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))
        super(CustomButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
        super(CustomButton, self).leaveEvent(event)

class FirstWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 300, 600, 400)  # Увеличенные размеры
        self.setMinimumSize(600, 400)  # Увеличенные минимальные размеры
        self.setWindowTitle('Вход в систему')

        self.register_button = CustomButton('Зарегистрироваться', self)
        self.label_login = QLabel('Введите логин:', self)
        self.login_input = QLineEdit(self)
        self.login_input.setMaxLength(10)
        self.login_input.setClearButtonEnabled(True)
        self.label_password = QLabel('Введите пароль:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setMaxLength(15)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setClearButtonEnabled(True)
        self.login_button = CustomButton('Войти', self)

        self.login_button.clicked.connect(self.login) #при нажатии кнопки вызывает функцию login
        self.register_button.clicked.connect(self.register) #при нажатии кнопки вызывает функцию register

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_login, alignment=Qt.AlignCenter)
        vbox.addWidget(self.login_input, alignment=Qt.AlignCenter)
        vbox.addWidget(self.label_password, alignment=Qt.AlignCenter)
        vbox.addWidget(self.password_input, alignment=Qt.AlignCenter)
        vbox.addWidget(self.login_button, alignment=Qt.AlignCenter)
        vbox.addWidget(self.register_button, alignment=Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(vbox)
        self.setLayout(main_layout)

        self.connection = sqlite3.connect('test.db') #подключение к базе данных test.db
        self.create_tables()

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        scaling_factor = min(width / 400, height / 200)
        new_font_size = int(12 * scaling_factor)
        new_button_size = QSize(int(150 * scaling_factor), int(30 * scaling_factor))

        self.register_button.setFixedSize(new_button_size)
        self.register_button.setStyleSheet(f"font-size: {new_font_size}px; border-radius: 10px;")
        self.login_button.setFixedSize(new_button_size)
        self.login_button.setStyleSheet(f"font-size: {new_font_size}px; border-radius: 10px;")
        self.login_input.setFixedSize(int(150 * scaling_factor), int(30 * scaling_factor))
        self.login_input.setStyleSheet(f"font-size: {new_font_size}px; border-radius: 5px;")
        self.password_input.setFixedSize(int(150 * scaling_factor), int(30 * scaling_factor))
        self.password_input.setStyleSheet(f"font-size: {new_font_size}px; border-radius: 5px;")
        self.label_login.setStyleSheet(f"font-size: {new_font_size}px;")
        self.label_password.setStyleSheet(f"font-size: {new_font_size}px;")

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth (
                login TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                is_realtor INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price REAL NOT NULL,
                area REAL NOT NULL,
                rooms INTEGER NOT NULL,
                address TEXT NOT NULL,
                floor INTEGER NOT NULL,
                photo BLOB
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartment_id INTEGER NOT NULL,
                user_login TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                phone TEXT,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id),
                FOREIGN KEY (user_login) REFERENCES auth (login)
            )
        ''')
        self.connection.commit()

    def get_is_realtor(self, login):
        cursor = self.connection.cursor()
        cursor.execute('SELECT is_realtor FROM auth WHERE login=?', (login,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM auth WHERE login=? AND password=?', (login, password))

        if cursor.fetchone():
            print(f'Успешный вход: Логин: {login}, Пароль: {password}')
            if login == "bazan":
                self.out_window = Admin(self.connection)  #передаем соединение
                self.out_window.show()
                self.close()
            elif self.get_is_realtor(login) == 1:
                self.out_window = Realtor(self.connection)  # передаем соединение
                self.out_window.show()
                self.close()
            else:
                self.out_window = Polzovatel(self.connection, login)  # передаем соединение и логин пользователя
                self.out_window.show()
                self.close()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def register(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Логин и пароль не могут быть пустыми')
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute('INSERT INTO auth (login, password) VALUES (?, ?)', (login, password))
            self.connection.commit()
            QMessageBox.information(self, 'Успех', 'Регистрация прошла успешно')
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, 'Ошибка', 'Логин уже занят')


class Admin(QWidget):
    def __init__(self, connection):  # Принимаем соединение
        super().__init__()
        self.connection = connection  # Сохраняем соединение
        self.setWindowTitle('Панель администратора')
        self.setGeometry(700, 300, 600, 400)  # Увеличенные размеры
        self.setMinimumSize(600, 400)  # Увеличенные минимальные размеры

        self.user_list = QListWidget(self)
        self.load_users()

        self.add_realtor_button = CustomButton('Сделать риелтором', self)
        self.remove_realtor_button = CustomButton('Убрать риелтора', self)
        self.delete_user_button = CustomButton('Удалить пользователя', self)

        self.add_realtor_button.clicked.connect(self.add_realtor)
        self.remove_realtor_button.clicked.connect(self.remove_realtor)
        self.delete_user_button.clicked.connect(self.delete_user)

        vbox = QVBoxLayout()
        vbox.addWidget(self.user_list)
        vbox.addWidget(self.add_realtor_button)
        vbox.addWidget(self.remove_realtor_button)
        vbox.addWidget(self.delete_user_button)

        self.setLayout(vbox)

    def load_users(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT login, is_realtor FROM auth')
        users = cursor.fetchall()
        self.user_list.clear()
        for login, is_realtor in users:
            status = 'Риелтор' if is_realtor else 'Пользователь'
            self.user_list.addItem(f"{login} ({status})")

    def add_realtor(self):
        selected_item = self.user_list.currentItem()
        if selected_item:
            login = selected_item.text().split(' ')[0]
            cursor = self.connection.cursor()
            cursor.execute('UPDATE auth SET is_realtor=1 WHERE login=?', (login,))
            self.connection.commit()
            self.load_users()

    def remove_realtor(self):
        selected_item = self.user_list.currentItem()
        if selected_item:
            login = selected_item.text().split(' ')[0]
            cursor = self.connection.cursor()
            cursor.execute('UPDATE auth SET is_realtor=0 WHERE login=?', (login,))
            self.connection.commit()
            self.load_users()

    def delete_user(self):
        selected_item = self.user_list.currentItem()
        if selected_item:
            login = selected_item.text().split(' ')[0]
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM auth WHERE login=?', (login,))
            self.connection.commit()
            self.load_users()
            QMessageBox.information(self, 'Успех', 'Пользователь успешно удален')

class ApartmentWidget(QWidget):
    def __init__(self, connection, apartment_id, price, area, rooms, address, floor, photo, user_login):
        super().__init__()
        self.connection = connection
        self.apartment_id = apartment_id
        self.user_login = user_login

        self.photo_label = QLabel(self)
        if photo:
            pixmap = QPixmap()
            pixmap.loadFromData(photo)
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("Фото отсутствует")

        self.info_label = QLabel(f"Цена: {price}, площадь: {area}, комнат: {rooms}, этаж: {floor}, адрес: {address}", self)
        self.book_button = CustomButton('Забронировать встречу', self)
        self.book_button.clicked.connect(self.book_meeting)

        vbox = QVBoxLayout()
        vbox.addWidget(self.photo_label, alignment=Qt.AlignCenter)
        vbox.addWidget(self.info_label)
        vbox.addWidget(self.book_button)

        self.setLayout(vbox)

    def generate_dates(self):
        dates = []
        today = datetime.today()
        for i in range(7):
            date = today + timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        return dates

    def generate_times(self):
        times = []
        for hour in range(9, 18):
            times.append(f"{hour:02}:00")
        return times

    def book_meeting(self):
        dates = self.generate_dates()
        date, ok = QInputDialog.getItem(self, 'Встреча', 'Выберите дату встречи:', dates, 0, False)
        if ok and date:
            times = self.generate_times()
            time, ok = QInputDialog.getItem(self, 'Встреча', 'Выберите время встречи:', times, 0, False)
            if ok and time:
                phone = None
                while not phone:
                    phone, ok = QInputDialog.getText(self, 'Встреча', 'Введите номер телефона:', QLineEdit.Normal, "")
                    if not phone and ok:
                        QMessageBox.warning(self, 'Ошибка', 'Номер телефона не может быть пустым')
                    elif not ok:
                        return

                cursor = self.connection.cursor()
                cursor.execute('SELECT * FROM bookings WHERE apartment_id=? AND date=? AND time=?',
                               (self.apartment_id, date, time))
                if cursor.fetchone():
                    QMessageBox.warning(self, 'Ошибка', 'Выбранное время уже занято')
                else:
                    cursor.execute(
                        'INSERT INTO bookings (apartment_id, user_login, date, time, phone) VALUES (?, ?, ?, ?, ?)',
                        (self.apartment_id, self.user_login, date, time, phone))
                    self.connection.commit()
                    QMessageBox.information(self, 'Успех', 'Встреча успешно забронирована')

    def enter_event(self, event):
        self.photo_label.setCursor(Qt.PointingHandCursor)

    def leave_event(self, event):
        self.photo_label.setCursor(Qt.ArrowCursor)

class Polzovatel(QWidget):
    def __init__(self, connection, user_login):  # Принимаем соединение и логин пользователя
        super().__init__()
        self.connection = connection  # Сохраняем соединение
        self.user_login = user_login  # Сохраняем логин пользователя
        self.setWindowTitle('Продажа жилья')
        self.setGeometry(620, 200, 760, 650)  # Увеличенные размеры
        self.setMinimumSize(760, 500)  # Увеличенные минимальные размеры

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)

        self.vbox = QVBoxLayout(self.scroll_widget)

        self.filter_button = CustomButton('Фильтр', self)
        self.filter_button.clicked.connect(self.show_filter_dialog)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.filter_button, alignment=Qt.AlignRight)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        self.load_apartments()

    def show_filter_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Фильтр')
        dialog.setGeometry(880, 200, 500, 400)  # Увеличенные размеры

        price_layout = QHBoxLayout()
        price_min_label = QLabel('Цена от:', dialog)
        price_min_input = QLineEdit(dialog)
        price_max_label = QLabel('до:', dialog)
        price_max_input = QLineEdit(dialog)
        price_layout.addWidget(price_min_label)
        price_layout.addWidget(price_min_input)
        price_layout.addWidget(price_max_label)
        price_layout.addWidget(price_max_input)

        floor_layout = QHBoxLayout()
        floor_min_label = QLabel('Этаж от:', dialog)
        floor_min_input = QLineEdit(dialog)
        floor_max_label = QLabel('до:', dialog)
        floor_max_input = QLineEdit(dialog)
        floor_layout.addWidget(floor_min_label)
        floor_layout.addWidget(floor_min_input)
        floor_layout.addWidget(floor_max_label)
        floor_layout.addWidget(floor_max_input)

        area_layout = QHBoxLayout()
        area_min_label = QLabel('Площадь от:', dialog)
        area_min_input = QLineEdit(dialog)
        area_max_label = QLabel('до:', dialog)
        area_max_input = QLineEdit(dialog)
        area_layout.addWidget(area_min_label)
        area_layout.addWidget(area_min_input)
        area_layout.addWidget(area_max_label)
        area_layout.addWidget(area_max_input)

        rooms_label = QLabel('Комнаты:', dialog)
        rooms_list = QListWidget(dialog)
        rooms_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for i in range(1, 6):
            rooms_list.addItem(str(i))

        apply_button = CustomButton('Применить', dialog)
        apply_button.clicked.connect(lambda: self.apply_filter(dialog, price_min_input.text(), price_max_input.text(), area_min_input.text(), area_max_input.text(), floor_min_input.text(), floor_max_input.text(), [item.text() for item in rooms_list.selectedItems()]))

        vbox = QVBoxLayout()
        vbox.addLayout(price_layout)
        vbox.addLayout(floor_layout)
        vbox.addLayout(area_layout)
        vbox.addWidget(rooms_label)
        vbox.addWidget(rooms_list)
        vbox.addWidget(apply_button)

        dialog.setLayout(vbox)
        dialog.exec_()

    def apply_filter(self, dialog, price_min, price_max, area_min, area_max, floor_min, floor_max, rooms):
        dialog.close()
        self.load_apartments(price_min, price_max, area_min, area_max, floor_min, floor_max, rooms)

    def load_apartments(self, price_min=None, price_max=None, area_min=None, area_max=None, floor_min=None, floor_max=None, rooms=None):
        query = 'SELECT id, price, area, rooms, address, floor, photo FROM apartments WHERE 1=1'
        params = []

        if price_min:
            query += ' AND price >= ?'
            params.append(float(price_min))
        if price_max:
            query += ' AND price <= ?'
            params.append(float(price_max))
        if area_min:
            query += ' AND area >= ?'
            params.append(float(area_min))
        if area_max:
            query += ' AND area <= ?'
            params.append(float(area_max))
        if floor_min:
            query += ' AND floor >= ?'
            params.append(int(floor_min))
        if floor_max:
            query += ' AND floor <= ?'
            params.append(int(floor_max))
        if rooms:
            query += ' AND rooms IN ({})'.format(','.join('?' for _ in rooms))
            params.extend(map(int, rooms))

        cursor = self.connection.cursor()
        cursor.execute(query, params)
        apartments = cursor.fetchall()

        for i in reversed(range(self.vbox.count())):
            widget = self.vbox.itemAt(i).widget()
            if widget is not None:
                self.vbox.removeWidget(widget)
                widget.setParent(None)

        self.vbox.addStretch()
        for id, price, area, rooms, address, floor, photo in apartments:
            apartment_widget = ApartmentWidget(self.connection, id, price, area, rooms, address, floor, photo, self.user_login)
            self.vbox.addWidget(apartment_widget)
        self.vbox.addStretch()


class BookingDialog(QDialog):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle('Забронированные встречи')
        self.setGeometry(700, 300, 600, 400)  # Увеличенные размеры
        self.setMinimumSize(600, 400)  # Увеличенные минимальные размеры

        self.booking_list = QListWidget(self)
        self.load_bookings()

        self.delete_button = CustomButton('Удалить встречу', self)
        self.delete_button.clicked.connect(self.delete_booking)

        vbox = QVBoxLayout()
        vbox.addWidget(self.booking_list)
        vbox.addWidget(self.delete_button)

        self.setLayout(vbox)

    def load_bookings(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT b.id, a.id, a.price, a.area, a.rooms, a.address, a.floor, b.user_login, b.date, b.time, b.phone
            FROM bookings b
            JOIN apartments a ON b.apartment_id = a.id
        ''')
        bookings = cursor.fetchall()
        self.booking_list.clear()
        for id, apartment_id, price, area, rooms, address, floor, user_login, date, time, phone in bookings:
            self.booking_list.addItem(f"Номер встречи: {id}, номер объявления: {apartment_id}\nЦена: {price}, площадь: {area}, комнат: {rooms}, этаж: {floor}\nАдрес: {address}\nПользователь: {user_login}, телефон: {phone}\nДата: {date}, время: {time}")

    def delete_booking(self):
        selected_item = self.booking_list.currentItem()
        if selected_item:
            booking_id_str = selected_item.text().split(':')[1].split(',')[0].strip()
            booking_id = int(booking_id_str)
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
            self.connection.commit()
            self.load_bookings()
            QMessageBox.information(self, 'Успех', 'Встреча успешно удалена')


class Realtor(QWidget):
    def __init__(self, connection):  # Принимаем соединение
        super().__init__()
        self.connection = connection  # Сохраняем соединение
        self.setWindowTitle('Панель риелтора')
        self.setGeometry(650, 250, 700, 500)  # Увеличенные размеры
        self.setMinimumSize(600, 400)  # Увеличенные минимальные размеры

        self.apartment_list = QListWidget(self)
        self.load_apartments()

        self.add_apartment_button = CustomButton('Добавить квартиру', self)
        self.remove_apartment_button = CustomButton('Удалить квартиру', self)
        self.view_bookings_button = CustomButton('Посмотреть забронированные встречи', self)

        self.add_apartment_button.clicked.connect(self.add_apartment)
        self.remove_apartment_button.clicked.connect(self.remove_apartment)
        self.view_bookings_button.clicked.connect(self.view_bookings)

        self.apartment_list.itemDoubleClicked.connect(self.show_apartment_photo)

        vbox = QVBoxLayout()
        vbox.addWidget(self.apartment_list)
        vbox.addWidget(self.add_apartment_button)
        vbox.addWidget(self.remove_apartment_button)
        vbox.addWidget(self.view_bookings_button)

        self.setLayout(vbox)

    def load_apartments(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, price, area, rooms, address, floor FROM apartments')
        apartments = cursor.fetchall()
        self.apartment_list.clear()
        for id, price, area, rooms, address, floor in apartments:
            self.apartment_list.addItem(f"Номер объявления: {id}\nЦена: {price}, площадь: {area}, комнат: {rooms}, этаж: {floor}\nАдрес: {address}")

    def add_apartment(self):
        price, ok = QInputDialog.getDouble(self, 'Добавить квартиру', 'Введите цену:')
        if ok:
            area, ok = QInputDialog.getDouble(self, 'Добавить квартиру', 'Введите площадь:')
            if ok:
                rooms, ok = QInputDialog.getInt(self, 'Добавить квартиру', 'Введите количество комнат:')
                if ok:
                    floor, ok = QInputDialog.getInt(self, 'Добавить квартиру', 'Введите этаж:')
                    if ok:
                        address, ok = QInputDialog.getText(self, 'Добавить квартиру', 'Введите адрес:')
                        if ok:
                            photo_path, ok = QFileDialog.getOpenFileName(self, 'Выберите фотографию', '', 'Images (*.png *.xpm *.jpg)')
                            if ok:
                                with open(photo_path, 'rb') as f:
                                    photo = f.read()
                                cursor = self.connection.cursor()
                                cursor.execute('INSERT INTO apartments (price, area, rooms, address, floor, photo) VALUES (?, ?, ?, ?, ?, ?)',
                                               (price, area, rooms, address, floor, photo))
                                self.connection.commit()
                                self.load_apartments()

    def remove_apartment(self):
        selected_item = self.apartment_list.currentItem()
        if selected_item:
            apartment_id_str = selected_item.text().split('\n')[0].split(':')[1].strip()
            apartment_id = int(apartment_id_str)
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM apartments WHERE id=?', (apartment_id,))
            self.connection.commit()
            self.load_apartments()

    def view_bookings(self):
        dialog = BookingDialog(self.connection, self)
        dialog.exec_()

    def show_apartment_photo(self, item):
        apartment_id_str = item.text().split('\n')[0].split(':')[1].strip()
        apartment_id = int(apartment_id_str)
        cursor = self.connection.cursor()
        cursor.execute('SELECT photo FROM apartments WHERE id=?', (apartment_id,))
        photo = cursor.fetchone()[0]
        if photo:
            pixmap = QPixmap()
            pixmap.loadFromData(photo)
            dialog = QDialog(self)
            dialog.setWindowTitle('Фотография квартиры')
            photo_label = QLabel(dialog)
            photo_label.setPixmap(pixmap)
            vbox = QVBoxLayout()
            vbox.addWidget(photo_label)
            dialog.setLayout(vbox)
            dialog.adjustSize()
            dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    app.setStyleSheet('''
        QWidget {
            background-color: #F0FFF0;
        }
        QPushButton {
            background-color: #C0FFC0;
            border-radius: 10px;
            padding: 10px;
            border: 2px solid #00af64;
        }
        QPushButton:hover {
            background-color: #A0FFA0;
        }
        QListWidget {
            background-color: white;
            border-radius: 5px;
            outline: none;
        }
        QListWidget::item {
            border: 1px solid #00af64;
            padding: 10px;
            border-radius: 5px;
        }
        QListWidget::item:selected {
            background-color: #98FB98;
            color: black;
            border-radius: 5px;
        }
        QLineEdit {
            background-color: white;
            border-radius: 10px;
            border: 2px solid #00af64;
        }
    ''')
    first_window = FirstWindow()
    first_window.show()
    sys.exit(app.exec_())