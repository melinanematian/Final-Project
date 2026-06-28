"""
models.py
---------
OOP models for the pink shop online stationery store project.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any


@dataclass
class User:
    username: str
    password: str
    balance: float
    role: str

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "User":
        return cls(
            username=row.get("username", "").strip(),
            password=row.get("password", "").strip(),
            balance=float(row.get("balance", 0) or 0),
            role=row.get("role", "").strip().lower(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password,
            "balance": f"{self.balance:.2f}",
            "role": self.role,
        }

    def check_password(self, entered_password: str) -> bool:
        return self.password == entered_password

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_customer(self) -> bool:
        return self.role == "customer"


@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int
    category: str
    discount: float = 0.0
    description: str = ""
    image: str = ""
    colors: str = ""

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Product":
        return cls(
            product_id=row.get("product_id", "").strip(),
            name=row.get("name", "").strip(),
            price=float(row.get("price", 0) or 0),
            stock=int(float(row.get("stock", 0) or 0)),
            category=row.get("category", "").strip(),
            discount=float(row.get("discount", 0) or 0),
            description=row.get("description", "").strip(),
            image=row.get("image", "").strip(),
            colors=row.get("colors", "").strip(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": f"{self.price:.2f}",
            "stock": str(self.stock),
            "category": self.category,
            "discount": f"{self.discount:.2f}",
            "description": self.description,
            "image": self.image,
            "colors": self.colors,
        }

    def final_price(self) -> float:
        return self.price - (self.price * self.discount / 100)

    def is_available(self, quantity: int = 1) -> bool:
        return self.stock >= quantity

    def reduce_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if quantity > self.stock:
            raise ValueError("Not enough stock.")
        self.stock -= quantity

    def color_options(self) -> list[str]:
        if not self.colors:
            return []
        return [color.strip() for color in self.colors.replace(",", "|").split("|") if color.strip()]


@dataclass
class Order:
    username: str
    product_id: str
    quantity: int
    total_price: float
    date: str
    color: str = ""

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Order":
        return cls(
            username=row.get("username", "").strip(),
            product_id=row.get("product_id", "").strip(),
            quantity=int(float(row.get("quantity", 0) or 0)),
            total_price=float(row.get("total_price", 0) or 0),
            date=row.get("date", "").strip(),
            color=row.get("color", "").strip(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "product_id": self.product_id,
            "quantity": str(self.quantity),
            "total_price": f"{self.total_price:.2f}",
            "date": self.date,
            "color": self.color,
        }

    @staticmethod
    def today(username: str, product_id: str, quantity: int, total_price: float, color: str = "") -> "Order":
        return Order(
            username=username,
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            date=date.today().isoformat(),
            color=color,
        )


@dataclass
class Comment:
    username: str
    product_id: str
    comment: str
    date: str

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Comment":
        return cls(
            username=row.get("username", "").strip(),
            product_id=row.get("product_id", "").strip(),
            comment=row.get("comment", "").strip(),
            date=row.get("date", "").strip(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "product_id": self.product_id,
            "comment": self.comment,
            "date": self.date,
        }

    @staticmethod
    def today(username: str, product_id: str, comment: str) -> "Comment":
        return Comment(username=username, product_id=product_id, comment=comment, date=date.today().isoformat())


@dataclass
class CartItem:
    product: Product
    quantity: int
    selected_color: str = ""

    def item_total(self) -> float:
        return self.product.final_price() * self.quantity
