"""
Stefan Schulz 11 Nov 2017
"""

import logging
import re
from typing import Tuple

from acres.util import acronym as acro_util
from acres.util import functions
from acres.util import variants

logger = logging.getLogger(__name__)


def _has_parenthesis(full: str) -> bool:
    """
    Check whether a given string contains parenthesis.

    :param full:
    :return:
    """
    if "(" in full or ")" in full:
        return True
    return False


def _is_full_too_short(full: str) -> bool:
    """
    Check whether a given full form is too short.

    @todo ignore whitespaces?

    :param full:
    :return:
    """
    too_short = 5
    if len(full) <= too_short:
        return True
    return False


def _starts_with_stopword(full: str) -> bool:
    """
    Check whether the full form starts with a stopword.

    :param full:
    :return:
    """
    if functions.is_stopword(full.split(' ', 1)[0]):
        return True
    return False


def _has_capitals(full: str) -> bool:
    """
    Check whether a string has at least one capital letter.

    :param full:
    :return:
    """
    if full.islower():
        return False
    return True


def _is_schwarzt_hearst_valid(acro: str, full: str) -> bool:
    """
    Check whether the full form length is within the bounds defined by Park/Roy and used by
    Schwarzt/Hearst.

    Park, Youngja, and Roy J. Byrd.
    "Hybrid text mining for finding abbreviations and their definitions."
    Proceedings of the 2001 conference on empirical methods in natural language processing. 2001.

    :param acro:
    :param full:
    :return:
    """
    if len(full.split()) > min(len(acro) + 5, len(acro) * 2):
        return False
    return True


def _is_relative_length_valid(acro: str, full: str) -> bool:
    """
    Check whether the relative length of acronym to full form are within reasonable bounds.

    A full form can be up to 20 times longer than the acronym and the acronym has to be at most 60%
    of the full form.

    :param acro:
    :param full:
    :return:
    """
    if 0.05 <= len(acro) / len(full) <= 0.6:
        return True
    return False


def _is_levenshtein_distance_too_high(acro: str, full: str) -> bool:
    """
    Check whether the Levenshtein distance between the given acronym and a generated one is too
    high.

    :param acro:
    :param full:
    :return:
    """
    distance = functions.levenshtein(acro.upper(), acro_util.create_german_acronym(full))
    if distance < len(acro):
        return False
    return True


def _is_substring(acro: str, full: str) -> bool:
    """
    Check whether a given acronym is present in the full for.

    :param acro:
    :param full:
    :return:
    """
    if acro in full:
        return True
    return False


def _is_short_form(acro: str, full: str) -> bool:
    """
    Check whether a given expansion is shorter than the acronym.

    :param acro:
    :param full:
    :return:
    """
    if len(full.split()) < len(acro):
        return True
    return False


def _compute_full_valid(full: str) -> int:
    """

    :param full:
    :return:
    """
    ret = 0
    if _has_parenthesis(full):
        ret += 1

    if _is_full_too_short(full):
        ret += 2

    if _starts_with_stopword(full):
        ret += 4

    # TODO restrict to german
    # A valid expansion of a german acronym would require at least one noun, which is capitalized.
    if not _has_capitals(full):
        ret += 8

    return ret


def is_full_valid(full: str) -> bool:
    """
    Check whether the full form is valid.

    :param full:
    :return:
    """
    return _compute_full_valid(full) == 0


def _compute_expansion_valid(acro: str, full: str) -> int:
    """

    :param acro:
    :param full:
    :return:
    """
    ret = 0

    if not _is_schwarzt_hearst_valid(acro, full):
        ret += 1

    if not _is_relative_length_valid(acro, full):
        ret += 2

    if _is_levenshtein_distance_too_high(acro, full):
        ret += 4

    if _is_substring(acro, full):
        ret += 8

    return ret


def is_expansion_valid(acro: str, full: str) -> bool:
    """
    Check whether an expansion is valid for a given acronym.

    :param acro:
    :param full:
    :return:
    """
    return _compute_expansion_valid(acro, full) == 0


