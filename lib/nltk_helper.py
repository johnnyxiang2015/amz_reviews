import nltk
from nltk import FreqDist
from nltk.corpus import stopwords, brown
import nltk.classify.util, nltk.metrics

lemmatizer = nltk.stem.WordNetLemmatizer()
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
# import RAKE
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer as RankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

english_stopwords = stopwords.words("english")
english_stopwords = english_stopwords + ['sunday', 'monday', 'tuesday', 'thursday', 'friday', 'saturnday', 'january',
                                         'feburary', 'march', 'april', 'may', 'june', 'july',
                                         'august', 'september', 'october', 'november', 'december', 'ms.', 'mr.',
                                         '%'] + ["amazon", "month", "months", "thing", "everything", "pros", "cons",
                                                 "way", "baby",
                                                 "something"] + ["son", "daughter", "man", "women", "love", "husband",
                                                                 "child", "lot", "bit", "time", "hand", "side", "year",
                                                                 "kids", "ride", "times", "time", "head",
                                                                 "back", "place", "sun", "phone", "position", "issue",
                                                                 "easy", "ease", "model", "day", "night", "week",
                                                                 "year", "top", "double", "review", "difference",
                                                                 "version", "star", "stars",
                                                                 "woman", "man", "wife", "beginning"]

english_stopwords = list(set(english_stopwords))

LANGUAGE = "english"
SENTENCES_COUNT = 3
stemmer = Stemmer(LANGUAGE)
summarizer = Summarizer(stemmer)
summarizer.stop_words = get_stop_words(LANGUAGE)

rank_summarizer = RankSummarizer(stemmer)
rank_summarizer.stop_words = get_stop_words(LANGUAGE)


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words
    @param stop_word_file Path and file name of a file containing stop words.
    @return list A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


current_dir = os.path.dirname(__file__)
general_stopwords = load_stop_words(current_dir + "/stoplists/SmartStoplist.txt")
general_stopwords = general_stopwords + english_stopwords

replace_keywords = {
    "price": ["expensive", "cheaper", "worth", "prices", "money", "dollar", "penny", "priced"],
    "design/style": ["look", "looks", "looking", "style", "design"],
    "ease of use": ["easy", "ease", "convenient", "easily", "challenging", "difficult", "hard", "inconvenient",
                    "convenience", "inconvenience"],
    "quality": ["durable", "solid", "solidly"],
    "weight": ["light", "heavy", "lightweight", "light-weight"],
    "wheel": ["tire", "tires", "wheels"]
    # "size":["large","small","larger","big","tiny"]
}

#########################################
# tf-idf implementation
# from http://timtrueman.com/a-quick-foray-into-linear-algebra-and-python-tf-idf/
#########################################
import math


def freq(word, document, wt):
    total = 0
    for wd, weight in zip(document, wt):
        if wd == word:
            total += weight
    return total


def word_count(wt):
    total = 0
    for w in wt:
        total += w
    return total


# return len(document)
def num_docs_containing(word, document_list):
    count = 0
    for document in document_list:
        if word in document:
            count += 1
    return count


def tf(word, document, wt):
    return freq(word, document, wt) / float(word_count(wt))


def idf(word, document_list):
    return math.log(len(document_list) / num_docs_containing(word, document_list))


def tfidf(word, document, document_list, wt):
    return tf(word, document, wt) * idf(word, document_list)


#########################################
# extract top keywords from each doc.
# This defines features of our common feature vector
#########################################
import operator


def top_keywords(n, doc, corpus, wt):
    d = {}
    for word in set(doc):
        d[word] = tfidf(word, doc, corpus, wt)
    sorted_d = sorted(d.items(), key=operator.itemgetter(1))
    sorted_d.reverse()
    return [w[0] for w in sorted_d[:n]]


# This is a fast and simple noun phrase extractor (based on NLTK)
# Feel free to use it, just keep a link back to this post
# http://thetokenizer.com/2013/05/09/efficient-way-to-extract-the-main-topics-of-a-sentence/
# Create by Shlomi Babluki
# May, 2013


