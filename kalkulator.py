def kalkulator():
    a = input('Podaj pierwszą liczbę: ')
    b = input('Podaj drugą liczbę: ')
    operacja = input('Wybierz operację (+, -, *, /): ')
    if operacja == '+':
        wynik = float(a) + float(b)
    elif operacja == '-':
        wynik = float(a) - float(b)
    elif operacja == '*':
        wynik = float(a) * float(b)
    elif operacja == '/':
        wynik = float(a) / float(b)
    else:
        print('Nieznana operacja')
    print('Wynik to:', wynik)

kalkulator()