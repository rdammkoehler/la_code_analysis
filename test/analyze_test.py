from trendy import analyze


def test_given_no_input_return_undetermined():
    assert analyze(None) == 'undetermined'


def test_given_empty_input_return_undetermined():
    assert analyze([]) == 'undetermined'


def test_given_too_little_data_return_undetermined():
    assert analyze([(0, 0)]) == 'undetermined'


def test_given_data_trending_up_return_problematic():
    # so for some reason this was creating numpy.linalg.LinAlgError: Singular matrix
    # by taking 0,0 out we fixed it
    # now the issue is finding 'up' in the analysis results, so the prod code
    assert analyze([(1, 2), (2, 4), (3, 8), (4, 16), (5, 32)]) == 'problematic'


# todo more here about problematic data

def test_given_data_trending_down_return_satisfactory():
    assert analyze([(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)]) == 'satisfactory'


# todo more here about satisfactory data

def test_given_consistent_data_return_satisfactory():
    assert analyze([(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)]) == 'satisfactory'


# todo more here about satisfactory data from consistency