# This is our fast Part of Speech tagger
#############################################################################
brown_train = brown.tagged_sents(categories='news')
regexp_tagger = nltk.RegexpTagger(
    [
        (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
        (r'(-|:|;)$', ':'),
        (r'\'*$', 'MD'),
        (r'(The|the|A|a|An|an)$', 'AT'),
        (r'.*able$', 'JJ'),
        (r'^[A-Z].*$', 'NNP'),
        (r'.*ness$', 'NN'),
        (r'.*ly$', 'RB'),
        # (r'.*s$', 'NNS'),
        (r'.*ing$', 'VBG'),
        (r'.*ed$', 'VBD'),
        (r'.*ould$', 'MD'),
        (r'.*ed$', 'VBD'),
        (r'.*ment$', 'NN'),
        (r'.*ful$', 'JJ'),
        (r'.*ious$', 'JJ'),
        (r'.*ble$', 'JJ'),
        (r'.*ic$', 'JJ'),
        (r'.*ive$', 'JJ'),
        (r'.*ic$', 'JJ'),
        (r'.*est$', 'JJ'),
        (r'^a$', 'PREP'),
    ])

unigram_tagger = nltk.UnigramTagger(brown_train, backoff=regexp_tagger)
bigram_tagger = nltk.BigramTagger(brown_train, backoff=unigram_tagger)
#############################################################################


# This is our semi-CFG; Extend it according to your own needs
#############################################################################
# cfg = {"NNP+NN": "NNP", "NNP+NNP": "NNP", "NN+NN": "NNI", "NNI+NN": "NNI", "JJ+JJ": "JJ"}

cfg = {"NNP+NNP": "NNP", "NN+NN": "NNI", "NNI+NN": "NNI", "JJ+JJ": "JJ"}


# cfg["JJ+NN"] = "NNI"
#############################################################################


def tokenize_sentence(sentence):
    tokens = nltk.word_tokenize(sentence)
    return tokens


def normalize_tags(tagged):
    n_tagged = []

    for t in tagged:
        if t[1] is None:
            continue
        if t[1] == "NP-TL" or t[1] == "NP":
            n_tagged.append((t[0], "NNP"))
            continue
        if t[1].endswith("-TL"):
            n_tagged.append((t[0], t[1][:-3]))
            continue
        if t[1].endswith("S"):
            n_tagged.append((t[0], t[1][:-1]))
            continue

        n_tagged.append((t[0], t[1]))

    return n_tagged


def tag_sentence(sentence):
    tokens = tokenize_sentence(sentence)
    tags = normalize_tags(nltk.pos_tag(tokens))

    merge = True
    while merge:
        merge = False
        for x in range(0, len(tags) - 1):
            t1 = tags[x]
            t2 = tags[x + 1]
            key = "%s+%s" % (t1[1], t2[1])
            value = cfg.get(key, '')
            if value:
                merge = True
                tags.pop(x)
                tags.pop(x)
                match = "%s %s" % (t1[0], t2[0])
                pos = value
                tags.insert(x, (match, pos))
                break

    return tags


def extract_adjs(sentences):
    adjs = []
    for sentence in sentences:

        tokens = tokenize_sentence(sentence)
        # tags = normalize_tags(bigram_tagger.tag(tokens))
        tags = normalize_tags(nltk.pos_tag(tokens))

        merge = True
        while merge:
            merge = False
            for x in range(0, len(tags) - 1):
                t1 = tags[x]
                t2 = tags[x + 1]
                key = "%s+%s" % (t1[1], t2[1])
                value = cfg.get(key, '')
                if value:
                    merge = True
                    tags.pop(x)
                    tags.pop(x)
                    match = "%s %s" % (t1[0], t2[0])
                    pos = value
                    tags.insert(x, (match, pos))
                    break

        for t in tags:
            if t[1] == "JJ":
                adjs.append(t[0].lower())

    return adjs


def top_summary(text, sentence_count=3, is_ummarizer=None):
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))

    if is_ummarizer is None:
        is_ummarizer = summarizer
    return [s._text for s in is_ummarizer(parser.document, sentence_count)]


def find_support_sentences(feature, all_sentences):
    feature_words = [feature]

    if feature in replace_keywords:
        feature_words = feature_words + replace_keywords[feature]

    # print feature_words

    support_sentences = []

    for sentence in all_sentences:
        tokens = tokenize_sentence(sentence[0])

        # tokens = [lemmatizer.lemmatize(t) for t in tokens]

        if any(feature_word in sentence[0] for feature_word in feature_words):
            tags = tag_sentence(sentence[0])
            # tags = normalize_tags(nltk.pos_tag(tokens))
            # print sentence[0]
            # print tags

            matched = [t[0] for t in tags if t[0] in feature_words and "VB" not in t[1]]

            if len(matched) > 0:
                support_sentences.append(sentence)

    return support_sentences


# support_sentences = [sentence for sentence in all_sentences if any(feature_word in nltk.word_tokenize(sentence[0]) for feature_word in feature_words)]




