from flask import Flask, jsonify, request, render_template
from sqlalchemy.orm import sessionmaker
from models import User, Announcement, engine_table
from datetime import datetime

app = Flask("My site")  # Моё приложение


@app.route("/")
def test_site():
    """Стартовая страница для http://127.0.0.1:5000"""
    return render_template('index.html')


def validate_data(data, required_fields):
    """Проверяет наличие всех обязательных полей/ Валидация"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"{field} is required"
    return True, None


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    required_fields = ['name', 'password']
    is_valid, error_message = validate_data(data, required_fields)
    if not is_valid or len(data['name']) < 3:
        return jsonify({"error": error_message}), 400
    else:
        # Создание нового пользователя
        new_user = User(
            name=data['name'],
            password=data['password'],  # Здесь лучше использовать хеширование пароля!
            registration_time=datetime.now()
        )
        # Сохранение в базу данных
        with sessionmaker(bind=engine_table)() as session:
            session.add(new_user)
            session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@app.route('/announcement', methods=['POST'])
def create_announcement():
    data = request.get_json()
    required_fields = ['title', 'description', 'author']
    is_valid, error_message = validate_data(data, required_fields)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    else:
        new_announcement = Announcement(
            title=data['title'],
            description=data['description'],
            author=data['author'],
            created_at=datetime.now()
        )
        # Сохранение в базу данных
        with sessionmaker(bind=engine_table)() as session:
            session.add(new_announcement)
            session.commit()

        return jsonify({'message': 'Announcement created successfully'}), 201


@app.route('/announcement/<int:id>', methods=['DELETE'])
def delete_announcement(id):
    with sessionmaker(bind=engine_table)() as session:
        announcement = session.query(Announcement).get(id)
        if announcement:
            session.delete(announcement)
            session.commit()
            return jsonify({'message': 'Announcement delete successfully'}), 201
        else:
            return jsonify({'error': 'Announcement no delete successfully'}), 409


@app.route('/announcement/<int:id>', methods=['PATCH'])
def update_announcement(id):
    data = request.get_json()
    required_fields = ['title', 'description', 'author']
    is_valid, error_message = validate_data(data, required_fields)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    else:
        # Получаем существующее объявление по ID
        with sessionmaker(bind=engine_table)() as session:
            announcement = session.query(Announcement).get(id)

            if not announcement:
                return jsonify({'error': 'Announcement not found'}), 404

            # Обновляем поля объявления
            announcement.title = data['title']
            announcement.description = data['description']
            announcement.author = data['author']

            # Сохраняем изменения в базу данных
            session.commit()

        return jsonify({'message': 'Announcement updated successfully'}), 200


@app.route('/announcements', methods=['GET'])
def get_announcements():
    with sessionmaker(bind=engine_table)() as session:
        announcements = session.query(Announcement).all()
        results = []
        for announcement in announcements:
            results.append({
                'id': announcement.id,
                'title': announcement.title,
                'description': announcement.description,
                'author': announcement.author,
                'created_at': announcement.created_at.isoformat(),
            })

    return jsonify(results)


if __name__ == '__main__':
    app.run()
