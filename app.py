import os
from flask import Flask, jsonify, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

auth = HTTPBasicAuth()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
manager = Manager(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username

# 查询所有用户
@app.route('/api/users', methods=['GET'])
@auth.login_required
def get_allusers():

    users = [
        {
            'id': 1,
            'username': u'huichao'
        }
    ]

    users.clear()

    for i in User.query.all():
        user = {
             'id': i.id,
             'username': i.username
         }

        users.append(user)

    return jsonify(users)


# 查询指定用户
@app.route('/api/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_users(user_id):
    user = {
        'id': user_id,
        'username': User.query.filter_by(id=user_id).first().username
    }
    return jsonify(user)

# 增加一个用户
@app.route('/api/users', methods=['POST'])
@auth.login_required
def create_user():
    if not request.json or not 'username' in request.json:
        abort(400)
    user = User(username=request.json['username'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'result': True})

# 删除一个用户
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': True})

# 更新用户
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if not request.json:
        abort(400)
    user = User.query.filter_by(id=user_id).first()
    user.username = request.json['username']
    db.session.add(user)
    db.session.commit()
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

if __name__ == '__main__':
    manager.run()