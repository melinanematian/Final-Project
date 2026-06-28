"""
main.py
=======

فایل اصلی اجرای پروژه فروشگاه اینترنتی / لوازم‌التحریری pink shop است.
این فایل نقش «درِ ورودی برنامه» را دارد؛ یعنی برنامه از اینجا شروع می‌شود.

مسئولیت‌های اصلی این فایل:
1. ساخت پنجره اصلی برنامه با Tkinter
2. تنظیم ظاهر صورتی و هماهنگ برنامه
3. ساخت صفحه ورود
4. ساخت صفحه ثبت‌نام مشتری جدید
5. بررسی نام کاربری و رمز عبور
6. تشخیص نقش کاربر: customer یا admin
7. باز کردن پنل مشتری یا پنل ادمین بر اساس نقش کاربر
8. اتصال کل برنامه به CSVManager برای خواندن و نوشتن فایل‌های CSV
9. واضح کردن خط چشمک‌زن تایپ داخل کادرهای username و password

نحوه اجرا:
    python main.py

نکته مهم:
این فایل باید از داخل پوشه اصلی پروژه اجرا شود؛ همان پوشه‌ای که کنار main.py فایل‌های
models.py ،data_manager.py و پوشه panels قرار دارند.
"""

# این خط باعث می‌شود Type Hintهایی مثل User | None در نسخه‌های مختلف پایتون بهتر کار کنند.
from __future__ import annotations

# tkinter کتابخانه اصلی ساخت پنجره و رابط گرافیکی در پایتون است.
import tkinter as tk

# ttk نسخه مرتب‌تر و مدرن‌تر بعضی ویجت‌های tkinter است.
# messagebox هم برای نشان دادن پیام خطا، هشدار و پیام موفقیت استفاده می‌شود.
from tkinter import ttk, messagebox

# CSVManager کلاس مدیریت فایل‌های CSV است و در data_manager.py نوشته شده.
# این کلاس کارهایی مثل خواندن کاربران، محصولات، سفارش‌ها و ذخیره تغییرات را انجام می‌دهد.
from data_manager import CSVManager

# User کلاس مدل کاربر است و در models.py نوشته شده.
# هر کاربر username، password، balance و role دارد.
from models import User

# پنل مشتری از فایل جداگانه panels/customer_panel.py وارد می‌شود.
# این همان بخشی است که امکانات مشتری مثل نمایش محصول، سبد خرید و checkout را دارد.
from panels.customer_panel import CustomerPanel

# پنل ادمین از فایل جداگانه panels/admin_panel.py وارد می‌شود.
# این بخش امکانات ادمین مثل اضافه کردن محصول، تغییر قیمت، افزایش موجودی و حذف محصول را دارد.
from panels.admin_panel import AdminPanel


# -----------------------------
# رنگ‌های ثابت پروژه
# -----------------------------
# برای اینکه ظاهر برنامه هماهنگ بماند، رنگ‌ها را یک بار اینجا تعریف می‌کنیم.
# بعد در کل main.py از همین اسم‌ها استفاده می‌کنیم.
PINK_BG = "#FFF0F6"       # پس‌زمینه خیلی روشن صورتی
PINK_CARD = "#FFFFFF"     # رنگ کارت‌ها؛ سفید
PINK_LIGHT = "#FFD6E7"    # صورتی روشن برای هدرها و دکمه‌ها
PINK_MAIN = "#FF69A6"     # صورتی اصلی برای دکمه‌های مهم
PINK_DARK = "#C2185B"     # صورتی تیره برای عنوان‌ها
PINK_ACCENT = "#F8BBD0"   # صورتی کمکی برای حالت hover و جدول
TEXT_DARK = "#3A2430"     # رنگ متن اصلی


