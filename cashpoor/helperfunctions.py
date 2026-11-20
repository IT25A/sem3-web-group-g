from cs50 import SQL
import math
import requests

from flask import redirect, render_template, session
from functools import wraps
from apisecrets import OWN_APIKEY


def apology(message: str, code=400):

    def escape(s):
        for old, new in [
            ("-", "--"),
            (" ", " "),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def update_rankings():
    """Update all user rankings"""

    db = SQL("sqlite:///cashpoor.db")

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


# Below must be changed to own API and some more!


def lookup(symbol):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        quote_data = response.json()

        price = float(quote_data["latestPrice"])

        if not math.isfinite(price) or price <= 0:
            return None

        return {
            "name": quote_data["companyName"],
            "price": price,
            "symbol": symbol.upper(),
        }

    except requests.RequestException as e:
        print(f"Request error: {e}")

    except (KeyError, ValueError, TypeError) as e:
        print(f"Data parsing error: {e}")

    return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
