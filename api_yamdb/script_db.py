# python manage.py shell
import csv
import os

from users.models import User

path = "C:/Final/api_yamdb/api_yamdb/static/data"
os.chdir(path)
# from reviews.models import Genre, Category, Title, Review, Comment

# User
with open('users.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        p = User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row['role'],
            bio=row['bio'],
            first_name=row['first_name'],
            last_name=row['last_name'])
        p.save()
