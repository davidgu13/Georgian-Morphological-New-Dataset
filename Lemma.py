__author__ = "David Guriel"
import copy
from utils import *
from prettytable import PrettyTable

class Lemma:
    def __init__(self, idx:int, translation:str, preverb:str, version:str, root:str, ts:str, aor_indic_3rd_sg:str, alternative_root='', masdar_prf='', masdar_imprf='', lemma_form=''):
        self.idx = int(idx)
        self.translation = translation
        self.preverb = preverb
        # self.version = self.version = SUBJECTIVE_VERSION if version=='subj' else zip_pronouns([version]*6)
        if version=='subj': # Subjective Version - 'ი' for 1st & 2nd person object, 'უ' for 3 person object
            self.version = set_screeve_markers(SUBJECTIVE_VERSION, mode='obj')
        else:
            self.version = set_screeve_markers([version]*6, mode='subj')
        self.lemma_form = lemma_form

        self.root = root
        self.passive_marker = '' # used in Intransitive & Indirect class
        self.ts = ts
        self.aor_indic_3rd_sg = aor_indic_3rd_sg # used for Aorist Subjunctive and 3rd Subjunctive Screeves.
        self.alter_root = alternative_root # used for Screeve 7,8,10,11 (which are morphologically highly related to each other)

        self.masdar_prf = masdar_prf # not necessarily exist, can be ''
        self.masdar_imprf = masdar_imprf # not necessarily exist, can be ''

    def gen_lemma_form(self, screeves):
        if self.lemma_form=='': # calculating the lemma name, if not already given
            self.lemma_form = self.version['sg3']['sg3'] + self.root + self.passive_marker + self.ts + screeves[0].paas['sg3']['sg3']['suff']  # 1st Screeve, 3rd person singular


    def generate_clean_paradigm(self, screeves, use_unimorph_format, verbose, file):
        self.gen_lemma_form(screeves)
        if verbose: file.write(f"#{self.idx} - {self.lemma_form} - {self.translation}:\n")

        for screeve in screeves: # print the 71 verbal forms (66 + 5 Imperative)
            _ = screeve.generate_forms(copy.copy(self), use_unimorph_format, verbose, file)

        # region print masdars
        for s1,s2,f in [('PRF','Perfective',self.masdar_prf), ('IPFV','Imperfective',self.masdar_imprf)]:
            if f != '':
                if use_unimorph_format: file.write(f"{self.lemma_form}\t{f}\tV;V.MSDR;{s1}\n")
                else: file.write(f"Masdar form, {s2}: ", f, '\n')
        # endregion print masdars
        # print('\n\n')



class Transitive_Lemma(Lemma):
    def __init__(self, idx:int, translation:str, preverb:str, version:str, root:str, ts:str, aor_indic_3rd_sg:str, aor_indic_vowel:str, aor_subjn_vowel:str,
                 perfect_version:str, pluperfect_version:str, third_subjn_vowel:str, alternative_root='', masdar_prf='', masdar_imprf='', lemma_form=''):
        super(Transitive_Lemma, self).__init__(idx, translation, preverb, version, root, ts, aor_indic_3rd_sg, alternative_root, masdar_prf, masdar_imprf, lemma_form)
        self.aor_indic_vowel = aor_indic_vowel
        self.aor_subjn_vowel = aor_subjn_vowel
        self.third_subjn_vowel = third_subjn_vowel
        if perfect_version=='OV':
            self.perfect_version = set_screeve_markers(SUBJECTIVE_VERSION, mode='subj')
        else:
            raise Exception("Unhandled case!")
        if pluperfect_version=='IOV': self.pluperfect_version = set_screeve_markers(['ე']*6, mode='subj')
        else:
            raise Exception("Unhandled case!")


class Intransitive_Lemma(Lemma):
    def __init__(self, idx:int, translation:str, lemma_formation:int, valency: int, preverb:str, version:str, root:str, ts:str,
                 aor_indic_3rd_sg:str, aor_indic_vowel:str,
                 perfect_ts:str, pluperfect_ts:str, perfect_marker:str, perfects_3rd_IDO:str,
                 alternative_root='', masdar_prf='', masdar_imprf='', lemma_form=''):
        super(Intransitive_Lemma, self).__init__(idx, translation, preverb, version, root, ts, aor_indic_3rd_sg, alternative_root, masdar_prf, masdar_imprf, lemma_form)
        self.aor_indic_vowel = aor_indic_vowel
        # self.aor_subj_vowel = aor_subj_vowel # if the rule in the Screeve formation is too specific, use this property to assign it,
                                               # and act similarly to the way aor_indic_vowel is used
        self.perfect_ts = perfect_ts
        self.pluperfect_ts = pluperfect_ts
        self.valency = valency
        if self.valency==1:
            self.perfect_marker = perfect_marker
        elif self.valency==2:
            assert perfects_3rd_IDO in {'', 'ს', 'ჰ'}
            self.perfects_3rd_IDO = perfects_3rd_IDO # should be
        else:
            raise Exception("Invalid valency for Intransitive class!")

        if lemma_formation in [1,2,3]: # Option 1 for prefixal (ი version), 2 for d (დ) addition, 3 for markerless
            self.formation_option = lemma_formation
        else: raise Exception('Invalid Formation value!')

        self.passive_marker = 'დ' if self.formation_option==2 else ''
        # Other modifications of the stem are found in Intransitive_Screeve class!


