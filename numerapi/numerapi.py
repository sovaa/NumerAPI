# -*- coding: utf-8 -*-

import datetime
import errno
import logging
import os
import zipfile

from numerapi.api_manager import NumerApiManager
from numerapi.manager import IManager


class NumerAPI(object):
    """Wrapper around the Numerai API"""

    def __init__(self, public_id=None, secret_key=None, verbosity="INFO", manager: IManager = NumerApiManager()):
        """
        initialize Numerai API wrapper for Python

        public_id: first part of your token generated at
                   Numer.ai->Account->Custom API keys
        secret_key: second part of your token generated at
                    Numer.ai->Account->Custom API keys
        verbosity: indicates what level of messages should be displayed
            valid values: "debug", "info", "warning", "error", "critical"
        """
        if public_id and secret_key:
            token = (public_id, secret_key)
        elif not public_id and not secret_key:
            token = None
        else:
            print("You need to supply both a public id and a secret key.")
            token = None

        manager.set_token(token)
        self._manager = manager
        self.logger = logging.getLogger(__name__)

        # set up logging
        numeric_log_level = getattr(logging, verbosity.upper())
        if not isinstance(numeric_log_level, int):
            raise ValueError('invalid verbosity: %s' % verbosity)
        log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        logging.basicConfig(format=log_format, level=numeric_log_level)
        self.submission_id = None

    @property
    def manager(self) -> IManager:
        return self._manager

    @manager.setter
    def manager(self, manager: IManager):
        self._manager = manager

    def download_current_dataset(self, dest_path=".", dest_filename=None,
                                 unzip=True):
        """download dataset for current round

        dest_path: desired location of dataset file (optional)
        dest_filename: desired filename of dataset file (optional)
        unzip: indicates whether to unzip dataset
        """
        self.logger.info("downloading current dataset...")
        dest_filename, dataset_path = NumerAPI.get_download_paths(dest_path, dest_filename)

        if os.path.exists(dataset_path):
            self.logger.info("target file {} already exists".format(dataset_path))
        else:
            # create parent folder if necessary
            try:
                os.makedirs(dest_path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            self.manager.download_data_set(dataset_path)

        if unzip:
            unzip_dir_path = os.path.join(dest_path, dest_filename[:-4])
            if os.path.exists(unzip_dir_path):
                self.logger.info('destination unzip path already exists: {}'.format(dest_filename))
            else:
                self.unzip_data_set(dest_path, dataset_path, dest_filename)

        return dataset_path

    def unzip_data_set(self, dest_path: str, dataset_path: str, dest_filename: str) -> None:
        # remove the ".zip" in the end
        dataset_name = dest_filename[:-4]

        # construct full path (including file name) for unzipping
        unzip_path = os.path.join(dest_path, dataset_name)
        self.logger.info('unzipping {} to {}'.format(dataset_path, unzip_path))

        # create parent directory for unzipped data
        try:
            os.makedirs(unzip_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        with zipfile.ZipFile(dataset_path, "r") as z:
            z.extractall(unzip_path)

        import shutil
        tourn_file = '%s/numerai_dataset/numerai_tournament_data.csv' % unzip_path
        train_file = '%s/numerai_dataset/numerai_training_data.csv' % unzip_path

        assert os.path.exists(tourn_file)
        assert os.path.exists(train_file)

        shutil.move(
            tourn_file,
            '%s/numerai_tournament_data.csv' % unzip_path)
        shutil.move(
            train_file,
            '%s/numerai_training_data.csv' % unzip_path)

    @staticmethod
    def get_download_paths(dest_path: str, dest_filename: str) -> (str, str):
        # set up download path
        if dest_filename is None:
            now = datetime.datetime.now().strftime("%Y%m%d")
            dest_filename = "numerai_dataset_{0}.zip".format(now)
        else:
            # ensure it ends with ".zip"
            if not dest_filename.endswith(".zip"):
                dest_filename += ".zip"
        dataset_path = os.path.join(dest_path, dest_filename)

        return dest_filename, dataset_path

    def get_leaderboard(self, round_num: int = 0):
        """ retrieves the leaderboard for the given round

        round_num: The round you are interested in, defaults to current round.
        """
        if not isinstance(round_num, int):
            raise ValueError('type of round_num argument should be int but was "%s"' % str(type(round_num)))

        self.logger.info("getting leaderboard for round {}".format(round_num))
        result = self.manager.get_leaderboard(round_num)
        return result['data']['rounds'][0]['leaderboard']

    def get_staking_leaderboard(self, round_num=0):
        """ retrieves the leaderboard of the staking competition for the given
        round

        round_num: The round you are interested in, defaults to current round.
        """
        self.logger.info("getting stakes for round {}".format(round_num))
        result = self.manager.get_staking_leaderboard(round_num)
        stakes = result['data']['rounds'][0]['leaderboard']

        # filter those with actual stakes
        stakes = [item for item in stakes if item["stake"]["soc"] is not None]
        return stakes

    def get_competitions(self):
        """ get information about rounds """
        self.logger.info("getting rounds...")
        result = self.manager.get_competitions()
        return result['data']['rounds']

    def get_current_round(self):
        data = self.manager.get_current_round()
        round_num = data['data']['rounds'][0]["number"]
        return round_num

    def get_submission_ids(self):
        """get dict with username->submission_id mapping"""
        data = self.manager.get_submission_ids()
        data = data['data']['rounds'][0]['leaderboard']
        mapping = {item['username']: item['submissionId'] for item in data}
        return mapping

    def get_user(self):
        """get all information about you! """
        user = self.manager.get_user()
        return user['data']['user']

    def get_payments(self):
        """all your payments"""
        payments = self.manager.get_payments()
        return payments['data']['user']['payments']

    def get_transactions(self):
        """all deposits and withdrawals"""
        return self.manager.get_transactions()['data']['user']

    def get_stakes(self):
        """all your stakes"""
        return self.manager.get_stakes()['data']['user']['stakeTxs']

    def submission_status(self, submission_id=None):
        """display submission status of the last submission associated with
        the account

        submission_id: submission of interest, defaults to the last submission
            done with the account
        """
        if submission_id is None:
            submission_id = self.submission_id

        if submission_id is None:
            raise ValueError('You need to submit something first or provide a submission ID')

        data = self.manager.get_submission(submission_id)
        status = data['data']['submissions'][0]
        return status

    def upload_predictions(self, file_path):
        """uploads predictions from file

        file_path: CSV file with predictions that will get uploaded
        """
        self.logger.info("uploading prediction...")
        create = self.manager.upload_predictions(file_path)

        self.submission_id = create['data']['create_submission']['id']
        return self.submission_id

    def stake(self, confidence, value):
        """ participate in the staking competition

        confidence: your confidence (C) value
        value: amount of NMR you are willing to stake
        """
        # TODO: does not seem to be complete

        query = '''
          mutation($code: String,
            $confidence: String!
            $password: String
            $round: Int!
            $value: String!) {
              stake(code: $code
                    confidence: $confidence
                    password: $password
                    round: $round
                    value: $value) {
                id
                status
                txHash
                value
              }
        }
        '''
        arguments = {'code': 'somecode',
                     'confidence': str(confidence),
                     'password': "somepassword",
                     'round': self.get_current_round(),
                     'value': str(value)}
        result = self.manager.raw_query(query, arguments, authorization=True)
        return result
