
from pathlib import Path

import traceback

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL = True
except Exception:
    HAS_RTL = False

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.graphics import (
    Color, RoundedRectangle, Line,
    Ellipse, Rectangle
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView

# ==================================================
# واژگان قرآن نهم (درس ۱ و ۲)
# برای اضافه کردن واژه‌ی جدید، یک خط به لیست زیر اضافه کن:
# (شماره درس, "واژه", "معنی")
# ==================================================

WORDS = [
    # ----- درس ۱: سوره شوری و زخرف -----
    (1, "شَرَعَ", "تشریع کرد، مقرّر کرد"),
    (1, "وَصّی", "سفارش کرد، وصیت کرد"),
    (1, "أَوْحَیْنا", "وحی کردیم"),
    (1, "وَصَّیْنا", "سفارش کردیم، وصیت کردیم"),
    (1, "لا تَتَفَرَّقوا", "متفرّق نشوید، پراکنده نشوید"),
    (1, "سَأَلْتَ", "پرسیدی از"),
    (1, "هُنَّ", "آنها، ایشان"),
    (1, "مَهْد", "محل آرامش"),
    (1, "لَعَلَّ", "تا، شاید"),
    (1, "تَهْتَدُونَ", "هدایت شوید، هدایت می‌شوید"),
    (1, "قَدَر", "اندازه"),
    (1, "بَلْدَة", "سرزمین"),
    (1, "مَیْت", "مرده"),

    # ----- درس ۲: سوره دخان و جاثیه -----
    (2, "مُبارَك / مُبارَكَة", "مبارک، با برکت"),
    (2, "مُنْذِر", "هشداردهنده، بیم‌دهنده"),
    (2, "عِنْد", "نزد"),
    (2, "مُرْسِل", "ارسال‌کننده، فرستنده"),
    (2, "بَیْن", "میان، بین"),
    (2, "یُحْیِی", "زنده می‌کند"),
    (2, "یُمِیت", "می‌میراند"),
    (2, "مُوقِنِین", "اهل یقین"),
]


def _normalize(value):
    """حذف اعراب و یکسان‌سازی حروف عربی/فارسی برای جست‌وجو."""
    value = str(value)
    for ch in "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640":
        value = value.replace(ch, "")
    return (
        value.replace("ك", "ک")
        .replace("ي", "ی")
        .replace("ى", "ی")
        .replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .strip()
    )


class WordManager:

    def __init__(self):
        self.words = [
            {"lesson": lesson, "word": word, "meaning": meaning}
            for lesson, word, meaning in WORDS
        ]
        self.lessons = sorted({w["lesson"] for w in self.words})

    def get_all_words(self):
        return list(self.words)

    def search(self, value):
        key = _normalize(value)
        if not key:
            return self.get_all_words()
        return [
            w for w in self.words
            if key in _normalize(w["word"])
            or key in _normalize(w["meaning"])
        ]


# ==================================================
# تنظیمات اصلی
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

BG = (0.008, 0.018, 0.043, 1)
NAVY = (0.018, 0.035, 0.072, 1)
CARD = (0.025, 0.050, 0.095, 1)
CARD2 = (0.040, 0.065, 0.115, 1)

GOLD = (0.88, 0.65, 0.30, 1)
GOLD_LIGHT = (1.0, 0.81, 0.48, 1)

WHITE = (0.96, 0.96, 0.98, 1)
MUTED = (0.60, 0.66, 0.76, 1)
BORDER = (0.30, 0.34, 0.42, 0.55)


# ==================================================
# فونت فارسی
# ==================================================

FONT_NAME = "Roboto"

FONT_CANDIDATES = [
    BASE_DIR / "assets" / "fonts" / "Vazirmatn-Regular.ttf",
    BASE_DIR / "assets" / "fonts" / "IRANSans.ttf",
    Path("C:/Windows/Fonts/tahoma.ttf"),
    Path("/system/fonts/NotoNaskhArabic-Regular.ttf"),
    Path("/system/fonts/NotoSansArabic-Regular.ttf"),
    Path("/system/fonts/NotoSansArabicUI-Regular.ttf"),
    Path("/system/fonts/DroidNaskh-Regular.ttf"),
    Path("/system/fonts/DroidSansArabic.ttf"),
]

for font_path in FONT_CANDIDATES:
    if font_path.is_file():
        LabelBase.register(
            name="QuranFont",
            fn_regular=str(font_path)
        )
        FONT_NAME = "QuranFont"
        break


def rtl_text(value):
    if not HAS_RTL:
        return str(value)
    return get_display(
        arabic_reshaper.reshape(str(value))
    )


# ==================================================
# برچسب فارسی
# ==================================================

class AppLabel(Label):

    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", FONT_NAME)
        kwargs.setdefault("halign", "right")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)

        self._busy = False
        self._ready = True

        self._shape_text(self.text)

        self.bind(size=self._resize)

    def _shape_text(self, value):
        self._busy = True
        self.text = rtl_text(value)
        self._busy = False

    def on_text(self, instance, value):
        if getattr(self, "_ready", False) and not self._busy:
            self._shape_text(value)

    def _resize(self, *_):
        self.text_size = (self.width, self.height)


