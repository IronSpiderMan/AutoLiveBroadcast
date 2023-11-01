import os.path
import sys

BASE_PATH = sys.path[0]

STOP_WORDS = os.path.join(BASE_PATH, 'resources/stop_words')
EXCLUDED_SENTENCES = os.path.join(BASE_PATH, 'resources/excluded_sentences')
COMMENTS_PERSIST = os.path.join(BASE_PATH, "resources/sqlite")
QA_PERSIST = os.path.join(BASE_PATH, "resources/qa_vector_store")
SPEECHES = os.path.join(BASE_PATH, "resources/speeches")
SCRIPTS = os.path.join(BASE_PATH, "resources/script.txt")
