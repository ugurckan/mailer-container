import re
import smtplib
import sqlite3
from os.path import exists
from getpass import getpass
import email.utils
import msvcrt

# Checks if the database file already exists
if not exists("mailer_container.db"):
    # Creates a new database called mailer_container with a SQLite3 DB
    db = sqlite3.connect("mailer_container.db")

    # Gets a cursor object
    cursor = db.cursor()

    # Creates the "emails" table if it doesn't exist
    create_table = """CREATE TABLE IF NOT EXISTS emails (
                        name TEXT PRIMARY KEY,
                        surname TEXT,
                        Email_Address TEXT
                        );"""

    cursor.execute(create_table)

    # Closes the database connection after creating the table
    db.close()

# Opens the database connection using a context manager
with sqlite3.connect("mailer_container.db") as db:
    cursor = db.cursor()

    # Check if there is any existing data in the table
    cursor.execute("SELECT * FROM emails")
    existing_data = cursor.fetchone()

    if existing_data is None:
        # Request receiver details from the user
        name = input("Enter the new_receiver's name: ")
        surname = input("Enter the new_receiver's surname: ")
        Email_Address = input("Enter the new_receiver's email address: ")

        # Add the details to the table only if they are provided
        if name and surname and Email_Address:
            cursor.execute("INSERT INTO emails (name, surname, Email_Address) VALUES (?, ?, ?)",
                       (name, surname, Email_Address))
            db.commit()

# Closes the cursor and the database connection
cursor.close()
db.close()


# displays the asterisks instead of the password characters 
def get_password(prompt="Password: "):
    password = ""
    print(prompt, end="")
    while True:
        char = msvcrt.getch()
        if char == b"\r":
            break
        elif char == b"\x08":
            if password:
                password = password[:-1]
                print("\b \b", end="")
        else:
            password += char.decode("utf-8")
            print("*", end="")
    print()
    return password


# Checks either if the email is entered correctly or not
def valid_email(check):
    # Regular expression pattern for basic email format validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Checks if the email matches the pattern
    if re.match(pattern, check):
        return True
    else:
        return False

# this function logs in to user's email account.
# users have to give access from their email provider
# for example for gmail: https://myaccount.google.com/lesssecureapps
# users can generate a valid password up to the app and up to the device from: 
# https://myaccount.google.com/apppasswords


def login(return_to_menu=False):
    print("\n            ___________________________________________\n")
    print("\n            ----- Welcome to Multiple Email Sender -----\n")
    print("            _________________  Login  _________________\n\n")

    while True:
        try:
            sender_email = str(input("""  Please enter your email address from the email providers listed below: 
- hotmail.com
- gmail.com
- icloud.com
- yahoo.com

: """)).lower()
            while True:
                if valid_email(sender_email):
                    break
                else:
                    sender_email = str(input("  Please enter a valid email address: "))
                    continue

            password = get_password("Please enter your password: ")
            print("\n  Please wait! Logging in")

            # Declares the server variable with a default value
            server = None

            while True:
                try:
                    if sender_email == "":
                        print("Please enter an email!")
                    elif sender_email[-11:] == "hotmail.com":
                        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
                    elif sender_email[-9:] == "gmail.com":
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                    elif sender_email[-10:] == "icloud.com":
                        server = smtplib.SMTP("smtp.mail.me.com", 587)
                    elif sender_email[-9:] == "yahoo.com":
                        server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
                    else:
                        print("Please enter your email address from the email providers listed below:\n"
                              "hotmail.com\n"
                              "gmail.com\n"
                              "icloud.com\n"
                              "yahoo.com\n")
                        continue

                    # Encrypts the traffic
                    server.starttls()
                    server.login(sender_email, password)
                    print("\n  Logged in successfully")

                    # Attempts to login using the provided email and password
                    server.login(sender_email, password)
                except smtplib.SMTPAuthenticationError:
                    print("\n  Login failed! Please check your username and password!\n")
                    password = get_password("Please re-enter your password: ")
                    continue
                except smtplib.SMTPException as e:
                    print("\n  An error occurred during login:", str(e))
                    continue
                return sender_email, password

        except KeyboardInterrupt:
            print("\n  Login process interrupted.")

        if return_to_menu:
            return  # Return only if `return_to_menu` is True
        
        return sender_email, password


