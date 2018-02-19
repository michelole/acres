from .context import functions


def test_split_ngram():
    # pass
    assert functions.split_ngram("a b c") == []
    #
    assert functions.split_ngram("a AK b") == [('a', 'AK', 'b')]
    #
    assert functions.split_ngram("l ACR1 b ACR2 c") == [(
        'l', 'ACR1', 'b ACR2 c'), ('l ACR1 b', 'ACR2', 'c')]
    #
    assert functions.split_ngram("ACR") == [('', 'ACR', '')]


def test_extract_acronym_definition():
    maxLength = 7

    assert functions.extract_acronym_definition(
        "EKG (Elektrokardiogramm)", maxLength) == ('EKG', 'Elektrokardiogramm')
    assert functions.extract_acronym_definition(
        "Elektrokardiogramm (EKG)", maxLength) == ('EKG', 'Elektrokardiogramm')
    assert functions.extract_acronym_definition(
        "Elektrokardiogramm", maxLength) is None


def test_is_acronym():
    # Single digits are not acronyms
    assert functions.is_acronym("A", 3) == False

    # Lower-case are not acronyms
    assert functions.is_acronym("ecg", 3) == False
    assert functions.is_acronym("Ecg", 3) == False

    # Double upper-case are acronyms
    assert functions.is_acronym("AK", 2)

    # Acronyms should be shorter or equal to the maximum length
    assert functions.is_acronym("EKG", 2) == False
    assert functions.is_acronym("EKG", 3)

    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert functions.is_acronym("ÄK", 3)

    # Acronyms can contain numbers
    assert functions.is_acronym("5FU", 7)


def test_simplify_german_string():
    assert functions.simplify_german_string("LEBER") == "leber"

    assert functions.simplify_german_string("ekg") == "ecg"
    assert functions.simplify_german_string("heißen") == "heissen"
    assert functions.simplify_german_string(
        "Elektrokardiogramm") == "electrocardiogramm"

    # XXX Is it expected?
    assert functions.simplify_german_string("herz") == "herc"
    assert functions.simplify_german_string("café") == "cafe"


def test_random_sub_list():
    # We output the input list if the length requested is larger or equal to
    # the input length
    assert functions.random_sub_list(["a", "b"], 2) == ["a", "b"]
    assert functions.random_sub_list(["a", "b"], 3) == ["a", "b"]

    # TODO use Random.seed() so that the output is deterministic
    assert functions.random_sub_list(["a", "b"], 1) in [["a"], ["b"]]
