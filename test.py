import time

print("Запускаю процесс, чтобы ноут не спал...")
print("Нажми Ctrl+C чтобы остановить")

while True:
    time.sleep(60)  # Спим 60 секунд
    print("Все еще работаю...")