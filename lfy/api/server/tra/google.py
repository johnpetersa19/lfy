"""谷歌翻译接口"""
import base64
import random
from gettext import gettext as _

import requests
from requests import ConnectTimeout, RequestException

from lfy.api.server import TIME_OUT, Server
from lfy.api.utils.debug import get_logger


def _get_session():
    """Inicializa uma sessão de requisição"""
    r1 = random.randint(10, 100)
    r2 = random.randint(111111111, 999999999)
    r3 = random.randint(5, 11)
    r4 = base64.b64encode(str(random.random())[2:].encode()).decode()

    session = requests.Session()
    session.headers = {
        'User-Agent': f'GoogleTranslate/6.{r1}.0.06.{r2} (Linux; U; Android {r3}; {r4})'
    }
    return session


class GoogleServer(Server):
    """google翻译"""

    def __init__(self):
        
        lang_key_ns = {
            "zh": 1,      # Chinês
            "en": 3,      # Inglês
            "ja": 4,      # Japonês
            "ko": 5,      # Coreano
            "de": 6,      # Alemão
            "fr": 7,      # Francês
            "it": 8,      # Italiano
            "pt-BR": 9,   # Português (Brasil) 
            "es": 10,     # Espanhol
            "ru": 11,     # Russo
            "ar": 12,     # Árabe
            "hi": 13,     # Hindi
            "bn": 14,     # Bengali
            "pt-PT": 15,  # Português (Portugal)
            "tr": 16,     # Turco
            "vi": 17,     # Vietnamita
            "ur": 18,     # Urdu
            "id": 19,     # Indonésio
            "th": 20,     # Tailandês
            "mr": 21,     # Marathi
            "te": 22,     # Telugu
            "ta": 23,     # Tamil
            "gu": 24,     # Gujarati
            "kn": 25,     # Kannada
            "ml": 26,     # Malayalam
            "pa": 27,     # Punjabi
            "or": 28,     # Odia
            "my": 29,     # Birmanês
            "pl": 30,     # Polonês
            "uk": 31,     # Ucraniano
            "nl": 32,     # Holandês
            "sv": 33,     # Sueco
            "fi": 34,     # Finlandês
            "no": 35,     # Norueguês
            "da": 36,     # Dinamarquês
            "hu": 37,     # Húngaro
            "cs": 38,     # Tcheco
            "ro": 39,     # Romeno
            "el": 40,     # Grego
            "sw": 41,     # Swahili
            "ha": 42,     # Hausa
            "yo": 43,     # Yoruba
            "zu": 44,     # Zulu
            "am": 45,     # Amárico
            "ig": 46,     # Igbo
            "af": 47,     # Afrikaans
            "ca": 48,     # Catalão
            "tl": 49,     # Tagalog
        }
        super().__init__("google", _("google"), lang_key_ns, session=_get_session())
        self.can_translate = True

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto", n=0):
        """翻译

        Args:
            text (str): 待翻译字符
            lang_to (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            lang_from (str, optional): 文本是什么语言. Defaults to "auto".

        Returns:
            str: _description_
        """

        if n > 3:
            raise ValueError(_("something error, try other translate engine?"))

        text = text.replace("#", "")
        url = 'https://translate.google.com/translate_a/t'
        params = {
            'tl': lang_to, 'sl': lang_from, 'ie': 'UTF-8',
            'oe': 'UTF-8', 'client': 'at', 'dj': '1',
            'format': "html", 'v': "1.0"
        }

        try:
            response = self.session.post(url, params=params, data={'q': text}, timeout=TIME_OUT)
        except ConnectTimeout as e0:
            print("google0", n, type(e0), e0)
            get_logger().error(e0)
            return False, _("The connection timed out. Maybe there is a network problem")
        except RequestException as e:
            print("google", n, type(e), e)
            get_logger().error(e)
            return self.translate_text(text, lang_to, lang_from, n + 1)

        s = ""
        for res in response.json():
            s += res[0]

        return True, s
