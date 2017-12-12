import requests
import errno
import os
import logging

from zope.interface import implementer
from numerapi.manager import IManager

API_TOURNAMENT_URL = 'https://api-tournament.numer.ai'


@implementer(IManager)
class NumerApiManager(object):
    def __init__(self, api_url: str=API_TOURNAMENT_URL):
        self.api_url = api_url
        self.token = None
        self.logger = logging.getLogger(__name__)

    def _handle_call_error(self, errors):
        if isinstance(errors, list):
            for error in errors:
                if "message" in error:
                    self.logger.error(error['message'])
        elif isinstance(errors, dict):
            if "detail" in errors:
                self.logger.error(errors['detail'])

    def set_token(self, token: tuple):
        self.token = token

    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        url = self.get_link_to_current_dataset()

        # download
        dataset_res = requests.get(url, stream=True)
        dataset_res.raise_for_status()

        # create parent folder if necessary
        try:
            os.makedirs(dest_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # write dataset to file
        with open(dataset_path, "wb") as f:
            for chunk in dataset_res.iter_content(1024):
                f.write(chunk)

    def get_current_round(self) -> dict:
        """get information about the current active round"""
        # zero is an alias for the current round!
        query = '''
            query {
              rounds(number: 0) {
                number
              }
            }
        '''
        return self.raw_query(query)

    def get_submission_ids(self):
        query = """
            query {
              rounds(number: 0) {
                leaderboard {
                  username
                  submissionId
                }
            }
        }
        """
        return self.raw_query(query)

    def get_competitions(self) -> dict:
        query = '''
            query {
              rounds {
                number
                resolveTime
                datasetId
                openTime
                resolvedGeneral
                resolvedStaking
              }
            }
        '''
        return self.raw_query(query)

    def get_submission(self, submission_id: str) -> dict:
        query = '''
            query($submission_id: String!) {
              submissions(id: $submission_id) {
                originality {
                  pending
                  value
                }
                concordance {
                  pending
                  value
                }
                consistency
                validation_logloss
              }
            }
            '''
        variable = {'submission_id': submission_id}
        return self.raw_query(query, variable, authorization=True)

    def get_staking_leaderboard(self, round_num: int):
        query = '''
            query($number: Int!) {
              rounds(number: $number) {
                leaderboard {
                  consistency
                  liveLogloss
                  username
                  validationLogloss
                  stake {
                    insertedAt
                    soc
                    confidence
                    value
                    txHash
                  }

                }
              }
            }
        '''
        arguments = {'number': round_num}
        return self.raw_query(query, arguments)

    def get_link_to_current_dataset(self):
        query = "query {dataset}"
        return self.raw_query(query)['data']['dataset']

    def upload_predictions(self, file_path: str) -> dict:
        auth_query = \
            '''
            query($filename: String!) {
                submission_upload_auth(filename: $filename) {
                    filename
                    url
                }
            }
            '''
        variable = {'filename': os.path.basename(file_path)}
        submission_resp = self.raw_query(auth_query, variable, authorization=True)
        submission_auth = submission_resp['data']['submission_upload_auth']

        with open(file_path, 'rb') as fh:
            requests.put(submission_auth['url'], data=fh.read())

        create_query = \
            '''
            mutation($filename: String!) {
                create_submission(filename: $filename) {
                    id
                }
            }
            '''
        variables = {'filename': submission_auth['filename']}
        return self.raw_query(create_query, variables, authorization=True)

    def get_leaderboard(self, round_num: int) -> dict:
        query = '''
            query($number: Int!) {
              rounds(number: $number) {
                leaderboard {
                  consistency
                  concordance {
                    pending
                    value
                  }
                  originality {
                    pending
                    value
                  }

                  liveLogloss
                  submissionId
                  username
                  validationLogloss
                  paymentGeneral {
                    nmrAmount
                    usdAmount
                  }
                  paymentStaking {
                    nmrAmount
                    usdAmount
                  }
                  totalPayments {
                    nmrAmount
                    usdAmount
                  }
                }
              }
            }
        '''
        arguments = {'number': round_num}
        return self.raw_query(query, arguments)

    def get_payments(self):
        """all your payments"""
        query = """
          query {
            user {
              payments {
                nmrAmount
                round {
                  number
                  openTime
                  resolveTime
                  resolvedGeneral
                  resolvedStaking
                }
                tournament
                usdAmount
              }

            }
          }
        """
        return self.raw_query(query, authorization=True)
    
    def get_transactions(self):
        """all deposits and withdrawals"""
        query = """
          query {
            user {

              nmrDeposits {
                from
                id
                posted
                status
                to
                txHash
                value
              }
              nmrWithdrawals {
                from
                id
                posted
                status
                to
                txHash
                value
              }
              usdWithdrawals {
                ethAmount
                confirmTime
                from
                posted
                sendTime
                status
                to
                txHash
                usdAmount
              }
            }
          }
        """
        return self.raw_query(query, authorization=True)

    def get_stakes(self):
        """all your stakes"""
        query = """
          query {
            user {
              stakeTxs {
                confidence
                insertedAt
                roundNumber
                soc
                staker
                status
                txHash
                value
              }
            }
          }
        """
        return self.raw_query(query, authorization=True)

    def get_user(self):
        """get all information about you! """
        query = """
          query {
            user {
              username
              banned
              assignedEthAddress
              availableNmr
              availableUsd
              email
              id
              mfaEnabled
              status
              insertedAt
              apiTokens {
                name
                public_id
                scopes
              }
            }
          }
        """
        return self.raw_query(query, authorization=True)

    def raw_query(self, query, variables=None, authorization=False):
        """send a raw request to the Numerai's GraphQL API

        query (str): the query
        variables (dict): dict of variables
        authorization (bool): does the request require authorization
        """
        body = {'query': query,
                'variables': variables}
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        if authorization and self.token:
            public_id, secret_key = self.token
            headers['Authorization'] = \
                'Token {}${}'.format(public_id, secret_key)
        r = requests.post(self.api_url, json=body, headers=headers)
        result = r.json()
        if "errors" in result:
            self._handle_call_error(result['errors'])
            # fail!
            raise ValueError

        return result
