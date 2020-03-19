from bs4 import BeautifulSoup
from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import RegexpTokenizer
import traceback
import json

from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from lib.constant import HTML_PARSER
from lib.models import esdb, Review, Product, ProductFeature, Aggregated
from lib.nltk_helper import extract_features, extract_adjs, top_summary

LANGUAGE = "english"
SENTENCES_COUNT = 3

COMMON_FEATURES = ["price", "quality", "design/style", "ease of use"]
STOPWORDS = stopwords.words('english')


def save_features(asin, features):
    query = ProductFeature.delete().where(ProductFeature.asin == asin)
    query.execute()

    for feature in features:
        print("Feature: ", feature["feature"], "-", str(
            int(feature["pos"] * 100 / (feature["pos"] + feature["neg"]))) + "%")
        print("Positive: ", feature["pos"])
        print("Negative: ", feature["neg"])
        print("Top Positive: ", feature["pos_summary"])
        print("Top Negative: ", feature["neg_summary"])

        try:
            product_feature = ProductFeature()
            product_feature.asin = asin
            product_feature.feature = feature["feature"]
            product_feature.neg = feature["neg"]
            product_feature.pos = feature["pos"]
            product_feature.pos_summary = feature["pos_summary"]
            product_feature.neg_summary = feature["neg_summary"]
            product_feature.save()
        except:
            pass


def review_top_keywords_by_asin(asin):
    reviews = Review.select().where(Review.asin == asin)

    print(len(reviews))

    sid = SentimentIntensityAnalyzer()
    product = Product.get(Product.asin == asin)

    corpus = []
    titles = []
    all_reviews = []
    all_words = []
    all_sentences = []
    all_sentences_with_stars = []
    wts = []
    ct = -1
    title_wt = 1.3

    positive_review_text = []
    negative_review_text = []
    positive_sentences = []
    negative_sentences = []

    tokenizer = RegexpTokenizer(r'\w+')

    for review in reviews:
        try:
            review_content = BeautifulSoup(review.content, HTML_PARSER).text
        except:
            review_content = review.content

        if review_content is None:
            continue
        review_text_paras = review_content.split("\n")

        for review_text in review_text_paras:
            words = tokenizer.tokenize(review_text)
            # print words
            words = [x for x in words if x.lower() not in STOPWORDS]
            wt = [1.0] * len(words)
            title = nltk.wordpunct_tokenize(review.title)
            title = [x for x in title if x.lower() not in STOPWORDS]
            wt.extend([title_wt] * len(title))
            lower_words = [x.lower() for x in words if len(x) > 1]
            ct += 1

            if review.rating > 3:
                positive_review_text.append(review_text)
                positive_sentences.extend([s for s in nltk.sent_tokenize(review_text) if
                                           30 <= len(s) <= 300 and sid.polarity_scores(s)["compound"] >= 0.25])
            else:
                negative_review_text.append(review_text)
                negative_sentences.extend([s for s in nltk.sent_tokenize(review_text) if
                                           30 <= len(s) <= 300 and sid.polarity_scores(s)["compound"] <= -0.25])

            all_words.extend(lower_words)
            all_sentences.extend(nltk.sent_tokenize(review_text))
            all_sentences_with_stars.extend(
                [(s, review.rating, review.helpful) for s in nltk.sent_tokenize(review_text)])

            corpus.append(lower_words)
            titles.append(review.title)
            all_reviews.append(review)
            wts.append(wt)

    try:
        excluded = product.brand.lower() + product.categories.lower()
    except:
        if product.categories is not None:
            excluded = product.categories.lower()
        else:
            excluded = ""

    features = extract_features(all_sentences_with_stars, 7, excluded, COMMON_FEATURES)
    save_features(asin, features)

    fdist = nltk.FreqDist([word for word in all_words if word not in excluded])
    most_used_words = fdist.most_common(30)
    print("most used words \n")
    print(most_used_words, "\n")

    adjs = extract_adjs(all_sentences)
    fdist = nltk.FreqDist(adjs)

    top_positive = [x for x in fdist.most_common(100) if sid.polarity_scores(x[0])['pos'] > 0.5 and x[1] >= 3][0:7]
    print("top positive:", top_positive, "\n")

    top_negative = [x for x in fdist.most_common(100) if sid.polarity_scores(x[0])['neg'] > 0.5 and x[1] >= 3][0:7]
    print("top negative:", top_negative, "\n")

    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    print("positive summary \n")
    positive_summary = top_summary("\n".join(positive_sentences), 3)
    for sentence in positive_summary:
        print("*", sentence, "\n")

    print("negative summary \n")
    negative_summary = top_summary("\n".join(negative_sentences), 3)
    for sentence in negative_summary:
        print("*", sentence, "\n")

    try:
        ar = Aggregated.get(Aggregated.asin == asin)
    except:
        ar = Aggregated()
        ar.asin = asin

    try:
        ar.most_used_words = json.dumps(most_used_words)
        ar.most_positive_words = json.dumps(top_positive)
        ar.most_negative_words = json.dumps(top_negative)
        ar.positive_summary = json.dumps(positive_summary)
        ar.negative_summary = json.dumps(negative_summary)

        sql = "select sum(pos),sum(neg) from product_features where asin = %s"
        cursor = esdb.execute_sql(sql, [ar.asin])
        row = cursor.fetchone()
        if row[0] is None:
            ar.pos_features = 0
        else:
            ar.pos_features = row[0]

        if row[1] is None:
            ar.neg_features = 0
        else:
            ar.neg_features = row[1]

        ar.save()
    except:
        print(traceback.format_exc())
