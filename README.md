# Frederik B. (frbb@itu.dk)

---

# 5 Minute presentation:
> https://drive.google.com/file/d/1lQ5iYVe0KQHBBjeMQgUEvDjMGf1XIuAQ/view?usp=drive_link

For better quality, watch the mp4 file in the folder.
# To run my agent run the following command:
```shell
python3 runner.py
```
You can also run the normal run.py file in the Pacman_Complete folder, but it might not work.

# Paths to code:
### My QLearning agent code
> PacmanAgentBuilder/Agents/QLearningAgent.py

> PacmanAgentBuilder/Qlearning/QValueStore.py
### Genetic algorithm (modified for QLearning reward functions)
> TournamentRunner.py

---

# Connect
### Connect to Server
```shell
ssh root@192.168.1.50
```

### Connect to Tmux Tournament Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantour'
```
### Connect to Tmux Sessions
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanQLearn1'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanQLearn2'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanQLearn3'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanQLearn4'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanQLearn5'
```
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmanQLearn6'
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

### Copy Snapshop data to local machine
```shell
rsync -avz --progress root@192.168.1.50:/root/PacMaster/Data/ /Users/frederik/Home/Python/PacMaster/Data
```

### Copy QLearning data to local machine
```shell
rsync -avz --progress root@192.168.1.50:/root/PacMaster/QLearningData/ /Users/frederik/Home/Python/PacMaster/QLearningData/
```