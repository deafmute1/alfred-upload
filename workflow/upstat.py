from workflow import Workflow, notify
import sys, subprocess
from argparse import ArgumentParser

backends = ["immich", "nextcloud"]

def parse_args():
    parser = ArgumentParser()
    # notify.notify is currently broken; use builtin alfred notification service instead
    #parser.add_argument('--notify', nargs='*', choices=backends.append("all"), default=None)
    parser.add_argument('--xml', nargs='*', choices=backends, default=backends)
    parser.add_argument('--info', default=None)
    r=parser.parse_args()
    return r

def main(wf):
    args = parse_args()
    # Standard logging for backends is that the last two lines are as folllows:
    # <Status string describing success/failure with time> \n <Link URL if success if exists>
    def get_info(b):
        if args.info is not None: 
            return [args.info, "NULL"]
        try:
            return subprocess.run(
                ['tail', '-n', '2', wf.datafile(f'{b}.log')], capture_output=True
            ).stdout.decode().split('\n') 
        except:
            return ["Failed to read data for {b}", " "]
    info={ b: get_info(b) for b in backends}
    
    # if args.notify is not None:
    #     for b in args.notify:
    #         notify.notify(title=f"{b} upload", message=info[b][0])
    if args.xml is not None:
        xml = {
            "nextcloud": { 
                "title": info['nextcloud'][0],
                "icon": "./B067A6DC-E67C-4FBB-AC5E-A1774A154167.png",
                "subtitle": "Status of last nc upload via alfred; ⌘C to copy URL if available",
                "copytext": info['nextcloud'][1] if info['nextcloud'][1].startswith("http") else None
            },
            "immich": { 
                "title": info['immich'][0],
                "icon": "./90B8229C-1951-491E-86E3-6A3E854F8445.png",
                "subtitle": "status of last immich upload via alfred",
                "valid":False
            },  
        }
        for b in args.xml:
            wf.add_item(**xml[b])
        wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))