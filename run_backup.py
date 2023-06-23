from duplicati_client import main
import os
import time
from datetime import datetime
import sys
from common import clear_txt,txt_out

def get_last_success_last_error():
    parameters={'type':'backup','id':id_of_requested_backup}
    main('describe',**parameters)
    res=txt_out.copy()
    clear_txt()

    t=[x for x in res if '- Backup:' in x][0]
    parts=t.split('\n')

    backup_info={x.split(':')[0] : x.split(':')[1] for x in parts if ':' in x}
    backup_info={k.replace('-','').strip() : v.strip() for k,v in backup_info.items()}


    last_success=backup_info.get('LastBackupFinished')
    last_success=datetime.strptime(last_success,'%Y%m%dT%H%M%SZ') if last_success is not None else None
    last_error=backup_info.get('LastErrorDate')
    last_error=datetime.strptime(last_error,'%Y%m%dT%H%M%SZ') if last_error is not None else None 
    return last_success,last_error


if __name__ == '__main__':
    backup_name=sys.argv[1]
    timeout=int(sys.argv[2].strip())
    poll_interval=int(sys.argv[3].strip())

    login_pass=os.environ['DUPLICATI_PASS']
    host=os.environ['DUPLICATI_HOST']

    # write params file with pass
    with open('parameters.yml','w') as f:
        f.write('password: {0}\n'.format(login_pass))
        f.write('url: {0}\n'.format(host))


    # first set params file

    parameters={'param-file':'parameters.yml'}
    main('params',**parameters)
    clear_txt()


    # login 
    main('login')
    clear_txt()

    # enable precision output
    parameters={'mode':'enable'}
    main('precise',**parameters)
    res=txt_out.copy()
    clear_txt()

    # list all backups and get the one with backup_name
    parameters={'type':'backups'}
    main('list',**parameters)
    res=txt_out.copy()
    clear_txt()

    t=[x for x in res if 'ID:' in x][0]

    names=[x.replace('-','').strip()[:-1] for x in t.split('\n')[::2]]
    ids=[x.replace("'","").replace("ID:",'').strip() for x in t.split('\n')[1::2]]

    name_to_id_map={n:id_t for n,id_t in zip(names,ids)}


    id_of_requested_backup = name_to_id_map[backup_name]


    print("About to backup {0} with id {1}".format(backup_name,id_of_requested_backup))

    # parse dates of last success,last error
    last_success,last_error=get_last_success_last_error()
    print("LastBackupSuccess: {0} LastBackupError: {1}".format(last_success,last_error))



    #send backup job for id
    parameters={'id':id_of_requested_backup}
    main('run',**parameters)
    res=txt_out.copy()
    clear_txt()

    print("Running backup ...")

    exit_code=2

    # wait till timeout or if the last_success, last_error changes
    now=time.time()
    max_time=now + timeout
    while time.time() < max_time:

        new_success,new_error=get_last_success_last_error()
        if new_success > last_success:
            exit_code=0
            break
        if new_error > last_error:
            exit_code=1
            break
        time.sleep(poll_interval)

    if exit_code == 2:
        out_msg='TIMEOUT'
    elif exit_code == 1:
        out_msg='FAILURE'
    else:
        out_msg='SUCCESS'
    print("Ended backup with {0}".format(out_msg))

    sys.exit(exit_code)
