import sqlite3
from sqlite3 import Connection

import pandas as pd
from pandas import DataFrame


class Contact:

    def __init__(self, first_name: str = None, last_name: str = None,
                 email: str = None, telephone: str = None):
        self.telephone = telephone
        self.email = email
        self.last_name = last_name
        self.first_name = first_name


class TelephoneContacts:

    def __init__(self):
        print("What do you want to do today?")
        print("Enter: \n1 to add a new contact,\n"
              "2 to update an existing contact,\n"
              "3 to delete a contact, \n"
              "4 to list all contacts \n"
              "5 Retrieve a contact information\n")
        self.feedback = int(input("select your option: "))
        self.db = Database()
        self.option_maker()

    def option_maker(self):
        return {1: self.add_contact, 2: self.update_contact,
                3: self.delete_contact, 4: self.list_contacts,
                5: self.retrieve_a_contact}[self.feedback]()

    def add_contact(self):
        first_name: str = input("Enter your first name: ")
        last_name: str = input("Enter your last name: ")
        email: str = input("Enter your email: ")
        telephone: str = str(input("Enter your telephone number: "))
        self.db.insert_record(first_name, last_name, email, telephone)

    def update_contact(self):
        current_telephone: str = str(input("Enter the telephone number of the contact to update: "))
        if self.check_if_record_exist(current_telephone):
            record = self.db.retrieve_contact_info(current_telephone).to_dict('records')[0]
            print(f"\nExisting record for telephone no: {current_telephone}")
            for key, value in record.items():
                print(key, ': ', value)
            print("\n")
            print("What information do you need to update?")
            print("Enter: \n1 to update first name,\n"
                  "2 to update last name,\n"
                  "3 to update email, \n"
                  "4 to update telephone number \n"
                  "You can select a combination of options i.e. 1234, 23, 34 \n")
            feedback = str(input("select your option: "))
            new_details = {}
            new_info = None

            if (int(feedback) == 1) or ('1' in feedback):
                new_info = self.get_feedback(new_details, 1)
            if int(feedback) == 2 or ('2' in feedback):
                new_info = self.get_feedback(new_details, 2)
            if int(feedback) == 3 or ('3' in feedback):
                new_info = self.get_feedback(new_details, 3)
            if int(feedback) == 4 or ('4' in feedback):
                new_info = self.get_feedback(new_details, 4)
            if len(feedback) == 1:
                self.db.update_single_field(current_telephone, int(feedback), new_info)
            else:
                self.db.update_contact_details(current_telephone, new_details)
        else:
            print(f"Telephone number: '{current_telephone}' do not not exist on the system")

    @staticmethod
    def get_feedback(new_details: dict, int_check):
        """ Get feedback and analyse response for db update """
        choices = {1: 'first_name', 2: 'last_name', 3: 'email', 4: 'telephone'}
        new_info = str(input(f"Enter the new {choices[int_check]}: "))
        new_details[choices[int_check]] = new_info
        return new_info

    def list_contacts(self):
        print('Telephone Contacts listing: \n')
        return self.db.list_all_contacts()

    def delete_contact(self):
        current_telephone: str = str(input("Enter the telephone number of the contact to delete: "))
        self.db.remove_record(current_telephone)

    def check_if_record_exist(self, telephone: str):
        return self.db.contact_exist(telephone)

    def retrieve_a_contact(self):
        telephone: str = str(input("Enter the telephone number of the contact: "))
        print(self.db.retrieve_contact_info(telephone))


class Database:

    def __init__(self):
        self.cursor = None

        self.connection = self._connection()
        self.create_table()

    @property
    def sqlite_version(self):
        self.cursor.execute("select sqlite_version();")
        version = self.cursor.fetchall()[0][0]
        return version

    @property
    def table_exists(self) -> bool:
        # query = " SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        query = " SELECT name FROM sqlite_master WHERE type ='table' AND name = 'Contacts';"
        return not pd.read_sql(query, self.connection).empty

    def create_table(self):
        if not self.table_exists:
            query = " CREATE TABLE IF NOT EXISTS Contacts " \
                    "(first_name TEXT NOT NULL," \
                    "last_name TEXT NOT NULL , " \
                    "email TEXT NOT NULL, " \
                    "telephone TEXT NOT NULL)"
            self.cursor.execute(query)
            self.connection.commit()
            print("SQLite table 'Contacts' created.")

    def retrieve_contact_info(self, telephone: str) -> DataFrame:
        query = f"SELECT * FROM Contacts where telephone = '{telephone}';"
        return pd.read_sql(query, self.connection)

    def contact_exist(self, telephone: str) -> bool:
        return not self.retrieve_contact_info(telephone).empty

    def insert_record(self, first_name: str, last_name: str, email: str, telephone: str):
        insertion_query = f"INSERT INTO Contacts (first_name, last_name, email, telephone)" \
                          f" VALUES ('{first_name}', '{last_name}', '{email}', '{telephone}');"
        print(insertion_query)
        self.cursor.execute(insertion_query)
        self.connection.commit()

    def update_contact_details(self, existing_telephone: str, new_details: dict):
        update_query = "UPDATE Contacts SET {} WHERE telephone = '{}';".format(
            ', '.join([f"{key} = '{value}'" for key, value in new_details.items()]),
            existing_telephone)
        self.cursor.execute(update_query)
        self.connection.commit()
        print("Successfully updated record. New record: \n")
        telephone = new_details['telephone'] if 'telephone' in new_details else existing_telephone
        print(new_details)
        print(self.retrieve_contact_info(telephone))

    def update_single_field(self, existing_telephone: str, choice: int, new_detail):
        choices = {1: 'first_name', 2: 'last_name', 3: 'email',
                   4: 'telephone'}
        update_query = f"UPDATE Contacts SET {choices[choice]} = '{new_detail}' " \
                       f"WHERE telephone = '{existing_telephone}';"
        self.cursor.execute(update_query)
        self.connection.commit()
        print("Successfully updated records. New records: \n")
        telephone = existing_telephone if choices[choice] != 'telephone' else new_detail
        print(self.retrieve_contact_info(telephone))

    def list_all_contacts(self):
        select_query = f"SELECT * FROM Contacts;"
        records = pd.read_sql(select_query, self.connection)
        print(records)

    def remove_record(self, telephone: str):
        delete_query = f"DELETE FROM Contacts WHERE telephone = '{telephone}' ;"
        self.cursor.execute(delete_query)
        self.connection.commit()
        print(f" '{telephone}' successfully deleted!")

    def _connection(self) -> Connection:
        try:
            sqlite_connection = sqlite3.connect('Contacts.db')
            self.cursor = sqlite_connection.cursor()
            print(f"Successfully connected to SQLite version: {self.sqlite_version}")
            return sqlite_connection

        except sqlite3.Error as e:
            print(e)


TelephoneContacts()
