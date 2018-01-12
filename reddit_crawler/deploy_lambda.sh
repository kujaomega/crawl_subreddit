#!/bin/bash
aws_access_key_id_string=`cat $HOME/.aws/credentials | grep aws_access_key_id`
aws_secret_access_key_string=`cat $HOME/.aws/credentials | grep aws_secret_access_key`

IFS=' = ' read -ra KEYID <<< "$aws_access_key_id_string"
#echo "${KEYID[1]}"

IFS=' = ' read -ra AKEY <<< "$aws_secret_access_key_string"
#echo "${AKEY[1]}"

docker build -t server-less-deploy-subreddit-crawler -f Dockerfile .
docker run -e "AWS_SECRET_ACCESS_KEY=${AKEY[1]}" -e "AWS_ACCESS_KEY_ID=${KEYID[1]}" -ti server-less-deploy-subreddit-crawler
