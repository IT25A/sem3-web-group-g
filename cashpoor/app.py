from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


from helperfunctions import (
    apology,
    login_required,
    lookup,
    usd,
    update_rankings,
)

# Configure application
app = Flask(__name__)

# Custom filters
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure library to use sqlite database
db = SQL("sqlite:///cashpoor.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    stocks = db.execute(
        """
        SELECT
            symbol AS symbol,
            company AS company,
            shares AS shares,
            price AS price,
            value AS value
        FROM stocks
        WHERE user_id = ?
        ORDER BY id DESC
    """,
        session["user_id"],
    )

    return render_template("index.html", stocks=stocks)


@app.route("/index")
@login_required
def stocksportfolio():
    """Show portfolio of stocks"""

    stocks = db.execute(
        """
        SELECT
            symbol AS symbol,
            company AS company,
            shares AS shares,
            price AS price,
            value AS value
        FROM stocks
        WHERE user_id = ?
        ORDER BY id DESC
    """,
        session["user_id"],
    )

    return render_template("index.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log an user in"""

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("You must provide username!", 403)

        elif not request.form.get("password"):
            return apology("You must provide password!", 403)

        rows = db.execute(
            """SELECT * FROM users WHERE username = ?""", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Invalid username or password!", 403)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log an user out"""

    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    session.clear()

    user = request.form.get("username")
    hash = request.form.get("password")
    conf = request.form.get("confirmation")

    existing = db.execute("""SELECT id FROM users WHERE username = ?""", user)

    if request.method == "POST":
        if not user:
            return apology("You need to provide a username!", 403)

        if not hash:
            return apology("You need to provide a password!", 403)

        if not conf:
            return apology("You need to provide a confirmation!", 403)

        if existing:
            return apology("Username already taken by somebody else!", 403)

        if hash == conf and not existing:
            db.execute(
                """INSERT INTO users (username, hash) VALUES(?, ?)""",
                user,
                generate_password_hash(hash),
            )

        elif hash != conf:
            return apology("The password and confirmation need to match!", 403)

        return redirect("/")

    elif request.method == "GET":
        return render_template("register.html")

    else:
        return apology("You need to provide the credentials!", 403)


@app.route("/awards")
@login_required
def awards():
    """Showcase all earned awards"""

    user = db.execute(
        """
        SELECT best_rank
        FROM users
        WHERE id = ?
    """,
        session["user_id"],
    )

    if not user:
        return apology("Specific user not found!", 404)

    best_rank = user[0]["best_rank"]

    return render_template("awards.html", best_rank=best_rank)


@app.route("/badges")
@login_required
def badges():
    """Show all earned badges"""

    user = db.execute(
        """
        SELECT best_rank
        FROM users
        WHERE id = ?
    """,
        session["user_id"],
    )

    if not user:
        return apology("Specific user not found!", 404)

    best_rank = user[0]["best_rank"]

    return render_template("badges.html", best_rank=best_rank)


@app.route("/leaderboard")
@login_required
def leaderboard():
    """Show leaderboard and update rankings"""

    db.execute(
        """
        UPDATE users
        SET best_rank = (
            SELECT COUNT(*) + 1
            FROM users AS other
            WHERE other.totaldepot > users.totaldepot
        )
        """
    )

    users = db.execute(
        """
        SELECT
            username,
            best_rank AS rank,
            totalshares,
            totalvalue,
            totaldepot
        FROM users
        ORDER BY best_rank ASC, username ASC
        """
    )

    return render_template("leaderboard.html", users=users)



@app.route("/buyshares", methods=["GET", "POST"])
@login_required
def buyshares():
    """Buy shares and update existing portfolio position"""

    if request.method == "POST":

        symbol = request.form.get("symbol", "").strip().upper()
        number = request.form.get("number", "").strip()

        if not symbol:
            return apology("You must provide a stock symbol!", 400)

        if not number:
            return apology("You must provide the number of shares!", 400)

        try:
            shares = int(number)

            if shares <= 0:
                return apology("You must buy at least one share!", 400)

        except ValueError:
            return apology("Invalid number of shares!", 400)

        stock = lookup(symbol)

        if stock is None:
            return apology("Invalid stock symbol or quote service unavailable!", 400)

        company = stock["name"]
        price = stock["price"]

        value = shares * price

        user = db.execute(
            """
            SELECT cash, totalvalue
            FROM users
            WHERE id = ?
            """,
            session["user_id"]
        )

        if not user:
            return apology("User account not found!", 404)

        cash = user[0]["cash"]
        totalvalue = user[0]["totalvalue"]

        if cash < value:
            return apology("You do not have enough cash!", 400)

        new_cash = cash - value
        new_totalvalue = totalvalue + value
        new_totaldepot = new_cash + new_totalvalue

        db.execute(
            """
            INSERT INTO stocks (
                user_id,
                symbol,
                company,
                shares,
                price,
                value,
                cost_basis
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(user_id, symbol, company)
            DO UPDATE SET

                shares = stocks.shares + excluded.shares,

                cost_basis = stocks.cost_basis + excluded.cost_basis,

                value = stocks.value + excluded.value,

                price = (
                    (stocks.cost_basis + excluded.cost_basis)
                    /
                    (stocks.shares + excluded.shares)
                )
            """,
            session["user_id"],
            symbol,
            company,
            shares,
            price,
            value,
            value
        )

        db.execute(
            """
            UPDATE users
            SET
                cash = ?,
                totalshares = totalshares + ?,
                totalvalue = ?,
                totaldepot = ?
            WHERE id = ?
            """,
            new_cash,
            shares,
            new_totalvalue,
            new_totaldepot,
            session["user_id"]
        )

        update_rankings()

        return redirect("/index")

    return render_template("buyshares.html")



@app.route("/sellshares", methods=["GET", "POST"])
@login_required
def sellshares():
    """Sell shares and update existing portfolio position"""

    if request.method == "POST":

        symbol = request.form.get("symbol", "").strip().upper()
        number = request.form.get("number", "").strip()

        if not symbol:
            return apology("You must provide a stock symbol!", 400)

        if not number:
            return apology("You must provide the number of shares!", 400)

        try:
            shares = int(number)

            if shares <= 0:
                return apology("You must sell at least one share!", 400)

        except ValueError:
            return apology("Invalid number of shares!", 400)

        stock = lookup(symbol)

        if stock is None:
            return apology("Invalid stock symbol or quote service unavailable!", 400)

        price = stock["price"]

        value = shares * price

        user = db.execute(
            """
            SELECT cash, totalshares, totalvalue
            FROM users
            WHERE id = ?
            """,
            session["user_id"]
        )

        if not user:
            return apology("User account not found!", 404)

        cash = user[0]["cash"]
        totalshares = user[0]["totalshares"]
        totalvalue = user[0]["totalvalue"]

        holding = db.execute(
            """
            SELECT id, company, shares, cost_basis
            FROM stocks
            WHERE user_id = ?
            AND symbol = ?
            """,
            session["user_id"],
            symbol
        )

        if not holding:
            return apology(f"You do not own any {symbol} shares!", 400)

        stock_id = holding[0]["id"]
        company = holding[0]["company"]
        shares_owned = holding[0]["shares"]
        remaining_cost_basis = holding[0]["cost_basis"]

        if shares > shares_owned:
            return apology(
                f"You only own {shares_owned} shares of {symbol}!",
                400
            )

        average_cost = remaining_cost_basis / shares_owned
        sold_cost_basis = average_cost * shares

        remaining_shares = shares_owned - shares
        new_cost_basis = remaining_cost_basis - sold_cost_basis

        if abs(new_cost_basis) < 0.000001:
            new_cost_basis = 0

        if remaining_shares > 0:

            new_average_price = new_cost_basis / remaining_shares

            db.execute(
                """
                UPDATE stocks
                SET
                    shares = ?,
                    price = ?,
                    value = ?,
                    cost_basis = ?
                WHERE id = ?
                AND user_id = ?
                """,
                remaining_shares,
                new_average_price,
                new_cost_basis,
                new_cost_basis,
                stock_id,
                session["user_id"]
            )

        else:

            db.execute(
                """
                DELETE FROM stocks
                WHERE id = ?
                AND user_id = ?
                """,
                stock_id,
                session["user_id"]
            )

        new_cash = cash + value
        new_totalshares = totalshares - shares
        new_totalvalue = totalvalue - sold_cost_basis

        if abs(new_totalvalue) < 0.000001:
            new_totalvalue = 0

        new_totaldepot = new_cash + new_totalvalue

        db.execute(
            """
            UPDATE users
            SET
                cash = ?,
                totalshares = ?,
                totalvalue = ?,
                totaldepot = ?
            WHERE id = ?
            """,
            new_cash,
            new_totalshares,
            new_totalvalue,
            new_totaldepot,
            session["user_id"]
        )

        update_rankings()

        return redirect("/index")

    return render_template("sellshares.html")