class OnlineStoreApp(tk.Tk):
    """
    کلاس اصلی برنامه.

    این کلاس از tk.Tk ارث‌بری می‌کند؛ یعنی خودش یک پنجره کامل Tkinter است.
    وقتی برنامه اجرا می‌شود، یک object از همین کلاس ساخته می‌شود.
    """

    def __init__(self) -> None:
        """سازنده برنامه؛ موقع شروع برنامه اجرا می‌شود."""

        # super().__init__ پنجره اصلی Tkinter را واقعاً می‌سازد.
        # بدون این خط، کلاس ما فقط یک کلاس معمولی می‌ماند و پنجره‌ای ساخته نمی‌شود.
        super().__init__()

        # عنوان پنجره برنامه. این عنوان در نوار بالای پنجره نمایش داده می‌شود.
        self.title("pink shop")

        # اندازه اولیه پنجره: عرض 1000 و ارتفاع 650 پیکسل.
        self.geometry("1000x650")

        # حداقل اندازه پنجره. کاربر نمی‌تواند پنجره را از این کوچکتر کند.
        self.minsize(900, 600)

        # این شیء مسئول کار با فایل‌های CSV است.
        # data_dir="data" یعنی فایل‌های users.csv، products.csv و ... داخل پوشه data هستند.
        self.data_manager = CSVManager(data_dir="data")

        # current_user یعنی کاربری که الان وارد برنامه شده.
        # اول برنامه هنوز هیچ‌کس وارد نشده، پس مقدارش None است.
        self.current_user: User | None = None

        # رنگ پس‌زمینه کل پنجره را تنظیم می‌کنیم.
        self.configure(bg=PINK_BG)

        # ظاهر کلی ttk را تنظیم می‌کنیم؛ مثل رنگ دکمه‌ها، لیبل‌ها و جدول‌ها.
        self._setup_style()

        # container یک Frame اصلی است که صفحه‌های مختلف داخل آن قرار می‌گیرند.
        # مثلاً اول LoginPage داخلش می‌آید، بعد اگر کاربر وارد شد CustomerPanel یا AdminPanel جایگزین می‌شود.
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # هنگام شروع برنامه، اولین صفحه‌ای که باید دیده شود صفحه ورود است.
        self.show_login_page()

    # ------------------------------------------------------------------
    # بخش تنظیم ظاهر برنامه
    # ------------------------------------------------------------------
    def _setup_style(self) -> None:
        """تنظیم استایل صورتی برای ویجت‌های ttk."""

        # ttk.Style شیء مخصوص تنظیم ظاهر ویجت‌های ttk است.
        style = ttk.Style()

        # theme_use("clam") معمولاً روی سیستم‌های مختلف ظاهر قابل‌قبول‌تری می‌دهد.
        # try/except گذاشتیم چون ممکن است روی بعضی سیستم‌ها این theme موجود نباشد.
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # استایل Frame معمولی.
        style.configure("TFrame", background=PINK_BG)

        # استایل کارت سفید وسط صفحه ورود و ثبت‌نام.
        style.configure("Card.TFrame", background=PINK_CARD, relief="flat")

        # استایل هدر پنل‌ها.
        style.configure("Header.TFrame", background=PINK_LIGHT)

        # استایل متن‌های معمولی.
        style.configure("TLabel", background=PINK_BG, foreground=TEXT_DARK, font=("Arial", 11))

        # استایل عنوان اصلی، مثل pink shop.
        style.configure("Title.TLabel", background=PINK_BG, foreground=PINK_DARK, font=("Arial", 22, "bold"))

        # استایل زیرعنوان.
        style.configure("Subtitle.TLabel", background=PINK_BG, foreground=TEXT_DARK, font=("Arial", 12))

        # استایل نوشته‌هایی که روی کارت سفید هستند.
        style.configure("Card.TLabel", background=PINK_CARD, foreground=TEXT_DARK, font=("Arial", 11))

        # استایل نوشته‌های مهم روی هدر.
        style.configure("Pink.TLabel", background=PINK_LIGHT, foreground=PINK_DARK, font=("Arial", 13, "bold"))

        # استایل دکمه‌های معمولی.
        style.configure(
            "TButton",
            font=("Arial", 11),
            padding=8,
            background=PINK_LIGHT,
            foreground=TEXT_DARK,
        )

        # وقتی ماوس روی دکمه معمولی می‌رود، رنگ آن تغییر کند.
        style.map("TButton", background=[("active", PINK_ACCENT)], foreground=[("active", TEXT_DARK)])

        # استایل دکمه اصلی، مثل دکمه ورود و ثبت‌نام.
        style.configure(
            "Primary.TButton",
            font=("Arial", 11, "bold"),
            padding=8,
            background=PINK_MAIN,
            foreground="white",
        )

        # حالت فعال دکمه اصلی.
        style.map("Primary.TButton", background=[("active", PINK_DARK)], foreground=[("active", "white")])

        # استایل جدول‌ها؛ مثلاً جدول سفارش‌ها یا محصولات اگر با Treeview نمایش داده شوند.
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 10),
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=TEXT_DARK,
        )

        # استایل سرستون‌های جدول.
        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background=PINK_ACCENT,
            foreground=TEXT_DARK,
        )

    # ------------------------------------------------------------------
    # بخش جابه‌جایی بین صفحه‌ها
    # ------------------------------------------------------------------
    def clear_container(self) -> None:
        """همه ویجت‌های داخل container را پاک می‌کند."""

        # winfo_children همه اجزای داخل container را برمی‌گرداند.
        # destroy هرکدام را از صفحه حذف می‌کند.
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_page(self) -> None:
        """نمایش صفحه ورود."""

        # وقتی به صفحه ورود برمی‌گردیم، یعنی کاربر فعلی دیگر وارد حساب نیست.
        self.current_user = None

        # صفحه قبلی را پاک می‌کنیم.
        self.clear_container()

        # یک صفحه ورود جدید می‌سازیم و داخل container قرار می‌دهیم.
        LoginPage(self.container, self).pack(fill="both", expand=True)

    def show_register_page(self) -> None:
        """نمایش صفحه ساخت حساب مشتری."""

        # صفحه ثبت‌نام هم قبل از login است، پس current_user باید None باشد.
        self.current_user = None

        # صفحه فعلی را پاک می‌کنیم.
        self.clear_container()

        # صفحه ثبت‌نام مشتری را نمایش می‌دهیم.
        CustomerRegisterPage(self.container, self).pack(fill="both", expand=True)

    def show_customer_panel(self, user: User) -> None:
        """بعد از ورود موفق مشتری، پنل مشتری را نمایش می‌دهد."""

        # کاربر واردشده را ذخیره می‌کنیم تا برنامه بداند الان چه کسی داخل حساب است.
        self.current_user = user

        # صفحه ورود را پاک می‌کنیم.
        self.clear_container()

        # پنل مشتری را می‌سازیم و user فعلی را به آن می‌دهیم.
        CustomerPanel(self.container, self, user).pack(fill="both", expand=True)

    def show_admin_panel(self, user: User) -> None:
        """بعد از ورود موفق ادمین، پنل ادمین را نمایش می‌دهد."""

        # ادمین واردشده را به عنوان کاربر فعلی ذخیره می‌کنیم.
        self.current_user = user

        # صفحه قبلی را پاک می‌کنیم.
        self.clear_container()

        # پنل ادمین را نمایش می‌دهیم.
        AdminPanel(self.container, self, user).pack(fill="both", expand=True)

    def logout(self) -> None:
        """خروج از حساب و برگشت به صفحه ورود."""

        # برای logout کافی است صفحه ورود را دوباره نشان بدهیم.
        self.show_login_page()


