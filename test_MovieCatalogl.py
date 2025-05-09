import unittest
import json
import os
from MovieCatalog import add_movie, delete_movie, search_movies, load_data, save_data

class TestMoviesCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовый файл перед всеми тестами"""
        cls.test_file = "test_movies.json"
        with open(cls.test_file, "w", encoding="utf-8") as f:
            json.dump({"movies": []}, f)
        
        # Подменяем файл данных на тестовый
        global DATA_FILE
        DATA_FILE = cls.test_file

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовый файл после всех тестов"""
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)

    def setUp(self):
        """Очищаем данные перед каждым тестом"""
        save_data({"movies": []})

    # Тесты для функции add_movie
    def test_add_movie_success(self):
        """Тест успешного добавления фильма"""
        result = add_movie("Интерстеллар", 2014, "Фантастика", 
                          "Кристофер Нолан", ["Мэттью Макконахи"], "url")
        self.assertEqual(result, "Фильм добавлен успешно.")
        movies = load_data()["movies"]
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0]["title"], "Интерстеллар")

    def test_add_movie_empty_title(self):
        """Тест добавления с пустым названием"""
        result = add_movie("", 2020, "Драма", "Режиссер", [], "")
        self.assertEqual(result, "Ошибка: некорректные данные.")
        self.assertEqual(len(load_data()["movies"]), 0)

    def test_add_movie_invalid_year_type(self):
        """Тест добавления с неверным типом года"""
        result = add_movie("Фильм", "2020", "Жанр", "Режиссер", [], "")
        self.assertEqual(result, "Ошибка: некорректные данные.")
        self.assertEqual(len(load_data()["movies"]), 0)

    def test_add_movie_long_title(self):
        """Тест добавления с очень длинным названием"""
        long_title = "Очень длинное название" * 50  # ~1000 символов
        result = add_movie(long_title, 2020, "Жанр", "Режиссер", [], "")
        self.assertEqual(result, "Фильм добавлен успешно.")
        movies = load_data()["movies"]
        self.assertEqual(movies[0]["title"], long_title)

    # Тесты для функции delete_movie
    def test_delete_movie_success(self):
        """Тест успешного удаления фильма"""
        add_movie("Фильм для удаления", 2020, "Жанр", "Режиссер", [], "")
        result = delete_movie("Фильм для удаления")
        self.assertEqual(result, "Фильм удалён успешно.")
        self.assertEqual(len(load_data()["movies"]), 0)

    def test_delete_nonexistent_movie(self):
        """Тест удаления несуществующего фильма"""
        result = delete_movie("Несуществующий фильм")
        self.assertEqual(result, "Ошибка: фильм не найден.")

    # Тесты для функции search_movies
    def test_search_by_genre_success(self):
        """Тест успешного поиска по жанру"""
        add_movie("Фильм 1", 2020, "Боевик", "Режиссер 1", [], "")
        add_movie("Фильм 2", 2021, "Комедия", "Режиссер 2", [], "")
        result = search_movies("genre", "Боевик")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Фильм 1")

    def test_search_by_year_success(self):
        """Тест успешного поиска по году"""
        add_movie("Фильм 1", 2020, "Жанр", "Режиссер", [], "")
        result = search_movies("year", 2020)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Фильм 1")

    def test_search_invalid_criteria(self):
        """Тест поиска по неверному критерию"""
        result = search_movies("invalid", "значение")
        self.assertEqual(result, "Ошибка: некорректный критерий поиска.")

    def test_search_no_results(self):
        """Тест поиска без результатов"""
        result = search_movies("genre", "Несуществующий жанр")
        self.assertEqual(result, "Фильмы не найдены.")

    # Тест граничного условия - пустой список актеров
    def test_add_movie_empty_actors(self):
        """Тест добавления фильма без актеров"""
        result = add_movie("Фильм без актеров", 2023, "Драма", "Режиссер", None, "")
        self.assertEqual(result, "Фильм добавлен успешно.")
        movie = load_data()["movies"][0]
        self.assertEqual(movie["actors"], None)

if __name__ == "__main__":
    unittest.main()