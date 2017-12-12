import pytest
import os

from numerapi.numerapi import NumerAPI


@pytest.fixture(name='api', scope='function')
def fixture_for_api():
    public_id = os.environ.get('NUMERAI_PUBLIC_ID', None)
    secret_key = os.environ.get('NUMERAI_SECRET_KEY', None)
    return NumerAPI(public_id=public_id, secret_key=secret_key, verbosity='DEBUG')


def test_get_competitions(api: NumerAPI):
    # get all competions
    res = api.get_competitions()
    assert isinstance(res, list)
    assert len(res) > 80


"""
# don't test downloading in integration test, it's ~150MB; api logic for download is tested with MockManager
def test_download_current_dataset(api: NumerAPI):
    path = api.download_current_dataset(unzip=True)
    assert os.path.exists(path)

    directory = path.replace(".zip", "")
    filename = "numerai_tournament_data.csv"
    assert os.path.exists(os.path.join(directory, filename))
"""


def test_get_current_round(api: NumerAPI):
    current_round = api.get_current_round()
    assert current_round >= 82


def test_raw_query(api: NumerAPI):
    query = "query {dataset}"
    result = api.manager.raw_query(query)
    assert isinstance(result, dict)
    assert "data" in result


def test_get_leaderboard(api: NumerAPI):
    lb = api.get_leaderboard(67)
    assert len(lb) == 1425


def test_get_staking_leaderboard(api: NumerAPI):
    stakes = api.get_staking_leaderboard(82)
    # 115 people staked that round
    assert len(stakes) == 115


def test_get_submission_ids(api: NumerAPI):
    ids = api.get_submission_ids()
    assert len(ids) > 0
    assert isinstance(ids, dict)


def test_error_handling(api: NumerAPI):
    # String instead of Int
    with pytest.raises(ValueError):
        api.get_leaderboard("foo")
    # round that doesn't exist
    with pytest.raises(ValueError):
        api.get_leaderboard(-1)
    # unauthendicated request
    with pytest.raises(ValueError):
        # set wrong token
        api.token = ("foo", "bar")
        api.submission_id = 1
        api.submission_status()