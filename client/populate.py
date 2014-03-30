import re
from getpass import getpass
import yaml
from pytz import timezone


def run():
    profile = {}

    print "Welcome to the profile populator. If, at any step, you'd prefer not to enter the requested information, just hit 'Enter' with a blank field to continue."

    def simple_request(var, cleanVar, cleanInput=None):
        input = raw_input(cleanVar + ": ")
        if input:
            if cleanInput:
                input = cleanInput(input)
            profile[var] = input

    # name
    simple_request('first_name', 'First name')
    simple_request('last_name', 'Last name')

    # gmail
    print "\nJasper uses your Gmail to send notifications. Alternatively, you can skip this step (or just fill in the email address if you want to receive email notifications) and setup a Mailgun account, as at http://jasperproject.github.io/documentation/software/#mailgun.\n"
    simple_request('gmail_address', 'Gmail address')
    profile['gmail_password'] = getpass()


    # phone number
    clean_number = lambda s: re.sub(r'[^0-9]', '', s)
    phone_number = clean_number(raw_input(
        "Phone number. 10 digits (no country code). Any dashes or spaces will be removed for you: "))
    while phone_number and len(phone_number) != 10:
        print("Invalid phone number. Must be 10 digits.")
        phone_number = clean_number(raw_input("Phone number: "))
    if phone_number:
        profile['phone_number'] = phone_number

    # carrier
    print("Phone carrier (for sending text notifications).")
    print(
        "Enter one of the following: 'AT&T', 'Verizon', 'T-Mobile' OR go to http://www.emailtextmessages.com and enter the email suffix for your carrier (e.g., for Virgin Mobile, enter 'vmobl.com').")
    carrier = raw_input('Carrier: ')
    if carrier:
        if carrier == 'AT&T':
            profile['carrier'] = 'txt.att.net'
        elif carrier == 'Verizon':
            profile['carrier'] = 'vtext.com'
        elif carrier == 'T-Mobile':
            profile['carrier'] = 'tmomail.net'
        else:
            profile['carrier'] = carrier

    # location
    print(
        "Location should be a 5-digit US zipcode (e.g., 08544). For weather requests.")
    zipcode = clean_number(raw_input("Zipcode: "))
    while zipcode and len(zipcode) != 5:
        print("Invalid zipcode. Must be 5 digits.")
        zipcode = clean_number(raw_input("Zipcode: "))
    if zipcode:
        profile['location'] = zipcode

    # timezone
    print(
        "Please enter a timezone from the list located in the TZ* column at http://en.wikipedia.org/wiki/List_of_tz_database_time_zones, or none at all.")
    tz = raw_input("Timezone: ")
    while tz:
        try:
            timezone(tz)
            profile['timezone'] = tz
            break
        except:
            print("Not a valid timezone. Try again.")
            tz = raw_input("Timezone: ")

    response = raw_input(
        "Would you prefer to have notifications sent by email (E) or text message (T)? ")
    while not response or (response != 'E' and response != 'T'):
        response = raw_input("Please choose email (E) or text message (T): ")
    profile['prefers_email'] = (response == 'E')

    # write to profile
    print("Writing to profile...")
    outputFile = open("profile.yml", "w")
    yaml.dump(profile, outputFile, default_flow_style=False)
    print("Done.")

if __name__ == "__main__":
    run()
