import requests

class SQLClient:
    def __init__(self, host='localhost', port=8000):
        self.base_url = f"http://{host}:{port}"

    def repl(self):
        try:
            while True:
                command = input("sql> ").strip()
                if command.lower() in ['exit', 'quit']:
                    print("Exiting.")
                    break
                response = self.send_command(command)
                if 'error' in response:
                    print(f"Error: {response['error']}")
                else:
                    print(response['result'])
        except KeyboardInterrupt:
            print("\nExiting.")

    def send_command(self, command):
        try:
            response = requests.post(
                f"{self.base_url}/execute",
                json={"command": command}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': response.json().get('detail', 'Unknown error')}
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

def main():
    client = SQLClient()
    client.repl()

if __name__ == '__main__':
    main()
