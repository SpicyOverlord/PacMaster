# Frederik B. (frbb@itu.dk)

---

# 5 Minute presentation:
> https://drive.google.com/file/d/1Q-ctIKGCo6JXhtWkjPEUfm6CXZywABmc/view?usp=sharing

For better quality, watch the mp4 file in the folder.
# To run my agent run the following command:
```shell
python3 runner.py
```
You can also run the normal run.py file in the Pacman_Complete folder, but it might not work.

# Paths to code:
### My agent code
> /PacmanAgentBuilder/Agents/FinalAgent.py
### Pathfinding algorithm
> /PacmanAgentBuilder/Utils/Map.py (the calculateShortestPath() function)
### Genetic algorithm
> /TournamentRunner.py

> /PacmanAgentBuilder/Genetics/WeightModifier.py


---

# Server commands

## Connect
### Connect to Server
```shell
ssh root@192.168.1.50
```

### Connect to Tmux Tournament Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantour'
```
### Connect to Tmux Test Session
```shell
ssh -t root@192.168.1.50 'tmux attach -t pacmantest'
```

## Sync
### Push to Linux server
```shell
git add --all && git commit -m "update" && git push
ssh -t root@192.168.1.50 'cd /root/PacMaster; git pull'
```

### Copy Tournament data to local machine
```shell
rsync -avz --progress root@192.168.1.50:/root/PacMaster/Tournaments/ /Users/frederik/Home/Python/PacMaster/Tournaments
```