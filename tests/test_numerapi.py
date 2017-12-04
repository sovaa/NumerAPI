from zope.interface import implementer
import pytest
import shutil
import errno
import os

from numerapi import NumerAPI
from numerapi.manager import IManager

SAMPLE_DATA_SET_PATH = 'tests/data/numerai_dataset.zip'
SAMPLE_DATA_DIR = 'tests/data/'
SAMPLE_TRAIN_FILE = 'sample_training.csv.bz2'
SAMPLE_TOURN_FILE = 'sample_tournament.csv.bz2'
SAMPLE_RESULT_FILE = 'sample_result.csv.bz2'

NAME_TRAIN_CSV = 'numerai_training_data.csv'
NAME_TOURN_CSV = 'numerai_tournament_data.csv'


@implementer(IManager)
class MagicManager(object):
    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        try:
            os.makedirs(dest_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        if not os.path.exists(dataset_path):
            shutil.copy(SAMPLE_DATA_SET_PATH, dataset_path)

    def raw_query(self, query, variables=None, authorization=False):
        # TODO: should be split into separate methods so we know what to test for
        pass


def test_magic_manager_download():
    manager = MagicManager()
    import tempfile

    with tempfile.TemporaryDirectory() as dest_path:
        dataset_path = os.path.join(dest_path, 'thedata.zip')
        assert not os.path.exists(dataset_path)

        manager.download_data_set(dest_path, dataset_path)
        assert os.path.exists(dataset_path)


"""
def test_get_competitions():
    api = NumerAPI()

    # get all competions
    res = api.get_competitions()
    assert isinstance(res, list)
    assert len(res) > 80


def test_download_current_dataset():
    api = NumerAPI()
    path = api.download_current_dataset(unzip=True)
    assert os.path.exists(path)

    directory = path.replace(".zip", "")
    filename = "numerai_tournament_data.csv"
    assert os.path.exists(os.path.join(directory, filename))


def test_get_current_round():
    api = NumerAPI()
    current_round = api.get_current_round()
    assert current_round >= 82


def test_raw_query():
    api = NumerAPI()
    query = "query {dataset}"
    result = api.raw_query(query)
    assert isinstance(result, dict)
    assert "data" in result


def test_get_leaderboard():
    api = NumerAPI()
    lb = api.get_leaderboard(67)
    assert len(lb) == 1425


def test_get_staking_leaderboard():
    api = NumerAPI()
    stakes = api.get_staking_leaderboard(82)
    # 115 people staked that round
    assert len(stakes) == 115


def test_get_submission_ids():
    api = NumerAPI()
    ids = api.get_submission_ids()
    assert len(ids) > 0
    assert isinstance(ids, dict)


def test_error_handling():
    api = NumerAPI()
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
"""
