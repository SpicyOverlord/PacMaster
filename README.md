# Connect
### Connect to Server
```shell
ssh root@192.168.1.50
```

### Connect to Tmux Tournament Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantour'
```

# Sync
### Push
```shell
git add --all && git commit -m "update" && git push
```
### pull from Linux server
```shell
ssh -t root@192.168.1.50 'cd /root/PacMaster; git pull'
```

### Copy Tournament data to local machine
```shell
scp -r root@192.168.1.50:/root/PacMaster/Tournaments /Users/frederik/Home/Python/PacMaster
```