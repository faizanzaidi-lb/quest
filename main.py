from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app
app = Flask(__name__)

# Set up SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Quest model
class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    reward_type = db.Column(db.String(20), nullable=False)  # e.g., gold, diamond
    reward_qty = db.Column(db.Integer, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Route to add a new quest
@app.route('/quests', methods=['POST'])
def add_quest():
    data = request.json
    new_quest = Quest(
        name=data['name'],
        reward_type=data['reward_type'],
        reward_qty=data['reward_qty']
    )
    db.session.add(new_quest)
    db.session.commit()
    return jsonify({"message": "Quest added successfully!"}), 201

# Route to get all quests
@app.route('/quests', methods=['GET'])
def get_quests():
    quests = Quest.query.all()
    return jsonify([{
        "id": quest.id,
        "name": quest.name,
        "reward_type": quest.reward_type,
        "reward_qty": quest.reward_qty
    } for quest in quests]), 200

# Route to get a specific quest by ID
@app.route('/quests/<int:id>', methods=['GET'])
def get_quest(id):
    quest = Quest.query.get(id)
    if quest is None:
        return jsonify({"error": "Quest not found"}), 404

    return jsonify({
        "id": quest.id,
        "name": quest.name,
        "reward_type": quest.reward_type,
        "reward_qty": quest.reward_qty
    }), 200

# Route to delete a quest by ID
@app.route('/quests/<int:id>', methods=['DELETE'])
def delete_quest(id):
    quest = Quest.query.get(id)
    if quest is None:
        return jsonify({"error": "Quest not found"}), 404

    db.session.delete(quest)
    db.session.commit()
    return jsonify({"message": "Quest deleted successfully!"}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)