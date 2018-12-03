import pymysql


class Odznaki:

    def __init__(self):
        self.conn = pymysql.connect('localhost', 'root', 'alfa147', 'mydb')
        self.c = self.conn.cursor()
        self.menuLogin()

    def addUser(self):
        imie = input("Imie = ")
        nazwisko = input("Nazwisko = ")
        self.login = input("Login = ")
        haslo = input("Hasło = ")

        self.c.execute(
            "INSERT INTO uzytkownicy(imie, nazwisko, login, haslo) VALUES (%s,%s,%s,%s)",
            (imie, nazwisko, self.login, haslo))
        czynapewno = input("Czy założyć konto? T/N ").lower()
        if czynapewno == "t":
            self.conn.commit()
            print("Pomyślnie założono konto")
            self.logowanie()
        else:
            self.conn.rollback()
            print("Anulowano operację")

    def logowanie(self):
        self.login = input("podaj login: ")
        haslo = input("podaj hasło: ")

        self.c = self.conn.cursor()
        self.c.execute("SELECT id_uzytkownicy FROM uzytkownicy where login=%s and haslo=%s", (self.login, haslo))
        self.id_u = self.c.fetchall()[0][0]

        self.c = self.conn.cursor()
        self.c.execute("SELECT * FROM uzytkownicy WHERE login=%s AND haslo=%s", (self.login, haslo))
        LogRes = self.c.fetchall()
        if (len(LogRes) == 1):
            print("zalogowano pomyślnie")
            self.menu()
        else:
            print("błędny login lub hasło")
            self.logowanie()

    def insertRange(self):

        self.c.execute("SELECT * FROM lancuchy_gorskie")
        print("%5s | %25s" % ("\nWybór", "Łańcuch Górski"))
        result = self.c.fetchall()
        for row in result:
            print("%5s | %25s" % (row[0], row[1]))
        lancuch = input("Wybierz łańcuch górski, w który się udałeś:")

        self.c.execute("SELECT * FROM pasma_gorskie WHERE lancuchy_gorskie_id_lancuchy_gorskie=%s", lancuch)
        print("%5s | %28s" % ("\nWybór", "Pasmo Górskie"))
        result = self.c.fetchall()
        for row in result:
            print("%5s | %28s" % (row[0], row[1]))
        pasmo = input("Wybierz pasmo górskie, którym podróżowałeś:")

        self.c.execute("SELECT * FROM pasma_szczyty WHERE pasma_gorskie_id_pasma_gorskie=%s", pasmo)
        print("%5s | %28s | %10s" % ("\nWybór", "Szczyt Górski", "Wysokość"))
        result = self.c.fetchall()
        for row in result:
            print("%5s | %28s | %10s" % (row[0], row[1], row[2]))

    def insertPeak(self):
        while True:
            dec = input("W -wybierz szczyt, na którym byłeś | Z -zmień lokalizację | S -zakończ i zapisz\n").lower()
            if dec == "w":
                szczyt = input("Podaj ID szczytu: ")
                self.c.execute(
                    "INSERT INTO osiagniecia(data_wycieczki, uzytkownicy_id_uzytkownicy, pasma_szczyty_id_pasma_szczyty ) VALUES (%s,%s,%s)",
                    (self.date, self.id_u, szczyt))
            elif dec == "z":
                self.insertRange()
            elif dec == "s":
                czynapewno = input("Zapisać wycieczkę? T/N ").lower()
                if czynapewno == "t":
                    self.conn.commit()
                    print("Pomyślnie zapisano")
                    break
                else:
                    self.conn.rollback()
                    print("Anulowano operację")
                    break

    def achievement(self):
        self.c.execute("SELECT data_wycieczki, nazwa_pasma, nazwa_szczytu, wysokosc FROM pasma_szczyty "
                       "JOIN osiagniecia ON pasma_szczyty_id_pasma_szczyty = id_pasma_szczyty "
                       "JOIN pasma_gorskie ON pasma_gorskie_id_pasma_gorskie = id_pasma_gorskie "
                       "JOIN uzytkownicy on osiagniecia.uzytkownicy_id_uzytkownicy = uzytkownicy.id_uzytkownicy "
                       "WHERE uzytkownicy.login = %s ORDER BY data_wycieczki DESC", self.login)
        Result = self.c.fetchall()
        print("%20s|%20s|%30s|%15s" % ("data", "pasma", "szczyty", "wysokość"))
        for row in Result:
            print("%20s|%20s|%30s|%15s" % (row[0], row[1], row[2], row[3]))

    def badges(self):
        self.c.execute(
            "SELECT nazwa, nazwa_pasma, COUNT(DISTINCT nazwa_szczytu) FROM osiagniecia "
            "JOIN uzytkownicy ON (osiagniecia.uzytkownicy_id_uzytkownicy = uzytkownicy.id_uzytkownicy) "
            "JOIN pasma_szczyty ON (pasma_szczyty.id_pasma_szczyty = osiagniecia.pasma_szczyty_id_pasma_szczyty) "
            "JOIN pasma_gorskie ON (pasma_gorskie.id_pasma_gorskie = pasma_szczyty.pasma_gorskie_id_pasma_gorskie) "
            "JOIN lancuchy_gorskie ON (lancuchy_gorskie.id_lancuchy_gorskie = pasma_gorskie.lancuchy_gorskie_id_lancuchy_gorskie) "
            "WHERE uzytkownicy.login = %s GROUP BY pasma_gorskie_id_pasma_gorskie", self.login)
        Result = self.c.fetchall()
        print("%20s|%20s|%20s" % ("łańcuchy górskie", "nazwa pasma", "liczba szczytów"))
        for row in Result:
            print("%20s|%20s|%20s" % (row[0], row[1], row[2]))

    def delete(self):
        self.achievement()
        datedel = input("Podaj datę wycieczki, którą chcesz usunąć: ")
        self.c.execute("DELETE FROM osiagniecia WHERE data_wycieczki=%s", datedel)
        czynapewno1 = input("Czy na pewno chcesz usunąć wycieczkę? T/N ")
        if czynapewno1 == "t":
            self.conn.commit()
            print("Pomyślnie usunięto")
        else:
            self.conn.rollback()
            print("Anulowano operację")

    def menuLogin(self):
        while True:
            dec = input("N -Załóż konto | L -Zaloguj się\n").lower()
            if dec == "n":
                self.addUser()
            elif dec == "l":
                self.logowanie()
                break

    def menu(self):
        while True:
            dec = input(
                "W -gdzie byłeś | T -twoje wycieczki | O -twoje odznaki | U -usuń wycieczkę | Q -zakończ\nCo chcesz zrobić: ").lower()
            if dec == "w":
                self.date = input("Podaj datę [RRRR-MM-DD] wycieczki: ")
                self.insertRange()
                self.insertPeak()
            elif dec == "t":
                self.achievement()
            elif dec == "o":
                self.badges()
            elif dec == "u":
                self.delete()
            elif dec == "q":
                break


ob = Odznaki()
