import psycopg2


def create_tables():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    """)
    print("Таблица clients создана")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phones(
        id SERIAL PRIMARY KEY,
        phone TEXT,
        client_id INTEGER NOT NULL REFERENCES clients(id)
    );
    """)
    print("Таблица phones создана")


def add_new_client(name, surname, email, phone = None):
    cur.execute("""
        INSERT INTO clients(name, surname, email) VALUES(%s, %s, %s) RETURNING id;""",
        (name, surname, email))
    client = cur.fetchone()
    print("Таблица clients заполнена")
    cur.execute("""
        INSERT INTO phones(phone, client_id) VALUES(%s, %s);""", (phone, client))
    print("Таблица phones заполнена")


def add_phone(email, phone):
    cur.execute("""
        SELECT FROM clients WHERE email = %s;""", (email))
    res = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO phones(phone, client_id) VALUES (%s, %s);""", (phone, res))
    print("Номер телефона записан")


def change_client(name, surname, new_name, new_surname, new_email):
    cur.execute("""
        SELECT id FROM clients WHERE name = %s AND surname = %s;""", (name, surname))
    res = cur.fetchone()[0]
    cur.execute("""
        UPDATE clients SET name = %s, surname = %s, email = %s WHERE id = %s;""",
        (new_name, new_surname, new_email, res))
    print(f'Данные клиента {res} обновлены')


def delete_phone(name, surname):
    cur.execute("""
        SELECT id FROM clients WHERE name = %s AND surname = %s;""", (name, surname))
    res = cur.fetchone()[0]
    cur.execute("""
        DELETE FROM phones WHERE id = %s;""", (res))
    print(f'Телефон клиента {res} удалён')


def delete_client(name, surname):
    cur.execute("""
        SELECT id FROM clients WHERE name = %s, surname = %s;""", (name, surname))
    res = cur.fetchone()[0]
    question = input(f'Вы уверены, что хотите удалить клиента {res}? y/n')
    if question != "y":
        print("Удаление отменено, спасибо")
    else:
        cur.execute("""
            DELETE FROM phones WHERE client_id = %s;""", (res))
        cur.execute("""
            DELETE FROM clients WHERE name = %s AND surname = %S""", (name, surname))
    print(f'Клиент {res} удалён')


def find_client(name, surname, email, phone):
    cur.execute("""
        SELECT name, surname, email, phone FROM clients c
        LEFT JOIN phones p ON p.client_id = c.id
        WHERE name = %s AND surname = %s AND email = %s AND p.phone = %s;
        """, (name, surname, email, phone))
    print(f'Найден {cur.fetchall()}')


if __name__ == '__main__':
    database = str(input("Введите название БД: "))
    user = str(input("Введите логин для доступа к БД: "))
    password = str(input("Ввеждите пароль для доступа к БД: "))
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        print("БД законнектилась")
    with conn.cursor() as cur:
        question1 = input("Вы хотите удалить таблицы перед созданием? y/n")
        if question1 != "y":
            print("Удаление отменено, спасибо")
        else:
            cur.execute("""DROP TABLE phones; DROP TABLE clients""")
            conn.commit()  # фиксируем в базе
            print("Таблицы clients и phones удалены")

        question2 = input("Вы хотите удалить данные из таблиц? y/n")
        if question2 != "y":
            print("Удаление отменено, спасибо")
        else:
            cur.execute("""DELETE * FROM phones; DELETE * FROM clients""")
            print("Данные из таблиц phones и clients удалены")
        countpeoples = int(input("Введите количество добавляемых клиентов: "))
        for i in range(countpeoples):
            add_new_client()
        conn.commit()  # фиксируем в базе
        print("Данные внесены в БД")

        add_phone("Ivan", "+79991234567")

        change_client("Ivan", "Ivanov", "Ivan", "Petrov", "123@456.ru")

        delete_phone("Ivan", "Petrov")

        delete_client("Ivan", "Petrov")

        find_client("Ivan", "Ivanov", "123@456.ru", "+79991234567")


    conn.close() # закрыть соединение
    print("Соединение с БД закрыто, всего доброго!")