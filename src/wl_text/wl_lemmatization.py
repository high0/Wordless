#
# Wordless: Text - Lemmatization
#
# Copyright (C) 2018-2021  Ye Lei (叶磊)
#
# This source file is licensed under GNU GPLv3.
# For details, see: https://github.com/BLKSerene/Wordless/blob/master/LICENSE.txt
#
# All other rights reserved.
#

import re

import nltk
import pymorphy2
import spacy

from wl_text import wl_matching, wl_pos_tagging, wl_text_utils
from wl_utils import wl_conversion, wl_misc

def wl_lemmatize(main, tokens, lang, tokenized = 'No', tagged = 'No', lemmatizer = 'default'):
    empty_offsets = []
    mapping_lemmas = {}
    lemmas = []

    tokens = [str(token) for token in tokens]

    re_tags = wl_matching.get_re_tags(main)

    if tagged == 'Yes':
        tags = [''.join(re.findall(re_tags, token)) for token in tokens]
        tokens = [re.sub(re_tags, '', token) for token in tokens]
    else:
        tags = [''] * len(tokens)

    # Record empty tokens
    for i, token in reversed(list(enumerate(tokens))):
        if not token.strip():
            empty_offsets.append(i)

            tokens.remove(token)

    wl_text_utils.check_lemmatizers(main, lang)

    if tokens and lang in main.settings_global['lemmatizers']:
        if lemmatizer == 'default':
            lemmatizer = main.settings_custom['lemmatization']['lemmatizers'][lang]

        # Dutch, English, French, German, Greek (Modern), Italian, Portuguese, Spanish
        if 'spaCy' in lemmatizer:
            nlp = main.__dict__[f'spacy_nlp_{lang}']

            doc = spacy.tokens.Doc(nlp.vocab, words = tokens)
            nlp.tagger(doc)

            lemmas = [token.lemma_ for token in doc]
        # English
        elif lemmatizer == main.tr('NLTK - WordNet Lemmatizer'):
            word_net_lemmatizer = nltk.WordNetLemmatizer()

            for token, pos in wl_pos_tagging.wl_pos_tag(
                main, tokens,
                lang = 'eng',
                pos_tagger = 'NLTK - Perceptron POS Tagger',
                tagset = 'universal'
            ):
                if pos == 'ADJ':
                    lemmas.append(word_net_lemmatizer.lemmatize(token, pos = nltk.corpus.wordnet.ADJ))
                elif pos in ['NOUN', 'PROPN']:
                    lemmas.append(word_net_lemmatizer.lemmatize(token, pos = nltk.corpus.wordnet.NOUN))
                elif pos == 'ADV':
                    lemmas.append(word_net_lemmatizer.lemmatize(token, pos = nltk.corpus.wordnet.ADV))
                elif pos in ['VERB', 'AUX']:
                    lemmas.append(word_net_lemmatizer.lemmatize(token, pos = nltk.corpus.wordnet.VERB))
                else:
                    lemmas.append(word_net_lemmatizer.lemmatize(token))
        # Greek (Ancient)
        elif lemmatizer == main.tr('lemmalist-greek - Greek (Ancient) Lemma List'):
            with open(wl_misc.get_normalized_path('lemmatization/lemmalist-greek/lemmalist-greek.txt'), 'r', encoding = 'utf_8') as f:
                for line in f.readlines():
                    line = line.rstrip()

                    if line:
                        lemma, *words = line.split()

                        for word in words:
                            mapping_lemmas[word] = lemma
        # Russian & Ukrainian
        elif lemmatizer == main.tr('pymorphy2 - Morphological Analyzer'):
            if lang == 'rus':
                morphological_analyzer = pymorphy2.MorphAnalyzer(lang = 'ru')
            else:
                morphological_analyzer = pymorphy2.MorphAnalyzer(lang = 'uk')

            for token in tokens:
                lemmas.append(morphological_analyzer.parse(token)[0].normal_form)
        # Tibetan
        elif lemmatizer == main.tr('botok - Tibetan Lemmatizer'):
            wl_text_utils.check_word_tokenizers(main,
                                                      lang = 'bod')
            tokens = main.botok_word_tokenizer.tokenize(' '.join(tokens))

            for token in tokens:
                if token.lemma:
                    lemmas.append(token.lemma)
                else:
                    lemmas.append(token.text)
        # Other Languages
        elif 'Lemmatization Lists' in lemmatizer:
            lang = wl_conversion.to_iso_639_1(main, lang)

            with open(wl_misc.get_normalized_path(f'lemmatization/Lemmatization Lists/lemmatization-{lang}.txt'), 'r', encoding = 'utf_8_sig') as f:
                for line in f:
                    try:
                        lemma, word = line.rstrip().split('\t')

                        mapping_lemmas[word] = lemma
                    except:
                        pass
    else:
        lemmas = tokens

    if mapping_lemmas:
        lemmas = [mapping_lemmas.get(token, token) for token in tokens]

    # Insert empty lemmas
    for empty_offset in sorted(empty_offsets):
        lemmas.insert(empty_offset, '')

    return [lemma + tag for lemma, tag in zip(lemmas, tags)]
