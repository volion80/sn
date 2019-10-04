from config import Config
import clearbit
from pyhunter import PyHunter


def verify_email(email):
    hunter = PyHunter(Config.EMAIL_HUNTER_API_KEY)
    hunt_res = hunter.email_verifier(email)
    return hunt_res['result'] != 'undeliverable'


def lookup_user_data(email):
    data = {}
    clearbit.key = Config.CLEARBIT_API_KEY
    lookup = clearbit.Enrichment.find(email=email, stream=True)
    if lookup is not None:
        data['person'] = lookup['person']
        data['company'] = lookup['company']['name']
    return data
