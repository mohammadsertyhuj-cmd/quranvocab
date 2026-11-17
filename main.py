
from pathlib import Path

import os
import random
from functools import lru_cache
import re
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
from kivy.clock import Clock
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
from kivy.storage.jsonstore import JsonStore

# ==================================================
# آموزش قرآن نهم (درس ۱ تا ۱۱)
# برای اضافه کردن واژه‌ی جدید، یک خط به لیست زیر اضافه کن:
# (شماره درس, "واژه", "معنی")
# ==================================================

WORDS = [
    # ===== درس ۱ =====
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

    # ===== درس ۲ =====
    (2, "مُبارَک، مُبارَکَة", "مبارک، با برکت"),
    (2, "مُنْذِر", "هشداردهنده، بیم‌دهنده"),
    (2, "عِنْد", "نزد"),
    (2, "مُرْسِل", "ارسال‌کننده، فرستنده"),
    (2, "بَیْن", "میان، بین"),
    (2, "یُحْیِی", "زنده می‌کند"),
    (2, "یُمِیت", "می‌میراند"),
    (2, "أَوَّلِین", "پیشین، پیشینیان"),
    (2, "مُوقِنِین", "اهل یقین"),
    (2, "بَصائِر", "بصیرت‌ها، بینش‌ها"),
    (2, "سَیِّئات", "کارهای بد، بدی‌ها، جمع سَیِّئَة"),
    (2, "سَواء", "یکسان، مساوی"),
    (2, "مَحْیا", "زندگی"),
    (2, "مَمات", "مرگ"),
    (2, "ساءَ", "چه بد است"),
    (2, "یَحْکُمُونَ", "حکم می‌کنند، قضاوت می‌کنند"),
    (2, "تَسْتَوِی", "مساوی است"),

    # ===== درس ۳ =====
    (3, "أَجَل", "سرآمد، مدّت"),
    (3, "مُسَمًّی", "مشخص، معیّن"),
    (3, "خَوْف", "ترس"),
    (3, "یَحْزَنُونَ", "اندوهگین می‌شوند، غمگین می‌شوند"),
    (3, "أَصْحاب", "اهل، یاران"),
    (3, "خالِدِینَ", "جاودان"),
    (3, "جَزاء", "پاداش"),
    (3, "کانُوا یَعْمَلُونَ", "انجام می‌دادند، عمل می‌کردند"),
    (3, "صَدُّوا", "مانع شدند"),
    (3, "أَضَلَّ", "محو و نابود کرد، گمراه کرد"),
    (3, "أَعْمال", "اعمال، کارها"),
    (3, "نُزِّلَ", "نازل شد"),
    (3, "اتَّبَعُوا", "تبعیت کردند، پیروی کردند"),
    (3, "أُنْزِلَ", "نازل شد"),

    # ===== درس ۴ =====
    (4, "سَکِینَة", "آرامش"),
    (4, "جُنُود", "لشکریان، جمع جُند"),
    (4, "یُدْخِلُ", "وارد می‌کند"),
    (4, "تَجْرِی", "روان است"),
    (4, "تَحْت", "زیر"),
    (4, "أَنْهار", "رودها"),
    (4, "فَوْز", "موفقیت، رستگاری"),
    (4, "عَظِیم", "بزرگ"),
    (4, "إِخْوَة", "برادران"),
    (4, "أَصْلِحُوا", "اصلاح کنید"),
    (4, "تُرْحَمُونَ", "مورد رحمت قرار می‌گیرید"),
    (4, "لا یَسْخَرْ", "نباید مسخره کند"),
    (4, "عَسَی", "شاید"),
    (4, "یَکُونُونَ، یَکُونُوا", "می‌باشند، باشند"),
    (4, "نِساء", "زنان"),

    # ===== درس ۵ =====
    (5, "کانُوا", "بودند"),
    (5, "أَسْحار", "سَحَرها، جمع سَحَر"),
    (5, "یَسْتَغْفِرُونَ", "استغفار می‌کنند، آمرزش می‌خواهند"),
    (5, "أَمْوال", "ثروت، جمع مال"),
    (5, "سائِل", "نیازمند، درخواست‌کننده"),
    (5, "مَحْرُوم", "محروم، نیازمند"),
    (5, "یَسَّرْنا", "آسان کردیم"),
    (5, "ذِکْر", "پند، یاد"),
    (5, "آل", "آل، خاندان"),
    (5, "مُدَّکِر", "پندگیرنده"),
    (5, "نُذُر", "هشدارها، هشداردهندگان"),
    (5, "أَخَذْنا", "مجازات کردیم، گرفتیم"),

    # ===== درس ۶ =====
    (6, "عَلَّمَ", "یاد داد، آموخت"),
    (6, "بَیان", "سخن، سخن گفتن"),
    (6, "نَجْم", "علف، گیاه بدون ساقه"),
    (6, "یَسْجُدُ", "سجده می‌کند"),
    (6, "رَفَعَ", "برافراشت"),
    (6, "وَضَعَ", "قرار داد، نهاد"),
    (6, "میزان", "ترازو، معیار"),
    (6, "لا تَطْغَوْا", "طغیان نکنید، از حد نگذرید"),
    (6, "رَأَیْتُمْ", "دیدید، دقت کردید"),
    (6, "تَزْرَعُونَ", "می‌رویانید، زراعت می‌کنید"),
    (6, "زارِع", "کشاورز، رویاننده"),
    (6, "نَشاءُ", "می‌خواهیم"),
    (6, "تَشْرَبُونَ", "می‌آشامید، می‌نوشید"),
    (6, "تَشْکُرُونَ", "شکر می‌کنید، سپاسگزاری می‌کنید"),

    # ===== درس ۷ =====
    (7, "رُسُل", "پیامبران، جمع رَسول"),
    (7, "بَیِّنات", "دلایل روشن، جمع بَیِّنَة"),
    (7, "یَقُومَ ... بِ", "رفتار کند ... به، به پا دارد"),
    (7, "حَدِید", "آهن"),
    (7, "بَأْس", "سختی"),
    (7, "مَنافِع", "فایده‌ها"),
    (7, "یَنْصُرُ", "یاری می‌کند"),
    (7, "قَوِیّ", "قوی، قدرتمند"),
    (7, "نَفْس", "شخص، انسان"),
    (7, "غَد", "فردا"),
    (7, "لا تَکُونُوا", "نباشید"),
    (7, "نَسُوا", "فراموش کردند"),
    (7, "فاسِق", "نافرمان، گناهکار، منحرف"),
    (7, "یَسْتَوِی", "مساوی است"),
    (7, "نار", "آتش"),
    (7, "فائِز", "رستگار، موفّق"),

    # ===== درس ۸ =====
    (8, "تُنْجِی", "نجات می‌دهد"),
    (8, "تُؤْمِنُونَ", "ایمان می‌آورید"),
    (8, "تُجاهِدُونَ", "جهاد و تلاش می‌کنید"),
    (8, "کُنْتُمْ تَعْلَمُونَ", "می‌دانستید"),
    (8, "یَغْفِرْ", "می‌آمرزد، می‌پوشاند"),
    (8, "ذُنُوب", "گناهان، جمع ذَنْب"),
    (8, "مَساکِن", "خانه‌ها، جمع مَسْکَن"),
    (8, "عَدْن", "جاودان"),
    (8, "إِذا", "وقتی که"),
    (8, "نُودِیَ", "ندا داده شد"),
    (8, "بَیْع", "خرید و فروش"),
    (8, "ذلِکُمْ", "این، آن"),
    (8, "قُضِیَتْ", "تمام شد"),
    (8, "انْتَشِرُوا", "پراکنده شوید"),
    (8, "ابْتَغُوا", "بجویید، طلب کنید"),
    (8, "تُفْلِحُونَ", "رستگار می‌شوید، موفّق می‌شوید"),

    # ===== درس ۹ =====
    (9, "یَتَّقِ (یَتَّقِی)", "تقوا داشته باشد"),
    (9, "یَجْعَلْ", "قرار می‌دهد"),
    (9, "مَخْرَج", "راه نجات، محل خروج"),
    (9, "حَیْثُ", "جا، هرکجا"),
    (9, "یَحْتَسِبُ", "گمان می‌کند"),
    (9, "یَتَوَکَّلُ", "توکّل می‌کند"),
    (9, "حَسْب", "کافی است"),
    (9, "قَدْر", "اندازه"),
    (9, "یَد", "دست، جمع: أَیْدی"),
    (9, "مَوْت", "مرگ"),
    (9, "یَبْلُو", "می‌آزماید"),
    (9, "أَیّ", "کدام، کدام یک"),
    (9, "کُنَّا نَسْمَعُ", "گوش شنوا داشتیم، می‌شنیدیم"),
    (9, "أَوْ", "یا"),
    (9, "نَعْقِلُ", "اندیشه و درک می‌کنیم"),
    (9, "سَعِیر", "دوزخ، آتش فروزان"),

    # ===== درس ۱۰ =====
    (10, "أَنْذِرْ", "هشدار ده"),
    (10, "یَأْتِی", "می‌آید"),
    (10, "یُؤَخِّرُ", "به تأخیر می‌اندازد، مهلت می‌دهد به"),
    (10, "دَخَلَ", "داخل شد به، وارد شد به"),
    (10, "لا تَزِدْ", "نیفزای، زیاد نکن"),
    (10, "تَبار", "هلاکت، نابودی"),
    (10, "قُمْ", "برخیز، به پا خیز"),
    (10, "قَلِیل", "اندک، کم"),
    (10, "نِصْف", "نصف، نیم"),
    (10, "رَتِّلْ", "آرام و با دقت بخوان"),
    (10, "ثَقِیل", "سنگین، گران‌بار، با ارزش"),
    (10, "سَبْح", "کار و تلاش"),
    (10, "طَوِیل", "طولانی، بسیار"),
    (10, "اُذْکُرْ", "یاد کن"),
    (10, "اتَّخِذْ", "بگیر، قرار بده"),

    # ===== درس ۱۱ =====
    (11, "عَمَّ (عَنْ + ما)", "از چه"),
    (11, "کَلَّا", "هرگز چنین نیست"),
    (11, "ثُمَّ", "سپس، باز هم"),
    (11, "لَمْ نَجْعَلْ", "قرار ندادیم"),
    (11, "مِهاد", "محل آرامش و استراحت"),
    (11, "أَزْواج", "گونه‌ها و شکل‌ها (ی مختلف)، جمع زَوْج"),
    (11, "سُبات", "آسایش و آرامش"),
    (11, "مَعاش", "کسب و کار، زندگی"),
    (11, "یَنْظُرُونَ", "می‌بینند، دقت می‌کنند"),
    (11, "إِبِل", "شتر"),
    (11, "کَیْفَ", "چگونه"),
    (11, "خُلِقَتْ", "خلق شد"),
    (11, "رُفِعَتْ", "برافراشته شد"),
    (11, "نُصِبَتْ", "برپا شد"),
    (11, "سُطِحَتْ", "گسترده شد، هموار شد"),
]

