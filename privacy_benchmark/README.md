Testing out some rough custom permissions.

Link your postgres in the `settings.py` and create the db.

```python
python manage.py makemigrations
python manage.py migrate
python manage.py populate_custom_data
python manage.py benchmark_queries
```