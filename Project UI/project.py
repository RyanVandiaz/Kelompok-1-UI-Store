import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.secret_key = 'uinumberone'
login_manager = LoginManager(app)

class User(UserMixin):
    def __init__(self, id, balance):
        self.id = id
        self.balance = balance

    @property
    def balance(self):
        for user in user_data:
            if user['username'] == self.id:
                return user.get('balance', 0)
        return 0

    @balance.setter
    def balance(self, new_balance):
        for user in user_data:
            if user['username'] == self.id:
                user['balance'] = new_balance
                update_user_data()
                return

    @property
    def purchases(self):
        for user in user_data:
            if user['username'] == self.id:
                return user.get('purchases', [])
        return []

    @purchases.setter
    def purchases(self, new_purchases):
        for user in user_data:
            if user['username'] == self.id:
                user['purchases'] = new_purchases
                update_user_data()
                return

@login_manager.user_loader
def load_user(user_id):
    for user in user_data:
        if user['username'] == user_id:
            return User(user_id, user.get('balance', 0))
    return None

user_data = []

try:
    with open('user_data.json', 'r') as json_file:
        user_data = json.load(json_file)
except FileNotFoundError:
    pass

def update_user_data():
    with open('user_data.json', 'w') as json_file:
        json.dump(user_data, json_file, indent=2)

def add_purchase_to_user(username, item):
    for user in user_data:
        if user['username'] == username:
            if 'purchases' not in user:
                user['purchases'] = []
            user['purchases'].append(item)
            update_user_data()
            return

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username').lower()
    password = request.form.get('password').lower()

    for user in user_data:
        if user['username'] == username and user['password'] == password:
            user_obj = User(username, user.get('balance', 0))
            login_user(user_obj)
            return redirect(url_for('shop'))

    return render_template('index.html')

@app.route('/buatakun')
def buatakun_hlm():
    return render_template('buatakun.html')

@app.route('/buatakun', methods=['POST'])
def buatakun():
    new_username = request.form.get('new-username')
    new_password = request.form.get('new-password')

    for user in user_data:
        if user['username'] == new_username:
            return 'Akun sudah ada... Silahkan pilih yang lain.'

    user_data.append({'username': new_username.lower(), 'password': new_password.lower(), 'balance': 1000000})
    update_user_data()
    return render_template('index.html')

@app.route('/shop')
@login_required
def shop():
    return render_template('shop.html')

@app.route('/profile/<username>')
def profile(username):
    for user in user_data:
        if user['username'] == username:
            return render_template('profile.html', username=username, balance=user.get('balance', 0), purchases=current_user.purchases)
    return 'User not found.'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/market')
@login_required
def market():
    items = get_market_items()
    return render_template('market.html', items=items)

def get_market_items():
    return [
        {'id': 'item1', 'T-Shirt UI Est.1849': 'T-Shirt UI Est.1849', 'price': 195000, 'image': 'model.png'},
        {'id': 'item2', 'Snapback UI': 'Snapback UI', 'price': 85000, 'image': 'topi.png'},
        # ... item lainnya ...
    ]

def find_item_by_id(item_id):
    for item in get_market_items():
        if item['id'] == item_id:
            return item
    return None

@app.route('/buy/<item_id>', methods=['POST'])
@login_required
def buy(item_id):
    item = find_item_by_id(item_id)
    if item and current_user.balance >= item['price']:
        new_balance = current_user.balance - item['price']
        current_user.balance = new_balance

        add_purchase_to_user(current_user.id, item)

        update_user_data()
        return redirect(url_for('pembelian_berhasil', item_id=item_id))
    else:
        return redirect(url_for('pembelian_gagal', item_id=item_id))

@app.route('/pembelian_berhasil/<item_id>')
@login_required
def pembelian_berhasil(item_id):
    purchased_item = find_item_by_id(item_id)
    return render_template('pembelian_berhasil.html', item=purchased_item)

@app.route('/pembelian_gagal/<item_id>')
@login_required
def pembelian_gagal(item_id):
    return render_template('pembelian_gagal.html', item=None)

@app.route('/history')
@login_required
def history():
    return render_template('history.html', purchases=current_user.purchases)

if __name__ == '__main__':
    app.run(debug=True, port=8085)
