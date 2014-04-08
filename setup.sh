echo "\nWelcome to Matt and Jay's Calendar Client"
echo ""
echo "Let's begin."
echo ""
echo ""
echo "You may be prompted for your password. This is to \ninstall the appropriate software to run the client."
echo ""

echo "Downloading pip, a python package installer"
sudo python get-pip.py

echo ""
echo ""
echo "Using pip to install all of the required packages."
sudo pip install -r requirements.txt

echo ""
echo ""
echo ""
echo "Installation complete! Now running the setup script."
python setup.py



