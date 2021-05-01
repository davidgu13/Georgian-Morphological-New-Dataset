__author__ = "David Guriel"
from Screeve import *
import pandas as pd
import argparse
from datetime import datetime
class Conjugation:
    def __init__(self, screeves_list:[Screeve]):
        self.screeves = screeves_list

    def gen_paradigm(self, lemma:Lemma, use_unimorph_format, verbose, f):
        lemma.generate_clean_paradigm(self.screeves, use_unimorph_format, verbose, f)

    @staticmethod
    def gen_lemma_object(row, conj):
        if conj=='tv':
            obj = Transitive_Lemma(*row.tolist())
        elif conj=='itv':
            obj = Intransitive_Lemma(*row.tolist())
        elif conj=='med':
            obj = Medial_Lemma(*row.tolist())
        elif conj=='ind':
            obj = Indirect_Lemma(*row.tolist())
        elif conj=='stat':
            obj = Stative_Lemma(*row.tolist())
        else:
            raise Exception("Unknown Conjugation class!")
        return obj


if __name__=='__main__':
    # For next time - update the README file!
    print(f"Exexuted on {datetime.now()}")
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", help="The Excel file from which to read the lemmas' data. "
                                "\nNote: execute this code only on verbs with valency>=2, otherwise syntactically wrong forms will be generated!!!")
    parser.add_argument('-v', '--verbose', help="Whether to print the output file with extra details", action="store_true")
    parser.add_argument('-u', "--use_unimorph_format", help="The meaning is implied from the name...", action="store_true")
    args = parser.parse_args()
    file_path, verbose, use_unimorph_format = args.file_path, args.verbose, args.use_unimorph_format


    transitive_class = Conjugation(define_Transitive_Screeves())
    TV_df = pd.read_excel(file_path, sheet_name=0)
    TV_df = TV_df.drop(columns=TV_df.columns.tolist()[16:]) # Note the column add on the Excel!
    TV_df.fillna('', inplace=True)

    intransitive_class = Conjugation(define_Intransitive_Screeves())
    ITV_df = pd.read_excel(file_path, sheet_name=1)
    ITV_df = ITV_df.drop(columns=ITV_df.columns.tolist()[18:])
    ITV_df.fillna('', inplace=True)

    medial_class = Conjugation(define_Medial_Screeves())
    MED_df = pd.read_excel(file_path, sheet_name=2)
    MED_df = MED_df.drop(columns=MED_df.columns.tolist()[10:])
    MED_df.fillna('', inplace=True)

    indirect_class = Conjugation(define_Indirect_Screeves())
    IND_df = pd.read_excel(file_path, sheet_name=3)
    IND_df = IND_df.drop(columns=IND_df.columns.tolist()[15:])
    IND_df.fillna('', inplace=True)

    stative_class = Conjugation(define_Stative_Screeves())
    STAT_df = pd.read_excel(file_path, sheet_name=4)
    STAT_df = STAT_df.drop(columns=STAT_df.columns.tolist()[12:])
    STAT_df.fillna('', inplace=True)


    TV_lemmas_dict = {(idx+1):transitive_class.gen_lemma_object(row,'tv') for idx,row in TV_df.iterrows()}
    ITV_lemmas_dict = {(idx+1):intransitive_class.gen_lemma_object(row,'itv') for idx,row in ITV_df.iterrows()}
    MED_lemmas_dict = {(idx+1):medial_class.gen_lemma_object(row,'med') for idx,row in MED_df.iterrows()}
    IND_lemmas_dict = {(idx+1):indirect_class.gen_lemma_object(row,'ind') for idx,row in IND_df.iterrows()}
    STAT_lemmas_dict = {(idx+1):stative_class.gen_lemma_object(row,'stat') for idx,row in STAT_df.iterrows()}


    conjugations_names = ['Transitive', 'Intransitive', 'Medial', 'Indirect', 'Stative']
    if not os.path.isdir("Clean Paradigms"):
        os.mkdir("Clean Paradigms")
    for dir_name in conjugations_names:
        if not os.path.isdir(os.path.join("Clean Paradigms", dir_name)):
            os.mkdir(os.path.join("Clean Paradigms", dir_name))
    choice_mapping = dict(zip(range(5),zip([transitive_class, intransitive_class, medial_class, indirect_class, stative_class],
                                           [TV_lemmas_dict, ITV_lemmas_dict, MED_lemmas_dict, IND_lemmas_dict, STAT_lemmas_dict])))

    class_choice = 0  # can be either 0,1,2,3,4 ; write -1 for locking.
    lemma_choices = [18, -1, -1, -1, -1] # when index isn't used, always insert 0 or -1 to disable the possibility of overriding
    assert 0 <= class_choice < len(conjugations_names)

    # for i in range(31,47):
    #     c = i # remove when serial generation is done
    c = lemma_choices[class_choice]
    example_lemma = choice_mapping[class_choice][1][c]
    with open(os.path.join("Clean Paradigms", conjugations_names[class_choice], example_lemma.translation + ".txt"), 'w+', encoding='utf8') as f:
        choice_mapping[class_choice][0].gen_paradigm(example_lemma, use_unimorph_format, verbose, f)
