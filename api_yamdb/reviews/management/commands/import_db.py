import csv

from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


def import_csv_db():
    LIB = (
        (User, 'static/data/users.csv'),
        (Category, 'static/data/category.csv'),
        (Genre, 'static/data/genre.csv'),
        (Title, 'static/data/titles.csv'),
        (Title.genre.through, 'static/data/genre_title.csv'),
        (Review, 'static/data/review.csv'),
        (Comment, 'static/data/comments.csv')
    )

    for model, file in LIB:
        for row in csv.DictReader(open(file, encoding='utf-8')):
            if file == 'static/data/users.csv':
                p = model(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                p.save()
            elif (file == 'static/data/category.csv'
                  or file == 'static/data/genre.csv'):
                p = model(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
                p.save()
            elif file == 'static/data/titles.csv':
                p = model(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(id=row['category'])
                )
                p.save()
            elif file == 'static/data/genre_title.csv':
                p = model(
                    id=row['id'],
                    title=Title.objects.get(id=row['title_id']),
                    genre=Genre.objects.get(id=row['genre_id'])
                )
                p.save()
            elif file == 'static/data/review.csv':
                p = model(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                )
                p.save()
            elif file == 'static/data/comments.csv':
                p = model(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date']
                )
                p.save()
        print(f"Загрузка данных из таблицы {file} завершена успешно.")


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Начало загрузки данных в базу данных')
        try:
            import_csv_db()

        except Exception as error:
            print(f"Сбой в работе импорта: {error}.")

        finally:
            print('Загрузка всех данных произведена успешно')
