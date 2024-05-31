import os
from workflow import Workflow
import sys, subprocess
from argparse import ArgumentParser

backends = ["immich", "nextcloud", "ptpimg"]
pretty_names = {
    "immich" : "Immich",
    "nextcloud": "Nextcloud",
    "ptpimg": "ptpimg.me"
}
icons = {
    "immich" : "./90B8229C-1951-491E-86E3-6A3E854F8445.png",
    "nextcloud": "./B067A6DC-E67C-4FBB-AC5E-A1774A154167.png",
    "ptpimg": "./icon.png"
}
def parse_args():
    parser = ArgumentParser()
    # notify.notify is currently broken; use builtin alfred notification service instead
    #parser.add_argument('--notify', nargs='*', choices=backends.append("all"), default=None)
    parser.add_argument('--xml', nargs='*', choices=backends)
    #parser.add_argument('--info', default=None)
    r=parser.parse_args()
    if r.xml == []:
        r.xml = backends 
    return r

def main(wf):
    args = parse_args()

    # Standard logging for backends is that the last two lines are as folllows:
    # <source filepath> \n <0 if success else 1>;<Link URL if exists>
    def get_info(b):
        try:
            res = subprocess.run(
                ['tail', '-n', '2', wf.datafile(f'{b}.log')], capture_output=True
            ).stdout.decode().split('\n')
            res = res[:1] + res[1].split(';') 
            r = {
                "url": res[2] if res[2].startswith('http') else 'None',
                "filename": os.path.basename(res[0]),
                "status": "Success" if int(res[1]) == 0 else "Failure",
                "copytext": ''
            }
            if r['status'] == "Success" and r['url'] is not None: 
                r['copytext'] = "; ⌘C to copy URL"
            return r 
        except:
            return {
                "url":  'None',
                "filename": 'None',
                "status": "Failed to retrieve status data",
                "copytext": ''
            }
    info={ b: get_info(b) for b in backends}
    
    # if args.notify is not None:
    #     for b in args.notify:
    #         notify.notify(title=f"{b} upload", message=info[b][0])
    if args.xml is not None:
        for backend in args.xml:
            info_b = info[backend] 
            wf.add_item(  
                title=pretty_names[backend] + ': ' +  info_b['status'],
                icon=icons[backend],
                subtitle='File: ' + info_b['filename'] + info_b['copytext'],
                copytext=info_b['url'],
                valid=True if info_b['copytext'] != '' else False
            )
        wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow(libraries=['./libs'], update_settings={'github_slug': 'deafmute1/alfred-upload'})
    sys.exit(wf.run(main))