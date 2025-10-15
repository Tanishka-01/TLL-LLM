#!/usr/bin/env bash

# https://jitsi.support/how-to/run-jitsi-on-linux-setup-guide/

echo "set hostname to be meet.jitsi.local"

# update system
sudo apt update && sudo apt upgrade -y

# install jitsi meet
sudo apt install wget
wget -qO - https://download.jitsi.org/jitsi-key.gpg.key | sudo apt-key add -
echo "deb https://download.jitsi.org stable/" | sudo tee /etc/apt/sources.list.d/jitsi-stable.list
sudo apt update
sudo apt install jitsi-meet

echo "127.0.0.1 meet.jitsi.local" >> /etc/hosts # adds jitsi domain to host list

# configure nginx and ssl (doesn't work so idk)
#sudo apt install certbot
#sudo certbot --nginx -d meet.jitsi.local
#sudo crontab << "0 1 * * * /usr/bin/certbot renew --quiet"
