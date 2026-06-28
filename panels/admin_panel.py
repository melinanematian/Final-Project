"""
admin_panel.py
--------------
پنل مدیر برای پروژه pink shop.

امکانات:
- نمایش همه محصولات با عکس، قیمت، موجودی و دسته‌بندی
- افزایش موجودی هر محصول
- کاهش موجودی هر محصول
- تغییر قیمت هر محصول
- تغییر تخفیف هر محصول
- حذف محصول
- افزودن محصول جدید همراه با انتخاب/آپلود عکس
- مشاهده سفارش‌ها و گزارش فروش ساده
"""

from __future__ import annotations

from pathlib import Path
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import List

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

from models import User, Product


PINK_BG = "#FFF0F6"
PINK_CARD = "#FFFFFF"
PINK_LIGHT = "#FFD6E7"
PINK_DARK = "#C2185B"
PINK_MAIN = "#FF69A6"
TEXT_DARK = "#3A2430"


class AdminPanel(ttk.Frame):
    """پنل فارسی مدیر فروشگاه."""

    def __init__(self, parent: ttk.Frame, app: tk.Tk, user: User) -> None:
        super().__init__(parent)
        self.app = app
        self.user = user
        self.products: List[Product] = []
        self.product_images: dict[str, tk.PhotoImage] = {}
        self.content: ttk.Frame | None = None
        self.products_cards_frame: ttk.Frame | None = None
        self.category_var = tk.StringVar(value="همه")
        self.search_var = tk.StringVar()
        self._build_ui()
        self.show_products_page()

    # ---------- ابزارهای عمومی ----------

    def normalize_number_text(self, text: str) -> str:
        """اعداد فارسی/عربی را به انگلیسی تبدیل می‌کند."""
        translation = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
        cleaned = text.translate(translation)
        return cleaned.replace(",", "").replace("،", "").replace(" ", "").strip()

    def ask_positive_int(self, title: str, prompt: str, min_value: int = 0) -> int | None:
        while True:
            raw = simpledialog.askstring(title, prompt)
            if raw is None:
                return None
            raw = self.normalize_number_text(raw)
            try:
                value = int(raw)
            except ValueError:
                messagebox.showerror("عدد نامعتبر", "لطفاً فقط عدد وارد کن. عدد فارسی و انگلیسی هر دو قابل قبول‌اند.")
                continue
            if value < min_value:
                messagebox.showerror("عدد نامعتبر", f"عدد باید حداقل {min_value} باشد.")
                continue
            return value

    def ask_positive_float(self, title: str, prompt: str, min_value: float = 0) -> float | None:
        while True:
            raw = simpledialog.askstring(title, prompt)
            if raw is None:
                return None
            raw = self.normalize_number_text(raw)
            try:
                value = float(raw)
            except ValueError:
                messagebox.showerror("عدد نامعتبر", "لطفاً فقط عدد وارد کن. عدد فارسی و انگلیسی هر دو قابل قبول‌اند.")
                continue
            if value < min_value:
                messagebox.showerror("عدد نامعتبر", f"عدد باید حداقل {min_value:,.0f} باشد.")
                continue
            return value

    def clear_content(self) -> None:
        if self.content is None:
            return
        for widget in self.content.winfo_children():
            widget.destroy()

    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    def image_path_for_product(self, product: Product) -> Path:
        return self.project_root() / "images" / product.image

    def load_product_thumbnail(self, product: Product, size: tuple[int, int] = (140, 110)) -> tk.PhotoImage | None:
        cache_key = f"{product.product_id}_{size[0]}x{size[1]}"
        if cache_key in self.product_images:
            return self.product_images[cache_key]
        path = self.image_path_for_product(product)
        if not product.image or not path.exists():
            return None
        try:
            if Image is not None and ImageTk is not None:
                img = Image.open(path).convert("RGBA")
                img.thumbnail(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            else:
                photo = tk.PhotoImage(file=str(path))
            self.product_images[cache_key] = photo
            return photo
        except Exception:
            return None

    # ---------- ساخت ظاهر ----------

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=18, style="Header.TFrame")
        header.pack(fill="x")

        ttk.Label(
            header,
            text=f"پنل مدیر pink shop - خوش آمدی {self.user.username}",
            style="Pink.TLabel",
        ).pack(side="left")

        ttk.Button(header, text="خروج", command=self.app.logout).pack(side="right")

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        menu = ttk.Frame(main, padding=15, style="Card.TFrame")
        menu.pack(side="left", fill="y")

        ttk.Label(menu, text="منوی مدیر", style="Card.TLabel", font=("Arial", 14, "bold")).pack(pady=(0, 12))

        buttons = [
            ("نمایش محصولات", self.show_products_page),
            ("افزودن محصول جدید", self.show_add_product_page),
            ("مشاهده سفارش‌ها", self.show_orders_page),
            ("گزارش فروش", self.show_sales_report_page),
            ("به‌روزرسانی", self.show_products_page),
        ]
        for text, command in buttons:
            ttk.Button(menu, text=text, command=command, width=22).pack(fill="x", pady=5)

        self.content = ttk.Frame(main, padding=20)
        self.content.pack(side="right", fill="both", expand=True)

    # ---------- نمایش محصولات ----------

    def show_products_page(self) -> None:
        self.clear_content()
        self.product_images = {}
        self.products = self.app.data_manager.load_products()

        top = ttk.Frame(self.content)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="مدیریت محصولات", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="+ افزودن محصول جدید", style="Primary.TButton", command=self.show_add_product_page).pack(side="right")

        controls = ttk.Frame(self.content, padding=10, style="Card.TFrame")
        controls.pack(fill="x", pady=(0, 12))
        ttk.Label(controls, text="جستجو:", style="Card.TLabel").pack(side="left")
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=28)
        search_entry.pack(side="left", padx=6)
        search_entry.bind("<Return>", lambda event: self.populate_products())

        categories = ["همه"] + sorted({p.category for p in self.products if p.category})
        ttk.Label(controls, text="دسته‌بندی:", style="Card.TLabel").pack(side="left", padx=(15, 0))
        category_combo = ttk.Combobox(controls, textvariable=self.category_var, values=categories, state="readonly", width=18)
        category_combo.pack(side="left", padx=6)
        category_combo.bind("<<ComboboxSelected>>", lambda event: self.populate_products())
        ttk.Button(controls, text="اعمال", command=self.populate_products).pack(side="left", padx=5)
        ttk.Button(controls, text="نمایش همه", command=self.clear_filters).pack(side="left", padx=5)

        canvas = tk.Canvas(self.content, bg=PINK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        self.products_cards_frame = ttk.Frame(canvas)
        self.products_cards_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.products_cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.populate_products()

    def clear_filters(self) -> None:
        self.search_var.set("")
        self.category_var.set("همه")
        self.populate_products()

    def filtered_products(self) -> List[Product]:
        keyword = self.search_var.get().strip().lower()
        category = self.category_var.get().strip()
        result = []
        for product in self.products:
            text = f"{product.product_id} {product.name} {product.category} {product.description}".lower()
            if keyword and keyword not in text:
                continue
            if category != "همه" and product.category != category:
                continue
            result.append(product)
        return result

    def populate_products(self) -> None:
        frame = self.products_cards_frame
        if frame is None:
            return
        for widget in frame.winfo_children():
            widget.destroy()

        products = self.filtered_products()
        if not products:
            ttk.Label(frame, text="محصولی پیدا نشد.", style="Subtitle.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        columns_count = 3
        for index, product in enumerate(products):
            row = index // columns_count
            col = index % columns_count
            card = ttk.Frame(frame, padding=12, style="Card.TFrame")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            frame.columnconfigure(col, weight=1)

            img = self.load_product_thumbnail(product)
            if img:
                ttk.Label(card, image=img, style="Card.TLabel").pack(pady=(0, 8))
            else:
                ttk.Label(card, text="بدون عکس", style="Card.TLabel").pack(pady=(0, 8))

            ttk.Label(card, text=product.name, style="Card.TLabel", font=("Arial", 13, "bold"), wraplength=220).pack(anchor="center")
            ttk.Label(card, text=f"کد: {product.product_id}", style="Card.TLabel", font=("Arial", 10)).pack(pady=(2, 0))
            ttk.Label(card, text=f"دسته‌بندی: {product.category}", style="Card.TLabel", font=("Arial", 10)).pack(pady=(2, 0))
            ttk.Label(card, text=f"موجودی: {product.stock}", style="Card.TLabel", font=("Arial", 10)).pack(pady=(2, 0))
            ttk.Label(card, text=f"قیمت اصلی: {product.price:,.0f} تومان", style="Card.TLabel", foreground=PINK_DARK, font=("Arial", 11, "bold")).pack(pady=(6, 0))
            ttk.Label(card, text=f"تخفیف: {product.discount:,.0f}%", style="Card.TLabel", font=("Arial", 10)).pack(pady=(2, 0))
            ttk.Label(card, text=f"قیمت نهایی: {product.final_price():,.0f} تومان", style="Card.TLabel", foreground=PINK_MAIN, font=("Arial", 11, "bold")).pack(pady=(2, 8))

            actions = ttk.Frame(card, style="Card.TFrame")
            actions.pack(fill="x")
            ttk.Button(actions, text="افزایش موجودی", command=lambda p=product: self.increase_product_stock(p)).pack(fill="x", pady=3)
            ttk.Button(actions, text="کاهش موجودی", command=lambda p=product: self.decrease_product_stock(p)).pack(fill="x", pady=3)
            ttk.Button(actions, text="تغییر قیمت", command=lambda p=product: self.change_product_price(p)).pack(fill="x", pady=3)
            ttk.Button(actions, text="تغییر تخفیف", command=lambda p=product: self.change_product_discount(p)).pack(fill="x", pady=3)
            ttk.Button(actions, text="ویرایش توضیحات", command=lambda p=product: self.edit_product_description(p)).pack(fill="x", pady=3)
            ttk.Button(actions, text="حذف محصول", command=lambda p=product: self.delete_product(p)).pack(fill="x", pady=3)

    def delete_product(self, product: Product) -> None:
        """حذف محصول از products.csv بعد از تأیید مدیر."""
        has_orders = any(order.product_id == product.product_id for order in self.app.data_manager.load_orders())
        extra_warning = ""
        if has_orders:
            extra_warning = "\n\nتوجه: برای این محصول قبلاً سفارش ثبت شده است. سفارش‌های قبلی حذف نمی‌شوند، فقط خود محصول از لیست فروشگاه حذف می‌شود."

        confirmed = messagebox.askyesno(
            "حذف محصول",
            f"آیا مطمئنی می‌خواهی محصول زیر حذف شود؟\n\n{product.name}\nکد: {product.product_id}{extra_warning}",
        )
        if not confirmed:
            return

        products = self.app.data_manager.load_products()
        new_products = [p for p in products if p.product_id != product.product_id]
        if len(new_products) == len(products):
            messagebox.showerror("خطا", "محصول پیدا نشد.")
            return

        try:
            self.app.data_manager.save_products(new_products)
            messagebox.showinfo("انجام شد", "محصول با موفقیت حذف شد.")
            self.show_products_page()
        except Exception as error:
            messagebox.showerror("خطا", f"محصول حذف نشد.\n\n{error}")

    def increase_product_stock(self, product: Product) -> None:
        amount = self.ask_positive_int("افزایش موجودی محصول", f"چند عدد به موجودی '{product.name}' اضافه شود؟", min_value=1)
        if amount is None:
            return
        product.stock += amount
        try:
            self.app.data_manager.update_product(product)
            messagebox.showinfo("انجام شد", f"{amount} عدد به موجودی محصول اضافه شد.")
            self.show_products_page()
        except Exception as error:
            messagebox.showerror("خطا", f"موجودی ذخیره نشد.\n\n{error}")


    def decrease_product_stock(self, product: Product) -> None:
        """کاهش موجودی محصول توسط مدیر.

        مقدار کاهش نباید از موجودی فعلی بیشتر باشد؛ چون موجودی منفی در فروشگاه معنی ندارد.
        """
        amount = self.ask_positive_int(
            "کاهش موجودی محصول",
            f"چند عدد از موجودی '{product.name}' کم شود؟\nموجودی فعلی: {product.stock}",
            min_value=1,
        )
        if amount is None:
            return
        if amount > product.stock:
            messagebox.showerror("عدد نامعتبر", "مقدار کاهش نمی‌تواند از موجودی فعلی بیشتر باشد.")
            return
        product.stock -= amount
        try:
            self.app.data_manager.update_product(product)
            messagebox.showinfo("انجام شد", f"{amount} عدد از موجودی محصول کم شد.")
            self.show_products_page()
        except Exception as error:
            messagebox.showerror("خطا", f"موجودی ذخیره نشد.\n\n{error}")

    def change_product_price(self, product: Product) -> None:
        new_price = self.ask_positive_float("تغییر قیمت", f"قیمت جدید برای '{product.name}' را وارد کن:", min_value=0)
        if new_price is None:
            return
        product.price = new_price
        try:
            self.app.data_manager.update_product(product)
            messagebox.showinfo("انجام شد", "قیمت محصول تغییر کرد.")
            self.show_products_page()
        except Exception as error:
            messagebox.showerror("خطا", f"قیمت ذخیره نشد.\n\n{error}")


    def change_product_discount(self, product: Product) -> None:
        """تغییر درصد تخفیف محصول توسط مدیر.

        تخفیف در فایل products.csv به صورت درصد ذخیره می‌شود.
        مثال: عدد 10 یعنی ده درصد تخفیف.
        """
        new_discount = self.ask_positive_float(
            "تغییر تخفیف",
            f"درصد تخفیف جدید برای '{product.name}' را وارد کن:\nمثلاً 10 یعنی ۱۰ درصد",
            min_value=0,
        )
        if new_discount is None:
            return
        if new_discount > 100:
            messagebox.showerror("تخفیف نامعتبر", "درصد تخفیف نمی‌تواند بیشتر از 100 باشد.")
            return
        product.discount = new_discount
        try:
            self.app.data_manager.update_product(product)
            messagebox.showinfo("انجام شد", "تخفیف محصول تغییر کرد.")
            self.show_products_page()
        except Exception as error:
            messagebox.showerror("خطا", f"تخفیف ذخیره نشد.\n\n{error}")

    def edit_product_description(self, product: Product) -> None:
        new_description = simpledialog.askstring("ویرایش توضیحات", "توضیح جدید محصول:", initialvalue=product.description)
        if new_description is None:
            return
        product.description = new_description.strip()
        try:
            self.app.data_manager.update_product(product)
            messagebox.showinfo("انجام شد", "توضیحات محصول تغییر کرد.")
            self.show_products_page()
        except Exception as error:
            messagebox.showerror("خطا", f"توضیحات ذخیره نشد.\n\n{error}")

    # ---------- افزودن محصول جدید ----------

    def show_add_product_page(self) -> None:
        self.clear_content()
        ttk.Label(self.content, text="افزودن محصول جدید", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        card = ttk.Frame(self.content, padding=18, style="Card.TFrame")
        card.pack(fill="x")

        fields = {
            "product_id": tk.StringVar(),
            "name": tk.StringVar(),
            "price": tk.StringVar(),
            "stock": tk.StringVar(),
            "category": tk.StringVar(value="نوشت‌افزار"),
            "discount": tk.StringVar(value="0"),
            "colors": tk.StringVar(),
            "image": tk.StringVar(),
        }

        labels = [
            ("product_id", "کد محصول"),
            ("name", "نام محصول"),
            ("price", "قیمت"),
            ("stock", "موجودی"),
            ("category", "دسته‌بندی"),
            ("discount", "تخفیف درصدی"),
            ("colors", "رنگ‌ها/مدل‌ها با | جدا شوند"),
        ]

        for row, (key, label) in enumerate(labels):
            ttk.Label(card, text=label + ":", style="Card.TLabel", font=("Arial", 11, "bold")).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
            if key == "category":
                combo = ttk.Combobox(card, textvariable=fields[key], values=["نوشت‌افزار", "کیف و جامدادی", "ماشین حساب", "پوشه"], width=32)
                combo.grid(row=row, column=1, sticky="ew", pady=6)
            else:
                ttk.Entry(card, textvariable=fields[key], width=36).grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Label(card, text="توضیحات:", style="Card.TLabel", font=("Arial", 11, "bold")).grid(row=7, column=0, sticky="nw", padx=(0, 10), pady=6)
        description_text = tk.Text(card, height=5, width=42, wrap="word", bg="white", fg=TEXT_DARK)
        description_text.grid(row=7, column=1, sticky="ew", pady=6)

        image_label_var = tk.StringVar(value="عکسی انتخاب نشده")
        ttk.Label(card, text="عکس محصول:", style="Card.TLabel", font=("Arial", 11, "bold")).grid(row=8, column=0, sticky="w", padx=(0, 10), pady=6)
        image_row = ttk.Frame(card, style="Card.TFrame")
        image_row.grid(row=8, column=1, sticky="ew", pady=6)
        ttk.Label(image_row, textvariable=image_label_var, style="Card.TLabel").pack(side="left")

        selected_image_path = {"path": ""}

        def choose_image() -> None:
            path = filedialog.askopenfilename(
                title="انتخاب عکس محصول",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
            )
            if not path:
                return
            selected_image_path["path"] = path
            image_label_var.set(Path(path).name)

        ttk.Button(image_row, text="انتخاب/آپلود عکس", command=choose_image).pack(side="right")

        def save_product() -> None:
            try:
                product_id = fields["product_id"].get().strip()
                name = fields["name"].get().strip()
                if not product_id or not name:
                    messagebox.showerror("اطلاعات ناقص", "کد محصول و نام محصول الزامی هستند.")
                    return
                if self.app.data_manager.find_product(product_id) is not None:
                    messagebox.showerror("کد تکراری", "این کد محصول قبلاً وجود دارد.")
                    return
                price = float(self.normalize_number_text(fields["price"].get()))
                stock = int(self.normalize_number_text(fields["stock"].get()))
                discount = float(self.normalize_number_text(fields["discount"].get() or "0"))
                category = fields["category"].get().strip() or "نوشت‌افزار"
                colors = fields["colors"].get().strip()
                description = description_text.get("1.0", "end").strip()
            except ValueError:
                messagebox.showerror("عدد نامعتبر", "قیمت، موجودی و تخفیف باید عدد باشند.")
                return

            image_filename = ""
            if selected_image_path["path"]:
                src = Path(selected_image_path["path"])
                suffix = src.suffix.lower() or ".png"
                image_filename = f"{product_id.lower()}{suffix}"
                dest = self.project_root() / "images" / image_filename
                try:
                    shutil.copy2(src, dest)
                except Exception as error:
                    messagebox.showerror("خطای عکس", f"عکس کپی نشد.\n\n{error}")
                    return

            new_product = Product(
                product_id=product_id,
                name=name,
                price=price,
                stock=stock,
                category=category,
                discount=discount,
                description=description,
                image=image_filename,
                colors=colors,
            )
            try:
                self.app.data_manager.add_product(new_product)
            except Exception as error:
                messagebox.showerror("خطای ذخیره", f"محصول ذخیره نشد.\n\n{error}")
                return
            messagebox.showinfo("انجام شد", "محصول جدید با موفقیت اضافه شد.")
            self.show_products_page()

        actions = ttk.Frame(self.content)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="ذخیره محصول", style="Primary.TButton", command=save_product).pack(side="left", padx=5)
        ttk.Button(actions, text="بازگشت", command=self.show_products_page).pack(side="left", padx=5)

    # ---------- سفارش‌ها و گزارش فروش ----------

    def show_orders_page(self) -> None:
        self.clear_content()
        ttk.Label(self.content, text="سفارش‌ها", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        columns = ("date", "username", "product", "color", "qty", "total")
        tree = ttk.Treeview(self.content, columns=columns, show="headings", height=16)
        headings = {
            "date": "تاریخ",
            "username": "کاربر",
            "product": "محصول",
            "color": "رنگ/مدل",
            "qty": "تعداد",
            "total": "مبلغ کل",
        }
        widths = {"date": 110, "username": 120, "product": 220, "color": 110, "qty": 70, "total": 140}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        tree.pack(fill="both", expand=True)

        product_map = {p.product_id: p.name for p in self.app.data_manager.load_products()}
        for order in self.app.data_manager.load_orders():
            tree.insert(
                "",
                "end",
                values=(order.date, order.username, product_map.get(order.product_id, order.product_id), order.color or "-", order.quantity, f"{order.total_price:,.0f}"),
            )

    def show_sales_report_page(self) -> None:
        self.clear_content()
        ttk.Label(self.content, text="گزارش فروش", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        total = self.app.data_manager.total_sales()
        orders = self.app.data_manager.load_orders()
        quantity_by_product = self.app.data_manager.quantity_by_product()
        sales_by_product = self.app.data_manager.sales_by_product()
        products = {p.product_id: p for p in self.app.data_manager.load_products()}

        summary = ttk.Frame(self.content, padding=18, style="Card.TFrame")
        summary.pack(fill="x", pady=(0, 12))
        ttk.Label(summary, text=f"فروش کل: {total:,.0f} تومان", style="Card.TLabel", font=("Arial", 15, "bold"), foreground=PINK_DARK).pack(anchor="w")
        ttk.Label(summary, text=f"تعداد سفارش‌ها: {len(orders)}", style="Card.TLabel", font=("Arial", 12)).pack(anchor="w", pady=(6, 0))

        columns = ("product", "quantity", "sales")
        tree = ttk.Treeview(self.content, columns=columns, show="headings", height=14)
        tree.heading("product", text="محصول")
        tree.heading("quantity", text="تعداد فروش")
        tree.heading("sales", text="مبلغ فروش")
        tree.column("product", width=260, anchor="center")
        tree.column("quantity", width=120, anchor="center")
        tree.column("sales", width=150, anchor="center")
        tree.pack(fill="both", expand=True)

        for product_id, quantity in sorted(quantity_by_product.items()):
            product_name = products[product_id].name if product_id in products else product_id
            tree.insert("", "end", values=(product_name, quantity, f"{sales_by_product.get(product_id, 0):,.0f}"))
