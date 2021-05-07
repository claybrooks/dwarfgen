from .lang_generators import cpp

KNOWN_GENERATORS = {
    'cpp': cpp
}

def register_generator(lang, module):
    KNOWN_GENERATORS[lang] = module

def get_ext(lang):
    return KNOWN_GENERATORS[lang].get_ext()

def generate(lang, jidl):
    return KNOWN_GENERATORS[lang].generate(jidl)
