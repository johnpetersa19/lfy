"""谷歌翻译接口"""
import random
import re
from gettext import gettext as _
from urllib.parse import urlparse

import requests
from requests import RequestException

from lfy.api.server import TIME_OUT, Server
from lfy.api.utils.debug import get_logger


def _init_session():
    session = requests.Session()
    url = 'https://www.bing.com/translator'
    headers = {
        'User-Agent': '',
        'Referer': url
    }
    session.headers.update(headers)
    response = session.get(url, timeout=TIME_OUT)
    session.headers.update({'my_host': urlparse(response.url).hostname})

    content = response.text

    params_pattern = re.compile(
        r'params_AbusePreventionHelper\s*=\s*(\[.*?]);', re.DOTALL)
    match = params_pattern.search(content)
    if match:
        params = match.group(1)
        key, token, _time = [p.strip('"').replace('[', '') \
                             .replace(']', '') for p in params.split(',')]
        session.headers.update({'key': key, 'token': token})
    match = re.search(r'IG:"(\w+)"', content)

    if match:
        ig_value = match.group(1)
        session.headers.update({'IG': ig_value})

    return session


class BingServer(Server):
    """bing翻译，无需apikey"""

    def __init__(self):
       
        lang_key_ns = {
            "zh-Hans": 1,   # Chinês simplificado
            "en": 3,        # Inglês
            "ja": 4,        # Japonês
            "ko": 5,        # Coreano
            "de": 6,        # Alemão
            "fr": 7,        # Francês
            "it": 8,        # Italiano
            "pt-BR": 9,     # Português (Brasil)
            "es": 10,       # Espanhol
            "ru": 11,       # Russo
            "ar": 12,       # Árabe
            "hi": 13,       # Hindi
            "bn": 14,       # Bengali
            "pt-PT": 15,    # Português (Portugal)
            "tr": 16,       # Turco
            "vi": 17,       # Vietnamita
            "ur": 18,       # Urdu
            "id": 19,       # Indonésio
            "th": 20,       # Tailandês
            "mr": 21,       # Marathi
            "te": 22,       # Telugu
            "ta": 23,       # Tamil
            "gu": 24,       # Gujarati
            "kn": 25,       # Kannada
            "ml": 26,       # Malayalam
            "pa": 27,       # Punjabi
            "or": 28,       # Odia
            "my": 29,       # Birmanês
            "pl": 30,       # Polonês
            "uk": 31,       # Ucraniano
            "nl": 32,       # Holandês
            "sv": 33,       # Sueco
            "fi": 34,       # Finlandês
            "no": 35,       # Norueguês
            "da": 36,       # Dinamarquês
            "hu": 37,       # Húngaro
            "cs": 38,       # Tcheco
            "ro": 39,       # Romeno
            "el": 40,       # Grego
            "sw": 41,       # Swahili
            "ha": 42,       # Hausa
            "yo": 43,       # Yoruba
            "zu": 44,       # Zulu
            "am": 45,       # Amárico
            "ig": 46,       # Igbo
            "af": 47,       # Afrikaans
            "ca": 48,       # Catalão
            "tl": 49,       # Tagalog
        }
        super().__init__("bing", _("bing"), lang_key_ns)
        self.can_translate = True

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto", n=0):
        """翻译

        Args:
            text (str): 待翻译字符
            lang_to (str, optional): 翻译成什么语言. Defaults to "zh-cn".
            lang_from (str, optional): 文本是什么语言. Defaults to "auto".
            n (int, optional): 刷新了几次. Defaults to "auto".

        Returns:
            str: _description_
        """

        if n > 5:
            raise ValueError(_("something error, try other translate engine?"))

        hs = self.session.headers
        if "IG" not in hs:
            try:
                self.session = _init_session()
                hs = self.session.headers
                print(hs["my_host"])
            except RequestException as e:
                get_logger().error(e)
                print("bing-session", n, type(e), e)
                return self.translate_text(text, lang_to, lang_from, n + 1)

        # 自动重定向的新url，注意辨别
        host = hs["my_host"]
        if "my_iid" not in hs:
            iid = f"translator.{random.randint(5019, 5026)}.{random.randint(1, 3)}"
            self.session.headers.update({'my_iid': iid})
            hs = self.session.headers
        url = f'https://{host}/ttranslatev3?isVertical=1&&IG={hs["IG"]}&IID={hs["my_iid"]}'

        data = {'': '', 'text': text, 'to': lang_to,
                'token': hs['token'], 'key': hs['key'], "fromLang": lang_from}
        if "auto" == lang_from:
            data['fromLang'] = "auto-detect"
            data['tryFetchingGenderDebiasedTranslations'] = True

        try:
            response = self.session.post(url, data=data, timeout=TIME_OUT)
        except RequestException as e:
            get_logger().error(e)
            print("bing-post", n, type(e), e)
            return self.translate_text(text, lang_to, lang_from, n + 1)

        # 没有代理时，中国区出现这个
        if len(response.text.strip()) == 0:
            return self.translate_text(text, lang_to, lang_from, n + 1)

        res = response.json()

        if isinstance(res, list):
            return True, res[0]["translations"][0]["text"]

        if isinstance(res, dict):
            if 'ShowCaptcha' in res.keys():
                self.session = _init_session()
                print("bing-ShowCaptcha", n)
                return self.translate_text(text, lang_to, lang_from, n + 1)

            if 'statusCode' in res.keys() and res['statusCode'] == 400:
                res['errorMessage'] = _('1000 characters limit! You send {len_text} characters.').format(len_text=len(text))
                return False, res["errorMessage"]

        return False, str(res)