class Medial_Lemma(Lemma):
    def __init__(self, idx: int, translation: str, version:str, root:str, ts:str, future_ts:str, alternative_root='', masdar_prf='', masdar_imprf='', lemma_form=''):
        super(Medial_Lemma, self).__init__(idx, translation, '', version, root, ts, 'ა', alternative_root, masdar_prf, masdar_imprf, lemma_form) # preverb=''
        self.future_ts = future_ts

        self.perfect_version = set_screeve_markers(SUBJECTIVE_VERSION, mode='subj') # if it is not always correct, then modify manuaaly or copy from Transitive_class
        self.pluperfect_version = set_screeve_markers(['ე']*6, mode='subj')


class Indirect_Lemma(Lemma):
    """
    Very different from Transitive/Intransitive class:
    - Preverb is always optional
    - Series 2 almost never exists!
    - The root and TS can change "arbitrarily", so we define independent properties for them.
    - There is always Inversion, and objects are marked with copula (not with set B affixes).
    """
    def __init__(self, idx: int, translation: str, preverb: str, version: str, root_pres: str, ts_pres: str,
                 pres_S_3sg_pref:str, pres_IDO_3sg_suffix:str, root_fut: str, ts_fut: str, root_perf:str, ts_perf:str, passive_marker:str, d_or_od:str, masdar:str):
        super().__init__(idx, translation, preverb, version, root_pres, ts_pres, '', masdar_imprf=masdar)

        if version=='subj': # Subjective Version - 'ი' for 1st & 2nd person *subject*, 'უ' for 3 person object
            self.version = set_screeve_markers(SUBJECTIVE_VERSION, mode='subj')

        self.root_fut = root_fut
        self.ts_fut = ts_fut
        self.pres_S_3sg_pref = pres_S_3sg_pref
        self.pres_IDO_3sg_suffix = pres_IDO_3sg_suffix
        self.root_perf = root_perf
        self.ts_perf = ts_perf
        self.screeve_marker_d = d_or_od
        self.passive_marker = passive_marker

    def gen_lemma_form(self, screeves):
        if self.lemma_form=='': # calculating the lemma name, if not already given
            self.lemma_form = self.pres_S_3sg_pref + self.version['sg3']['sg3'] + self.root + self.passive_marker + self.ts + self.pres_IDO_3sg_suffix  # 1st Screeve, 3rd person singular


class Stative_Lemma(Lemma):
    def __init__(self, idx: int, translation: str, valency:int, version: str, root_pres: str, ts_pres: str, root_fut:str, ts_fut:str, s3sg_pref, o3sg_suff, aor_indic_3rd_sg: str, exist_screeves:str):
        super().__init__(idx, translation, '', version, root_pres, ts_pres, aor_indic_3rd_sg)
        # self.version = SUBJECTIVE_VERSION if version == 'subj' else zip_pronouns([version] * 6)
        self.valency = valency
        self.exist_screeves = [int(c) for c in exist_screeves.split(',')] # can maximally be [1,4,7,8,9,10]
        # self.screeves2idx = dict(zip([1,4,7,8,9,10],range(1,7)))
        self.s3sg_pref = s3sg_pref # ჰ, ს
        self.o3sg_suff = o3sg_suff # ა / ს
        self.root_fut = root_fut
        self.ts_fut = ts_fut

    def gen_lemma_form(self, screeves):
        if self.lemma_form=='': # calculating the lemma name, if not already given
            self.lemma_form = self.s3sg_pref + self.version['sg3'] + self.root + self.passive_marker + self.ts + self.o3sg_suff  # 1st Screeve, 3rd person singular

    def generate_clean_paradigm(self, screeves, use_unimorph_format, verbose, file):
        self.gen_lemma_form(screeves)
        if verbose: file.write(f"#{self.idx} - {self.lemma_form} - {self.translation}:\n")

        for i,screeve in enumerate(screeves): # print the verbal forms (no Imperatives, no Masdars)
            if screeve.idx in self.exist_screeves:
                screeve.generate_forms(copy.copy(self), use_unimorph_format, verbose, file)