class LoginPage(ttk.Frame):
    """
    صفحه ورود برنامه.

    این صفحه نام کاربری و رمز عبور را می‌گیرد، سپس با data_manager بررسی می‌کند.
    اگر role کاربر customer باشد، پنل مشتری باز می‌شود.
    اگر role کاربر admin باشد، پنل ادمین باز می‌شود.
    """

    def __init__(self, parent: ttk.Frame, app: OnlineStoreApp) -> None:
        """ساخت صفحه ورود."""

        # این صفحه خودش یک Frame است، پس باید سازنده Frame اجرا شود.
        super().__init__(parent)

        # app همان برنامه اصلی است. با ذخیره آن می‌توانیم از این صفحه به data_manager و صفحه‌های دیگر برسیم.
        self.app = app

        # StringVar متغیر مخصوص Tkinter است که به Entry وصل می‌شود.
        # وقتی کاربر در کادر تایپ می‌کند، مقدار این متغیر هم عوض می‌شود.
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # بعد از آماده شدن متغیرها، ظاهر صفحه را می‌سازیم.
        self._build_ui()

    def _build_ui(self) -> None:
        """ساخت اجزای صفحه ورود؛ مثل عنوان، کادر username، کادر password و دکمه‌ها."""

        # outer قاب اصلی این صفحه است.
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)

        # عنوان بالای صفحه. طبق خواسته کاربر، نام فروشگاه انگلیسی است.
        top_title = ttk.Label(outer, text="pink shop", style="Title.TLabel")
        top_title.pack(pady=(45, 6))

        # زیرعنوان کوتاه انگلیسی.
        subtitle = ttk.Label(
            outer,
            text="online stationery store",
            style="Subtitle.TLabel",
        )
        subtitle.pack(pady=(0, 25))

        # card همان کارت سفید وسط صفحه است که فرم ورود داخلش قرار دارد.
        card = ttk.Frame(outer, style="Card.TFrame", padding=35)
        card.place(relx=0.5, rely=0.55, anchor="center", width=460, height=420)

        # عنوان فرم ورود.
        title = ttk.Label(
            card,
            text="ورود",
            style="Card.TLabel",
            font=("Arial", 24, "bold"),
            foreground=PINK_DARK,
        )
        title.pack(pady=(5, 8))

        # توضیح کوتاه زیر عنوان.
        subtitle = ttk.Label(
            card,
            text="اطلاعات حساب خود را وارد کنید",
            style="Card.TLabel",
            font=("Arial", 12),
        )
        subtitle.pack(pady=(0, 25))

        # برچسب نام کاربری.
        username_label = ttk.Label(card, text="نام کاربری", style="Card.TLabel")
        username_label.pack(anchor="w", pady=(0, 5))

        # برای کادر نام کاربری از tk.Entry استفاده شده، نه ttk.Entry.
        # دلیلش این است که tk.Entry اجازه می‌دهد رنگ و ضخامت خط چشمک‌زن تایپ را دقیق‌تر تنظیم کنیم.
        username_entry = tk.Entry(
            card,
            textvariable=self.username_var,
            font=("Arial", 12),
            bg="white",
            fg=TEXT_DARK,
            insertbackground="#FF1493",   # رنگ خط چشمک‌زن تایپ
            insertwidth=4,                 # ضخامت خط چشمک‌زن تایپ
            insertontime=500,              # مدت روشن بودن چشمک‌زن
            insertofftime=400,             # مدت خاموش بودن چشمک‌زن
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PINK_LIGHT,
            highlightcolor=PINK_DARK,
            cursor="xterm",
        )
        username_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # برچسب رمز عبور.
        password_label = ttk.Label(card, text="رمز عبور", style="Card.TLabel")
        password_label.pack(anchor="w", pady=(0, 5))

        # کادر رمز عبور هم از tk.Entry ساخته شده تا خط چشمک‌زن واضح باشد.
        # show="*" باعث می‌شود رمز هنگام تایپ به شکل ستاره نمایش داده شود.
        password_entry = tk.Entry(
            card,
            textvariable=self.password_var,
            show="*",
            font=("Arial", 12),
            bg="white",
            fg=TEXT_DARK,
            insertbackground="#FF1493",   # رنگ خط چشمک‌زن تایپ
            insertwidth=4,
            insertontime=500,
            insertofftime=400,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PINK_LIGHT,
            highlightcolor=PINK_DARK,
            cursor="xterm",
        )
        password_entry.pack(fill="x", pady=(0, 20), ipady=5)

        # دکمه ورود. با کلیک روی آن تابع handle_login اجرا می‌شود.
        login_button = ttk.Button(card, text="ورود", style="Primary.TButton", command=self.handle_login)
        login_button.pack(fill="x", pady=(0, 10))

        # دکمه ساخت حساب مشتری.
        # این دکمه فقط حساب customer می‌سازد، نه admin؛ پس امنیت حساب ادمین حفظ می‌شود.
        register_button = ttk.Button(
            card,
            text="ساخت حساب مشتری",
            command=self.app.show_register_page,
        )
        register_button.pack(fill="x", pady=(0, 10))

        # دیگر هیچ نام کاربری یا رمز پیشنهادی در صفحه ورود نمایش داده نمی‌شود.
        # این کار انجام شد تا کاربران عادی رمز ادمین را نبینند.

        # این تابع کوچک باعث می‌شود کمی بعد از باز شدن صفحه، کادر username فعال شود.
        # focus_force روی مک و Spyder بهتر از focus معمولی عمل می‌کند.
        def focus_username() -> None:
            username_entry.focus_force()
            username_entry.icursor(tk.END)

        # after یعنی 150 میلی‌ثانیه بعد از ساخت صفحه، focus_username اجرا شود.
        self.after(150, focus_username)

        # اگر کاربر داخل username یا password کلید Enter بزند، ورود انجام شود.
        username_entry.bind("<Return>", lambda event: self.handle_login())
        password_entry.bind("<Return>", lambda event: self.handle_login())

    def handle_login(self) -> None:
        """بررسی فرم ورود و انتقال کاربر به پنل مناسب."""

        # متن واردشده در username را می‌گیریم و فاصله‌های اول و آخرش را حذف می‌کنیم.
        username = self.username_var.get().strip()

        # متن واردشده در password را می‌گیریم.
        password = self.password_var.get().strip()

        # اگر نام کاربری خالی باشد، پیام خطا می‌دهیم و ادامه نمی‌دهیم.
        if not username:
            messagebox.showerror("خطای ورود", "نام کاربری را وارد کنید.")
            return

        # اگر رمز عبور خالی باشد، پیام خطا می‌دهیم.
        if not password:
            messagebox.showerror("خطای ورود", "رمز عبور را وارد کنید.")
            return

        # authenticate در data_manager کاربر را از users.csv پیدا می‌کند و رمز را چک می‌کند.
        try:
            user = self.app.data_manager.authenticate(username, password)
        except Exception as error:
            # اگر فایل users.csv مشکلی داشته باشد، این پیام نشان داده می‌شود.
            messagebox.showerror("خطای داده", f"اطلاعات کاربران خوانده نشد.\n\n{error}")
            return

        # اگر user برابر None باشد، یعنی نام کاربری یا رمز اشتباه است.
        if user is None:
            messagebox.showerror("خطای ورود", "نام کاربری یا رمز عبور اشتباه است.")
            return

        # اگر نقش کاربر customer باشد، پنل مشتری باز می‌شود.
        if user.is_customer():
            self.app.show_customer_panel(user)

        # اگر نقش کاربر admin باشد، پنل ادمین باز می‌شود.
        elif user.is_admin():
            self.app.show_admin_panel(user)

        # اگر role چیز دیگری باشد، یعنی داده داخل users.csv معتبر نیست.
        else:
            messagebox.showerror("خطای نقش کاربر", f"نقش کاربر نامشخص است: {user.role}")