# ==================================================
# کارت پایه
# ==================================================

class PremiumCard(BoxLayout):

    def __init__(
        self,
        panel_color=CARD,
        radius=dp(22),
        border=True,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.radius = radius

        with self.canvas.before:
            Color(*panel_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[radius]
            )

            if border:
                Color(*BORDER)
                self.outline = Line(
                    rounded_rectangle=(
                        self.x, self.y,
                        self.width, self.height,
                        radius
                    ),
                    width=0.75
                )
            else:
                self.outline = None

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas
        )

    def update_canvas(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

        if self.outline:
            self.outline.rounded_rectangle = (
                self.x, self.y,
                self.width, self.height,
                self.radius
            )


# ==================================================
# کارت قابل کلیک
# ==================================================

class TapCard(PremiumCard):

    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback()
            return True

        return super().on_touch_up(touch)


# ==================================================
# دکمه اصلی
# ==================================================

class GoldButton(Button):

    def __init__(self, **kwargs):
        raw = kwargs.pop("text", "")

        super().__init__(
            text=rtl_text(raw),
            **kwargs
        )

        self.font_name = FONT_NAME
        self.font_size = sp(14)
        self.bold = True
        self.color = BG

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(*GOLD_LIGHT)
            self.shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )

        self.bind(
            pos=self.update_shape,
            size=self.update_shape
        )

    def update_shape(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size


# ==================================================
# کارت هنری بالای صفحه
# ==================================================

class IslamicHero(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:

            Color(0.018, 0.043, 0.090, 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(28)]
            )

            # هاله نور ماه
            Color(0.75, 0.49, 0.20, 0.10)
            self.halo = Ellipse(
                size=(dp(150), dp(150))
            )

            # قوس معماری
            Color(0.60, 0.43, 0.22, 0.85)
            self.arch = Line(
                points=[],
                width=1.25
            )

            # خط طلایی پایین
            Color(*GOLD)
            self.bottom_line = Line(
                points=[],
                width=1
            )

            # هلال
            Color(*GOLD_LIGHT)
            self.moon = Ellipse(
                size=(dp(30), dp(30))
            )

            Color(0.018, 0.043, 0.090, 1)
            self.moon_cover = Ellipse(
                size=(dp(27), dp(27))
            )

            # سیلوئت شهر
            Color(0.008, 0.018, 0.043, 1)
            self.city = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_art,
            size=self.update_art
        )

        # فانوس‌ها
        self.left_lantern = AppLabel(
            text="♜",
            color=GOLD_LIGHT,
            font_size=sp(35),
            halign="center",
            size_hint=(None, None),
            size=(dp(55), dp(65))
        )
        self.right_lantern = AppLabel(
            text="♜",
            color=GOLD_LIGHT,
            font_size=sp(35),
            halign="center",
            size_hint=(None, None),
            size=(dp(55), dp(65))
        )

        self.add_widget(self.left_lantern)
        self.add_widget(self.right_lantern)

        self.title = AppLabel(
            text="واژگان قرآن نهم",
            color=GOLD_LIGHT,
            font_size=sp(28),
            bold=True,
            halign="center",
            size_hint=(0.92, None),
            height=dp(48),
            pos_hint={"center_x": 0.5, "center_y": 0.43}
        )

        self.subtitle = AppLabel(
            text="یادگیری عمیق، با طراحی مدرن",
            color=WHITE,
            font_size=sp(12),
            halign="center",
            size_hint=(0.9, None),
            height=dp(27),
            pos_hint={"center_x": 0.5, "center_y": 0.30}
        )

        self.add_widget(self.title)
        self.add_widget(self.subtitle)

    def update_art(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.halo.pos = (
            self.center_x - dp(75),
            self.y + self.height * 0.43
        )

        cx = self.center_x
        top = self.top - dp(8)
        width = self.width

        # قوس اسلامی
        points = [
            self.x + dp(18), self.y + self.height * 0.30,
            self.x + dp(18), self.y + self.height * 0.72,
            cx - dp(55), top - dp(75),
            cx, top - dp(30),
            cx + dp(55), top - dp(75),
            self.right - dp(18), self.y + self.height * 0.72,
            self.right - dp(18), self.y + self.height * 0.30
        ]

        self.arch.points = points

        self.bottom_line.points = [
            self.x + dp(20), self.y + dp(13),
            cx, self.y + dp(7),
            self.right - dp(20), self.y + dp(13)
        ]

        self.moon.pos = (
            cx - dp(15),
            self.y + self.height * 0.70
        )

        self.moon_cover.pos = (
            cx - dp(6),
            self.y + self.height * 0.72
        )

        # نمای ساده شهر
        self.city.pos = (
            self.x + dp(35),
            self.y + self.height * 0.34
        )
        self.city.size = (
            width - dp(70),
            dp(24)
        )

        self.left_lantern.pos = (
            self.x + dp(8),
            self.y + self.height * 0.48
        )

        self.right_lantern.pos = (
            self.right - dp(63),
            self.y + self.height * 0.48
        )


# ==================================================
# کارت آمار
# ==================================================

class StatCard(PremiumCard):

    def __init__(self, icon, title, value, **kwargs):

        super().__init__(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(2),
            radius=dp(20),
            panel_color=(0.035, 0.060, 0.112, 1),
            **kwargs
        )

        self.add_widget(AppLabel(
            text=icon,
            color=GOLD,
            font_size=sp(23),
            halign="center"
        ))

        self.add_widget(AppLabel(
            text=title,
            color=MUTED,
            font_size=sp(11),
            halign="center"
        ))

        self.add_widget(AppLabel(
            text=str(value),
            color=GOLD_LIGHT,
            font_size=sp(22),
            bold=True,
            halign="center"
        ))


# ==================================================
# کارت واژگان
# ==================================================

class WordCard(PremiumCard):

    def __init__(self, item, callback, **kwargs):

        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(85),
            padding=[dp(14), dp(10)],
            spacing=dp(10),
            radius=dp(19),
            **kwargs
        )

        text_box = BoxLayout(
            orientation="vertical",
            spacing=dp(2)
        )

        text_box.add_widget(AppLabel(
            text=item["word"],
            color=GOLD_LIGHT,
            font_size=sp(22),
            bold=True
        ))

        text_box.add_widget(AppLabel(
            text=item["meaning"],
            color=MUTED,
            font_size=sp(13)
        ))

        self.add_widget(text_box)

        btn = GoldButton(
            text="معنی",
            size_hint_x=None,
            width=dp(65)
        )

        btn.bind(
            on_release=lambda *_: callback(item)
        )

        self.add_widget(btn)


