"""
customer_panel.py
-----------------
بخش نفر ۲ برای پروژه فروشگاه اینترنتی لوازم‌التحریر صورتی.

امکانات پیاده‌سازی‌شده:
- پنل مشتری
- نمایش لیست محصولات
- جستجو و فیلتر محصول
- نمایش جزئیات محصول همراه با توضیحات، تخفیف، عکس و کامنت‌ها
- افزودن محصول به سبد خرید
- مشاهده، حذف و خالی کردن سبد خرید
- پرداخت نهایی با بررسی موجودی کالا و موجودی حساب
- ثبت سفارش در orders.csv
- مشاهده سفارش‌های مشتری
- ثبت و نمایش کامنت محصول
"""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import List, Optional

try:
    from PIL import Image, ImageTk
except ImportError:  # اگر Pillow نصب نبود، برنامه با PhotoImage ساده اجرا می‌شود.
    Image = None
    ImageTk = None

from models import User, Product, CartItem, Order, Comment


PINK_BG = "#FFF0F6"
PINK_CARD = "#FFFFFF"
PINK_LIGHT = "#FFD6E7"
PINK_DARK = "#C2185B"
TEXT_DARK = "#3A2430"


class CustomerPanel(ttk.Frame):
    """پنل مشتری؛ این فایل بخش اصلی نفر ۲ است."""

    def __init__(self, parent: ttk.Frame, app: tk.Tk, user: User) -> None:
        super().__init__(parent)
        self.app = app
        self.user = user

        # سبد خرید مشتری فعلی. هر عضو آن یک CartItem است.
        self.cart: List[CartItem] = []

        # محصولات کامل و محصولات فیلترشده برای نمایش در جدول.
        self.products: List[Product] = []
        self.filtered_products: List[Product] = []

        # متغیرهای گرافیکی Tkinter برای سرچ، دسته‌بندی و موجودی حساب.
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="همه")
        self.balance_var = tk.StringVar()

        # نگهداری اجزای صفحه برای اینکه بعداً بتوانیم پاک یا آپدیتشان کنیم.
        self.content: ttk.Frame | None = None
        self.product_tree: ttk.Treeview | None = None
        self.cart_tree: ttk.Treeview | None = None
        self.orders_tree: ttk.Treeview | None = None
        self.comment_box: tk.Text | None = None

        # اگر عکس را در یک متغیر نگه نداریم، Tkinter ممکن است آن را از حافظه پاک کند.
        self.current_product_image: tk.PhotoImage | None = None
        self.product_images: dict[str, tk.PhotoImage] = {}
        self.icons: dict[str, tk.PhotoImage] = {}
        self.selected_product_id: str | None = None

        self.refresh_user()
        self.load_icons()
        self._build_ui()
        self.show_products_page()


    def load_icons(self) -> None:
        """آیکن‌های دکمه‌ها را از پوشه images می‌خواند.

        برای افزودن به سبد، فقط عکس استفاده می‌شود؛ نه ایموجی، نه متن اضافه.
        عکس هم با Pillow و کیفیت بهتر resize می‌شود تا تار و پیکسلی دیده نشود.
        """
        project_root = Path(__file__).resolve().parent.parent

        # آیکن جزئیات کوچک است.
        details_path = project_root / "images" / "details_icon.png"
        if details_path.exists():
            try:
                self.icons["details"] = tk.PhotoImage(file=str(details_path))
            except tk.TclError:
                pass

        # آیکن سبد خرید بزرگ‌تر و با resize نرم‌تر ساخته می‌شود.
        cart_path = project_root / "images" / "cart_plus.png"
        if cart_path.exists():
            try:
                if Image is not None and ImageTk is not None:
                    cart_img = Image.open(cart_path).convert("RGBA")
                    cart_img = cart_img.resize((52, 52), Image.Resampling.LANCZOS)
                    self.icons["cart"] = ImageTk.PhotoImage(cart_img)
                else:
                    self.icons["cart"] = tk.PhotoImage(file=str(cart_path))
            except Exception:
                pass

    def make_icon_button(self, parent: ttk.Frame, text: str, command, icon_key: str | None = None, primary: bool = False):
        """دکمه عمومی می‌سازد؛ اگر آیکن موجود باشد، کنار متن می‌آید."""
        image = self.icons.get(icon_key or "")
        style = "Primary.TButton" if primary else "TButton"
        if image is not None:
            return ttk.Button(parent, text=text, image=image, compound="left", command=command, style=style)
        return ttk.Button(parent, text=text, command=command, style=style)

    def make_cart_button(self, parent: ttk.Frame, command):
        """دکمه افزودن به سبد: فقط عکس سبد، بدون ایموجی و متن اضافه."""
        image = self.icons.get("cart")
        if image is not None:
            return ttk.Button(parent, image=image, command=command, style="Primary.TButton")
        return ttk.Button(parent, text="افزودن به سبد", command=command, style="Primary.TButton")

    # ---------- ظاهر کلی پنل مشتری ----------

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=18, style="Header.TFrame")
        header.pack(fill="x")

        title = ttk.Label(
            header,
            text=f"پنل مشتری pink shop - خوش آمدی {self.user.username}",
            style="Pink.TLabel",
        )
        title.pack(side="left")

        balance_label = ttk.Label(header, textvariable=self.balance_var, style="Pink.TLabel")
        balance_label.pack(side="left", padx=25)

        increase_balance_btn = ttk.Button(
            header,
            text="افزایش موجودی",
            command=self.increase_balance,
            style="Primary.TButton",
        )
        increase_balance_btn.pack(side="left", padx=(0, 15))

        logout_btn = ttk.Button(header, text="خروج", command=self.app.logout)
        logout_btn.pack(side="right")

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        menu = ttk.Frame(main, padding=15, style="Card.TFrame")
        menu.pack(side="left", fill="y")

        ttk.Label(menu, text="منو", style="Card.TLabel", font=("Arial", 14, "bold")).pack(pady=(0, 12))

        buttons = [
            ("نمایش محصولات", self.show_products_page),
            ("جزئیات محصول", self.show_selected_product_details),
            ("سبد خرید", self.show_cart_page),
            ("سفارش‌های من", self.show_orders_page),
            ("افزایش موجودی", self.increase_balance),
            ("به‌روزرسانی", self.show_products_page),
        ]
        for text, command in buttons:
            ttk.Button(menu, text=text, command=command, width=20).pack(fill="x", pady=5)

        self.content = ttk.Frame(main, padding=20)
        self.content.pack(side="right", fill="both", expand=True)

    def clear_content(self) -> None:
        """محتوای وسط صفحه را پاک می‌کند تا صفحه جدید نمایش داده شود."""
        if self.content is None:
            return
        for widget in self.content.winfo_children():
            widget.destroy()

    def refresh_user(self) -> None:
        """اطلاعات کاربر را دوباره از CSV می‌خواند تا موجودی حساب به‌روز باشد."""
        found_user = self.app.data_manager.find_user(self.user.username)
        if found_user is not None:
            self.user = found_user
        self.balance_var.set(f"موجودی: {self.user.balance:,.0f} تومان")

    # ---------- صفحه محصولات ----------

    def show_products_page(self) -> None:
        """صفحه محصولات را با کارت‌های تصویری و دکمه سریع خرید نمایش می‌دهد."""
        self.clear_content()
        self.refresh_user()
        self.products = self.app.data_manager.load_products()
        self.filtered_products = list(self.products)
        self.selected_product_id = None
        self.product_images = {}

        top = ttk.Frame(self.content)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="محصولات pink shop", style="Title.TLabel").pack(side="left")
        ttk.Label(top, text="هر محصول یک کارت دارد؛ با دکمه سبد خرید سریع اضافه کن یا جزئیات را ببین.", style="Subtitle.TLabel").pack(side="left", padx=18)

        controls = ttk.Frame(self.content, padding=10, style="Card.TFrame")
        controls.pack(fill="x", pady=(0, 14))

        ttk.Label(controls, text="جستجو:", style="Card.TLabel").pack(side="left")
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=28)
        search_entry.pack(side="left", padx=6)
        search_entry.bind("<Return>", lambda event: self.apply_search_filter())

        ttk.Label(controls, text="دسته‌بندی:", style="Card.TLabel").pack(side="left", padx=(15, 0))
        categories = ["همه"] + sorted({p.category for p in self.products if p.category})
        category_combo = ttk.Combobox(
            controls,
            textvariable=self.category_var,
            values=categories,
            width=18,
            state="readonly",
        )
        category_combo.pack(side="left", padx=6)
        category_combo.bind("<<ComboboxSelected>>", lambda event: self.apply_search_filter())

        ttk.Button(controls, text="اعمال فیلتر", command=self.apply_search_filter).pack(side="left", padx=5)
        ttk.Button(controls, text="نمایش همه", command=self.clear_search_filter).pack(side="left", padx=5)
        self.make_icon_button(controls, "سبد خرید", self.show_cart_page, "cart", True).pack(side="right", padx=5)

        # یک ناحیه اسکرولی برای کارت محصولات می‌سازیم.
        canvas = tk.Canvas(self.content, bg=PINK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        self.products_cards_frame = ttk.Frame(canvas)

        self.products_cards_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.products_cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.populate_product_tree(self.filtered_products)

    def load_product_thumbnail(self, product: Product) -> tk.PhotoImage | None:
        """عکس کوچک هر محصول را برای کارت محصول می‌خواند و در حافظه نگه می‌دارد."""
        if product.product_id in self.product_images:
            return self.product_images[product.product_id]
        image_path = self.image_path_for_product(product)
        if product.image and image_path.exists():
            try:
                photo = tk.PhotoImage(file=str(image_path))
                self.product_images[product.product_id] = photo
                return photo
            except tk.TclError:
                return None
        return None

    def populate_product_tree(self, products: List[Product]) -> None:
        """در نسخه جدید، به جای جدول خشک، محصولات را به شکل کارت تصویری نشان می‌دهد."""
        frame = getattr(self, "products_cards_frame", None)
        if frame is None:
            return
        for widget in frame.winfo_children():
            widget.destroy()

        if not products:
            ttk.Label(frame, text="محصولی با این جستجو پیدا نشد.", style="Subtitle.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        columns_count = 3
        for index, product in enumerate(products):
            row = index // columns_count
            col = index % columns_count
            card = ttk.Frame(frame, padding=12, style="Card.TFrame")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            frame.columnconfigure(col, weight=1)

            image = self.load_product_thumbnail(product)
            if image is not None:
                image_label = ttk.Label(card, image=image, style="Card.TLabel")
                image_label.pack(pady=(0, 8))
            else:
                ttk.Label(card, text="بدون عکس", style="Card.TLabel").pack(pady=(0, 8))

            ttk.Label(card, text=product.name, style="Card.TLabel", font=("Arial", 13, "bold"), wraplength=210).pack(anchor="center")
            ttk.Label(card, text=f"{product.category} | موجودی: {product.stock}", style="Card.TLabel", font=("Arial", 10)).pack(pady=(4, 0))

            if product.discount > 0:
                price_text = f"{product.final_price():,.0f} تومان  •  {product.discount:.0f}% تخفیف"
            else:
                price_text = f"{product.final_price():,.0f} تومان"
            ttk.Label(card, text=price_text, style="Card.TLabel", foreground=PINK_DARK, font=("Arial", 11, "bold")).pack(pady=(6, 8))

            buttons = ttk.Frame(card, style="Card.TFrame")
            buttons.pack(fill="x")
            self.make_icon_button(buttons, "جزئیات", lambda p=product: self.show_product_details(p), "details").pack(side="left", expand=True, fill="x", padx=(0, 4))
            self.make_cart_button(buttons, lambda p=product: self.add_product_to_cart(p)).pack(side="left", expand=True, fill="x", padx=(4, 0), ipady=4)

    def apply_search_filter(self) -> None:
        """بر اساس متن جستجو و دسته‌بندی، محصولات را فیلتر می‌کند."""
        keyword = self.search_var.get().strip().lower()
        category = self.category_var.get().strip()
        result: List[Product] = []

        for product in self.products:
            text = f"{product.product_id} {product.name} {product.category} {product.description}".lower()
            matches_keyword = not keyword or keyword in text
            matches_category = category == "همه" or product.category == category
            if matches_keyword and matches_category:
                result.append(product)

        self.filtered_products = result
        self.populate_product_tree(result)

    def clear_search_filter(self) -> None:
        self.search_var.set("")
        self.category_var.set("همه")
        self.filtered_products = list(self.products)
        self.populate_product_tree(self.filtered_products)

    def get_selected_product(self) -> Optional[Product]:
        """در نسخه کارتی معمولاً محصول مستقیم به تابع داده می‌شود؛ این تابع برای دکمه قدیمی جزئیات است."""
        if self.selected_product_id:
            return self.app.data_manager.find_product(self.selected_product_id)
        if self.filtered_products:
            return self.filtered_products[0]
        return None

    def show_selected_product_details(self) -> None:
        product = self.get_selected_product()
        if product is None:
            messagebox.showwarning("محصولی انتخاب نشده", "اول یک محصول را انتخاب کن.")
            return
        self.show_product_details(product)

    def image_path_for_product(self, product: Product) -> Path:
        """مسیر عکس محصول را از روی اسم فایل داخل products.csv می‌سازد."""
        project_root = Path(__file__).resolve().parent.parent
        return project_root / "images" / product.image



    def product_color_options(self, product: Product) -> list[str]:
        """رنگ‌های قابل انتخاب محصول را از فیلد colors می‌خواند."""
        if not getattr(product, "colors", ""):
            return []
        return [color.strip() for color in product.colors.replace(",", "|").split("|") if color.strip()]

    def choose_product_color(self, product: Product) -> str:
        """اگر محصول چند رنگ داشته باشد، قبل از افزودن به سبد رنگ را از مشتری می‌پرسد."""
        colors = self.product_color_options(product)
        if not colors:
            return ""
        if len(colors) == 1:
            return colors[0]

        dialog = tk.Toplevel(self)
        dialog.title("انتخاب رنگ")
        dialog.geometry("330x180")
        dialog.configure(bg=PINK_BG)
        dialog.grab_set()

        selected_color = tk.StringVar(value=colors[0])
        ttk.Label(dialog, text=f"رنگ {product.name} را انتخاب کن:", style="Subtitle.TLabel").pack(pady=(18, 8))
        combo = ttk.Combobox(dialog, values=colors, textvariable=selected_color, state="readonly", width=28)
        combo.pack(pady=8)

        result = {"value": ""}

        def confirm() -> None:
            result["value"] = selected_color.get()
            dialog.destroy()

        def cancel() -> None:
            result["value"] = ""
            dialog.destroy()

        buttons = ttk.Frame(dialog)
        buttons.pack(pady=14)
        ttk.Button(buttons, text="تأیید", style="Primary.TButton", command=confirm).pack(side="left", padx=5)
        ttk.Button(buttons, text="انصراف", command=cancel).pack(side="left", padx=5)
        self.wait_window(dialog)
        return result["value"]

    def show_product_image(self, parent: ttk.Frame, product: Product) -> None:
        """عکس محصول را در صفحه جزئیات نمایش می‌دهد. اگر فایل نبود، پیام مناسب نشان می‌دهد."""
        image_frame = ttk.Frame(parent, style="Card.TFrame")
        image_frame.grid(row=0, column=2, rowspan=9, padx=(30, 0), sticky="n")

        ttk.Label(image_frame, text="تصویر محصول", style="Card.TLabel", font=("Arial", 11, "bold")).pack(pady=(0, 8))

        image_path = self.image_path_for_product(product)
        if product.image and image_path.exists():
            try:
                self.current_product_image = tk.PhotoImage(file=str(image_path))
                image_label = ttk.Label(image_frame, image=self.current_product_image, style="Card.TLabel")
                image_label.pack()
                ttk.Label(image_frame, text=product.image, style="Card.TLabel").pack(pady=(6, 0))
            except tk.TclError:
                self.current_product_image = None
                ttk.Label(image_frame, text="عکس قابل نمایش نیست.", style="Card.TLabel").pack()
        else:
            self.current_product_image = None
            ttk.Label(image_frame, text="فایل تصویر پیدا نشد.", style="Card.TLabel").pack()

    def show_product_details(self, product: Product) -> None:
        self.clear_content()

        top = ttk.Frame(self.content)
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="جزئیات محصول", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="بازگشت به محصولات", command=self.show_products_page).pack(side="right")

        card = ttk.Frame(self.content, padding=18, style="Card.TFrame")
        card.pack(fill="x", pady=8)

        details = [
            ("کد محصول", product.product_id),
            ("نام", product.name),
            ("قیمت اصلی", f"{product.price:,.0f} تومان"),
            ("تخفیف", f"{product.discount:.0f}%"),
            ("قیمت نهایی", f"{product.final_price():,.0f} تومان"),
            ("موجودی", str(product.stock)),
            ("دسته‌بندی", product.category),
            ("رنگ‌بندی", product.colors or "رنگ‌بندی ندارد"),
            ("نام فایل تصویر", product.image or "تصویری ثبت نشده"),
            ("توضیحات", product.description or "توضیحی ثبت نشده"),
        ]
        for row, (label, value) in enumerate(details):
            ttk.Label(card, text=f"{label}:", style="Card.TLabel", font=("Arial", 11, "bold")).grid(row=row, column=0, sticky="nw", padx=(0, 12), pady=4)
            ttk.Label(card, text=value, style="Card.TLabel", wraplength=600).grid(row=row, column=1, sticky="w", pady=4)

        self.show_product_image(card, product)

        actions = ttk.Frame(self.content)
        actions.pack(fill="x", pady=10)
        self.make_cart_button(actions, lambda: self.add_product_to_cart(product)).pack(side="left", padx=5, ipady=4)
        ttk.Button(actions, text="ثبت کامنت", command=lambda: self.add_comment_for_product(product)).pack(side="left", padx=5)
        ttk.Button(actions, text="به‌روزرسانی کامنت‌ها", command=lambda: self.show_product_details(product)).pack(side="left", padx=5)

        ttk.Label(self.content, text="کامنت‌ها", style="Subtitle.TLabel", font=("Arial", 13, "bold")).pack(anchor="w", pady=(15, 5))
        self.comment_box = tk.Text(self.content, height=8, wrap="word", bg=PINK_CARD, fg=TEXT_DARK, font=("Arial", 10))
        self.comment_box.pack(fill="both", expand=True)
        self.comment_box.insert("end", self.format_comments(product.product_id))
        self.comment_box.configure(state="disabled")

    def format_comments(self, product_id: str) -> str:
        comments = self.app.data_manager.comments_for_product(product_id)
        if not comments:
            return "هنوز کامنتی برای این محصول ثبت نشده است."
        lines = []
        for comment in comments:
            lines.append(f"{comment.date} - {comment.username}: {comment.comment}")
        return "\n".join(lines)

    # ---------- سبد خرید ----------

    def normalize_number_text(self, text: str) -> str:
        """عددهای فارسی/عربی را به انگلیسی تبدیل می‌کند و جداکننده‌ها را حذف می‌کند."""
        translation = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
        cleaned = text.translate(translation)
        cleaned = cleaned.replace(",", "").replace("،", "").replace(" ", "").strip()
        return cleaned

    def ask_positive_int(self, title: str, prompt: str, min_value: int = 1, max_value: int | None = None) -> int | None:
        """از کاربر عدد می‌گیرد؛ هم ارقام فارسی را قبول می‌کند هم انگلیسی."""
        while True:
            raw_value = simpledialog.askstring(title, prompt)
            if raw_value is None:
                return None
            raw_value = self.normalize_number_text(raw_value)
            try:
                value = int(raw_value)
            except ValueError:
                messagebox.showerror("عدد نامعتبر", "لطفاً فقط عدد وارد کن. هم عدد فارسی قبول است هم انگلیسی.")
                continue
            if value < min_value:
                messagebox.showerror("عدد نامعتبر", f"عدد باید حداقل {min_value} باشد.")
                continue
            if max_value is not None and value > max_value:
                messagebox.showerror("عدد نامعتبر", f"عدد نباید بیشتر از {max_value} باشد.")
                continue
            return value

    def increase_balance(self) -> None:
        """مشتری می‌تواند موجودی حساب خودش را افزایش دهد."""
        amount = self.ask_positive_int(
            "افزایش موجودی",
            "چه مبلغی به موجودی اضافه شود؟\nمثلاً: 500000 یا ۵۰۰۰۰۰",
            min_value=1000,
        )
        if amount is None:
            return
        try:
            self.refresh_user()
            self.user.balance += amount
            self.app.data_manager.update_user(self.user)
            self.refresh_user()
        except Exception as error:
            messagebox.showerror("خطای افزایش موجودی", f"موجودی به‌روزرسانی نشد.\n\n{error}")
            return
        messagebox.showinfo("افزایش موجودی", f"{amount:,.0f} تومان به موجودی اضافه شد.")

    def add_selected_to_cart(self) -> None:
        product = self.get_selected_product()
        if product is None:
            messagebox.showwarning("محصولی انتخاب نشده", "اول یک محصول را انتخاب کن.")
            return
        self.add_product_to_cart(product)

    def add_product_to_cart(self, product: Product) -> None:
        if product.stock <= 0:
            messagebox.showerror("ناموجود", "این محصول موجود نیست.")
            return

        selected_color = self.choose_product_color(product)
        if self.product_color_options(product) and not selected_color:
            return

        quantity = self.ask_positive_int(
            "تعداد",
            f"چند عدد از '{product.name}' می‌خواهی؟\nحداکثر موجودی: {product.stock}\nمثلاً: 2 یا ۲",
            min_value=1,
            max_value=product.stock,
        )
        if quantity is None:
            return

        existing = self.find_cart_item(product.product_id, selected_color)
        current_quantity = existing.quantity if existing else 0
        if current_quantity + quantity > product.stock:
            messagebox.showerror(
                "موجودی کافی نیست",
                f"فقط {product.stock} عدد موجود است. تو همین الان {current_quantity} عدد از این مدل در سبد داری.",
            )
            return

        if existing:
            existing.quantity += quantity
        else:
            self.cart.append(CartItem(product=product, quantity=quantity, selected_color=selected_color))

        color_text = f" با رنگ/مدل {selected_color}" if selected_color else ""
        messagebox.showinfo("سبد خرید", f"{quantity} عدد{color_text} به سبد خرید اضافه شد.")

    def find_cart_item(self, product_id: str, selected_color: str = "") -> Optional[CartItem]:
        for item in self.cart:
            if item.product.product_id == product_id and item.selected_color == selected_color:
                return item
        return None

    def show_cart_page(self) -> None:
        self.clear_content()
        self.refresh_user()

        ttk.Label(self.content, text="سبد خرید", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        columns = ("id", "name", "color", "quantity", "unit", "total")
        self.cart_tree = ttk.Treeview(self.content, columns=columns, show="headings", height=12)
        headings = {
            "id": "کد محصول",
            "name": "نام محصول",
            "color": "رنگ/مدل",
            "quantity": "تعداد",
            "unit": "قیمت واحد نهایی",
            "total": "قیمت کل",
        }
        widths = {"id": 90, "name": 220, "color": 120, "quantity": 80, "unit": 140, "total": 130}
        for col in columns:
            self.cart_tree.heading(col, text=headings[col])
            self.cart_tree.column(col, width=widths[col], anchor="center")
        self.cart_tree.pack(fill="both", expand=True)

        self.populate_cart_tree()

        total_label = ttk.Label(self.content, text=f"جمع سبد خرید: {self.cart_total():,.0f} تومان", style="Subtitle.TLabel", font=("Arial", 13, "bold"))
        total_label.pack(anchor="e", pady=10)

        actions = ttk.Frame(self.content)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="حذف آیتم انتخاب‌شده", command=self.remove_selected_cart_item).pack(side="left", padx=5)
        ttk.Button(actions, text="خالی کردن سبد", command=self.clear_cart).pack(side="left", padx=5)
        ttk.Button(actions, text="پرداخت نهایی", style="Primary.TButton", command=self.checkout).pack(side="left", padx=5)
        ttk.Button(actions, text="بازگشت به محصولات", command=self.show_products_page).pack(side="left", padx=5)

    def populate_cart_tree(self) -> None:
        if self.cart_tree is None:
            return
        self.cart_tree.delete(*self.cart_tree.get_children())
        for index, item in enumerate(self.cart):
            product = item.product
            self.cart_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    product.product_id,
                    product.name,
                    item.selected_color or "-",
                    item.quantity,
                    f"{product.final_price():,.0f}",
                    f"{item.item_total():,.0f}",
                ),
            )

    def cart_total(self) -> float:
        return sum(item.item_total() for item in self.cart)

    def remove_selected_cart_item(self) -> None:
        if self.cart_tree is None:
            return
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("آیتمی انتخاب نشده", "اول یک آیتم از سبد خرید انتخاب کن.")
            return
        selected_index = int(selected[0])
        if 0 <= selected_index < len(self.cart):
            self.cart.pop(selected_index)
        self.show_cart_page()

    def clear_cart(self) -> None:
        if not self.cart:
            messagebox.showinfo("سبد خرید", "سبد خرید از قبل خالی است.")
            return
        if messagebox.askyesno("خالی کردن سبد", "مطمئنی می‌خواهی سبد خرید را خالی کنی؟"):
            self.cart.clear()
            self.show_cart_page()

    def checkout(self) -> None:
        if not self.cart:
            messagebox.showerror("خطای پرداخت", "سبد خرید خالی است.")
            return

        products = self.app.data_manager.load_products()
        product_map = {product.product_id: product for product in products}
        self.refresh_user()

        for item in self.cart:
            fresh_product = product_map.get(item.product.product_id)
            if fresh_product is None:
                messagebox.showerror("خطای پرداخت", f"محصول {item.product.product_id} دیگر وجود ندارد.")
                return
            if item.quantity <= 0:
                messagebox.showerror("خطای پرداخت", "تعداد محصول در سبد خرید معتبر نیست.")
                return
            if not fresh_product.is_available(item.quantity):
                messagebox.showerror(
                    "خطای پرداخت",
                    f"موجودی محصول {fresh_product.name} کافی نیست. موجودی فعلی: {fresh_product.stock}",
                )
                return

        total = 0.0
        for item in self.cart:
            fresh_product = product_map[item.product.product_id]
            total += fresh_product.final_price() * item.quantity

        if self.user.balance < total:
            messagebox.showerror(
                "خطای پرداخت",
                f"موجودی حساب کافی نیست.\nجمع سبد: {total:,.0f}\nموجودی شما: {self.user.balance:,.0f}",
            )
            return

        if not messagebox.askyesno("تأیید پرداخت", f"مبلغ {total:,.0f} تومان پرداخت و خرید کامل شود؟"):
            return

        try:
            for item in self.cart:
                fresh_product = product_map[item.product.product_id]
                fresh_product.reduce_stock(item.quantity)
                item_total = fresh_product.final_price() * item.quantity
                order = Order.today(
                    username=self.user.username,
                    product_id=fresh_product.product_id,
                    quantity=item.quantity,
                    total_price=item_total,
                    color=item.selected_color,
                )
                self.app.data_manager.add_order(order)

            self.user.balance -= total
            self.app.data_manager.save_products(list(product_map.values()))
            self.app.data_manager.update_user(self.user)
            self.cart.clear()
            self.refresh_user()
        except Exception as error:
            messagebox.showerror("خطای پرداخت", f"خرید کامل نشد.\n\n{error}")
            return

        messagebox.showinfo("پرداخت موفق", "خرید با موفقیت انجام شد و سفارش در orders.csv ذخیره شد.")
        self.show_orders_page()

    # ---------- سفارش‌های من ----------

    def show_orders_page(self) -> None:
        self.clear_content()
        self.refresh_user()

        ttk.Label(self.content, text="سفارش‌های من", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        columns = ("date", "product_id", "product_name", "color", "quantity", "total")
        self.orders_tree = ttk.Treeview(self.content, columns=columns, show="headings", height=16)
        headings = {
            "date": "تاریخ",
            "product_id": "کد محصول",
            "product_name": "نام محصول",
            "color": "رنگ/مدل",
            "quantity": "تعداد",
            "total": "قیمت کل",
        }
        widths = {"date": 120, "product_id": 100, "product_name": 230, "color": 120, "quantity": 80, "total": 130}
        for col in columns:
            self.orders_tree.heading(col, text=headings[col])
            self.orders_tree.column(col, width=widths[col], anchor="center")
        self.orders_tree.pack(fill="both", expand=True)

        products = {product.product_id: product for product in self.app.data_manager.load_products()}
        orders = [order for order in self.app.data_manager.load_orders() if order.username == self.user.username]

        for index, order in enumerate(orders):
            product = products.get(order.product_id)
            product_name = product.name if product else "محصول نامشخص"
            self.orders_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(order.date, order.product_id, product_name, order.color or "-", order.quantity, f"{order.total_price:,.0f}"),
            )

        total_spent = sum(order.total_price for order in orders)
        ttk.Label(
            self.content,
            text=f"تعداد سفارش‌ها: {len(orders)}     مجموع خرید: {total_spent:,.0f} تومان",
            style="Subtitle.TLabel",
            font=("Arial", 13, "bold"),
        ).pack(anchor="e", pady=12)

        ttk.Button(self.content, text="بازگشت به محصولات", command=self.show_products_page).pack(anchor="w")

    # ---------- کامنت‌ها ----------

    def add_comment_for_product(self, product: Product) -> None:
        comment_text = simpledialog.askstring("ثبت کامنت", f"نظر خودت را برای {product.name} بنویس:")
        if comment_text is None:
            return
        comment_text = comment_text.strip()
        if not comment_text:
            messagebox.showerror("خطای کامنت", "متن کامنت نمی‌تواند خالی باشد.")
            return

        try:
            comment = Comment.today(self.user.username, product.product_id, comment_text)
            self.app.data_manager.add_comment(comment)
        except Exception as error:
            messagebox.showerror("خطای کامنت", f"کامنت ذخیره نشد.\n\n{error}")
            return

        messagebox.showinfo("کامنت", "کامنت شما در comments.csv ذخیره شد.")
        self.show_product_details(product)