# Adds a new receiver to the database
def add_new_email():
    new_name = str(input("Please enter the name of the receiver: ")).capitalize()
    new_surname = str(input("Please enter the surname of the receiver: ")).capitalize()

    while True:
        new_email = str(input("Please enter an email address to add to the database: ")).lower()
                    
        if valid_email(new_email):
            break
        else:
            new_email = str(input("Please enter a valid email address!"))
            continue

    with sqlite3.connect("mailer_container.db") as db:
        cursor = db.cursor()

        # Checks if the receiver already exists in the database
        cursor.execute("SELECT * FROM emails WHERE name = ?", (new_name,))
        existing_receiver = cursor.fetchone()

        if existing_receiver:
            print("\nReceiver already exists in the database!")
        else:
            # Inserts the new receiver into the table
            cursor.execute("INSERT INTO emails (name, surname, Email_Address) VALUES (?, ?, ?)",
                           (new_name, new_surname, new_email))
            db.commit()
            print(f"\n{new_name} {new_surname} is added to the contact list successfully")

    return main()


# Removes a receiver from the database
def delete_receiver():
    with sqlite3.connect("mailer_container.db") as db:
        cursor = db.cursor()

        list_all_receivers(return_to_menu=False)
        # Requests the index number of the receiver to remove from the database
        delete_index = int(input("Please enter the index number of the receiver you would like to remove from the database: "))

        cursor.execute("SELECT * FROM emails")
        receivers = cursor.fetchall()

        # Checks if the index is within the valid range
        if 1 <= delete_index <= len(receivers):
            receiver_to_remove = receivers[delete_index - 1][0]

            # Deletes the data from the database
            cursor.execute("DELETE FROM emails WHERE name = ?", (receiver_to_remove,))
            db.commit()
            print(f"\n{receiver_to_remove} is removed from the database successfully!")
        else:
            print(f"\nInvalid index number! Please make sure you entered a valid number.")

    return main()


# Updates a receiver's details
def update_receiver():
    with sqlite3.connect("mailer_container.db") as db:
        cursor = db.cursor()

        list_all_receivers(return_to_menu=False)
        # Requests the index number of the receiver to update the details
        update_index = int(input("Please enter the index number of the receiver that you want to update: "))

        cursor.execute("SELECT * FROM emails")
        receivers = cursor.fetchall()

        # Checks if the index is within the valid range
        if 1 <= update_index <= len(receivers):
            receiver_to_update = receivers[update_index - 1]

            # Extracts the current details of the receiver
            current_name, current_surname, current_email = receiver_to_update

            # Requests new inputs to update
            new_name = str(input("Please enter the new name: ")).capitalize()
            new_surname = str(input("Please enter the new surname: ")).capitalize()

            while True:
                new_email = str(input("Please enter the new email address: ")).lower()
                if valid_email(new_email):
                    break
                else:
                    print("Please enter a valid email address!")
                    continue

            # Executes the update query
            cursor.execute("UPDATE emails SET name = ?, surname = ?, Email_Address = ? WHERE name = ?",
                           (new_name, new_surname, new_email, current_name))
            db.commit()

            # Prints the details of the updated receiver
            cursor.execute("SELECT * FROM emails WHERE name = ?", (new_name,))
            updated_receiver = cursor.fetchone()

            if updated_receiver:
                updated_name, updated_surname, updated_email = updated_receiver
                print("\nDatabase updated!\n")
                print("Details of the updated receiver:")
                print(f"Name:    {updated_name}")
                print(f"Surname: {updated_surname}")
                print(f"Email:   {updated_email}")
            else:
                print("\nFailed to update the receiver!")
        else:
            print("\nInvalid index number! Please make sure you entered a valid number.")

    return main()


# Lists all of the receivers in the database
def list_all_receivers(return_to_menu=True):
    with sqlite3.connect("mailer_container.db") as db:
        cursor = db.cursor()

        print("\nReceivers in the database: \n")

        for index, row in enumerate(cursor.execute("SELECT * FROM emails"), start=1):
            name, surname, email = row
            print("--------------------------\n")
            print(f"{index} - Name:    {name}")
            print(f"    Surname: {surname}")
            print(f"    Email:   {email}\n")

    if return_to_menu:
        return main()