# ==================================================
# پنجره معنی
# ==================================================

class WordDetail(ModalView):

    def __init__(self, item, **kwargs):

        super().__init__(
            size_hint=(0.90, None),
            height=dp(280),
            background="",
            background_color=(0, 0, 0, 0),
            **kwargs
        )

        panel = PremiumCard(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(13),
            panel_color=NAVY,
            radius=dp(26)
        )

        panel.add_widget(AppLabel(
            text="واژه قرآنی",
            color=GOLD,
            font_size=sp(14),
            halign="center",
            size_hint_y=None,
            height=dp(28)
        ))

        word = AppLabel(
            text=item["word"],
            color=GOLD_LIGHT,
            font_size=sp(35),
            bold=True,
            halign="center"
        )

        panel.add_widget(word)

        meaning = AppLabel(
            text=item["meaning"],
            color=WHITE,
            font_size=sp(23),
            halign="center",
            opacity=0
        )

        panel.add_widget(meaning)

        panel.add_widget(AppLabel(
            text="تلفظ صوتی در مرحله بعد اضافه می‌شود",
            color=MUTED,
            font_size=sp(11),
            halign="center",
            size_hint_y=None,
            height=dp(25)
        ))

        close = GoldButton(
            text="بستن",
            size_hint_y=None,
            height=dp(45)
        )

        close.bind(
            on_release=lambda *_: self.dismiss()
        )

        panel.add_widget(close)
        self.add_widget(panel)

        self.bind(
            on_open=lambda *_: Animation(
                opacity=1,
                duration=0.4
            ).start(meaning)
        )


