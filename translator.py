import requests
import argparse
import sys
from bs4 import BeautifulSoup


languages = {'arabic': {'lang': 'Arabic', 'div_class': 'rtl arabic'}, 'german': {'lang': 'German', 'div_class': 'ltr'},
             'english': {'lang': 'English', 'div_class': 'ltr'}, 'spanish': {'lang': 'Spanish', 'div_class': 'ltr'},
             'french': {'lang': 'French', 'div_class': 'ltr'}, 'hebrew': {'lang': 'Hebrew', 'div_class': 'rtl'},
             'japanese': {'lang': 'Japanese', 'div_class': 'ltr'}, 'dutch': {'lang': 'Dutch', 'div_class': 'ltr'},
             'polish': {'lang': 'Polish', 'div_class': 'ltr'}, 'portuguese': {'lang': 'Portuguese', 'div_class': 'ltr'},
             'romanian': {'lang': 'Romanian', 'div_class': 'ltr'}, 'russian': {'lang': 'Russian', 'div_class': 'ltr'},
             'turkish': {'lang': 'Turkish', 'div_class': 'ltr'}}


def get_input_info():

    parser = argparse.ArgumentParser()

    parser.add_argument('lang_1')
    parser.add_argument('lang_2')
    parser.add_argument('word')

    args = parser.parse_args()
    translate_from, translate_into, word_to_translate = args.lang_1, args.lang_2, args.word

    return translate_from, translate_into, word_to_translate


def make_sentences_list(soup, div_class):
    sentences = soup.find_all('div', {'class': div_class})
    return [sentence.text.strip() for sentence in sentences]


def make_words_list(soup):
    words = soup.find_all('div', {'id': 'translations-content'})
    return [word.strip() for word in words[0].text.split()]


def get_page_info(translate_from, translate_into, word_to_translate):

    url = f'http://context.reverso.net/translation/' \
          f'{languages[translate_from]["lang"].lower()}-{languages[translate_into]["lang"].lower()}/{word_to_translate}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    s = requests.Session()
    page = s.get(url, headers=headers)

    status = page.status_code

    while not status:
        page = requests.get(url, headers=headers)
        status = page.status_code

    soup = BeautifulSoup(page.content, 'html.parser')
    try:
        words_list = make_words_list(soup)
    except IndexError:
        print(f'Sorry, unable to find {word_to_translate}')
        sys.exit()

    into_sentences_list = make_sentences_list(soup, f"trg {languages[translate_into]['div_class']}")
    from_sentences_list = make_sentences_list(soup, f"src {languages[translate_from]['div_class']}")

    return words_list, into_sentences_list, from_sentences_list


def get_translation(translate_from, translate_into, word_to_translate, all_items=True):

    words_list, into_sentences_list, from_sentences_list = get_page_info(
        translate_from, translate_into, word_to_translate)

    if all_items:

        printable_text = f"{languages[translate_into]['lang']} Translations:\n"

        for word in words_list[:5]:
            printable_text += f"{word}\n"

        printable_text += f"\n{languages[translate_into]['lang']} Example:\n"

        for into_sent, from_sent in zip(into_sentences_list, from_sentences_list):
            printable_text += f"{from_sent}\n{into_sent}\n\n"

        return printable_text

    else:
        printable_text = f"{languages[translate_into]['lang']} Translations:\n"

        for word in words_list:
            printable_text += f"{word}\n"

        printable_text += f"\n{languages[translate_into]['lang']} Example:\n"
        printable_text += f"{from_sentences_list[0]}\n{into_sentences_list[0]}\n\n\n"

        return printable_text


def main():

    translate_from, translate_into, word_to_translate = get_input_info()

    try:
        assert translate_from in [key for key in languages]
    except AssertionError:
        print(f"Sorry, the program doesn't support {translate_from}")
        sys.exit()
    else:
        if translate_into != 'all':
            try:
                assert translate_into in [key for key in languages]
            except AssertionError:
                print(f"Sorry, the program doesn't support {translate_into}")
                sys.exit()
            else:
                translation = get_translation(translate_from, translate_into, word_to_translate)
                file = open(f'{word_to_translate}.txt', 'w', encoding='utf-8')
                file.write(translation)
                file.close()
                print(translation, end='')
        else:
            file = open(f'{word_to_translate}.txt', 'w', encoding='utf-8')
            for key in languages:
                if key != translate_from:
                    translation = get_translation(translate_from, key, word_to_translate, all_items=False)
                    file.write(translation)
                    print(translation, end='')

            file.close()


main()