def get_acronym_score(acro: str, full: str, language: str = "de") -> Tuple[str, float, str]:
    """
    TODO: All morphosaurus stuff eliminated. Could check past versions later whether this is worth
    while considering again

    Scores Acronym / resolution pairs according to a series of well-formedness criteria using a
    n-gram frequency list from related corpus.

    The scoring function should work both for acronyms extracted from a corpus (for which strict
    matching criteria should be applied) and for acronyms harvested from the Web for which the
    criteria may be relaxed once strong evidence from acronym - definition patterns exist
    E.g., "ARDS (akutes Atemnotsyndrom)" : There might be acronym - definition patterns
    in well-written clinical documents.

    In the latter case, full would take this form, i.e. a string that contains both the acronym and
    the expansion

    For checking for valid German expansions it is important to consider variants,
    therefore invoke spelling variant generator from acres.util.text.
    At this place more rules can be added


    TODO:
    all scoring / penalization is pure heuristics. Plausibility should be tested with many
    examples !

    @todo use acres.util.acronym.is_valid_expansion(acro, full) as well
    Maybe some of the checks, especially boolean ones, (e.g. length) should be moved there.

    @todo evaluate scoring higher shorter valid expansions

    :param acro: acronym to be expanded
    :param full: long form to be checked whether it qualifies as an acronym expansion
    :param language: Expansion language. Matters especially regarding the possible infixes for \
    single noun composition
    :return: score that rates the likelihood that the full form is a valid expansion of the acronym
    """

    # see below cases in which the lat letter of an acronym is stripped
    last_letter_stripped = False
    is_acronym_definition_pair = False
    acro = acro.strip()
    full = full.strip()

    #
    # ELIMINATION RULES
    #

    # acronym must have at least two characters: all those expressions like "Streptococcus B" or
    # "Vitamin C" should not be considered containg acronyms. Normally these compositions are
    # lexicalised
    # May be relevant for assessing single letter forms like "A cerebralis"

    if _has_parenthesis(full):
        return (full, 0, "Parenthesis in full expression ")

    if _is_full_too_short(full):
        return (full, 0, "Full expression too short")

    if _starts_with_stopword(full):
        return (full, 0, "first word in stopword list")

    if len(acro) < 2:   # TODO is_acronym()
        return (full, 0, "Single letter acronym")

    if language == "de":
        if not _has_capitals(full):
            return (full, 0, "Full form without capitals")

    # length restrictions (according to analysis of
    # "acro_full_reference.txt" (modified from Wikipedia))
    # TODO: could be much greater then 5. Look for cases in which this is an issue
    if not _is_relative_length_valid(acro, full):
        return (full, 0, "Full form too long or too short")

    # Schwartz / Hearst rule
    if not _is_schwarzt_hearst_valid(acro, full):
        return (full, 0, "Contradicts Schwartz / Hearst rule")
    # SCHWARTZ, Ariel S.; HEARST, Marti A. A simple algorithm for identifying abbreviation
    # definitions in biomedical text. In: Biocomputing 2003. 2002. S. 451-462.

    if _is_levenshtein_distance_too_high(acro, full):
        return (full, 0, "Levenshtein edit distance too high")

    # ACRONYM DEFINITION PATTERNS
    # full form contains an acronym definition pattern (normally only yielded
    # from Web scraping, unlikely in clinical texts)
    # acronym is included; is then removed from full form
    # TODO move to separate method
    acro_def_pattern = acro_util.extract_acronym_definition(full, 7)
    if acro_def_pattern is not None:
        is_acronym_definition_pair = True
        if acro_def_pattern[0] == acro:
            full = acro_def_pattern[1]
            # high score, but also might be something else

    else:
        # acronym must not occur within full form (case sensitive)
        if _is_substring(acro, full):
            return (full, 0, "Acronym case-sensitive substring of full")
        if _has_parenthesis(full):
            return (full, 0, "Parenthesis in full")

    # from here no elimination
    acro_low = acro.lower()
    full_low = full.lower()

    if language == "de":
        # Plural form of acronym reduced to singular ("s", often not found in non English full
        # forms) e.g. "EKGs", "EKGS", "NTx", "NTX" (Nierentransplantation)
        # These characters cannot be always expected to occur in the full form
        # We assume that plurals and genitives of acronyms are often marked with
        # "s", however not necessarily lower case.
        # This means that "S" and "X" are not required to match
        singular_acro = acro_util.trim_plural(acro)
        if singular_acro != acro:
            acro = singular_acro
            acro_low = singular_acro.lower()
            last_letter_stripped = True

    # GENERATION OF VARIANTS
    # Typical substitutions, mostly concerning the inconsistent use
    # of k, c, and z in clinical texts
    # can be enhanced by frequent translations in acres.util.text.

    lst_var = variants.generate_all_variants_by_rules(full)
    full_old = full
    score = 0.0

    # Iterates over all variants. The best score is then returned.
    for full in lst_var:
        go_next = False
        old_score = score
        full_low = full.lower()
        # here no direct eliminations

        # first chars must be the same, certain tolerance with acronym definition pairs
        if acro_low[0] != full_low[0]:  # TODO split_expansion should get it
            if not is_acronym_definition_pair:
                go_next = True  # TODO continue

        # last char of acronym must occur in last word of full
        # but not at the end unless it is a single letter
        # "EKG" = "Entwicklung" should not match
        # "Hepatitis A" -> "HEPA" should match
        # HOWEVER: not applicable if last letter stripped
        # TODO move to split_expansion (or a semantic-powered version of it)
        if not last_letter_stripped:
            last_word = full_low.split(" ")[-1]
            if len(last_word) == 1 and acro_low[-1] != last_word:
                # Rightmost acronym character is not equal rightmost single-char word
                if not is_acronym_definition_pair:
                    go_next = True
            if not acro_low[-1] in last_word[0:-1]:
                # Rightmost acronym character is not in rightmost word
                if not is_acronym_definition_pair:
                    go_next = True

        if not go_next:
            score = 1
            regex = "^"
            for char in acro_low:
                regex = regex + char + ".*"
            if re.search(regex, full_low) is None:  # TODO split_expansion
                if is_acronym_definition_pair:
                    score = score * 0.1     # TODO score = 0.1
                else:
                    score = 0
            else:

                # rightmost expansion should start with upper case initial
                if language == "de":
                    if full.split(" ")[-1][0].islower():
                        score = score * 0.25

                # exact match of real acronym with generated acronym
                if language == "de":
                    if acro.upper() == acro_util.create_german_acronym(full):
                        score = score * 2

                # if short full form, the coincidence of the first two letters of full and acronym
                # increases score
                if _is_short_form(acro, full):
                    if full.upper()[0:2] == acro.upper()[0:2]:
                        score = score * 2

        if old_score > score:
            score = old_score

    # decapitalized acronym should not occur within decap full form,
    # if acronym has three or more letters

    if is_acronym_definition_pair:
        score = score * 10
    else:

        if _is_substring(acro_low, full_low):
            score = score * 0.2

    return full_old, round(score, 2), 'End'
