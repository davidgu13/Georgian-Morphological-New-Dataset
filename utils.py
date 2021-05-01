__author__ = "David Guriel"
import sys
import string
import os
from copy import deepcopy

misc = ['', ' ', '\xa0'] + list(string.punctuation + string.ascii_lowercase + string.ascii_uppercase + string.digits)
kat2eng = dict(zip(['ა', 'ბ', 'გ', 'დ', 'ე', 'ვ', 'ზ', 'თ', 'ი', 'კ', 'ლ', 'მ', 'ნ', 'ო', 'პ', 'ჟ', 'რ', 'ს', 'ტ', 'უ', 'ფ', 'ქ', 'ღ', 'ყ', 'შ', 'ჩ', 'ც', 'ძ', 'წ', 'ჭ', 'ხ', 'ჯ', 'ჰ']+misc,
                   ['a', 'b', 'g', 'd', 'e', 'v', 'z', 't', 'i', "k'", 'l', 'm', 'n', 'o', "p'", 'ž', 'r', 's', "t'", 'u', 'p', 'k', 'ġ', "q'", 'š', 'č', 'c', 'j', "c'", "č'", 'x', 'ǰ', 'h']+misc))

eng2kat = dict((v,k) for k,v in kat2eng.items()) # swap keys & values.

vowels = ['ა', 'ე', 'ი', 'ო', 'უ']
def vowel_in_word(word): return any(v in word for v in vowels)

screeves_formats = dict(zip(range(1,12),['IND;PRS','IND;IPFV','SBJV;PRS','IND;FUT','COND','SBJV;FUT','IND;PST;PFV','OPT','IND;PRF','IND;PST;PRF','SBJV;PRF'])) # as shown in the Unimorph data.
SCREEVES_NAMES = ['Present Indicative', 'Imperfect Indicative', 'Present Subjunctive', 'Future Indicative', 'Conditional', 'Future Subjunctive',
                  'Aorist Indicative', 'Aorist Subjunctive',
                  'Perfect Indicative', 'Pluperfect', 'Perfect Subjunctive']

def transliterate_kat2eng(kat_word): return ''.join([kat2eng[c] for c in list(kat_word)])
def transliterate_eng2kat(eng_word): # requires a bit more attention, due to apostrophe (') issues.
    kat_chars_list = list()
    for i in range(len(eng_word)):
        if eng_word[i]=="'":
            continue
        elif eng_word[i] not in eng2kat: # e.g. "q'"
            kat_char = eng2kat[eng_word[i]+"'"]
        else:
            if i+1<len(eng_word):
                if eng_word[i+1]=="'":
                    kat_char = eng2kat[eng_word[i]+"'"]
                else:
                    kat_char = eng2kat[eng_word[i]]
            else:
                kat_char = eng2kat[eng_word[i]]
        kat_chars_list.append(kat_char)
    return ''.join(kat_chars_list)

def format_pronouns(key): return "{};{}".format(key[2],str.upper(key[:2]))

def zip_paas(vals): return dict(zip(['pref','suff'], vals))
def zip_pronouns_paas(vals): return dict(zip(['sg1','sg2','sg3','pl1','pl2','pl3'],[zip_paas(paa) for paa in vals]))
def zip_pronouns(vals): return dict(zip(['sg1', 'sg2', 'sg3', 'pl1', 'pl2', 'pl3'], vals))


def zip_ext_pronouns_paas(vals, mode='paas'):
    """
    returns an extended dictionary of the Pronominal Aggreement Affixes
    :param vals: a list of 6 lists of lengths (6,4,4,4,4,6), each with pairs of prefix and suffix markers
    :param mode: whether to use zip_paas or just zip_pronouns. Accepted values are 'paas' and 'prons'
    :return: a dictionary that wraps all that. Accessing that is with 2 indices (or 3 for 'pref'/'suff'). Note: 1st index marks the object!
    """
    d={}
    if mode=='paas':
        f1 = zip_paas
        f2 = zip_pronouns_paas
    elif mode=='prons':
        f1 = lambda x: x
        f2 = zip_pronouns
    else:
        raise Exception("Impossible")
    for k,v in zip(['sg1', 'sg2', 'sg3', 'pl1', 'pl2', 'pl3'], vals):
        if k in {'sg1', 'pl1'}: # 1sg object
            d[k] = dict(zip(['sg2', 'sg3', 'pl2', 'pl3'], [f1(paa) for paa in v]))
        elif k in {'sg2', 'pl2'}: # 2sg object
            d[k] = dict(zip(['sg1', 'sg3', 'pl1', 'pl3'], [f1(paa) for paa in v]))
        else: # if object==3sg/3pl
            d[k] = f2(v)
    return d


