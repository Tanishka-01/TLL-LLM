# constants.py
"""
Minimal constants file for TTS/STT pipeline
"""

import os

def get_xdg_home(env, default):
    """Get XDG home directory with Flatpak support"""
    # Simple implementation - just return the default path
    base = os.getenv(env) or os.path.expanduser(default)
    return base

# Data and cache directories
data_dir = get_xdg_home("XDG_DATA_HOME", "~/.local/share")
cache_dir = get_xdg_home("XDG_CACHE_HOME", "~/.cache")

# Speech recognition languages
SPEACH_RECOGNITION_LANGUAGES = {
'en': 'English',
    'es': 'Spanish', 
    'nl': 'Dutch',
    'ko': 'Korean',
    'it': 'Italian',
    'de': 'German',
    'th': 'Thai',
    'ru': 'Russian',
    'pt': 'Portuguese',
    'pl': 'Polish',
    'id': 'Indonesian',
    'zh': 'Chinese',
    'sv': 'Swedish',
    'cs': 'Czech',
    'ja': 'Japanese',
    'fr': 'French',
    'ro': 'Romanian',
    'tr': 'Turkish',
    'ca': 'Catalan',
    'hu': 'Hungarian',
    'uk': 'Ukrainian',
    'el': 'Greek',
    'bg': 'Bulgarian',
    'ar': 'Arabic',
    'sr': 'Serbian',
    'mk': 'Macedonian',
    'lv': 'Latvian',
    'sl': 'Slovenian',
    'hi': 'Hindi',
    'gl': 'Galician',
    'da': 'Danish',
    'ur': 'Urdu',
    'sk': 'Slovak',
    'he': 'Hebrew',
    'fi': 'Finnish',
    'az': 'Azerbaijani',
    'lt': 'Lithuanian',
    'et': 'Estonian',
    'nn': 'Norwegian Nynorsk',
    'cy': 'Welsh',
    'pa': 'Punjabi',
    'af': 'Afrikaans',
    'fa': 'Persian',
    'eu': 'Basque',
    'vi': 'Vietnamese',
    'bn': 'Bengali',
    'ne': 'Nepali',
    'mr': 'Marathi',
    'be': 'Belarusian',
    'kk': 'Kazakh',
    'hy': 'Armenian',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'sq': 'Albanian'
}

# TTS voices (simplified)
TTS_VOICES = {
    '🇺🇸 Heart': 'af_heart',
    '🇺🇸 Alloy': 'af_alloy',
    '🇺🇸 Aoede': 'af_aoede',
    '🇺🇸 Bella': 'af_bella',
    '🇺🇸 Jessica': 'af_jessica',
    '🇺🇸 Kore': 'af_kore',
    '🇺🇸 Nicole': 'af_nicole',
    '🇺🇸 Nova': 'af_nova',
    '🇺🇸 River': 'af_river',
    '🇺🇸 Sarah': 'af_sarah',
    '🇺🇸 Sky': 'af_sky',
    '🇺🇸 Adam': 'am_adam',
    '🇺🇸 Echo': 'am_echo',
    '🇺🇸 Eric': 'am_eric',
    '🇺🇸 Fenrir': 'am_fenrir',
    '🇺🇸 Liam': 'am_liam',
    '🇺🇸 Michael': 'am_michael',
    '🇺🇸 Onyx': 'am_onyx',
    '🇺🇸 Puck': 'am_puck',
    '🇺🇸 Santa': 'am_santa',
    '🇬🇧 Alice': 'bf_alice',
    '🇬🇧 Emma': 'bf_emma',
    '🇬🇧 Isabella': 'bf_isabella',
    '🇬🇧 Lily': 'bf_lily',
    '🇬🇧 Daniel': 'bm_daniel',
    '🇬🇧 Fable': 'bm_fable',
    '🇬🇧 George': 'bm_george',
    '🇬🇧 Lewis': 'bm_lewis',
    #'🇯🇵 Alpha': 'jf_alpha',
    #'🇯🇵 Gongitsune': 'jf_gongitsune',
    #'🇯🇵 Nezumi': 'jf_nezumi',
    #'🇯🇵 Tebukuro': 'jf_tebukuro',
    #'🇯🇵 Kumo': 'jm_kumo',
    #'🇨🇳 Xiaobei': 'zf_xiaobei',
    #'🇨🇳 Xiaoni': 'zf_xiaoni',
    #'🇨🇳 Xiaoxiao': 'zf_xiaoxiao',
    #'🇨🇳 Xiaoyi': 'zf_xiaoyi',
    #'🇨🇳 Yunjian': 'zm_yunjian',
    #'🇨🇳 Yunxi': 'zm_yunxi',
    #'🇨🇳 Yunxia': 'zm_yunxia',
    #'🇨🇳 Yunyang': 'zm_yunyang',
    '🇪🇸 Dora': 'ef_dora',
    '🇪🇸 Alex': 'em_alex',
    '🇪🇸 Santa': 'em_santa',
    '🇫🇷 Siwis': 'ff_siwis',
    '🇮🇳 Alpha': 'hf_alpha',
    '🇮🇳 Beta': 'hf_beta',
    '🇮🇳 Omega': 'hm_omega',
    '🇮🇳 Psi': 'hm_psi',
    '🇮🇹 Sara': 'if_sara',
    '🇮🇹 Nicola': 'im_nicola',
    '🇵🇹 Dora': 'pf_dora',
    '🇵🇹 Alex': 'pm_alex',
    '🇵🇹 Santa': 'pm_santa'
}

# STT models
STT_MODELS = {
    'tiny': '~75 MB',
    'base': '~151 MB',
    'small': '~488 MB',
    'medium': '~1.5 GB',
    'large': '~2.9 GB'
}
