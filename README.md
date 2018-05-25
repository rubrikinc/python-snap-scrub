# python-snap-scrub  
This script will search the defined Rubrik cluster for a file on a defined VM. It will then provide feedback on the snapshots in which the file resides. Finally the user has the option to trigger deletes of the relevant snapshots from Rubrik. These deletes then are queued on Rubrik and they will be completely removed from all targets by Rubrik internal processes. 

## Setup .creds within the script path
```
{
	"cluster1": {
        	"servers":["IP","IP","IP","IP"],
        	"username": "user",
        	"password": "pw"
	}
}
```

## Usage TXT
```
> python .\snap_scrub.py --help
usage: snap_scrub.py [-h] -c
                     {Options defined in .creds} -v
                     VM -f FILENAME

optional arguments:
  -h, --help            show this help message and exit
  -c {Options defined in .creds}, --cluster {Options defined in .creds}
                        Choose a cluster in .creds
  -v VM, --vm VM        VM Name
  -f FILENAME, --filename FILENAME
                        File Name to Scrub
```

## Running the script - files being scrubbed
```
> python .\snap_scrub.py -c devops1 -v devops-vro -f cron-20180525.bz2
VM Details
        VM Name : devops-vro
        VM ID : VirtualMachine:::fbcb1f51-9520-4227-a68c-6fe145982f48-vm-128
        SLA : Gold (388a473c-3361-42ab-8f5b-08edb76891f6)
Snapshot Details
        Snaps for devops-vro : 67
        Snaps with cron-20180525.bz2 : 2

*** Remove 2 snapshot(s) for Virtual Machine devops-vro ? (Type YES) : YES

SLA Domain reassigned for snapshot removal : Unprotected (UNPROTECTED)

        Marking Snapshot for deletion : 9055700b-3183-457c-afcf-749e03f126c2
        Marking Snapshot for deletion : 7dfc7ccb-58c2-4e52-b060-2dade31ea72a

SLA Domain reassigned to resume protection : Gold (388a473c-3361-42ab-8f5b-08edb76891f6)
Complete
```

## Running the script - files already scrubbed
```
> python .\snap_scrub.py -c devops1 -v devops-vro -f cron-20180525.bz2
VM Details
        VM Name : devops-vro
        VM ID : VirtualMachine:::fbcb1f51-9520-4227-a68c-6fe145982f48-vm-128
        SLA : Gold (388a473c-3361-42ab-8f5b-08edb76891f6)
Snapshots of devops-vro with file cron-20180525.bz2 have been scrub
```