"""Google Translate API Interface"""
import base64
import random
from gettext import gettext as _

import requests
from requests import ConnectTimeout, RequestException

from lfy.api.server import TIME_OUT, Server
from lfy.api.utils.debug import get_logger


def _get_session():
    """Initialize a request session"""
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
    """Google Translate implementation"""

    def __init__(self):
        # Language mapping dictionary with standardized codes
        self.lang_mapping = {
            "zh": "zh-CN",      # Chinese
            "zh-cn": "zh-CN",   # Chinese (Simplified)
            "zh-tw": "zh-TW",   # Chinese (Traditional)
            "en": "en",         # English
            "ja": "ja",         # Japanese
            "ko": "ko",         # Korean
            "de": "de",         # German
            "fr": "fr",         # French
            "it": "it",         # Italian
            "pt-BR": "pt",      # Portuguese (Brazil)
            "pt-br": "pt",      # Portuguese (Brazil) lowercase
            "pt-PT": "pt",      # Portuguese (Portugal)
            "pt-pt": "pt",      # Portuguese (Portugal) lowercase
            "es": "es",         # Spanish
            "ru": "ru",         # Russian
            "ar": "ar",         # Arabic
            "hi": "hi",         # Hindi
            "bn": "bn",         # Bengali
            "tr": "tr",         # Turkish
            "vi": "vi",         # Vietnamese
            "ur": "ur",         # Urdu
            "id": "id",         # Indonesian
            "th": "th",         # Thai
            "mr": "mr",         # Marathi
            "te": "te",         # Telugu
            "ta": "ta",         # Tamil
            "gu": "gu",         # Gujarati
            "kn": "kn",         # Kannada
            "ml": "ml",         # Malayalam
            "pa": "pa",         # Punjabi
            "or": "or",         # Odia
            "my": "my",         # Burmese
            "pl": "pl",         # Polish
            "uk": "uk",         # Ukrainian
            "nl": "nl",         # Dutch
            "sv": "sv",         # Swedish
            "fi": "fi",         # Finnish
            "no": "no",         # Norwegian
            "da": "da",         # Danish
            "hu": "hu",         # Hungarian
            "cs": "cs",         # Czech
            "ro": "ro",         # Romanian
            "el": "el",         # Greek
            "sw": "sw",         # Swahili
            "ha": "ha",         # Hausa
            "yo": "yo",         # Yoruba
            "zu": "zu",         # Zulu
            "am": "am",         # Amharic
            "ig": "ig",         # Igbo
            "af": "af",         # Afrikaans
            "ca": "ca",         # Catalan
            "tl": "tl",         # Tagalog
        }
        
        lang_key_ns = {
            "zh": 1,      # Chinese
            "en": 3,      # English
            "ja": 4,      # Japanese
            "ko": 5,      # Korean
            "de": 6,      # German
            "fr": 7,      # French
            "it": 8,      # Italian
            "pt-BR": 9,   # Portuguese (Brazil)
            "es": 10,     # Spanish
            "ru": 11,     # Russian
            "ar": 12,     # Arabic
            "hi": 13,     # Hindi
            "bn": 14,     # Bengali
            "pt-PT": 15,  # Portuguese (Portugal)
            "tr": 16,     # Turkish
            "vi": 17,     # Vietnamese
            "ur": 18,     # Urdu
            "id": 19,     # Indonesian
            "th": 20,     # Thai
            "mr": 21,     # Marathi
            "te": 22,     # Telugu
            "ta": 23,     # Tamil
            "gu": 24,     # Gujarati
            "kn": 25,     # Kannada
            "ml": 26,     # Malayalam
            "pa": 27,     # Punjabi
            "or": 28,     # Odia
            "my": 29,     # Burmese
            "pl": 30,     # Polish
            "uk": 31,     # Ukrainian
            "nl": 32,     # Dutch
            "sv": 33,     # Swedish
            "fi": 34,     # Finnish
            "no": 35,     # Norwegian
            "da": 36,     # Danish
            "hu": 37,     # Hungarian
            "cs": 38,     # Czech
            "ro": 39,     # Romanian
            "el": 40,     # Greek
            "sw": 41,     # Swahili
            "ha": 42,     # Hausa
            "yo": 43,     # Yoruba
            "zu": 44,     # Zulu
            "am": 45,     # Amharic
            "ig": 46,     # Igbo
            "af": 47,     # Afrikaans
            "ca": 48,     # Catalan
            "tl": 49,     # Tagalog
        }
        super().__init__("google", _("google"), lang_key_ns, session=_get_session())
        self.can_translate = True

    def _normalize_lang_code(self, lang_code):
        """Normalize language code to Google Translate format"""
        lang_code = lang_code.lower()
        return self.lang_mapping.get(lang_code, lang_code)

    def translate_text(self, text, lang_to="zh-cn", lang_from="auto", n=0):
        """Translate text using Google Translate API

        Args:
            text (str): Text to translate
            lang_to (str, optional): Target language. Defaults to "zh-cn".
            lang_from (str, optional): Source language. Defaults to "auto".
            n (int, optional): Retry counter. Defaults to 0.

        Returns:
            tuple: (success (bool), translated_text (str))
        """
        if n > 3:
            raise ValueError(_("something error, try other translate engine?"))

        # Normalize language codes
        lang_to = self._normalize_lang_code(lang_to)
        lang_from = self._normalize_lang_code(lang_from) if lang_from != "auto" else "auto"

        # Remove # as it can cause issues with the API
        text = text.replace("#", "")
        
        url = 'https://translate.google.com/translate_a/t'
        params = {
            'tl': lang_to,
            'sl': lang_from,
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'client': 'at',
            'dj': '1',
            'format': "html",
            'v': "1.0"
        }

        try:
            response = self.session.post(url, params=params, data={'q': text}, timeout=TIME_OUT)
            response.encoding = 'utf-8'  # Explicitly set response encoding
            
            # Debug log for response analysis
            get_logger().debug(f"Google Translate response: {response.text}")
            
            json_response = response.json()
            
            # Improved response handling with specific Portuguese character support
            translated_text = ""
            if isinstance(json_response, list):
                # Handle array response format
                for segment in json_response:
                    if isinstance(segment, list) and segment and isinstance(segment[0], str):
                        translated_text += segment[0]
                    elif isinstance(segment, dict) and 'trans' in segment:
                        translated_text += segment['trans']
            elif isinstance(json_response, dict):
                # Handle dictionary response format
                if 'sentences' in json_response:
                    translated_text = ''.join(
                        sentence.get('trans', '')
                        for sentence in json_response['sentences']
                        if isinstance(sentence, dict)
                    )
            
            # HTML entities dictionary
            html_entities = {
                # Quotes and apostrophes
                '&quot;': '"',
                '&#39;': "'",
                '&ldquo;': '"',
                '&rdquo;': '"',
                '&lsquo;': ''',
                '&rsquo;': ''',
                
                # Lowercase accented characters
                '&aacute;': 'á',
                '&eacute;': 'é',
                '&iacute;': 'í',
                '&oacute;': 'ó',
                '&uacute;': 'ú',
                '&atilde;': 'ã',
                '&otilde;': 'õ',
                '&acirc;': 'â',
                '&ecirc;': 'ê',
                '&icirc;': 'î',
                '&ocirc;': 'ô',
                '&ucirc;': 'û',
                '&ccedil;': 'ç',
                
                # Uppercase accented characters
                '&Aacute;': 'Á',
                '&Eacute;': 'É',
                '&Iacute;': 'Í',
                '&Oacute;': 'Ó',
                '&Uacute;': 'Ú',
                '&Atilde;': 'Ã',
                '&Otilde;': 'Õ',
                '&Acirc;': 'Â',
                '&Ecirc;': 'Ê',
                '&Icirc;': 'Î',
                '&Ocirc;': 'Ô',
                '&Ucirc;': 'Û',
                '&Ccedil;': 'Ç',
                
                # Special symbols
                '&amp;': '&',
                '&lt;': '<',
                '&gt;': '>',
                '&deg;': '°',
                '&plusmn;': '±',
                '&times;': '×',
                '&divide;': '÷',
                '&micro;': 'µ',
                '&para;': '¶',
                '&middot;': '·',
                '&bull;': '•',
                '&hellip;': '…',
                '&prime;': '′',
                '&Prime;': '″',
                '&sect;': '§',
                '&copy;': '©',
                '&reg;': '®',
                '&trade;': '™',
                '&euro;': '€',
                '&pound;': '£',
                '&cent;': '¢',
                '&yen;': '¥',
                
                # Mathematical and other symbols
                '&sum;': '∑',
                '&prod;': '∏',
                '&radic;': '√',
                '&infin;': '∞',
                '&asymp;': '≈',
                '&ne;': '≠',
                '&le;': '≤',
                '&ge;': '≥',
                '&permil;': '‰',
                
                # Spaces and dashes
                '&nbsp;': ' ',
                '&ensp;': ' ',
                '&emsp;': ' ',
                '&ndash;': '–',
                '&mdash;': '—',
                
                # ASCII characters
                '&#33;': '!',
                '&#35;': '#',
                '&#36;': '$',
                '&#37;': '%',
                '&#38;': '&',
                '&#40;': '(',
                '&#41;': ')',
                '&#42;': '*',
                '&#43;': '+',
                '&#44;': ',',
                '&#45;': '-',
                '&#46;': '.',
                '&#47;': '/',
                '&#58;': ':',
                '&#59;': ';',
                '&#60;': '<',
                '&#61;': '=',
                '&#62;': '>',
                '&#63;': '?',
                '&#64;': '@',
                '&#91;': '[',
                '&#92;': '\\',
                '&#93;': ']',
                '&#94;': '^',
                '&#95;': '_',
                '&#96;': '`',
                '&#123;': '{',
                '&#124;': '|',
                '&#125;': '}',
                '&#126;': '~',
                '&#161;': '¡',
                '&#191;': '¿',
                
                # Other special symbols
                '&dagger;': '†',
                '&Dagger;': '‡',
                '&loz;': '◊',
                '&spades;': '♠',
                '&clubs;': '♣',
                '&hearts;': '♥',
                '&diams;': '♦'
            }
            
            def clean_special_chars(text):
                """Clean and preserve special characters in text"""
                # Replace HTML entities
                for entity, char in html_entities.items():
                    text = text.replace(entity, char)
                
                # Ensure proper encoding of special characters
                text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                
                # Fix common encodings issues
                text = text.replace('\\u0022', '"')
                text = text.replace('\\u0027', "'")
                text = text.replace('\\u0026', "&")
                text = text.replace('\\u003c', "<")
                text = text.replace('\\u003e', ">")
                
                # Preserve ASCII special characters
                special_chars = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¡¿'
                for char in special_chars:
                    text = text.replace(f'\\u{ord(char):04x}', char)
                
                return text
            
            # Apply the cleaning function
            translated_text = clean_special_chars(translated_text)
            
            return True, translated_text

        except ConnectTimeout as e0:
            get_logger().error(f"Google Translate timeout error: {e0}")
            return False, _("The connection timed out. Maybe there is a network problem")
            
        except RequestException as e:
            get_logger().error(f"Google Translate request error: {e}")
            return self.translate_text(text, lang_to, lang_from, n + 1)
        
        except (ValueError, KeyError) as e:
            get_logger().error(f"Google Translate parsing error: {e}")
            return False, _("Error processing translation response")
