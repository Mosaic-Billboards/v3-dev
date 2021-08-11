# RPI configuration

# install system 

sudo apt-get update -y
sudo apt-get install network-manager -y

# sign into github
# clone repo into /usr/bin/hagrid
# sign out of github

# install python modules

sudo pip3 install firebase_admin --no-input
sudo pip3 install dbus-python --no-input
sudo pip3 install requests --no-input
sudo pip3 install Pillow --no-input
sudo pip3 install pytz --no-input
sudo pip3 install wifi --no-input
sudo pip3 install cgi --no-input
sudo pip3 install numpy --no-input
sudo pip3 install gobject --no-input
sudo pip3 install python-dotenv --no-input
sudo pip3 install "python-dotenv[cli]" --no-input

# setup cron jobs
crontab -l > mycron
echo "* * * * * /usr/bin/bash /usr/bin/hagrid/jobs/ping.sh" >> mycron
echo "*/50 * * * * /usr/bin/bash /usr/bin/hagrid/jobs/auth.sh" >> mycron
echo "0 * * * * /usr/bin/bash /usr/bin/hagrid/jobs/firmware.sh" >> mycron
echo "*/5 * * * * /usr/bin/bash /usr/bin/hagrid/jobs/fetch_handle_owner_ads.sh" >> mycron
echo "0 */4 * * * /usr/bin/bash /usr/bin/hagrid/jobs/fetch_handle_ads.sh" >> mycron
crontab mycron
rm mycron

# set up systemd services

systemd_path="/etc/system/systemd"
services_path="/usr/bin/hagrid/services"

hagrid_init_path = "$services_path/hagrid_init.sh"
hagrid_online_path "$services_path/hagrid_online.sh"

cp $hagrid_init_path "$systemd_path/hagrid_init.sh"
cp $hagrid_online_path "$systemd_path/hagrid_online.sh"

sudo systemctl daemon-reload
sudo systemctl enable hagrid_init.service
sudo systemctl enable hagrid_online.service

# remove this install file and reset system
sh reset.sh
