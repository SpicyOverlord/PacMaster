# Connect
### Connect to Server
```shell
ssh root@192.168.1.50
```

### Connect to Tmux Tournament Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantour'
```
### Connect to Tmux Snapshot Sessions
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanDataCollector1'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanDataCollector2'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanDataCollector3'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanDataCollector4'
```

# Sync
### Push to Linux server
```shell
git add --all && git commit -m "update" && git push
ssh -t root@192.168.1.50 'cd /root/PacMaster; git pull'
```

### Copy Tournament data to local machine
```shell
rsync -avz --progress root@192.168.1.50:/root/PacMaster/Tournaments/ /Users/frederik/Home/Python/PacMaster/Tournaments
```

### Copy gamestate data to local machine
```shell
rsync -avz --progress root@192.168.1.50:/root/PacMaster/Data/ /Users/frederik/Home/Python/PacMaster/Data
```