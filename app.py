from flask import Flask, render_template, request, redirect, session
import random
import time

app = Flask(__name__)
app.secret_key = "secret123"

# ----- ADMIN (optional future use) -----
ADMIN_USER = "admin"
ADMIN_PASS = "1234"


# ----- LOGIN -----
@app.route("/")
def home_page():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":
        session["user"] = request.form["username"]
        return redirect("/game")

    return render_template("login.html")


# ----- WORD LIST -----
easy_words = ["apple", "table", "train", "money", "sky"]
medium_words = ["python", "bottle", "monkey", "planet", "laptop"]
hard_words = ["elephant", "diamond", "umbrella", "computer", "mountain"]


# ----- GAME -----
@app.route("/game", methods=["GET", "POST"])
def game():

    if "user" not in session:
        return redirect("/login")

    result = ""
    popup = ""
    max_attempts = 6

    # ---------- START GAME ----------
    if request.method == "POST" and "start" in request.form:

        level = request.form.get("level")

        if level == "easy":
            secret = random.choice(easy_words)

        elif level == "medium":
            secret = random.choice(medium_words)

        else:
            secret = random.choice(hard_words)

        session["secret"] = secret
        session["progress"] = "_" * len(secret)
        session["attempts"] = 0
        session["start_time"] = time.time()

    # ---------- GUESS ----------
    elif request.method == "POST":

        guess = request.form.get("guess", "").lower().strip()

        secret = session.get("secret", "")
        progress = session.get("progress", "")
        attempts = session.get("attempts", 0)

        if secret:

            attempts += 1
            session["attempts"] = attempts

            new_progress = ""

            for i in range(len(secret)):

                if i < len(guess) and guess[i] == secret[i]:
                    new_progress += secret[i]
                else:
                    new_progress += progress[i]

            session["progress"] = new_progress

            # ---------- WIN ----------
            if new_progress == secret:

                result = "🎉 You Win!"
                popup = "win"

                session.pop("secret", None)
                session.pop("progress", None)
                session.pop("attempts", None)
                session.pop("start_time", None)

            # ---------- LOSE ----------
            elif attempts >= max_attempts:

                result = f"💀 Game Over! Word was '{secret}'"
                popup = "lose"

                session.pop("secret", None)
                session.pop("progress", None)
                session.pop("attempts", None)
                session.pop("start_time", None)

            else:
                result = f"Progress: {new_progress}"

    # ---------- TIMER ----------
    time_left = 0

    if "start_time" in session:

        total_time = 30
        passed_time = int(time.time() - session["start_time"])
        time_left = total_time - passed_time

        if time_left <= 0:

            popup = "lose"
            result = "⏰ Time Over!"

            session.pop("secret", None)
            session.pop("progress", None)
            session.pop("attempts", None)
            session.pop("start_time", None)

            time_left = 0

    # ---------- DATA ----------
    first_letter = ""
    last_letter = ""
    word_length = ""
    progress = ""

    if "secret" in session:

        secret = session["secret"]

        first_letter = secret[0].upper()
        last_letter = secret[-1].upper()
        word_length = len(secret)
        progress = session["progress"]
        attempts = session["attempts"]

    else:
        attempts = 0

    # ---------- HEART SYSTEM ----------
    hearts_left = "❤️" * (max_attempts - attempts)

    return render_template(
        "index.html",
        first_letter=first_letter,
        last_letter=last_letter,
        word_length=word_length,
        progress=progress,
        result=result,
        attempts=attempts,
        max_attempts=max_attempts,
        popup=popup,
        hearts_left=hearts_left,
        time_left=time_left
    )


if __name__ == "__main__":
    app.run(debug=True)
