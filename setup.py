# The following is a setup script for the magic.

print """
    Now we are going to set up your email credentials so we can access
    your email and your calendar. Please enter your @gmail information.

    Your email credentials will be stored in a .txt file in this directory
    that our program will read from when pulling down your calendar/email
    information.

    We are ** not ** able to see your email or password.
"""

username = raw_input("Enter your email username (no @gmail.com): ")
password = raw_input("Enter your email password: ")

f = open("credentials.txt", "w+")
f.write(username + "\n")
f.write(password + "\n")
f.close()


print """
    credentials.txt created.

    The first line of credentials.txt is your email username, and
    the second line of the .txt file is your password.


    Now accessing your email and creating a checkpoint, so the program
    knows what emails are new vs. old.
"""

import skeleton
skeleton.create_connection()
skeleton.initialize_seen_email()

print """
        You should now be able to run the program by typing in the following:

        python skeleton.py
"""


