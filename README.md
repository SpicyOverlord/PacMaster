### Comment to Server
```shell
ssh root@192.168.1.50
```

### Connect to Tmux Tournament Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantour'
```

### Git push from local machine
```shell
git add --all && git commit -m "update" && git push
```
### Git pull on server
```shell
ssh -t root@192.168.1.50 'cd /root/PacMaster; git pull'
```

### Copy Tournament data to local machine
```shell
scp -r root@192.168.1.50:/root/PacMaster/Tournaments /Users/frederik/Home/Python/PacMaster
```