# اطلاعات مدرسه (اگر خالی باشد نمایش داده نمی‌شود)
SCHOOL_NAME = "فرهنگ شهید پرکار"
PROVINCE = "آذربایجان شرقی"
CITY = "مراغه"
COLLAB_NAME = "استاد عابدینی"


def _normalize(value):
    """حذف اعراب و یکسان‌سازی حروف عربی/فارسی برای جست‌وجو."""
    value = str(value)
    for ch in "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640":
        value = value.replace(ch, "")
    value = value.replace("\u200c", " ")
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



def fa_num(value):
    return str(value).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def _meaning_tokens(meaning):
    parts = re.split(r"[\s،]+", _normalize(meaning))
    return {p for p in parts if len(p) >= 4}


def build_questions(words, lesson=None, count=10):
    """ساخت سؤال چهارگزینه‌ای: معنی واژه را انتخاب کن."""
    pool = [w for w in words if lesson is None or w["lesson"] == lesson]
    random.shuffle(pool)
    chosen = pool[:count]

    all_meanings = sorted({w["meaning"] for w in words})
    questions = []

    for w in chosen:
        right_tokens = _meaning_tokens(w["meaning"])
        candidates = [
            m for m in all_meanings
            if m != w["meaning"]
            and not (_meaning_tokens(m) & right_tokens)
        ]
        random.shuffle(candidates)
        options = candidates[:3] + [w["meaning"]]
        random.shuffle(options)
        questions.append({
            "word": w["word"],
            "answer": w["meaning"],
            "options": options,
        })

    return questions


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