class CustomerRegisterPage(ttk.Frame):
    """
    صفحه ساخت حساب مشتری جدید.

    این صفحه برای این اضافه شد که هر مشتری بتواند برای خودش حساب بسازد.
    این صفحه فقط role=customer می‌سازد؛ یعنی هیچ کاربری از اینجا نمی‌تواند خودش را admin کند.
    """

    def __init__(self, parent: ttk.Frame, app: OnlineStoreApp) -> None:
        """ساخت صفحه ثبت‌نام مشتری."""

        # سازنده Frame اجرا می‌شود.
        super().__init__(parent)

        # app را ذخیره می‌کنیم تا بتوانیم به data_manager و صفحه ورود دسترسی داشته باشیم.
        self.app = app

        # متغیرهای فرم ثبت‌نام.
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # موجودی اولیه اختیاری است؛ پیش‌فرض آن را 0 گذاشتیم.
        self.balance_var = tk.StringVar(value="0")

        # ساخت ظاهر صفحه.
        self._build_ui()

    def normalize_number_text(self, text: str) -> str:
        """
        تبدیل عدد فارسی/عربی به عدد انگلیسی.

        کاربرد:
        اگر کاربر برای موجودی اولیه بنویسد ۱۲۳۴، برنامه بتواند آن را مثل 1234 بخواند.
        همچنین کاما، ویرگول فارسی و فاصله حذف می‌شود.
        """

        translation = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
        return text.translate(translation).replace(",", "").replace("،", "").replace(" ", "").strip()

    def _build_ui(self) -> None:
        """ساخت اجزای صفحه ثبت‌نام."""

        # قاب اصلی صفحه.
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)

        # عنوان فروشگاه و عنوان صفحه.
        ttk.Label(outer, text="pink shop", style="Title.TLabel").pack(pady=(45, 6))
        ttk.Label(outer, text="ساخت حساب مشتری", style="Subtitle.TLabel").pack(pady=(0, 25))

        # کارت سفید وسط صفحه.
        card = ttk.Frame(outer, style="Card.TFrame", padding=35)
        card.place(relx=0.5, rely=0.55, anchor="center", width=480, height=430)

        # عنوان فرم ثبت‌نام.
        ttk.Label(
            card,
            text="حساب جدید بساز",
            style="Card.TLabel",
            font=("Arial", 23, "bold"),
            foreground=PINK_DARK,
        ).pack(pady=(5, 18))

        # برچسب و کادر نام کاربری.
        ttk.Label(card, text="نام کاربری", style="Card.TLabel").pack(anchor="w", pady=(0, 5))
        username_entry = tk.Entry(
            card,
            textvariable=self.username_var,
            font=("Arial", 12),
            bg="white",
            fg=TEXT_DARK,
            insertbackground="#FF1493",
            insertwidth=4,
            insertontime=500,
            insertofftime=400,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PINK_LIGHT,
            highlightcolor=PINK_DARK,
            cursor="xterm",
        )
        username_entry.pack(fill="x", pady=(0, 13), ipady=5)

        # برچسب و کادر رمز عبور.
        ttk.Label(card, text="رمز عبور", style="Card.TLabel").pack(anchor="w", pady=(0, 5))
        password_entry = tk.Entry(
            card,
            textvariable=self.password_var,
            show="*",
            font=("Arial", 12),
            bg="white",
            fg=TEXT_DARK,
            insertbackground="#FF1493",
            insertwidth=4,
            insertontime=500,
            insertofftime=400,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PINK_LIGHT,
            highlightcolor=PINK_DARK,
            cursor="xterm",
        )
        password_entry.pack(fill="x", pady=(0, 13), ipady=5)

        # برچسب و کادر موجودی اولیه.
        # موجودی اولیه اختیاری است و اگر خالی بماند صفر در نظر گرفته می‌شود.
        ttk.Label(card, text="موجودی اولیه اختیاری", style="Card.TLabel").pack(anchor="w", pady=(0, 5))
        balance_entry = tk.Entry(
            card,
            textvariable=self.balance_var,
            font=("Arial", 12),
            bg="white",
            fg=TEXT_DARK,
            insertbackground="#FF1493",
            insertwidth=4,
            insertontime=500,
            insertofftime=400,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=PINK_LIGHT,
            highlightcolor=PINK_DARK,
            cursor="xterm",
        )
        balance_entry.pack(fill="x", pady=(0, 18), ipady=5)

        # دکمه ثبت‌نام.
        ttk.Button(card, text="ثبت‌نام", style="Primary.TButton", command=self.handle_register).pack(fill="x", pady=(0, 10))

        # دکمه برگشت به صفحه ورود.
        ttk.Button(card, text="بازگشت به ورود", command=self.app.show_login_page).pack(fill="x")

        # با زدن Enter در هرکدام از کادرها، ثبت‌نام انجام شود.
        username_entry.bind("<Return>", lambda event: self.handle_register())
        password_entry.bind("<Return>", lambda event: self.handle_register())
        balance_entry.bind("<Return>", lambda event: self.handle_register())

        # هنگام باز شدن صفحه، نشانگر تایپ داخل username فعال شود.
        self.after(150, lambda: username_entry.focus_force())

    def handle_register(self) -> None:
        """اعتبارسنجی فرم ثبت‌نام و ساخت حساب customer."""

        # گرفتن مقدارهای فرم.
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        raw_balance = self.balance_var.get().strip() or "0"

        # نام کاربری نباید خالی باشد.
        if not username:
            messagebox.showerror("ثبت‌نام", "نام کاربری را وارد کن.")
            return

        # رمز عبور نباید خالی باشد.
        if not password:
            messagebox.showerror("ثبت‌نام", "رمز عبور را وارد کن.")
            return

        # اگر این نام کاربری قبلاً در users.csv وجود داشته باشد، ثبت‌نام متوقف می‌شود.
        if self.app.data_manager.find_user(username) is not None:
            messagebox.showerror("ثبت‌نام", "این نام کاربری قبلاً وجود دارد.")
            return

        # موجودی اولیه ممکن است فارسی نوشته شده باشد، پس اول normalize می‌شود.
        try:
            balance = float(self.normalize_number_text(raw_balance))
        except ValueError:
            messagebox.showerror("ثبت‌نام", "موجودی اولیه باید عدد باشد.")
            return

        # موجودی منفی منطقی نیست.
        if balance < 0:
            messagebox.showerror("ثبت‌نام", "موجودی اولیه نمی‌تواند منفی باشد.")
            return

        # ساخت object از کلاس User.
        # role را عمداً customer می‌گذاریم تا کسی از فرم ثبت‌نام نتواند admin بسازد.
        user = User(username=username, password=password, balance=balance, role="customer")

        # ذخیره کاربر در users.csv.
        try:
            self.app.data_manager.update_user(user)
        except Exception as error:
            messagebox.showerror("ثبت‌نام", f"حساب ساخته نشد.\n\n{error}")
            return

        # پیام موفقیت و برگشت به صفحه ورود.
        messagebox.showinfo("ثبت‌نام", "حساب مشتری ساخته شد. حالا وارد شو.")
        self.app.show_login_page()


# این شرط یعنی اگر فایل main.py مستقیم اجرا شد، برنامه شروع شود.
# اگر این فایل فقط import شود، برنامه خودکار اجرا نمی‌شود.
if __name__ == "__main__":
    # ساخت object اصلی برنامه.
    app = OnlineStoreApp()

    # mainloop حلقه اصلی Tkinter است.
    # این خط باعث می‌شود پنجره باز بماند و کلیک‌ها، تایپ‌ها و دکمه‌ها کار کنند.
    app.mainloop()
