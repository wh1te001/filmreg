import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QDialog, QMessageBox, QFileDialog, QFormLayout, QComboBox, QGroupBox,
    QRadioButton, 
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

# Импортируем функции из MovieCatalog.py
from MovieCatalog import load_data, save_data, add_movie, delete_movie, search_movies


class AddEditMovieDialog(QDialog):
    def __init__(self, parent=None, movie=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить фильм" if not movie else "Изменить фильм")
        self.movie = movie
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.title_input = QLineEdit()
        self.year_input = QLineEdit()
        self.genre_input = QLineEdit()
        self.director_input = QLineEdit()
        self.actors_input = QLineEdit()
        self.poster_input = QLineEdit()

        layout.addRow("Название:", self.title_input)
        layout.addRow("Год:", self.year_input)
        layout.addRow("Жанр:", self.genre_input)
        layout.addRow("Режиссер:", self.director_input)
        layout.addRow("Актеры (через запятую):", self.actors_input)
        layout.addRow("Ссылка на постер:", self.poster_input)

        self.save_button = QPushButton("Добавить" if not self.movie else "Сохранить")
        self.cancel_button = QPushButton("Отмена")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if self.movie:
            self.title_input.setText(self.movie['title'])
            self.year_input.setText(str(self.movie['year']))
            self.genre_input.setText(self.movie['genre'])
            self.director_input.setText(self.movie['director'])
            self.actors_input.setText(", ".join(self.movie['actors']))
            self.poster_input.setText(self.movie.get('poster_url', ''))

    def get_data(self):
        return {
            'title': self.title_input.text().strip(),
            'year': int(self.year_input.text()) if self.year_input.text().isdigit() else None,
            'genre': self.genre_input.text().strip(),
            'director': self.director_input.text().strip(),
            'actors': [a.strip() for a in self.actors_input.text().split(',') if a.strip()],
            'poster_url': self.poster_input.text().strip()
        }


class DetailsDialog(QDialog):
    def __init__(self, parent=None, movie=None):
        super().__init__(parent)
        self.setWindowTitle(f"Подробности: {movie['title']}")
        self.movie = movie.copy()  # Работаем с копией, чтобы не менять оригинал до подтверждения
        self.is_editing = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.title_input = QLineEdit(self.movie['title'])
        self.year_input = QLineEdit(str(self.movie['year']))
        self.genre_input = QLineEdit(self.movie['genre'])
        self.director_input = QLineEdit(self.movie['director'])
        self.actors_input = QLineEdit(", ".join(self.movie['actors']))
        self.poster_url_input = QLineEdit(self.movie.get('poster_url', ''))  # Поле для ссылки на постер

        # Заблокировать редактирование по умолчанию
        self.set_inputs_readonly(True)

        form_layout.addRow("Название:", self.title_input)
        form_layout.addRow("Год:", self.year_input)
        form_layout.addRow("Жанр:", self.genre_input)
        form_layout.addRow("Режиссер:", self.director_input)
        form_layout.addRow("Актеры:", self.actors_input)
        form_layout.addRow("Ссылка на постер:", self.poster_url_input)

        layout.addLayout(form_layout)

        # Постер
        self.poster_label = QLabel("Постер")
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_poster()
        layout.addWidget(self.poster_label)

        # Кнопка "Изменить"
        self.edit_button = QPushButton("Изменить")
        self.edit_button.clicked.connect(self.toggle_edit)
        layout.addWidget(self.edit_button)

        self.setLayout(layout)

    def set_inputs_readonly(self, readonly=True):
        self.title_input.setReadOnly(readonly)
        self.year_input.setReadOnly(readonly)
        self.genre_input.setReadOnly(readonly)
        self.director_input.setReadOnly(readonly)
        self.actors_input.setReadOnly(readonly)
        self.poster_url_input.setReadOnly(readonly)

    def toggle_edit(self):
        self.is_editing = not self.is_editing

        if self.is_editing:
            self.set_inputs_readonly(False)
            self.edit_button.setText("Сохранить")
        else:
            # Сохраняем изменения
            self.movie['title'] = self.title_input.text().strip()
            try:
                self.movie['year'] = int(self.year_input.text())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Год должен быть числом.")
                return

            self.movie['genre'] = self.genre_input.text().strip()
            self.movie['director'] = self.director_input.text().strip()
            self.movie['actors'] = [a.strip() for a in self.actors_input.text().split(',') if a.strip()]
            self.movie['poster_url'] = self.poster_url_input.text().strip()  # Сохраняем ссылку на постер

            # Сохраняем в файл
            data = load_data()
            for i, m in enumerate(data["movies"]):
                if m["title"] == self.movie["title"]:
                    data["movies"][i] = self.movie
                    break
            save_data(data)

            # Обновляем предпросмотр постера
            self.load_poster()

            self.set_inputs_readonly(True)
            self.edit_button.setText("Изменить")

    def load_poster(self):
        url = self.movie.get('poster_url')
        if url:
            from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
            from PyQt6.QtCore import QUrl

            self.manager = QNetworkAccessManager()
            self.manager.finished.connect(lambda reply: self.handle_pixmap(reply.readAll()))
            self.manager.get(QNetworkRequest(QUrl(url)))

    def handle_pixmap(self, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.poster_label.setPixmap(pixmap.scaledToWidth(200))
class ExtendedSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Расширенный поиск")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.field_combo = QComboBox()
        self.field_combo.addItems(["title", "year", "genre", "director"])
        self.value_input = QLineEdit()

        layout.addRow("Поле:", self.field_combo)
        layout.addRow("Значение:", self.value_input)

        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.accept)
        layout.addRow(self.search_button)

        self.setLayout(layout)

    def get_criteria(self):
        return self.field_combo.currentText(), self.value_input.text()


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Экспортировать")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.csv_radio = QRadioButton("CSV")
        self.excel_radio = QRadioButton("Excel")
        self.csv_radio.setChecked(True)

        layout.addWidget(self.csv_radio)
        layout.addWidget(self.excel_radio)

        self.export_button = QPushButton("Экспортировать")
        self.export_button.clicked.connect(self.accept)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def get_format(self):
        return "csv" if self.csv_radio.isChecked() else "excel"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог фильмов")
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Основной макет
        main_layout = QVBoxLayout()

        # Верхняя часть: строка поиска
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.ext_search_button = QPushButton("Расш. поиск")
        self.settings_button = QPushButton("Настройки")

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.ext_search_button)
        top_layout.addWidget(self.settings_button)

        main_layout.addLayout(top_layout)

        # Средняя часть: таблица фильмов
        table_layout = QHBoxLayout()

        # Таблица фильмов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Год", "Жанр", "Режиссер"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellClicked.connect(self.show_poster)
        self.table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.table)

        # Постер
        self.poster_label = QLabel("Постер")
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.poster_label)

        main_layout.addLayout(table_layout)

        # Нижняя часть: кнопки управления
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить")
        self.del_button = QPushButton("Удалить")
        self.detail_button = QPushButton("Подробнее")
        self.export_button = QPushButton("Экспорт")

        self.add_button.clicked.connect(self.open_add_dialog)
        self.del_button.clicked.connect(self.delete_selected)
        self.detail_button.clicked.connect(self.show_details)
        self.ext_search_button.clicked.connect(self.open_extended_search)
        self.export_button.clicked.connect(self.export_movies)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.del_button)
        button_layout.addWidget(self.detail_button)
        button_layout.addWidget(self.export_button)

        main_layout.addLayout(button_layout)

        main_widget.setLayout(main_layout)

        self.load_movies()

    def load_movies(self, movies=None):
        if movies is None:
            data = load_data()
            movies = data["movies"]

        self.table.setRowCount(len(movies))
        for row, movie in enumerate(movies):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(movie['title']))
            self.table.setItem(row, 2, QTableWidgetItem(str(movie['year'])))
            self.table.setItem(row, 3, QTableWidgetItem(movie['genre']))
            self.table.setItem(row, 4, QTableWidgetItem(movie['director']))

    def show_poster(self, row, col):
        title = self.table.item(row, 1).text()
        data = load_data()
        movie = next((m for m in data["movies"] if m["title"] == title), None)
        if movie and movie.get("poster_url"):
            pixmap = QPixmap()
            from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
            from PyQt6.QtCore import QUrl

            self.manager = QNetworkAccessManager()
            self.manager.finished.connect(lambda reply: self.poster_label.setPixmap(
                QPixmap.fromImage(QImage.fromData(reply.readAll())).scaledToWidth(400)
            ))
            self.manager.get(QNetworkRequest(QUrl(movie["poster_url"])))

    def open_add_dialog(self):
        dialog = AddEditMovieDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = add_movie(**data)
            QMessageBox.information(self, "Результат", result)
            self.load_movies()

    def delete_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        title = selected[1].text()
        result = delete_movie(title)
        QMessageBox.information(self, "Результат", result)
        self.load_movies()

    def show_details(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        title = selected[1].text()
        data = load_data()
        movie = next((m for m in data["movies"] if m["title"] == title), None)
        if movie:
            dialog = DetailsDialog(self, movie)
            dialog.exec()
            self.load_movies()

    def open_extended_search(self):
        dialog = ExtendedSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key, value = dialog.get_criteria()
            try:
                if key == "year":
                    value = int(value)
                results = search_movies(key, value)
                if isinstance(results, str):
                    QMessageBox.warning(self, "Ошибка", results)
                else:
                    self.load_movies(results)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Некорректное значение.")

    def export_movies(self):
        dialog = ExportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            fmt = dialog.get_format()
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Сохранить как", 
                "", 
                f"{fmt.upper()} Files (*.{fmt})"
            )
            if not filename:
                return

            # Ensure the file has the correct extension
            if not filename.lower().endswith(f'.{fmt}'):
                filename += f'.{fmt}'

            data = load_data()["movies"]
            if fmt == "csv":
                # Убедимся, что файл имеет расширение .csv
                if not filename.lower().endswith('.csv'):
                    filename += '.csv'
                
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write("Название,Год,Жанр,Режиссер,Актеры\n")
                        for movie in data:
                            f.write(f'"{movie["title"]}",{movie["year"]},"{movie["genre"]}","{movie["director"]}","{", ".join(movie["actors"])}"\n')
                    QMessageBox.information(self, "Экспорт", f"Фильмы экспортированы в CSV: {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать в CSV: {str(e)}")
            elif fmt == "excel":
                try:
                    import pandas as pd
                    df = pd.DataFrame(data)
                    
                    # Make sure the filename ends with .xlsx
                    if not filename.lower().endswith('.xlsx'):
                        if filename.lower().endswith('.excel'):
                            filename = filename[:-6] + '.xlsx'
                        else:
                            filename += '.xlsx'
                    
                    # Use openpyxl as engine
                    df.to_excel(filename, index=False, engine='openpyxl')
                    QMessageBox.information(self, "Экспорт", f"Фильмы экспортированы в Excel: {filename}")
                except ImportError as e:
                    QMessageBox.critical(self, "Ошибка", 
                        "Для экспорта в Excel требуется установить openpyxl.\n"
                        "Установите его через pip: pip install openpyxl\n"
                        f"Ошибка: {str(e)}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", 
                        f"Не удалось экспортировать в Excel: {str(e)}\n"
                        f"Тип файла: {filename.split('.')[-1]}")
                    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())