# Prints out details of a specific receiver based on the name provided by the user
def search_receiver():
    with sqlite3.connect("mailer_container.db") as db:
        cursor = db.cursor()

        list_all_receivers(return_to_menu=False)
        # Requests the name of the receiver that the user wants to prints out the details
        search = str(input("Please enter the name of the receiver that you're searching for: ")).capitalize()

        cursor.execute("SELECT * FROM emails WHERE name = ?", (search,))

        # Retrieves the receiver details from the database
        found = cursor.fetchone()

        # If the receiver is found in the database, prints out the details
        if found:
            name, surname, email = found
            print("\nReceiver Details:\n")
            print(f"Name:    {name}")
            print(f"Surname: {surname}")
            print(f"Email:   {email}")
        else:
            print("\nThis receiver is not valid in the database! Please make sure you entered the correct name!")

    return main()


def content_editor():
    # Title - subject of the email will be written here
    subject = input("\nPlease enter a title: ")

    # Content - body of the email will be here
    body = input("Please write your email: ")

    message = f"Subject: {subject}\n\nEmail: {body}"
    print("Email template is updated successfully!\n")
    print(message)

    # Calls email_menu function
    email_menu()

    return message


# Creates a new database for email templates
def template_database(content_editor):
    with sqlite3.connect("template_db.db") as db:
        cursor = db.cursor()

        # Create the templates table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                body TEXT
            )
        """)
        print("Templates table created successfully.")

    return content_editor


# Calls the template_database function to ensure the table exists
template_database(None)


# Adds a new template to the database
def add_template(subject, body):
    with sqlite3.connect("template_db.db") as db:
        cursor = db.cursor()

        # Inserts the template into the database
        cursor.execute("INSERT INTO email_templates (subject, body) VALUES (?, ?)", (subject, body))
        db.commit()

        print("Email template is added successfully!\n")


# Removes a receiver from the database
def delete_template():
    with sqlite3.connect("template_db.db") as db:
        cursor = db.cursor()

        # Requests the ID number of the receiver to remove from the database
        delete_template_index = int(input("Please enter the index number of the receiver you would like to remove from the database: "))
        cursor.execute("SELECT * FROM email_templates")
        email_templates = cursor.fetchall()

        # Checks if the index is within the valid range
        if 1 <= delete_template_index <= len(email_templates):
            template_to_remove = email_templates[delete_template_index - 1][0]

            # Deletes the data from the database
            cursor.execute("DELETE FROM email_templates WHERE id = ?", (template_to_remove,))
            db.commit()
            print(f"\n{template_to_remove} is removed from the database successfully!")
        else:
            print(f"\nInvalid index number! Please make sure you entered a valid number.")

    return main()


# Displays all templates in the database
def list_templates():
    with sqlite3.connect("template_db.db") as db:
        cursor = db.cursor()

        # Retrieves all templates from the database
        cursor.execute("SELECT * FROM email_templates")
        email_templates = cursor.fetchall()

        # Prints the templates
        print("\nEmail Templates:\n")
        for template in email_templates:
            template_id, subject, body = template
            print(f"Template ID: {template_id}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print("-----------------------\n")


# Prompt the user to choose an option
def email_menu():
    while True:
        print("\nTemplate Menu:\n")
        print("1 - Add Template")
        print("2 - Delete Template")
        print("3 - List Templates")
        print("0 - Back to Main Menu")

        choice = input("\nPlease enter your choice: ")

        if choice == "1":
            subject = input("Please enter the email subject: ")
            body = input("Enter the email body: ")
            add_template(subject, body)
        elif choice == "2":
            delete_template() 
        elif choice == "3":
            list_templates()
        elif choice == "0":
            return main()
        else:
            print("\nInvalid choice. Please try again.\n")


# Prompts the user to enter their e-mail account and sends the selected template to all recipients
def send_email(sender_email, password, return_to_menu=False):

    sender_email = str(sender_email)  # Convert to string

    with sqlite3.connect("mailer_container.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT Email_Address FROM emails")
        receivers = cursor.fetchall()

        if not receivers:
            print("\nNo receivers found in the database.\n")
            return
        

    with sqlite3.connect("template_db.db") as template_db:
        template_cursor = template_db.cursor()
        template_cursor.execute("SELECT id, subject, body FROM email_templates")
        templates = template_cursor.fetchall()

        if templates is None:
            print("\nNo templates found in the database.\n")
            return

        list_templates()

        # Prompts the user to choose a template ID
        template_id = input("\nPlease enter the index number of the template you want to use: ")

        try:
            template_id = int(template_id)
        except ValueError:
            print("\nInvalid index number. Please enter a valid number.")
            return

        # Retrieves the chosen template from the database
        template_cursor.execute("SELECT subject, body FROM email_templates WHERE id = ?", (template_id,))
        template = template_cursor.fetchone()

        if template is None:
            print("\nInvalid index number. Please try again.")
            return
        
        subject, body = template
        
        
        # Composes the message using the template
        message = f"Subject: {subject}\n\n{body}"
        message = message.encode('utf-8')  # Encode the message using UTF-8
        
    # Gets the list of receivers' email addresses
    to_addrs = []
    for email_address in receivers:
        parsed_email = email.utils.parseaddr(email_address)[1]
        if parsed_email:
            to_addrs.append(parsed_email)

    if not to_addrs:
        print("\nNo valid receiver email addresses found.")
        return

    # Establishes a connection with the email server
    try:
        if sender_email.endswith("hotmail.com"):
            server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        elif sender_email.endswith("gmail.com"):
            server = smtplib.SMTP("smtp.gmail.com", 587)
        elif sender_email.endswith("icloud.com"):
            server = smtplib.SMTP("smtp.mail.me.com", 587)
        elif sender_email.endswith("yahoo.com"):
            server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
        else:
            print("\nUnsupported email provider. Please use either Hotmail, Gmail, iCloud, or Yahoo.")
            return

        server.starttls()
        server.login(sender_email, password)

        # Sends email to each receiver
        for email_address in to_addrs:
            server.sendmail(sender_email, email_address, message)
            print(f"Email sent to {email_address}")

        # Closes the server connection
        server.quit()

        print("\nEmails sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("\nLogin failed! Please check your username and password.")
    except smtplib.SMTPException as e:
        print("\nAn error occurred while sending emails:", str(e))
            
    if return_to_menu:
        return  # Return only if `return_to_menu` is True
    
    main()
    return sender_email, password


# !!! this function needs to be reviewed !!!
def container():
    # Container defined for the first 100 emails
    container_number = 1

    # Set up your email list and container variables
    email_list = []
    email_list.append(list_all_receivers(receiver_emails))

    # Loops through the emails and send them
    for number_of_emails, receiver_emails in enumerate(email_list):
        # If the email count is divisible by 100, create a new container
        if (number_of_emails+1) % 100 == 0:
            container_number += 1
             # Creates a new container here using the container_name variable
            container_name = f"Container {container_number}"
            print(f"Existing: {container_name} ")


# Main menu
def main():
    print("\n   _____________________________________________\n")
    print("   ----- Welcome to  Multiple Email Sender -----")
    print("   _____________________________________________\n\n")
    while True:
        menu = int(input("""    Please choose one of the operations below:

1 - Add a new receiver to the contact list
2 - Delete a receiver from the contact list
3 - Update a receiver's details
4 - Display the contact list
5 - Search a receiver in contact list
6 - Create an email template / edit the subject and the content of the email
7 - Send email to the list
0 - Quit

: """))

        try:
            if menu == int(1):
                add_new_email()
            if menu == int(2):
                delete_receiver()
            if menu == int(3):
                update_receiver()
            if menu == int(4):
                list_all_receivers()
            if menu == int(5):
                search_receiver()
            if menu == int(6):
                email_menu()
            if menu == int(7):
                login_result = login()
                sender_email = login_result[0]
                password = login_result[1]
                send_email(sender_email=sender_email, password=password)
            if menu == int(0):
                print("\n   _____________________________________________\n")
                print("   --Thank you for using Multiple Email Sender-- ")
                print("   _____________________________________________\n\n")
                quit()
            else:
                print("\n\nInvalid value!\nPlease enter a number between 0-7!\n\n")
                continue

        # Error handling if user enters a wrong type, value, etc
        except TypeError:
            print("\n    Invalid value! Please make sure that you wrote with the correct type\n")
        except ValueError:
            print("\n    Please enter the related number between 0 and 7!\n")
            continue


# runs the main menu at the beginning
main()
