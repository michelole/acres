import logging

import pytest

from acres import get_synonyms_from_ngrams

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@pytest.mark.skip(reason="this should be moved to benchmark.py")
def test_benchmark():
    # actual = get_synonyms_from_ngrams.find_embeddings("*", "TRINS", "*", 1, 2, 500, 1, 10)

    f = open("tests/data/Workbench.txt", "r", encoding="utf-8")
    # sRow = input("Select row number or press enter: ")
    for row in f:
        out = ""
        if row > " ":
            row = row.strip("\n")
            logger.info("=======================")
            logger.info("Analyzing: " + row)
            logger.info("=======================")
            row_nr = row.split("|")[0]
            left_context = row.split("|")[1]
            acro = row.split("|")[2]
            right_context = row.split("|")[3]
            probe = row.split("|")[4]

            v = get_synonyms_from_ngrams.test_input(probe, left_context, acro, right_context)
            if v == True:
                out = out + "<DEF> <ACR> <DEF>: Found"
            else:
                out = out + "<DEF> <ACR> <DEF>: Not Found\n"
                v = get_synonyms_from_ngrams.test_input(probe, "<SEL>", acro, right_context)
                if v == True:
                    out = out + "<SEL> <ACR> <DEF>: Found"
                else:
                    out = out + "<SEL> <ACR> <DEF>: Not Found\n"
                    v = get_synonyms_from_ngrams.test_input(probe, left_context, acro, "<SEL>")
                    if v == True:
                        out = out + "<DEF> <ACR> <SEL>: Found"
                    else:
                        out = out + "<DEF> <ACR> <SEL>: Not Found\n"
                        v = get_synonyms_from_ngrams.test_input(probe, "<SEL>", acro, "<SEL>")
                        if v == True:
                            out = out + "<SEL> <ACR> <SEL>: Found"
                        else:
                            out = out + "<SEL> <ACR> <SEL>: Not Found\n"
                            v = get_synonyms_from_ngrams.test_input(probe, "<VOID>", acro, "<SEL>")
                            if v == True:
                                out = out + "<VOID> <ACR> <SEL>: Found"
                            else:
                                out = out + "<VOID> <ACR> <SEL>: Not Found\n"
                                v = get_synonyms_from_ngrams.test_input(probe, "<SEL>", acro, "<VOID>")
                                if v == True:
                                    out = out + "<SEL> <ACR> <VOID>: Found"
                                else:
                                    out = out + "<SEL> <ACR> <VOID>: Not Found"
        logger.info("Final analysis: " + row)
        logger.info(out)

    f.close()
    

def test_find_embeddings():
    actual = get_synonyms_from_ngrams.find_embeddings("nach", "ICD", "Implantation", 1, 2, 500, 1, 10)
    actual = get_synonyms_from_ngrams.find_embeddings("*", "HF-Anstieg", "von", 1, 2, 500, 1, 10)
    actual = get_synonyms_from_ngrams.find_embeddings("*", "HT", "rein", 1, 2, 500, 1, 10)
    # viele Treffer, die mit Ht anfangen
    actual = get_synonyms_from_ngrams.find_embeddings("geplanten", "EPU", "*", 1, 2, 500, 1, 10)
    actual = get_synonyms_from_ngrams.find_embeddings("einem", "EDP", "von", 1, 2, 500, 1, 10)
    # wird nicht gefunden
    actual = get_synonyms_from_ngrams.find_embeddings("gutem", "AZ", "nach", 1, 2, 100, 1, 10)
    actual = get_synonyms_from_ngrams.find_embeddings("die", "VCS.", "*", 1, 2, 500, 1, 10)
    actual = get_synonyms_from_ngrams.find_embeddings("*", "DG's", "*", 1, 2, 500, 1, 10)
    # only without restricted context the resolution is found
    # only DG's resolved, not DGs
    actual = get_synonyms_from_ngrams.find_embeddings("die", "VCS.", "*", 1, 2, 500, 1, 10)
    # only works with final dot!
    actual = get_synonyms_from_ngrams.find_embeddings("re", "OL", "*", 1, 2, 500, 1, 10)

    actual = get_synonyms_from_ngrams.find_embeddings("gutem", "AZ", "nach", 1, 2, 100, 1, 10)

    actual = get_synonyms_from_ngrams.find_embeddings("die", "VCS", "", 3, 1, 100, 1, 10)

    expected = []

    assert set(expected).issubset(actual)


    actual = get_synonyms_from_ngrams.find_embeddings("re", "OL", "", 5, 1, 100, 6, 10)
    expected = []
    assert set(expected).issubset(actual)


    actual = get_synonyms_from_ngrams.find_embeddings("*", "PDU", "*", 10, 3, 50, 1, 5)
    expected = []
    assert set(expected).issubset(actual)

    # actual = get_synonyms_from_ngrams.find_embeddings("*", "EKG", "*", 10, 3, 50, 1, 5)
    # expected = ['0000019\tPhysikalischer Status']
    # assert set(expected).issubset(actual)

    # li = find_embeddings("", "morph.", "", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = find_embeddings("Mitralklappe", "morph.", "*", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = find_embeddings("", "morph.", "", ngramstat, index, 18, 3, 1000, 1, 1)
    # li = find_embeddings("", "morph.", "unauff.", ngramstat, index, 18, 3, 1000, 3, 7)
    # li = find_embeddings("*", "ms", "*", ngramstat, index, 8, 30, 500, 1, 5)
    # li = find_embeddings("Ð,Ð", "ms", "", ngramstat, index, 8, 3, 500, 1, 7)
    # out = (Filters.bestAcronymResolution("OL", li, normalisedTokens, "AA", ""))

    # Parms: minWinSize, minfreq, maxcount, minNumberTokens, maxNumberTokens
    # logger.debug(find_embeddings("TRINS", ngramstat, index, 1, 3, 10, 6))
    # logger.debug(find_embeddings("HRST", ngramstat, index, 15, 3, 20, 6)) # wird nicht gefunden!
    # logger.debug(find_embeddings("ACVB", ngramstat, index, 15, 3, 10, 9))# wird
    # nicht gefunden!

    # logger.debug(find_embeddings("Rö-Thorax", ngramstat, index, 10, 1, 20, 3)) #
    # wird gefunden!

    # logger.debug(find_embeddings("TRINS", ngramstat, index, 15, 1, 50, 3))
    # logger.debug(find_embeddings("TRINS", ngramstat, index, 15, 1, 100, 3))
    # logger.debug(find_embeddings("koronare Herzkrankheit", ngramstat, index, 20, 1, 100, 5))
    # logger.debug(find_embeddings("re OL", ngramstat, index, 5, 1, 100, 6)) # OL
    # kommt nur 4 mal vor !

    # logger.debug(find_embeddings("Herz- und", ngramstat, index, 20, 1, 100, 5))
    # logger.debug(find_embeddings("lab. maj", ngramstat, index, 20, 3, 100, 5, 6))

    # logger.debug(find_embeddings("gutem", "AZ", "nach Hause", ngramstat, index, 10, 3, 100, 3, 7))

    # logger.debug(find_embeddings("*", "PDU", "*", 10, 3, 50, 1, 5))
