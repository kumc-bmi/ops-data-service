import os
import requests
import subprocess


class ApiClient:
    def __init__(self, project, awardee, pmi_account, service_account, key_file):
        self.project = project
        self.awardee = awardee
        self.pmi_account = pmi_account
        self.service_account = service_account
        self.key_file = key_file
        self.token = None

    def get_ip(self):
        ipv6 = subprocess.run(
            ["curl", "-6", "https://ifconfig.co"], capture_output=True, text=True)
        ipv4 = subprocess.run(
            ["curl", "-4", "https://ifconfig.co"], capture_output=True, text=True)
        print("IPv6:", ipv6.stdout.strip())
        print("IPv4:", ipv4.stdout.strip())

    def authenticate(self):
        subprocess.run([
            "gcloud", "-q", "auth", "activate-service-account",
            f"--key-file={self.key_file}"
        ], check=True)
        self.token = subprocess.run(
            ["gcloud", "-q", "auth", "print-access-token"], capture_output=True, text=True).stdout.strip()
        if self.token.startswith('ya'):
            print('Authentication Token Ready!')
        else:
            print('Authentication Token Error!')

    def get_headers(self):
        if not self.token:
            raise ValueError(
                "Token is not available. Run authenticate() first.")
        return {'content-type': 'application/json', 'Authorization': f'Bearer {self.token}'}

    def get_api_version(self):
        requests.packages.urllib3.util.connection.HAS_IPV6 = False
        url = 'http://all-of-us-rdr-stable.appspot.com/rdr/v1/'
        resp = requests.get(url, headers=self.get_headers())
        print(resp.json())

    def get_participant_summary(self, count=25):
        url = f'https://{self.project}.appspot.com/rdr/v1/ParticipantSummary?_sort=lastModified&_count={count}&awardee={self.awardee}'
        resp = requests.get(url, headers=self.get_headers())
        if not resp or resp.status_code != 200:
            print(resp.text)
            print(
                f'Error: api request failed.\n\n{resp.text if resp else "Unknown error."}')
        else:
            ps_data = resp.json()
            print(f'Success: retrieved {len(ps_data["entry"])} records.')


if __name__ == "__main__":
    project = os.getenv('PROJECT')
    awardee = os.getenv('AWARDEE')
    pmi_account = os.getenv('PMI_ACCOUNT')
    service_account = os.getenv('SERVICE_ACCOUNT')
    key_file = os.getenv('KEY_FILE')

    if not all([project, awardee, pmi_account, service_account, key_file]):
        raise EnvironmentError(
            "All environment variables (PROJECT, AWARDEE, PMI_ACCOUNT, SERVICE_ACCOUNT, KEY_FILE) must be set.")

    client = ApiClient(project, awardee, pmi_account,
                       service_account, key_file)
    client.get_ip()
    client.authenticate()
    client.get_api_version()
    client.get_participant_summary()
