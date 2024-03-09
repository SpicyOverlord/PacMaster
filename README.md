
### Connect to Tmux Tournament Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantour'
```
### Copy Tournament data to local machine
```shell
scp -r root@192.168.1.50:/root/PacMaster/Tournaments /Users/frederik/Home/Python/PacMaster
```