# ==================================================
# برنامه اصلی
# ==================================================

class QuranVocabularyApp(App):

    title = "واژگان قرآن نهم"

    def build(self):
        try:
            return self._build_app()
        except Exception:
            err = traceback.format_exc()
            try:
                (BASE_DIR / "error_log.txt").write_text(
                    err, encoding="utf-8"
                )
            except Exception:
                pass
            print(err)
            scroll = ScrollView()
            label = Label(
                text="ERROR:\n\n" + err,
                size_hint_y=None,
                halign="left",
                valign="top",
                font_size=sp(11),
                padding=(dp(8), dp(8))
            )
            label.bind(
                width=lambda w, v: setattr(w, "text_size", (v, None)),
                texture_size=lambda w, v: setattr(w, "height", v[1])
            )
            scroll.add_widget(label)
            return scroll

    def _build_app(self):

        Window.clearcolor = BG

        self.manager = WordManager()
        self.all_words = self.manager.get_all_words()

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(10), dp(12), dp(8)],
            spacing=dp(8)
        )

        # محتوای صفحه
        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(2)
        )

        self.page = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(13),
            padding=[0, dp(3), 0, dp(15)]
        )

        self.page.bind(
            minimum_height=self.page.setter("height")
        )

        self.scroll.add_widget(self.page)
        root.add_widget(self.scroll)

        # نوار پایین
        nav_card = PremiumCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[dp(5), dp(5)],
            spacing=dp(3),
            radius=dp(22),
            panel_color=(0.018, 0.038, 0.078, 1)
        )

        self.nav_buttons = {}

        nav_items = [
            ("home", "⌂", "خانه", self.show_home),
            ("words", "▤", "واژگان", self.show_words),
            ("practice", "♧", "تمرین", lambda: self.coming_soon("تمرین")),
            ("quiz", "♜", "آزمون", lambda: self.coming_soon("آزمون")),
        ]

        for key, icon, label, callback in nav_items:

            item = BoxLayout(
                orientation="vertical",
                spacing=0
            )

            button = Button(
                text=rtl_text(icon + "\n" + label),
                font_name=FONT_NAME,
                font_size=sp(12),
                color=MUTED,
                background_normal="",
                background_down="",
                background_color=(0, 0, 0, 0)
            )

            button.bind(
                on_release=lambda _btn, cb=callback: cb()
            )

            item.add_widget(button)
            nav_card.add_widget(item)

            self.nav_buttons[key] = button

        root.add_widget(nav_card)

        self.show_home()

        return root

    # ---------- وضعیت منو ----------

    def set_nav(self, active):

        for key, button in self.nav_buttons.items():

            button.color = (
                GOLD_LIGHT if key == active else MUTED
            )

    def clear_page(self):
        self.page.clear_widgets()

    # ---------- عنوان بخش ----------

    def section_title(self, title, subtitle=""):

        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(1)
        )

        box.add_widget(AppLabel(
            text=title,
            color=WHITE,
            font_size=sp(20),
            bold=True
        ))

        if subtitle:
            box.add_widget(AppLabel(
                text=subtitle,
                color=MUTED,
                font_size=sp(11)
            ))

        return box

    # ---------- کارت معرفی سازنده ----------

    def creator_card(self):

        card = PremiumCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(82),
            padding=[dp(13), dp(9)],
            spacing=dp(12),
            radius=dp(24),
            panel_color=(0.028, 0.055, 0.105, 1)
        )

        icon = AppLabel(
            text="۞",
            color=GOLD_LIGHT,
            font_size=sp(39),
            halign="center",
            size_hint_x=None,
            width=dp(58)
        )

        card.add_widget(icon)

        info = BoxLayout(
            orientation="vertical",
            spacing=dp(1)
        )

        info.add_widget(AppLabel(
            text="محمد جواد نالان",
            color=WHITE,
            font_size=sp(17),
            bold=True
        ))

        info.add_widget(AppLabel(
            text="طراح و سازنده برنامه",
            color=MUTED,
            font_size=sp(11)
        ))

        card.add_widget(info)

        card.add_widget(AppLabel(
            text="‹",
            color=GOLD,
            font_size=sp(32),
            size_hint_x=None,
            width=dp(25),
            halign="center"
        ))

        return card

    # ---------- بنر شروع یادگیری ----------

    def learning_banner(self):

        card = TapCard(
            callback=self.show_words,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(125),
            padding=dp(15),
            spacing=dp(10),
            radius=dp(24),
            panel_color=(0.035, 0.065, 0.125, 1)
        )

        art = AppLabel(
            text="۞\n♧",
            color=GOLD_LIGHT,
            font_size=sp(38),
            halign="center",
            size_hint_x=0.40
        )

        card.add_widget(art)

        info = BoxLayout(
            orientation="vertical",
            spacing=dp(5)
        )

        info.add_widget(AppLabel(
            text="شروع یادگیری",
            color=GOLD_LIGHT,
            font_size=sp(20),
            bold=True
        ))

        info.add_widget(AppLabel(
            text="مرور واژگان و معانی",
            color=WHITE,
            font_size=sp(12)
        ))

        info.add_widget(AppLabel(
            text="برای ورود کلیک کن",
            color=MUTED,
            font_size=sp(10)
        ))

        card.add_widget(info)

        return card

    # ---------- کارت دسترسی ----------

    def action_card(self, icon, title, subtitle, callback):

        card = TapCard(
            callback=callback,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(91),
            padding=[dp(10), dp(8)],
            spacing=dp(7),
            radius=dp(19),
            panel_color=(0.030, 0.055, 0.105, 1)
        )

        card.add_widget(AppLabel(
            text=icon,
            color=GOLD,
            font_size=sp(26),
            halign="center",
            size_hint_x=0.32
        ))

        info = BoxLayout(
            orientation="vertical",
            spacing=dp(3)
        )

        info.add_widget(AppLabel(
            text=title,
            color=WHITE,
            font_size=sp(14),
            bold=True
        ))

        info.add_widget(AppLabel(
            text=subtitle,
            color=MUTED,
            font_size=sp(10)
        ))

        card.add_widget(info)

        return card

    # ---------- صفحه خانه ----------

    def show_home(self):

        self.set_nav("home")
        self.clear_page()

        self.page.add_widget(
            self.section_title(
                "خوش آمدی",
                "آماده‌ای واژگان قرآن را بهتر یاد بگیری؟"
            )
        )

        hero = IslamicHero(
            size_hint_y=None,
            height=dp(245)
        )

        self.page.add_widget(hero)

        self.page.add_widget(
            self.creator_card()
        )

        # آمار
        stats = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(105),
            spacing=dp(8)
        )

        stats.add_widget(
            StatCard("★", "واژگان", len(self.all_words))
        )

        stats.add_widget(
            StatCard("▤", "درس‌ها", len(self.manager.lessons))
        )

        stats.add_widget(
            StatCard("♜", "آزمون‌ها", "۰")
        )

        self.page.add_widget(stats)

        self.page.add_widget(
            self.learning_banner()
        )

        self.page.add_widget(
            self.section_title("دسترسی سریع")
        )

        actions = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(194),
            spacing=dp(9)
        )

        actions.add_widget(
            self.action_card(
                "▥",
                "آزمون",
                "سنجش آموخته‌ها",
                lambda: self.coming_soon("آزمون")
            )
        )

        actions.add_widget(
            self.action_card(
                "✦",
                "تمرین",
                "تقویت یادگیری",
                lambda: self.coming_soon("تمرین")
            )
        )

        actions.add_widget(
            self.action_card(
                "⌕",
                "جست‌وجو",
                "پیدا کردن معنی واژه",
                self.show_words
            )
        )

        actions.add_widget(
            self.action_card(
                "▤",
                "فهرست واژگان",
                "مشاهده همه واژه‌ها",
                self.show_words
            )
        )

        self.page.add_widget(actions)

        self.page.add_widget(
            self.section_title("آخرین واژگان")
        )

        for item in self.all_words[:4]:

            self.page.add_widget(
                WordCard(item, self.open_word)
            )

    # ---------- صفحه واژگان ----------

    def show_words(self):

        self.set_nav("words")
        self.clear_page()

        self.page.add_widget(
            self.section_title(
                "فهرست واژگان",
                f"{len(self.all_words)} واژه در مجموعه فعلی"
            )
        )

        self.search_input = TextInput(
            hint_text=rtl_text("جست‌وجوی واژه عربی یا معنی فارسی..."),
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(13), dp(13)],
            background_normal="",
            background_active="",
            background_color=CARD2,
            foreground_color=WHITE,
            hint_text_color=MUTED,
            cursor_color=GOLD_LIGHT,
            font_size=sp(13),
            font_name=FONT_NAME,
            halign="right"
        )

        if "base_direction" in self.search_input.properties():
            self.search_input.base_direction = "rtl"

        self.page.add_widget(self.search_input)

        self.result_title = AppLabel(
            text="همه واژگان",
            color=GOLD,
            font_size=sp(13),
            size_hint_y=None,
            height=dp(28)
        )

        self.page.add_widget(self.result_title)

        self.results = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(9)
        )

        self.results.bind(
            minimum_height=self.results.setter("height")
        )

        self.page.add_widget(self.results)

        self.search_input.bind(
            text=self.on_search
        )

        self.refresh_words(self.all_words)

    # ---------- نمایش واژگان ----------

    def refresh_words(self, items):

        self.results.clear_widgets()

        if not items:

            self.results.add_widget(AppLabel(
                text="واژه‌ای پیدا نشد",
                color=MUTED,
                size_hint_y=None,
                height=dp(60),
                halign="center"
            ))

            return

        for item in items:

            card = WordCard(
                item,
                self.open_word
            )

            self.results.add_widget(card)

            card.opacity = 0

            Animation(
                opacity=1,
                duration=0.22
            ).start(card)

    # ---------- جست‌وجو ----------

    def on_search(self, _instance, value):

        results = self.manager.search(value)

        self.result_title.text = (
            f"نتایج جست‌وجو: {len(results)}"
            if value.strip()
            else "همه واژگان"
        )

        self.refresh_words(
            results if value.strip() else self.all_words
        )

    # ---------- نمایش معنی ----------

    def open_word(self, item):
        WordDetail(item).open()

    # ---------- بخش‌های آینده ----------

    def coming_soon(self, section):

        popup = ModalView(
            size_hint=(0.85, None),
            height=dp(175),
            background="",
            background_color=(0, 0, 0, 0)
        )

        panel = PremiumCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10),
            radius=dp(23),
            panel_color=NAVY
        )

        panel.add_widget(AppLabel(
            text=f"بخش {section}",
            color=GOLD_LIGHT,
            font_size=sp(21),
            bold=True,
            halign="center"
        ))

        panel.add_widget(AppLabel(
            text="این بخش در مرحله بعدی توسعه فعال می‌شود.",
            color=WHITE,
            font_size=sp(12),
            halign="center"
        ))

        close = GoldButton(
            text="متوجه شدم",
            size_hint_y=None,
            height=dp(44)
        )

        close.bind(
            on_release=lambda *_: popup.dismiss()
        )

        panel.add_widget(close)

        popup.add_widget(panel)
        popup.open()


if __name__ == "__main__":
    QuranVocabularyApp().run()