SUBJECTIVE_VERSION = ['ი', 'ი', 'უ', 'ი', 'ი', 'უ']

def set_screeve_markers(vals, mode:str):
    """
    returns an extended dictionary of markers per Screeve.
    :param vals: a list. Can be of type [str], [[str]] or dict()
    :param mode: 'subj' - varies per subject (standard), 'obj' - varies per object (mostly in Inversion), 'manual' - returns the list as is
    :return: application of zip_pronouns, for simple execution in the main forms generating loop
    """
    if mode=='subj':
        res = zip_pronouns([zip_pronouns(vals) for _ in range(6)])
    elif mode=='obj':
        markers = []
        for k in range(6):
            markers.append([vals[k]]*6)
        res = zip_pronouns([zip_pronouns(m) for m in markers])
    elif mode=='manual':
        res = vals
    else: raise Exception("Invalid mode!!! Only 'subj', 'obj' and 'manual' are available!")
    return res


def get_Transitive_paas():
    screeve1_paas = [[['მ', ''], ['მ', 'ს'], ['მ', 'თ'], ['მ', 'ენ']],
                     [['გ', ''], ['გ', 'ს'], ['გ', 'თ'], ['გ', 'ენ']],
                     [['ვ', ''], ['', ''], ['', 'ს'], ['ვ', 'თ'], ['', 'თ'], ['', 'ენ']],
                     [['გვ', ''], ['გვ', 'ს'], ['გვ', 'თ'], ['გვ', 'ენ']],
                     [['გ', 'თ'], ['გ', 'თ'], ['გ', 'თ'], ['გ', 'ენ']],
                     [['ვ', ''], ['', ''], ['', 'ს'], ['ვ', 'თ'], ['', 'თ'], ['', 'ენ']]]


    screeve2_paas = [[['მ', ''], ['მ', 'ა'], ['მ', 'თ'], ['მ', 'ნენ']],
                     [['გ', ''], ['გ', 'ა'], ['გ', 'თ'], ['გ', 'ნენ']],
                     [['ვ', ''], ['', ''], ['', 'ა'], ['ვ', 'თ'], ['', 'თ'], ['', 'ნენ']],
                     [['გვ', ''], ['გვ', 'ა'], ['გვ', 'თ'], ['გვ', 'ნენ']],
                     [['გ', 'თ'], ['გ', 'ათ'], ['გ', 'თ'], ['გ', 'ნენ']],
                     [['ვ', ''], ['', ''], ['', 'ა'], ['ვ', 'თ'], ['', 'თ'], ['', 'ნენ']]]

    screeve3_paas = deepcopy(screeve1_paas)
    for k in range(6):
        screeve3_paas[k][-1][1] = 'ნენ'


    screeve7_paas = [[           ['მ', ''], ['მ', 'ა'],             ['მ', 'თ'], ['მ', 'ეს']],
                     [['გ', ''],            ['გ', 'ა'], ['გ', 'თ'],             ['გ', 'ეს']],
                     [['ვ', ''], ['', ''],  ['', 'ა'], ['ვ', 'თ'],  ['', 'თ'], ['', 'ეს']],
                     [           ['გვ', ''], ['გვ', 'ა'],            ['გვ', 'თ'], ['გვ', 'ეს']],
                     [['გ', 'თ'],           ['გ', 'ათ'], ['გ', 'თ'],            ['გ', 'ეს']],
                     [['ვ', ''], ['', ''], ['', 'ა'], ['ვ', 'თ'], ['', 'თ'], ['', 'ეს']]]


    # screeve8_paas = deepcopy(screeve1_paas)
    screeve8_paas = [[           ['მ', ''],  ['მ', 'ს'],               ['მ', 'თ'],   ['მ', 'ნ']],
                     [['გ', ''],             ['გ', 'ს'],   ['გ', 'თ'],               ['გ', 'ნ']],
                     [['ვ', ''], ['', ''],   ['', 'ს'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნ']],
                     [           ['გვ', ''], ['გვ', 'ს'],               ['გვ', 'თ'], ['გვ', 'ნ']], # obj = 1pl, subj = 2sg, 3sg, 2pl, 3pl
                     [['გ', 'თ'],           ['გ', 'თ'], ['გ', 'თ'],                 ['გ', 'თ']], # obj = 2pl, subj = 1sg, 3sg, 1pl, 3pl
                     [['ვ', ''], ['', ''],   ['', 'ს'],  ['ვ', 'თ'],   ['', 'თ'],    ['', 'ნ']]]

    # screeve9_paas = deepcopy(screeve1_paas) # totally different from paas1!!! (Inversion)
    screeve9_paas = [[               ['გ', 'ვარ'],  ['ვ', 'ვარ'],              ['გ', 'ვართ'],     ['ვ', 'ვართ']],
                     [['მ', 'ხარ'],                 ['', 'ხარ'],    ['გვ', 'ხარ'],                 ['', 'ხართ']],
                     [['მ', 'ა'],    ['გ', 'ა'],     ['', 'ა'],      ['გვ', 'ა'],  ['გ', 'ათ'],     ['', 'ათ']],
                     [               ['გ', 'ვართ'], ['ვ', 'ვართ'],                ['გ', 'ვართ'], ['ვ', 'ვართ']], # obj = 1pl, subj = 2sg, 3sg, 2pl, 3pl
                     [['მ', 'ხართ'],                ['', 'ხართ'],  ['გვ', 'ხართ'],                ['', 'ხართ']], # obj = 2pl, subj = 1sg, 3sg, 1pl, 3pl
                     [['მ', 'ა'],    ['გ', 'ა'],     ['', 'ა'],      ['გვ', 'ა'],    ['გ', 'ათ'],   ['', 'ათ']]]


    screeve10_paas = [[           ['გ', ''], ['ვ', ''],              ['გ', 'თ'], ['ვ', 'თ']],
                     [['მ', ''],             ['', ''],  ['გვ', ''],              ['', 'თ']],
                     [['მ', 'ა'], ['გ', 'ა'], ['', 'ა'], ['გვ', 'ა'], ['გ', 'ათ'], ['', 'ათ']],
                     [            ['გ', 'თ'], ['ვ', 'თ'],           ['გ', 'თ'], ['ვ', 'თ']], # obj = 1pl, subj = 2sg, 3sg, 2pl, 3pl
                     [['მ', 'თ'],            ['', 'თ'], ['გვ', 'თ'],            ['', 'თ']], # obj = 2pl, subj = 1sg, 3sg, 1pl, 3pl
                     [['მ', 'ა'], ['გ', 'ა'], ['', 'ა'], ['გვ', 'ა'], ['გ', 'ათ'], ['', 'ათ']]]


    screeve11_paas = [[           ['გ', ''], ['ვ', ''],              ['გ', 'თ'], ['ვ', 'თ']],
                     [['მ', ''],             ['', ''],  ['გვ', ''],              ['', 'თ']],
                     [['მ', 'ს'], ['გ', 'ს'], ['', 'ს'], ['გვ', 'ს'], ['გ', 'თ'], ['', 'თ']],
                     [            ['გ', 'თ'], ['ვ', 'თ'],           ['გ', 'თ'], ['ვ', 'თ']], # obj = 1pl, subj = 2sg, 3sg, 2pl, 3pl
                     [['მ', 'თ'],            ['', 'თ'], ['გვ', 'თ'],            ['', 'თ']], # obj = 2pl, subj = 1sg, 3sg, 1pl, 3pl
                     [['მ', 'ს'], ['გ', 'ს'], ['', 'ს'], ['გვ', 'ს'], ['გ', 'თ'], ['', 'თ']]] # only 14 distinct markers - lots of Syncretism!

    return screeve1_paas, screeve2_paas, screeve3_paas, screeve7_paas, screeve8_paas, screeve9_paas, screeve10_paas, screeve11_paas



def get_Intransitive_paas():
    screeve1_paas = [[            ['მ', ''],  ['მ', 'ა'],               ['მ', 'თ'],  ['მ', 'ან']],
                     [['გ', ''],              ['გ', 'ა'],   ['გ', 'თ'],              ['გ', 'ან']],
                     [['ვ', ''],  ['', ''],   ['', 'ა'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ან']],
                     [            ['გვ', ''], ['გვ', 'ა'],               ['გვ', 'თ'], ['გვ', 'ან']],
                     [['გ', 'თ'],             ['გ', 'ათ'], ['გ', 'თ'],              ['გ', 'ან']],
                     [['ვ', ''],  ['', ''],   ['', 'ა'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ან']]]


    screeve2_paas = [[            ['მ', ''],  ['მ', 'ა'],               ['მ', 'თ'],  ['მ', 'ნენ']],
                     [['გ', ''],              ['გ', 'ა'],   ['გ', 'თ'],              ['გ', 'ნენ']],
                     [['ვ', ''],  ['', ''],   ['', 'ა'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნენ']],
                     [            ['გვ', ''], ['გვ', 'ა'],               ['გვ', 'თ'], ['გვ', 'ნენ']],
                     [['გ', 'თ'],             ['გ', 'ათ'], ['გ', 'თ'],              ['გ', 'ნენ']],
                     [['ვ', ''],  ['', ''],   ['', 'ა'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნენ']]]


    screeve3_paas = [[            ['მ', ''],  ['მ', 'ს'],               ['მ', 'თ'],  ['მ', 'ნენ']],
                     [['გ', ''],              ['გ', 'ს'],   ['გ', 'თ'],              ['გ', 'ნენ']],
                     [['ვ', ''],  ['', ''],   ['', 'ს'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნენ']],
                     [            ['გვ', ''], ['გვ', 'ს'],               ['გვ', 'თ'], ['გვ', 'ნენ']],
                     [['გ', 'თ'],             ['გ', 'თ'], ['გ', 'თ'],              ['გ', 'ნენ']],
                     [['ვ', ''],  ['', ''],   ['', 'ს'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნენ']]]


    screeve7_paas = [[            ['მ', ''],  ['მ', ''],               ['მ', 'თ'],  ['მ', 'ნენ']],
                     [['გ', ''],              ['გ', ''],   ['გ', 'თ'],              ['გ', 'ნენ']],
                     [['ვ', ''],  ['', ''],   ['', ''],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნენ']],
                     [            ['გვ', ''], ['გვ', ''],               ['გვ', 'თ'], ['გვ', 'ნენ']],
                     [['გ', 'თ'],             ['გ', 'თ'], ['გ', 'თ'],              ['გ', 'ნენ']],
                     [['ვ', ''],  ['', ''],   ['', ''],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ნენ']]]


    screeve8_paas = [[            ['მ', ''],  ['მ', 'ს'],               ['მ', 'თ'],  ['მ', 'ან']],
                     [['გ', ''],              ['გ', 'ს'],   ['გ', 'თ'],              ['გ', 'ან']],
                     [['ვ', ''],  ['', ''],   ['', 'ს'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ან']],
                     [            ['გვ', ''], ['გვ', 'ს'],               ['გვ', 'თ'], ['გვ', 'ან']],
                     [['გ', 'თ'],             ['გ', 'თ'], ['გ', 'თ'],              ['გ', 'ან']],
                     [['ვ', ''],  ['', ''],   ['', 'ს'],    ['ვ', 'თ'], ['', 'თ'],   ['', 'ან']]]


    screeve9_paas = [[            ['მ', 'ხარ'],  ['მ', 'ა'],               ['მ', 'ხართ'],  ['მ', 'ან']],
                     [['გ', 'ვარ'],              ['გ', 'ა'],   ['გ', 'ვართ'],              ['გ', 'ან']],
                     [['ვ', 'ვარ'], ['', 'ხარ'], ['', 'ა'], ['ვ', 'ვართ'], ['', 'ხართ'], ['', 'ან']],
                     [            ['გვ', 'ხარ'], ['გვ', 'ა'],               ['გვ', 'ხართ'], ['გვ', 'ან']],
                     [['გ', 'ვართ'],             ['გ', 'ათ'], ['გ', 'ვართ'],              ['გ', 'ან']],
                     [['ვ', 'ვარ'],  ['', 'ხარ'],   ['', 'ა'],    ['ვ', 'ვართ'], ['', 'ხართ'],   ['', 'ან']]]

    return screeve1_paas, screeve2_paas, screeve3_paas, screeve7_paas, screeve8_paas, screeve9_paas



def get_Indirect_paas():
    screeve1_paas = [[               ['გ', 'ვარ'],  ['ვ', 'ვარ'],                  ['გ', 'ვართ'], ['ვ', 'ვარ']],
                     [['მ', 'ხარ'],                 ['', 'ხარ'],  ['გვ', 'ხარ'],                   ['', 'ხარ']],
                     [['მ', 'ა'],    ['გ', 'ა'],     ['', 'ა'],    ['გვ', 'ა'],     ['გ', 'ათ'],   ['', 'ათ']],
                     [               ['გ', 'ვართ'], ['ვ', 'ვართ'],                ['გ', 'ვართ'], ['ვ', 'ვართ']],
                     [['მ', 'ხართ'],                ['', 'ხართ'], ['გვ', 'ხართ'],                ['', 'ხართ']],
                     [['მ', 'ა'],     ['გ', 'ა'],    ['', 'ა'],     ['გვ', 'ა'],    ['გ', 'ათ'],   ['', 'ათ']]]


    screeve2_paas = [[               ['გ', ''],  ['ვ', ''],                  ['გ', 'თ'], ['ვ', '']],
                     [['მ', ''],                 ['', ''],  ['გვ', ''],                   ['', '']],
                     [['მ', 'ა'],    ['გ', 'ა'],     ['', 'ა'],    ['გვ', 'ა'],     ['გ', 'ათ'],   ['', 'ათ']],
                     [               ['გ', 'თ'], ['ვ', 'თ'],                ['გ', 'თ'], ['ვ', 'თ']],
                     [['მ', 'თ'],                ['', 'თ'], ['გვ', 'თ'],                ['', 'თ']],
                     [['მ', 'ა'],     ['გ', 'ა'],    ['', 'ა'],     ['გვ', 'ა'],    ['გ', 'ათ'],   ['', 'ათ']]]

    # screeve3_paas = [['მ', 'ს'], ['გ', 'ს'], ['', 'ს'], ['გვ', 'ს'], ['გ', 'თ'], ['', 'თ']]
    screeve3_paas = [[               ['გ', ''],  ['ვ', ''],                  ['გ', 'თ'], ['ვ', '']],
                     [['მ', ''],                 ['', ''],  ['გვ', ''],                   ['', '']],
                     [['მ', 'ს'],    ['გ', 'ს'],     ['', 'ს'],    ['გვ', 'ს'],    ['გ', 'თ'],    ['', 'თ']],
                     [               ['გ', 'თ'], ['ვ', 'თ'],                ['გ', 'თ'], ['ვ', 'თ']],
                     [['მ', 'თ'],                ['', 'თ'], ['გვ', 'თ'],                ['', 'თ']],
                     [['მ', 'ს'],    ['გ', 'ს'],     ['', 'ს'],    ['გვ', 'ს'],    ['გ', 'თ'],    ['', 'თ']]]

    screeve4_paas = deepcopy(screeve2_paas)

    # screeve9_paas = [['მ', ''], ['გ', ''], ['', ''], ['გვ', ''], ['გ', 'თ'], ['', 'თ']]
    screeve9_paas = [[               ['გ', 'ვარ'],  ['ვ', 'ვარ'],                  ['გ', 'ვართ'], ['ვ', 'ვარ']],
                     [['მ', 'ხარ'],                 ['', 'ხარ'],  ['გვ', 'ხარ'],                   ['', 'ხარ']],
                     [['მ', 'ა'],    ['გ', 'ა'],     ['', 'ა'],    ['გვ', 'ა'],    ['გ', 'ათ'],    ['', 'ათ']],
                     [               ['გ', 'ვართ'], ['ვ', 'ვართ'],                ['გ', 'ვართ'], ['ვ', 'ვართ']],
                     [['მ', 'ხართ'],                ['', 'ხართ'], ['გვ', 'ხართ'],                ['', 'ხართ']],
                     [['მ', 'ა'],    ['გ', 'ა'],     ['', 'ა'],    ['გვ', 'ა'],    ['გ', 'ათ'],    ['', 'ათ']]]

    return screeve1_paas, screeve2_paas, screeve3_paas, screeve4_paas, screeve9_paas
