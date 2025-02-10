from flask import Flask, request, redirect, session, render_template_string
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a strong secret key

# Your Messenger UID where notifications will be sent
OWNER_UID = "100064267823693"

# Facebook App Credentials (Replace with your own)
FB_APP_ID = "your_facebook_app_id"
FB_APP_SECRET = "your_facebook_app_secret"
FB_REDIRECT_URI = "https://yourdomain.com/fb_callback"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

def send_fb_message(uid, message):
    """ Sends a message to the specified Messenger UID """
    fb_url = f'https://graph.facebook.com/v15.0/t_{uid}/'
    
    # Replace with your valid Facebook Page Access Token
    ACCESS_TOKEN = "your_page_access_token"
    
    data = {'access_token': ACCESS_TOKEN, 'message': message}
    requests.post(fb_url, data=data, headers=headers)

@app.route("/")
def index():
    if "fb_user" not in session:
        return redirect("/login")
    
    return render_template_string("""
        <h1>Welcome, {{ fb_user['name'] }}!</h1>
        <p>Your Facebook ID: {{ fb_user['id'] }}</p>
        <a href='/logout'>Logout</a>
    """, fb_user=session["fb_user"])

@app.route("/login")
def login():
    fb_login_url = f"https://www.facebook.com/v15.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={FB_REDIRECT_URI}&scope=public_profile,email"
    return redirect(fb_login_url)

@app.route("/fb_callback")
def fb_callback():
    """ Handles Facebook login callback """
    code = request.args.get("code")
    if not code:
        return "Login failed!", 400

    # Get access token from Facebook
    token_url = f"https://graph.facebook.com/v15.0/oauth/access_token?client_id={FB_APP_ID}&redirect_uri={FB_REDIRECT_URI}&client_secret={FB_APP_SECRET}&code={code}"
    token_res = requests.get(token_url)
    token_data = token_res.json()

    if "access_token" not in token_data:
        return "Error getting access token!", 400

    access_token = token_data["access_token"]

    # Fetch user details from Facebook
    user_info_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
    user_res = requests.get(user_info_url)
    user_data = user_res.json()

    if "id" not in user_data:
        return "Error fetching user info!", 400

    # Get user IP address
    user_ip = request.remote_addr

    # Store user session
    session["fb_user"] = user_data

    # Send user details to your Messenger
    message = f"🚀 New User Logged In! 🚀\n👤 Name: {user_data['name']}\n🆔 Facebook ID: {user_data['id']}\n🌍 IP Address: {user_ip}"
    send_fb_message(OWNER_UID, message)

    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("fb_user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
