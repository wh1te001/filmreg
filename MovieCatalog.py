import json

DATA_FILE = "movies.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"movies": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def add_movie(title, year, genre, director, actors, poster_url):
    if not title or not isinstance(year, int) or not genre:
        return "Ошибка: некорректные данные."

    data = load_data()
    new_movie = {
        "title": title,
        "year": year,
        "genre": genre,
        "director": director,
        "actors": actors,
        "poster_url": poster_url
    }
    data["movies"].append(new_movie)
    save_data(data)
    return "Фильм добавлен успешно."

def delete_movie(title):
    data = load_data()
    movies = data["movies"]
    for movie in movies:
        if movie["title"] == title:
            movies.remove(movie)
            save_data(data)
            return "Фильм удалён успешно."
    return "Ошибка: фильм не найден."

def search_movies(key, value):
    data = load_data()
    if key not in ["title", "year", "genre", "director"]:
        return "Ошибка: некорректный критерий поиска."

    result = []
    for movie in data["movies"]:
        if key == "year":
            if movie[key] == value:
                result.append(movie)
        else:
            if value.lower() in movie[key].lower():
                result.append(movie)
    return result if result else "Фильмы не найдены."
