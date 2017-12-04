from zope.interface import implementer
from uuid import uuid4 as uuid

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

    def get_leaderboard(self, _: int) -> dict:
        # TODO: only include submitted solutions during tests
        return {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "validationLogloss": 0.6818856968749493,
                    "username": "usigma03",
                    "totalPayments": {
                      "usdAmount": "0.00",
                      "nmrAmount": "18.85"
                    },
                    "submissionId": "3983e678-05df-4dc6-b494-0a04f6d1c1fb",
                    "paymentStaking": None,
                    "paymentGeneral": None,
                    "originality": {
                      "value": True,
                      "pending": False
                    },
                    "liveLogloss": None,
                    "consistency": 100,
                    "concordance": {
                      "value": True,
                      "pending": False
                    }
                  }
                ]
              }
            ]
          }
        }

    def get_submissions(self, submission_id: str) -> dict:
        # TODO: return true status from executor
        return {
            'data': {
                'submissions': [
                    {
                        'originality': {
                            'pending': True,
                            'value': None
                        },
                        'concordance': {
                            'pending': True,
                            'value': None
                        },
                        'consistency': True,
                        'validation_logloss': 0.693
                    }
                ]
            }
        }

    def upload_predictions(self, file_path: str) -> dict:
        # TODO: score and add to leaderboard
        submission_id = str(uuid())
        return {
            'data': {
                'create_submission': {
                    'id': submission_id
                }
            }
        }

    def raw_query(self, query, variables=None, authorization=False):
        raise NotImplementedError('do not call this method for this implementation')


def test_magic_manager_download():
    manager = MagicManager()
    import tempfile

    with tempfile.TemporaryDirectory() as dest_path:
        dataset_path = os.path.join(dest_path, 'thedata.zip')
        assert not os.path.exists(dataset_path)

        manager.download_data_set(dest_path, dataset_path)
        assert os.path.exists(dataset_path)


def test_get_leaderboard():
    api = NumerAPI(manager=MagicManager())
    lb = api.get_leaderboard(67)
    assert len(lb) > 0  # TODO: check our submission is here instead


def test_upload_predictions():
    # TODO: verify status of our upload is pending
    api = NumerAPI(manager=MagicManager())
    submission_id = api.upload_predictions('some/path.csv')
    assert len(submission_id.strip()) > 0


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