@lru_cache(maxsize=4096)
def _shape(value):
    return get_display(
        arabic_reshaper.reshape(value)
    )


def rtl_text(value):
    if not HAS_RTL:
        return str(value)
    return _shape(str(value))


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
# دکمه گزینه / انتخاب درس
# ==================================================

class ChipButton(Button):

    COLORS = {
        "normal": (CARD2, WHITE),
        "active": (GOLD_LIGHT, BG),
        "correct": ((0.13, 0.55, 0.32, 1), WHITE),
        "wrong": ((0.70, 0.18, 0.20, 1), WHITE),
    }

    def __init__(self, text, state="normal", radius=dp(16), **kwargs):
        super().__init__(text=rtl_text(text), **kwargs)

        self.font_name = FONT_NAME
        self.font_size = sp(13)
        self.halign = "center"
        self.valign = "middle"

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            self._bg_color = Color(*CARD2)
            self._bg_shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[radius]
            )

        self.bind(
            pos=self._update_shape,
            size=self._update_shape
        )

        self.set_state(state)

    def _update_shape(self, *_):
        self._bg_shape.pos = self.pos
        self._bg_shape.size = self.size
        self.text_size = (max(self.width - dp(16), 0), None)

    def set_state(self, state):
        bg, fg = self.COLORS[state]
        self._bg_color.rgba = bg
        self.color = fg


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
            text="آموزش قرآن نهم",
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
            text="واژه قرآنی  |  درس " + fa_num(item["lesson"]),
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

    title = "آموزش قرآن نهم"

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
        self.load_stats()
        self.words_lesson = None

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
            ("practice", "♧", "تمرین", lambda: self.show_picker("practice")),
            ("quiz", "♜", "آزمون", lambda: self.show_picker("exam")),
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
        self.scroll.scroll_y = 1

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

    # ---------- کارت مدرسه ----------

    def teacher_card(self):

        lines = []

        if SCHOOL_NAME.strip():
            lines.append(("مدرسه: " + SCHOOL_NAME.strip(), WHITE, 15))

        place = " - ".join(
            part.strip() for part in (PROVINCE, CITY) if part.strip()
        )

        if place:
            lines.append((place, MUTED, 12))

        if COLLAB_NAME.strip():
            lines.append(("با همکاری: " + COLLAB_NAME.strip(), GOLD_LIGHT, 13))

        if not lines:
            return None

        card = PremiumCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(27 * len(lines) + 22),
            padding=[dp(14), dp(10)],
            spacing=dp(2),
            radius=dp(20),
            panel_color=(0.028, 0.055, 0.105, 1)
        )

        for text, color, size in lines:
            card.add_widget(AppLabel(
                text=text,
                color=color,
                font_size=sp(size)
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

        teacher_card = self.teacher_card()
        if teacher_card is not None:
            self.page.add_widget(teacher_card)

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
            StatCard("♜", "آزمون‌ها", fa_num(self.exam_count))
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
                lambda: self.show_picker("exam")
            )
        )

        actions.add_widget(
            self.action_card(
                "✦",
                "تمرین",
                "تقویت یادگیری",
                lambda: self.show_picker("practice")
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

        self.words_lesson = None

        self.page.add_widget(
            self.section_title(
                "فهرست واژگان",
                f"{fa_num(len(self.all_words))} واژه از "
                f"{fa_num(len(self.manager.lessons))} درس"
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

        # انتخاب درس
        chips_scroll = ScrollView(
            do_scroll_y=False,
            size_hint_y=None,
            height=dp(42),
            bar_width=0
        )

        chips_row = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=dp(7)
        )

        chips_row.bind(
            minimum_width=chips_row.setter("width")
        )

        self.chip_buttons = {}

        for key in [None] + list(self.manager.lessons):

            label = "همه" if key is None else "درس " + fa_num(key)

            chip = ChipButton(
                label,
                state="active" if key is None else "normal",
                size_hint_x=None,
                width=dp(78)
            )

            chip.bind(
                on_release=lambda _b, k=key: self.set_words_lesson(k)
            )

            chips_row.add_widget(chip)
            self.chip_buttons[key] = chip

        chips_scroll.add_widget(chips_row)
        self.page.add_widget(chips_scroll)

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

    def set_words_lesson(self, lesson):

        self.words_lesson = lesson

        for key, chip in self.chip_buttons.items():
            chip.set_state("active" if key == lesson else "normal")

        self.update_words()

    def update_words(self):

        text = self.search_input.text.strip()
        items = self.manager.search(text)

        if self.words_lesson is not None:
            items = [
                w for w in items
                if w["lesson"] == self.words_lesson
            ]

        if text or self.words_lesson is not None:
            self.result_title.text = (
                f"نتایج: {fa_num(len(items))} واژه"
            )
        else:
            self.result_title.text = "همه واژگان"

        self.refresh_words(items)

    # ---------- نمایش واژگان (صفحه‌بندی برای سرعت) ----------

    PAGE_SIZE = 15

    def refresh_words(self, items):

        self.results.clear_widgets()
        self.more_button = None
        self.pending_words = list(items)
        self.shown_words = 0

        if not items:

            self.results.add_widget(AppLabel(
                text="واژه‌ای پیدا نشد",
                color=MUTED,
                size_hint_y=None,
                height=dp(60),
                halign="center"
            ))

            return

        self.load_more_words()

    def load_more_words(self, *_):

        if self.more_button is not None:
            self.results.remove_widget(self.more_button)
            self.more_button = None

        start = self.shown_words
        end = min(start + self.PAGE_SIZE, len(self.pending_words))

        for item in self.pending_words[start:end]:
            self.results.add_widget(
                WordCard(item, self.open_word)
            )

        self.shown_words = end
        left = len(self.pending_words) - end

        if left > 0:

            self.more_button = GoldButton(
                text="نمایش بیشتر (" + fa_num(left) + " واژه‌ی دیگر)",
                size_hint_y=None,
                height=dp(50)
            )

            self.more_button.bind(on_release=self.load_more_words)
            self.results.add_widget(self.more_button)

    # ---------- جست‌وجو ----------

    def on_search(self, _instance, value):

        event = getattr(self, "_search_event", None)

        if event is not None:
            event.cancel()

        self._search_event = Clock.schedule_once(
            lambda _dt: self.update_words(),
            0.3
        )

    # ---------- نمایش معنی ----------

    def open_word(self, item):
        WordDetail(item).open()

    # ---------- آمار آزمون ----------

    def load_stats(self):

        self.exam_count = 0
        self.best_percent = 0
        self.store = None

        try:
            self.store = JsonStore(
                os.path.join(self.user_data_dir, "stats.json")
            )

            if self.store.exists("stats"):
                data = self.store.get("stats")
                self.exam_count = int(data.get("exams", 0))
                self.best_percent = int(data.get("best", 0))

        except Exception:
            self.store = None

    def save_stats(self):

        try:
            if self.store is not None:
                self.store.put(
                    "stats",
                    exams=self.exam_count,
                    best=self.best_percent
                )
        except Exception:
            pass

    # ---------- انتخاب درس (آزمون / تمرین) ----------

    def show_picker(self, mode):

        exam = (mode == "exam")

        self.set_nav("quiz" if exam else "practice")
        self.clear_page()

        self.page.add_widget(self.section_title(
            "آزمون" if exam else "تمرین",
            "درس مورد نظر را انتخاب کن"
        ))

        self.page.add_widget(AppLabel(
            text=(
                "معنی هر واژه را از بین چهار گزینه انتخاب کن."
                if exam else
                "کارت‌ها را مرور کن؛ کارتی که بلد نبودی دوباره می‌آید."
            ),
            color=MUTED,
            font_size=sp(11),
            size_hint_y=None,
            height=dp(36)
        ))

        if exam and self.best_percent:
            self.page.add_widget(AppLabel(
                text="بهترین نتیجه‌ی تو: " + fa_num(self.best_percent) + " درصد",
                color=GOLD,
                font_size=sp(12),
                size_hint_y=None,
                height=dp(26)
            ))

        starter = self.start_exam if exam else self.start_practice

        all_btn = GoldButton(
            text="همه درس‌ها",
            size_hint_y=None,
            height=dp(54)
        )

        all_btn.bind(on_release=lambda *_: starter(None))
        self.page.add_widget(all_btn)

        grid = GridLayout(
            cols=3,
            size_hint_y=None,
            spacing=dp(9),
            row_default_height=dp(52),
            row_force_default=True
        )

        grid.bind(minimum_height=grid.setter("height"))

        for lesson in self.manager.lessons:

            btn = ChipButton("درس " + fa_num(lesson))

            btn.bind(
                on_release=lambda _b, l=lesson: starter(l)
            )

            grid.add_widget(btn)

        self.page.add_widget(grid)

    def lesson_label(self, lesson):
        return "همه درس‌ها" if lesson is None else "درس " + fa_num(lesson)

    # ---------- تمرین (کارت مرور) ----------

    def start_practice(self, lesson):

        cards = [
            w for w in self.all_words
            if lesson is None or w["lesson"] == lesson
        ]

        random.shuffle(cards)

        self.practice = {
            "cards": cards,
            "index": 0,
            "lesson": lesson,
            "again": 0,
        }

        self.show_flashcard()

    def show_flashcard(self):

        p = self.practice

        self.set_nav("practice")
        self.clear_page()

        if p["index"] >= len(p["cards"]):
            self.show_practice_result()
            return

        item = p["cards"][p["index"]]
        remaining = len(p["cards"]) - p["index"]

        self.page.add_widget(self.section_title(
            "تمرین  |  " + self.lesson_label(p["lesson"]),
            "باقی‌مانده: " + fa_num(remaining) + " کارت"
        ))

        card = PremiumCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(250),
            padding=dp(16),
            spacing=dp(8),
            radius=dp(26),
            panel_color=(0.035, 0.065, 0.125, 1)
        )

        card.add_widget(AppLabel(
            text=item["word"],
            color=GOLD_LIGHT,
            font_size=sp(34),
            halign="center"
        ))

        meaning = AppLabel(
            text=item["meaning"],
            color=WHITE,
            font_size=sp(19),
            halign="center",
            opacity=0
        )

        card.add_widget(meaning)
        self.page.add_widget(card)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(54),
            spacing=dp(10)
        )

        show_btn = GoldButton(text="نمایش معنی")

        def reveal(*_):
            meaning.opacity = 1
            buttons.clear_widgets()

            again_btn = ChipButton("دوباره می‌خوانم", state="wrong")
            known_btn = ChipButton("بلد بودم", state="correct")

            again_btn.bind(on_release=lambda *_: self.practice_next(False))
            known_btn.bind(on_release=lambda *_: self.practice_next(True))

            buttons.add_widget(again_btn)
            buttons.add_widget(known_btn)

        show_btn.bind(on_release=reveal)
        buttons.add_widget(show_btn)
        self.page.add_widget(buttons)

    def practice_next(self, known):

        p = self.practice
        item = p["cards"][p["index"]]

        if not known:
            p["cards"].append(item)
            p["again"] += 1

        p["index"] += 1
        self.show_flashcard()

    def show_practice_result(self):

        p = self.practice

        self.page.add_widget(self.section_title(
            "تمرین تمام شد",
            self.lesson_label(p["lesson"])
        ))

        panel = PremiumCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=dp(16),
            spacing=dp(6),
            radius=dp(24),
            panel_color=(0.035, 0.065, 0.125, 1)
        )

        panel.add_widget(AppLabel(
            text="آفرین! همه‌ی کارت‌ها را مرور کردی.",
            color=GOLD_LIGHT,
            font_size=sp(17),
            halign="center"
        ))

        panel.add_widget(AppLabel(
            text="تعداد تکرارها: " + fa_num(p["again"]),
            color=MUTED,
            font_size=sp(12),
            halign="center"
        ))

        self.page.add_widget(panel)

        again = GoldButton(
            text="تمرین دوباره",
            size_hint_y=None,
            height=dp(52)
        )

        again.bind(on_release=lambda *_: self.start_practice(p["lesson"]))
        self.page.add_widget(again)

        other = ChipButton(
            "انتخاب درس دیگر",
            size_hint_y=None,
            height=dp(52)
        )

        other.bind(on_release=lambda *_: self.show_picker("practice"))
        self.page.add_widget(other)

    # ---------- آزمون ----------

    def start_exam(self, lesson):

        count = 15 if lesson is None else 10

        self.exam = {
            "lesson": lesson,
            "questions": build_questions(self.all_words, lesson, count),
            "index": 0,
            "score": 0,
            "wrong": [],
            "answered": False,
        }

        self.show_question()

    def show_question(self):

        ex = self.exam
        q = ex["questions"][ex["index"]]
        total = len(ex["questions"])
        last = (ex["index"] == total - 1)

        self.set_nav("quiz")
        self.clear_page()

        self.page.add_widget(self.section_title(
            "آزمون  |  " + self.lesson_label(ex["lesson"]),
            "سؤال " + fa_num(ex["index"] + 1) + " از " + fa_num(total)
            + "   |   امتیاز: " + fa_num(ex["score"])
        ))

        qcard = PremiumCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=dp(14),
            spacing=dp(4),
            radius=dp(24),
            panel_color=(0.035, 0.065, 0.125, 1)
        )

        qcard.add_widget(AppLabel(
            text="معنی این واژه چیست؟",
            color=MUTED,
            font_size=sp(12),
            halign="center",
            size_hint_y=None,
            height=dp(24)
        ))

        qcard.add_widget(AppLabel(
            text=q["word"],
            color=GOLD_LIGHT,
            font_size=sp(32),
            halign="center"
        ))

        self.page.add_widget(qcard)

        self.option_buttons = []

        for i, option in enumerate(q["options"]):

            btn = ChipButton(
                option,
                size_hint_y=None,
                height=dp(58)
            )

            btn.bind(on_release=lambda _b, i=i: self.answer(i))

            self.page.add_widget(btn)
            self.option_buttons.append(btn)

        self.next_btn = GoldButton(
            text="مشاهده نتیجه" if last else "سؤال بعدی",
            size_hint_y=None,
            height=dp(52),
            opacity=0,
            disabled=True
        )

        self.next_btn.bind(on_release=lambda *_: self.next_question())
        self.page.add_widget(self.next_btn)

    def answer(self, index):

        ex = self.exam

        if ex["answered"]:
            return

        ex["answered"] = True

        q = ex["questions"][ex["index"]]
        chosen = q["options"][index]

        if chosen == q["answer"]:
            ex["score"] += 1
        else:
            ex["wrong"].append({
                "word": q["word"],
                "answer": q["answer"],
                "chosen": chosen,
            })

        for i, btn in enumerate(self.option_buttons):

            if q["options"][i] == q["answer"]:
                btn.set_state("correct")
            elif i == index:
                btn.set_state("wrong")

        self.next_btn.opacity = 1
        self.next_btn.disabled = False

    def next_question(self):

        ex = self.exam
        ex["index"] += 1
        ex["answered"] = False

        if ex["index"] >= len(ex["questions"]):
            self.finish_exam()
        else:
            self.show_question()

    def finish_exam(self):

        ex = self.exam
        total = len(ex["questions"])
        score = ex["score"]
        percent = round(score * 100 / total) if total else 0

        self.exam_count += 1
        self.best_percent = max(self.best_percent, percent)
        self.save_stats()

        self.set_nav("quiz")
        self.clear_page()

        self.page.add_widget(self.section_title(
            "نتیجه‌ی آزمون",
            self.lesson_label(ex["lesson"])
        ))

        if percent >= 90:
            message = "عالی بود!"
        elif percent >= 70:
            message = "آفرین، ادامه بده!"
        elif percent >= 50:
            message = "خوب است، کمی بیشتر مرور کن."
        else:
            message = "بیشتر تمرین کن، می‌توانی!"

        panel = PremiumCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(170),
            padding=dp(16),
            spacing=dp(4),
            radius=dp(26),
            panel_color=(0.035, 0.065, 0.125, 1)
        )

        panel.add_widget(AppLabel(
            text=fa_num(score) + " از " + fa_num(total),
            color=GOLD_LIGHT,
            font_size=sp(34),
            halign="center"
        ))

        panel.add_widget(AppLabel(
            text=fa_num(percent) + " درصد",
            color=WHITE,
            font_size=sp(16),
            halign="center"
        ))

        panel.add_widget(AppLabel(
            text=message,
            color=MUTED,
            font_size=sp(13),
            halign="center"
        ))

        self.page.add_widget(panel)

        again = GoldButton(
            text="آزمون دوباره",
            size_hint_y=None,
            height=dp(52)
        )

        again.bind(on_release=lambda *_: self.start_exam(ex["lesson"]))
        self.page.add_widget(again)

        other = ChipButton(
            "انتخاب درس دیگر",
            size_hint_y=None,
            height=dp(52)
        )

        other.bind(on_release=lambda *_: self.show_picker("exam"))
        self.page.add_widget(other)

        if ex["wrong"]:

            self.page.add_widget(self.section_title(
                "واژه‌هایی که باید مرور کنی"
            ))

            for item in ex["wrong"]:

                card = PremiumCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(86),
                    padding=[dp(14), dp(8)],
                    spacing=dp(1),
                    radius=dp(18)
                )

                card.add_widget(AppLabel(
                    text=item["word"],
                    color=GOLD_LIGHT,
                    font_size=sp(19)
                ))

                card.add_widget(AppLabel(
                    text="پاسخ درست: " + item["answer"],
                    color=WHITE,
                    font_size=sp(12)
                ))

                card.add_widget(AppLabel(
                    text="پاسخ تو: " + item["chosen"],
                    color=MUTED,
                    font_size=sp(11)
                ))

                self.page.add_widget(card)

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
