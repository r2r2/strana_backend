#!/bin/bash

echo -e '\n\n\t\t \033[34m ======Deploy script===== \033[37m  '

if [[ ! -z $1 ]]; then
  echo -e '\nusing images tag: \033[31m'$1'\033[37m\n\n'
  tagd=$1
else
 echo -e 'no input image tag \nInsert docker image tag: '
 #read tagd
   #tagd="6db626ef072823ab1b2ed159bb7b837abfa8095a"
  echo 'using latest'
    tagd='latest'
fi


cd /var/www/strana
docker login itpro72.ru:5050 > /dev/null 2>&1


echo -e 'Deploy to \033[32m  __ARTW_dev \033[36m '$tagd'  tag.\033[37m Yes? '; read p
if [[ $(echo ${p:0:1} | tr '[:upper:]' '[:lower:]') == 'y' ]]; then
 TAG=$tagd docker-compose -f docker-compose.yml  -f docker-compose.production.yml pull frontend
 TAG=$tagd docker-compose -f docker-compose.yml  -f docker-compose.production.yml up -d frontend
fi

echo -e 'Deploy to \033[31m  __STRANA_prod \033[36m '$tagd'tag.\033[37m Yes? '; read p
if [[ $(echo ${p:0:1} | tr '[:upper:]' '[:lower:]') == 'y' ]]; then
  eval `ssh-agent -s`
  ssh-add ssh/artw_strana
  TAG=$tagd DOCKER_HOST="ssh://bb-idaproject@strana.com" docker-compose -f docker-compose.yml -f docker-compose.frontend.yml -f docker-compose.production.yml --env-file .env_prod pull frontend
  TAG=$tagd DOCKER_HOST="ssh://bb-idaproject@strana.com" docker-compose -f docker-compose.yml -f docker-compose.frontend.yml -f docker-compose.production.yml --env-file .env_prod up -d frontend
fi