def extract_features(sentences, limit=10, excluded=None, required=None):
    features = []

    for sentence_with_start in sentences:
        sentence = sentence_with_start[0]
        star = sentence_with_start[1]
        helpful = sentence_with_start[2]
        # tokens = [t for t in nltk.wordpunct_tokenize(sentence.lower()) if t not in general_stopwords]
        # tokens = filter(lambda token: token not in general_stopwords, tokenizer.tokenize(sentence.lower()))
        tokens = tokenize_sentence(sentence)

        # tokens = [lemmatizer.lemmatize(t) for t in tokens]
        tags = normalize_tags(bigram_tagger.tag(tokens))
        # tags = normalize_tags(nltk.pos_tag(tokens))
        # print sentence, tokens, tags
        merge = True
        while merge:
            merge = False
            for x in range(0, len(tags) - 1):
                t1 = tags[x]
                t2 = tags[x + 1]
                key = "%s+%s" % (t1[1], t2[1])
                value = cfg.get(key, '')

                # print t1, t2, value
                if value:
                    merge = True
                    tags.pop(x)
                    tags.pop(x)
                    match = "%s %s" % (t1[0], t2[0])
                    pos = value
                    tags.insert(x, (match, pos))
                    break
                    # 	print sentence
        # print tags
        replace_keywords_words = [v for k, vs in replace_keywords.items() for v in vs]
        for t in tags:

            for k, vs in replace_keywords.items():
                if t[0] in vs and "VB" not in t[1]:
                    features.append(k)
                    break

            if "NN" in t[1] and t[0] not in replace_keywords_words:
                features.append(t[0].lower())

    # combine single and plur
    features = [lemmatizer.lemmatize(t) for t in features]
    fdist = FreqDist(features)
    features = fdist.most_common(limit * 3)

    if required != None:
        features_words = [x[0] for x in features]
        for r in required:
            if r not in features_words:
                features.append([r, fdist[r]])

    features = redundancy_pruning(features, excluded)

    # print features

    features = semantic_summary(features, sentences)

    # print features


    final_features = []
    if required is not None:
        final_features = [feature for feature in features if
                          feature["feature"] in required and (feature["neg"] + feature["neg"]) > 5]

    for feature in features:

        if required is not None and feature["feature"] in required:
            continue
        final_features.append(feature)

        if len(final_features) >= limit:
            break

    return final_features


def redundancy_pruning(features, excluded=None):
    if excluded is None:
        excluded = ""
    else:
        excluded = excluded.lower()

    r_features = []

    ff = [f[0] for f in features]

    for feature in features:
        is_redundant = False
        for f in ff:
            if feature[0] in f and feature[0] != f:
                # print feature[0], "rrr"
                is_redundant = True
                break

        if not is_redundant and feature[0] not in general_stopwords and feature[0] not in excluded:
            r_features.append(feature)

    return r_features


def semantic_summary(features, all_sentences):
    dir = os.path.dirname(__file__)
    sid = SentimentIntensityAnalyzer(dir + "/stoplists/vader_lexicon.txt")

    options = []

    for feature in features:
        option = {
            "feature": feature[0],
            "neg": 0,
            "pos": 0,
            "frq": feature[1]
        }

        support_sentences = find_support_sentences(feature[0], all_sentences)

        sentences_with_orientation = {
            "pos": [],
            "neg": []
        }

        for ss in support_sentences:
            s = ss[0]
            stars = ss[1]
            helpful = ss[2]

            # feats = dict([(word, True) for word in nltk.wordpunct_tokenize(s)] )
            # if word not in english_stopwords

            opt = ""
            scores = sid.polarity_scores(s)

            if scores["compound"] + 0.7 * (stars - 3) / 2 < -0.2:
                opt = "neg"
            elif scores["compound"] + 0.7 * (stars - 3) / 2 > 0.2:
                opt = "pos"

            # manual correction
            # positives
            if any(mw in nltk.word_tokenize(s) for mw in ["positives", "pros"]):
                opt = "pos"
            elif any(mw in nltk.word_tokenize(s) for mw in ["negatives"]):
                opt = "neg"

            if opt != "":
                option[opt] = int(option[opt] + 1 + helpful * 0.5)
                sentences_with_orientation[opt].append(
                    [s, (scores["compound"] + 0.7 * (float(stars) - 3) / 2) * float(helpful * 0.3 + 1)])

        if (len(sentences_with_orientation["pos"]) + len(sentences_with_orientation["neg"])) < 5:
            # options.pop(feature[0],None)
            continue

        if len(sentences_with_orientation["pos"]) > 0:
            sorted_sentences_with_orientation_pos = sorted(sentences_with_orientation["pos"], key=lambda v: v[1],
                                                           reverse=True)
            # option["pos_summary"] = sorted_sentences_with_orientation_pos[0]

            option["pos_summary"] = top_summary("\n ".join([t[0] for t in sentences_with_orientation["pos"]]), 1,
                                                rank_summarizer)
        else:
            option["pos_summary"] = []

        if len(sentences_with_orientation["neg"]) > 0:

            sorted_sentences_with_orientation_neg = sorted(sentences_with_orientation["neg"], key=lambda v: v[1])
            # option["neg_summary"] = sorted_sentences_with_orientation_neg[0]

            # option["neg_summary"].append(top_summary("\n ".join([t[0] for t in sentences_with_orientation["neg"]]),1))
            option["neg_summary"] = top_summary("\n ".join([t[0] for t in sentences_with_orientation["neg"]]), 1,
                                                rank_summarizer)
        else:
            option["neg_summary"] = []

        options.append(option)

    options = sorted(options, key=lambda v: v["neg"] + v["pos"], reverse=True)
    return options
