from MovieCatalog import add_movie, delete_movie, search_movies
import json

def display_movie(movie):
    """Выводит информацию о фильме в читаемом формате"""
    print(f"\nНазвание: {movie['title']}")
    print(f"Год: {movie['year']}")
    print(f"Жанр: {movie['genre']}")
    print(f"Режиссер: {movie['director']}")
    print(f"Актеры: {', '.join(movie['actors'])}")
    if movie['poster_url']:
        print(f"Постер: {movie['poster_url']}")

def input_movie_data():
    """Запрашивает у пользователя данные о фильме"""
    print("\nДобавление нового фильма")
    title = input("Введите название фильма: ").strip()
    while not title:
        print("Название не может быть пустым!")
        title = input("Введите название фильма: ").strip()
    
    year = None
    while year is None:
        try:
            year = int(input("Введите год выпуска: ").strip())
        except ValueError:
            print("Год должен быть числом!")
    
    genre = input("Введите жанр: ").strip()
    director = input("Введите режиссера: ").strip()
    
    actors_input = input("Введите актеров через запятую: ").strip()
    actors = [actor.strip() for actor in actors_input.split(",")] if actors_input else []
    
    poster_url = input("Введите ссылку на постер (необязательно): ").strip()
    
    return title, year, genre, director, actors, poster_url

def show_search_menu():
    """Отображает меню поиска и обрабатывает выбор"""
    print("\nПоиск фильмов")
    print("1 - По названию")
    print("2 - По году")
    print("3 - По жанру")
    print("4 - По режиссеру")
    print("0 - Назад")
    
    choice = input("Выберите критерий поиска: ").strip()
    
    if choice == "0":
        return
    
    key = None
    if choice == "1":
        key = "title"
    elif choice == "2":
        key = "year"
    elif choice == "3":
        key = "genre"
    elif choice == "4":
        key = "director"
    else:
        print("Неверный выбор!")
        return
    
    value = input(f"Введите значение для поиска ({key}): ").strip()
    
    if key == "year":
        try:
            value = int(value)
        except ValueError:
            print("Год должен быть числом!")
            return
    
    results = search_movies(key, value)
    
    if isinstance(results, str):  # Сообщение об ошибке
        print(results)
    elif not results:
        print("Фильмы не найдены")
    else:
        if len(results) % 10 == 1:
            print(f"\nНайден {len(results)} фильм:")
        elif len(results) % 10 == 2 or 3 or 4:
            print(f"\nНайдено {len(results)} фильма:")
        else:
            print(f"\nНайдено {len(results)} фильмов:")
        for movie in results:
            display_movie(movie)

def show_all_movies():
    """Показывает все фильмы в коллекции"""
    with open("movies.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    if not data["movies"]:
        print("\nВ коллекции пока нет фильмов")
        return
    
    print("\nВсе фильмы в коллекции:")
    for idx, movie in enumerate(data["movies"], 1):
        print(f"\n{idx}. {movie['title']} ({movie['year']})")
        print(f"   Жанр: {movie['genre']}, Режиссер: {movie['director']}")

def delete_movie_interface():
    """Интерфейс для удаления фильма"""
    title = input("\nВведите название фильма для удаления: ").strip()
    if not title:
        print("Название не может быть пустым!")
        return
    
    result = delete_movie(title)
    print(result)

def main():
    """Основная функция с главным меню"""
    while True:
        print("\n=== Учет фильмов и сериалов ===")
        print("1 - Добавить фильм")
        print("2 - Удалить фильм")
        print("3 - Поиск фильмов")
        print("4 - Показать все фильмы")
        print("0 - Выход")
        
        choice = input("Выберите действие: ").strip()
        
        if choice == "0":
            print("До свидания!")
            break
        elif choice == "1":
            movie_data = input_movie_data()
            result = add_movie(*movie_data)
            print(result)
        elif choice == "2":
            delete_movie_interface()
        elif choice == "3":
            show_search_menu()
        elif choice == "4":
            show_all_movies()
        else:
            print("Неверный выбор! Попробуйте снова.")

if __name__ == "__main__":
    main()