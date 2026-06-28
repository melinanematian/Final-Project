"""
data_manager.py
---------------
CSV read/write layer for the Pink Stationery Online Store project.

This file is mainly the responsibility of Person 1.

Goal:
- Keep all CSV logic in one place.
- Other files should not directly repeat CSV reading/writing code.
- If a CSV file is missing, this file creates it automatically.
- If values are invalid, it raises clear errors instead of crashing silently.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict, Optional

from models import User, Product, Order, Comment


class CSVManager:
    """Manages all CSV files used in the project."""

    USER_FIELDS = ["username", "password", "balance", "role"]
    PRODUCT_FIELDS = [
        "product_id",
        "name",
        "price",
        "stock",
        "category",
        "discount",
        "description",
        "image",
        "colors",
    ]
    ORDER_FIELDS = ["username", "product_id", "quantity", "total_price", "date", "color"]
    COMMENT_FIELDS = ["username", "product_id", "comment", "date"]

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.users_path = self.data_dir / "users.csv"
        self.products_path = self.data_dir / "products.csv"
        self.orders_path = self.data_dir / "orders.csv"
        self.comments_path = self.data_dir / "comments.csv"

        self.ensure_files_exist()

    # ---------- General CSV helpers ----------

    def ensure_files_exist(self) -> None:
        """Create all required CSV files if they do not exist."""
        self._ensure_file(self.users_path, self.USER_FIELDS)
        self._ensure_file(self.products_path, self.PRODUCT_FIELDS)
        self._ensure_file(self.orders_path, self.ORDER_FIELDS)
        self._ensure_file(self.comments_path, self.COMMENT_FIELDS)

    def _ensure_file(self, path: Path, fieldnames: List[str]) -> None:
        """Create a CSV file with header if it does not exist."""
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

    def _read_csv(self, path: Path, fieldnames: List[str]) -> List[Dict[str, str]]:
        """Read CSV file and return list of dictionaries."""
        self._ensure_file(path, fieldnames)
        with path.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # If file exists but header is wrong or empty, return empty list safely.
        if reader.fieldnames is None:
            return []

        return rows

    def _write_csv(self, path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
        """Write list of dictionaries to CSV file."""
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # ---------- Users ----------

    def load_users(self) -> List[User]:
        rows = self._read_csv(self.users_path, self.USER_FIELDS)
        users: List[User] = []
        for row in rows:
            try:
                if row.get("username"):
                    users.append(User.from_dict(row))
            except ValueError:
                # Skip invalid rows, but keep program running.
                # Person 1 can explain this in presentation as "safe loading".
                continue
        return users

    def save_users(self, users: List[User]) -> None:
        self._write_csv(self.users_path, self.USER_FIELDS, [user.to_dict() for user in users])

    def find_user(self, username: str) -> Optional[User]:
        username = username.strip()
        for user in self.load_users():
            if user.username == username:
                return user
        return None

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Return user if username/password are correct, otherwise None."""
        user = self.find_user(username)
        if user and user.check_password(password):
            return user
        return None

    def update_user(self, updated_user: User) -> None:
        """Update one user in users.csv."""
        users = self.load_users()
        found = False
        for index, user in enumerate(users):
            if user.username == updated_user.username:
                users[index] = updated_user
                found = True
                break
        if not found:
            users.append(updated_user)
        self.save_users(users)

    # ---------- Products ----------

    def load_products(self) -> List[Product]:
        rows = self._read_csv(self.products_path, self.PRODUCT_FIELDS)
        products: List[Product] = []
        for row in rows:
            try:
                if row.get("product_id"):
                    products.append(Product.from_dict(row))
            except ValueError:
                continue
        return products

    def save_products(self, products: List[Product]) -> None:
        self._write_csv(
            self.products_path,
            self.PRODUCT_FIELDS,
            [product.to_dict() for product in products],
        )

    def find_product(self, product_id: str) -> Optional[Product]:
        product_id = product_id.strip()
        for product in self.load_products():
            if product.product_id == product_id:
                return product
        return None

    def add_product(self, product: Product) -> None:
        """Add a new product; product_id must be unique."""
        products = self.load_products()
        if any(p.product_id == product.product_id for p in products):
            raise ValueError("Product ID already exists.")
        products.append(product)
        self.save_products(products)

    def update_product(self, updated_product: Product) -> None:
        """Update product by product_id."""
        products = self.load_products()
        for index, product in enumerate(products):
            if product.product_id == updated_product.product_id:
                products[index] = updated_product
                self.save_products(products)
                return
        raise ValueError("Product not found.")

    # ---------- Orders ----------

    def load_orders(self) -> List[Order]:
        rows = self._read_csv(self.orders_path, self.ORDER_FIELDS)
        orders: List[Order] = []
        for row in rows:
            try:
                if row.get("username") and row.get("product_id"):
                    orders.append(Order.from_dict(row))
            except ValueError:
                continue
        return orders

    def save_orders(self, orders: List[Order]) -> None:
        self._write_csv(self.orders_path, self.ORDER_FIELDS, [order.to_dict() for order in orders])

    def add_order(self, order: Order) -> None:
        orders = self.load_orders()
        orders.append(order)
        self.save_orders(orders)

    # ---------- Comments ----------

    def load_comments(self) -> List[Comment]:
        rows = self._read_csv(self.comments_path, self.COMMENT_FIELDS)
        comments: List[Comment] = []
        for row in rows:
            try:
                if row.get("username") and row.get("product_id"):
                    comments.append(Comment.from_dict(row))
            except ValueError:
                continue
        return comments

    def save_comments(self, comments: List[Comment]) -> None:
        self._write_csv(
            self.comments_path,
            self.COMMENT_FIELDS,
            [comment.to_dict() for comment in comments],
        )

    def add_comment(self, comment: Comment) -> None:
        comments = self.load_comments()
        comments.append(comment)
        self.save_comments(comments)

    def comments_for_product(self, product_id: str) -> List[Comment]:
        return [c for c in self.load_comments() if c.product_id == product_id]

    # ---------- Sales report helpers for Person 3 ----------

    def total_sales(self) -> float:
        """Return total income from all orders."""
        return sum(order.total_price for order in self.load_orders())

    def sales_by_product(self) -> Dict[str, float]:
        """Return total sales amount grouped by product_id."""
        report: Dict[str, float] = {}
        for order in self.load_orders():
            report[order.product_id] = report.get(order.product_id, 0) + order.total_price
        return report

    def quantity_by_product(self) -> Dict[str, int]:
        """Return sold quantity grouped by product_id."""
        report: Dict[str, int] = {}
        for order in self.load_orders():
            report[order.product_id] = report.get(order.product_id, 0) + order.quantity
        return report
