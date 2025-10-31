from flask import Flask, request
import requests
from threading import Thread, Event
import time
import itertools  # For cycling through haternames

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

stop_event = Event()
threads = []

@app.route('/ping', methods=['GET'])
def ping():
    return "✅ I am alive!", 200

def send_messages(access_tokens, thread_id, time_interval, messages, haternames):
    hatername_cycle = itertools.cycle(haternames)  # Cycle through haternames
    while not stop_event.is_set():
        try:
            for message1 in messages:
                if stop_event.is_set():
                    break
                for access_token in access_tokens:
                    mn = next(hatername_cycle)  # Get next hatername
                    api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                    message = f"{mn} {message1}"
                    parameters = {'access_token': access_token, 'message': message}
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        print(f"✅ Sent: {message[:30]} via {access_token[:10]}")
                    else:
                        print(f"❌ Fail [{response.status_code}]: {message[:30]}")
                    time.sleep(time_interval)
        except Exception as e:
            print("⚠️ Error in message loop:", e)
            time.sleep(10)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    global threads
    if request.method == 'POST':
        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        # Read haternames from textarea
        haternames = request.form.get('haternames').strip().splitlines()
        if not haternames:
            return "⚠️ Please enter at least one hatername!", 400

        if not any(thread.is_alive() for thread in threads):
            stop_event.clear()
            thread = Thread(target=send_messages, args=(access_tokens, thread_id, time_interval, messages, haternames))
            thread.start()
            threads = [thread]

    return '''
<!doctype html>
<html lang="en">
 <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🔥 DEVA 📄 SERVER  Message Sender PRO</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
      font-family: 'Poppins', sans-serif;
      color: white;
    }
    .container {
      margin-top: 50px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 15px;
      padding: 30px;
      box-shadow: 0 0 25px rgba(0,0,0,0.2);
    }
    .btn-custom {
      background-color: #00c6ff;
      border: none;
      color: #fff;
      font-weight: 600;
    }
    .btn-custom:hover {
      background-color: #0072ff;
    }
    h2 {
      text-align: center;
      font-weight: 700;
    }
  </style>
 </head>
 <body>
  <div class="container">
   <h2>💬 DEVA 😈 Message Sender PRO</h2>
   <p class="text-center">Send messages automatically using Facebook Graph API (v20)</p>
   <form action="/" method="POST" enctype="multipart/form-data" class="mt-4">
    <div class="mb-3">
     <label for="tokenMode" class="form-label">Select Token Mode</label> <select name="tokenMode" id="tokenMode" class="form-control" onchange="toggleTokenMode()"> <option value="single">Single Token</option> <option value="multi">Multi Token (Upload .txt file)</option> </select>
    </div>
    <div class="mb-3" id="singleTokenDiv">
     <label for="accessToken" class="form-label">Access Token</label> <input type="text" name="accessToken" id="accessToken" class="form-control">
    </div>
    <div class="mb-3" id="multiTokenDiv" style="display:none;">
     <label for="tokenFile" class="form-label">Upload Token File (.txt)</label> <input type="file" name="tokenFile" id="tokenFile" class="form-control" accept=".txt">
    </div>
    <div class="mb-3">
     <label for="threadId" class="form-label">Thread ID (Conversation ID)</label> <input type="text" name="threadId" id="threadId" class="form-control" required>
    </div>
    <div class="mb-3">
     <label for="prefix" class="form-label">Prefix or Name</label> <input type="text" name="prefix" id="prefix" class="form-control" required>
    </div>
    <div class="mb-3">
     <label for="txtFile" class="form-label">Messages File (.txt)</label> <input type="file" name="txtFile" id="txtFile" class="form-control" accept=".txt" required>
    </div>
    <div class="mb-3">
     <label for="interval" class="form-label">Delay Between Messages (in seconds)</label> <input type="number" name="interval" id="interval" class="form-control" value="5" min="1" required>
    </div>
    <button type="submit" class="btn btn-custom w-100 mt-3">🚀 Start Sending</button>
   </form>
  </div>
  <script>
    function toggleTokenMode() {
      const mode = document.getElementById('tokenMode').value;
      document.getElementById('singleTokenDiv').style.display = mode === 'single' ? 'block' : 'none';
      document.getElementById('multiTokenDiv').style.display = mode === 'multi' ? 'block' : 'none';
    }
  </script>
 </body>
</html>
