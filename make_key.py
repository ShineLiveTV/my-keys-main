import datetime
import os

def main():
    os.system('clear')
    print("\033[96m" + "="*40)
    print("      SHINE KOKO KEY GENERATOR")
    print("="*40 + "\033[0m")
    
    key_name = input("\033[97m[?] Enter Key Name (e.g. SHINE-VIP-01): \033[0m")
    
    print("\n[ Select Duration ]")
    print("[1] 1 Hour")
    print("[2] 3 Hours")
    print("[3] 5 Hours")
    print("[4] 1 Day")
    print("[5] 3 Days")
    print("[6] 7 Days")
    print("[7] 15 Days")
    print("[8] 30 Days")
    
    choice = input("\033[97m\n[?] Choice: \033[0m")
    
    durations = {
        "1": 1, "2": 3, "3": 5, "4": 24,
        "5": 72, "6": 168, "7": 360, "8": 720
    }
    
    if choice in durations:
        hours = durations[choice]
        expiry = datetime.datetime.now() + datetime.timedelta(hours=hours)
        expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
        
        final_line = f"{key_name} | {expiry_str}"
        
        print("\033[92m" + "\n" + "="*40)
        print(" SUCCESS! COPY THE LINE BELOW:")
        print("="*40 + "\033[0m")
        print(f"\n\033[93m{final_line}\033[0m\n")
        print("\033[96m" + "="*40)
        print(" Paste this line into keys.txt on GitHub")
        print("="*40 + "\033[0m")
    else:
        print("\033[91m[!] Invalid Choice!\033[0m")

if __name__ == "__main__":
    main()
