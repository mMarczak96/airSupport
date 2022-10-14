# Start

Start of my first git project that will combine bunch of tools to develop app that will be able to handle aerodynamic numerical investigation

git commands 

git status - checking changes between local and online repository
git add - adding wanted files to the commit ("git add ." - adds all new files)
git reset or git reset <file_name> - removing changes from commit
git commit -m "title" -m "message" - creating a local commit
git reset HEAD~1 - uncommiting last change
git push - sending commit to the online repository
git pull - updates local repository 
git branch - checks on which branch we are currently working on
git branch -d <branch_name> - delating branch
git checkout <branch_name> - changing branches
git checkout - b <branch_name> - creating new branch 
git diff <branch_name> - checking differences between current and given branch
git merge <branch_name> - merging current and given branch
git log - list of all commits, we can get git hash (inividual git number, that can be later use to reset git)
git reset <hash_number> - reseting to wanted version of repository

docker commands

docker run 'image' - runs given image e.g nginx (used only once)
docker run 'image':4.0 - runs given image in wanted version  
docker run -it 'image'- allows interactive terminal in docker
docker ps - list all running containers
docker ps -a -lst both running and stopped containers 
docker inspect 'name' - more detialied info about container
docker stop 'name' - stop given container 
docker rm 'name' - stops and remove given container
docker images - list of all imgaes running on docker 
docker rmi 'image' eg.nginx - remove given image
docker pull 'image' - download and image 
docker run -d 'command' - runs command in detached mode 
docker attach 'id' - attaches command with given id 
docker run -v /'directory':/'command' 'command' - stores data from command in to docker directory
docker logs 'name' - lost logs from a container

remarks:
container lives as long as a procecess running on it
when id of a command is needed only first few symbols are necessary that the id will differ from others
