from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
from datetime import datetime
import os  # ← نحتاج هذا للوصول إلى المتغيرات البيئية

app = Flask(__name__)
app.secret_key = 'xza_secure_key'  # Important for session security

added_uids = {}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin":
            session['logged_in'] = True
            return redirect('/panel')
        return render_template("login.html", error="❌ Incorrect username or password.")
    return render_template('login.html')

@app.route('/panel')
def panel():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('panel.html')

@app.route('/add_friend', methods=['POST'])
def add_friend():
    uid = request.form.get("uid")
    days = request.form.get("days")

    if uid in added_uids:
        return jsonify({"status": "exists", "message": "❗ This account has already been added."})

    try:
        response = requests.get(f"https://xza-add.onrender.com/panel_add?uid={uid}")
        if response.status_code == 200:
            added_uids[uid] = {
                "days": days,
                "time": datetime.now().isoformat()
            }
            return jsonify({"status": "success", "message": "✅ Account added successfully."})
        else:
            return jsonify({"status": "error", "message": "❌ Failed to add account."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/remove_friend', methods=['POST'])
def remove_friend():
    uid = request.form.get("uid")
    try:
        response = requests.get(f"https://remove-xza-1.onrender.com/panel_remove?uid={uid}")
        if response.status_code == 200:
            added_uids.pop(uid, None)
            return jsonify({"status": "success", "message": "🗑️ Successfully removed."})
        else:
            return jsonify({"status": "error", "message": "❌ Failed to remove."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_days')
def get_days():
    uid = request.args.get("uid")
    if uid in added_uids:
        data = added_uids[uid]
        return jsonify({"status": "success", "message": f"📅 This account was added {data['days']} day(s) ago."})
    return jsonify({"status": "not_found", "message": "❗ UID not found."})

@app.route('/send_likes', methods=['POST'])
def send_likes():
    uid = request.form.get("uid")
    if not uid:
        return jsonify({"status": "error", "message": "❗ UID is required."})

    try:
        response = requests.get(f"https://like-dev-xza.onrender.com/like?uid={uid}&server_name=ME")
        if response.status_code == 200:
            return response.json()  # Return the full result from API
        else:
            return jsonify({"status": "error", "message": "❌ Failed to send likes."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ✅ هنا نضيف تشغيل التطبيق بالطريقة التي طلبتها
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))