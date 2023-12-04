from collections import UserDict
from datetime import datetime, date
import json

class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

class Name(Field):
    pass  

class Birthday(Field):
    @Field.value.setter
    def value(self, value: str):
        try:
            # Перевірка та встановлення коректної дати
            self.__value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError as e:
            raise ValueError("Incorrect birthday format. Use the YYYY-MM-DD format") from e

class Phone(Field):
    @Field.value.setter
    def value(self, value):
        # Перевірка коректності номера телефону
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. Please enter a 10 digit phone number.")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                break

    def edit_phone(self, old_phone_number, new_phone_number):
        phone_exists = False
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number
                phone_exists = True
                break

        if not phone_exists:
            raise ValueError("Phone number to edit does not exist in the contact's phone list.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def days_to_birthday(self):
        if self.birthday:
            today = date.today()
            next_birthday = date(today.year, self.birthday.value.month, self.birthday.value.day)
            if next_birthday < today:
                next_birthday = date(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            delta = next_birthday - today
            return delta.days

    def __str__(self):
        phone_list = "; ".join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name}, phones: {phone_list}"

class AddressBook(UserDict):
    # Метод для додавання записів
    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.data, file, default=self.serialize_record, indent=4)
    
    # Метод для збереження записів в файл
    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            self.data = {key: self.deserialize_record(value) for key, value in data.items()}

    # Метод для серіалізації записів в файл
    def serialize_record(self, record):
        if isinstance(record, Record):
            serialized_phones = [phone.value for phone in record.phones]
            return {
                'name': record.name.value,
                'phones': serialized_phones,
                'birthday': str(record.birthday.value) if record.birthday else None
            }

    # Метод для десеріалізації записів з файлу
    def deserialize_record(self, data):
        name = data.get('name')
        birthday = data.get('birthday')
        phones = data.get('phones', [])
        
        record = Record(name, birthday)
        for phone_number in phones:
            record.add_phone(phone_number)
        
        return record

    # Метод для пошуку контактів за іменем або номером телефону
    def search_contacts(self, search_string):
        found_contacts = []
        for record in self.data.values():
            if (search_string in record.name.value) or any(search_string in phone.value for phone in record.phones):
                found_contacts.append(record)
        return found_contacts
