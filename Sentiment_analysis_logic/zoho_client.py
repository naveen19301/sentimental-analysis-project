import requests
from datetime import datetime, timedelta
import utils

class ZohoDeskClient:
    def __init__(self, config):
        self.config = config
        self.access_token = None
        self.token_expiry = None
        self.org_id = config['ORG_ID']

    def generate_access_token(self):
        url = "https://accounts.zoho.in/oauth/v2/token"
        params = {
            "refresh_token": self.config['REFRESH_TOKEN'],
            "client_id": self.config['CLIENT_ID'],
            "client_secret": self.config['CLIENT_SECRET'],
            "grant_type": "refresh_token"
        }
        response = requests.post(url, params=params).json()
        self.access_token = response.get("access_token")
        self.token_expiry = datetime.now() + timedelta(minutes=50)
        return self.access_token

    def get_valid_token(self):
        if self.access_token is None or self.token_expiry is None or datetime.now() >= self.token_expiry:
            return self.generate_access_token()
        return self.access_token

    def zoho_get(self, url):
        token = self.get_valid_token()
        headers = {"Authorization": f"Zoho-oauthtoken {token}", "orgId": self.org_id}
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            token = self.generate_access_token()
            headers = {"Authorization": f"Zoho-oauthtoken {token}", "orgId": self.org_id}
            response = requests.get(url, headers=headers)
        return response.json()

    def get_ticket_by_number(self, ticket_number):
        url = f"https://desk.zoho.in/api/v1/tickets/search?ticketNumber={ticket_number}"
        return self.zoho_get(url)

    def get_threads_list(self, ticket_id):
        url = f"https://desk.zoho.in/api/v1/tickets/{ticket_id}/threads"
        return self.zoho_get(url)

    def get_thread_full(self, ticket_id, thread_id):
        url = f"https://desk.zoho.in/api/v1/tickets/{ticket_id}/threads/{thread_id}"
        return self.zoho_get(url)

    def extract_full_threads(self, ticket_id, thread_list, contact_name):
        inbound = []
        outbound = []

        if "data" not in thread_list:
            return inbound, outbound

        for t in thread_list["data"]:
            thread_id = t["id"]
            try:
                full_thread = self.get_thread_full(ticket_id, thread_id)

                content = (
                    full_thread.get("content") or
                    full_thread.get("description") or
                    full_thread.get("body") or ""
                )

                author = (
                    full_thread.get("author", {}).get("name") or
                    full_thread.get("createdBy", {}).get("name") or ""
                )

                if contact_name and contact_name.lower() in author.lower():
                    text = utils.extract_fresh_message(content)
                    if text and len(text) > 5:
                        inbound.append(text)
                else:
                    text = utils.extract_full_text(content)
                    if text and len(text) > 5:
                        outbound.append(text)

            except Exception as e:
                print(f"      ⚠️ Thread error: {e}")
                continue

        return inbound[::-1], outbound[::-1]
