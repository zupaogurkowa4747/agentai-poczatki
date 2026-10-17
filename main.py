import subprocess
import ollama
import os
import webbrowser

def run_command(command: str) -> str:
    """Wykonuje polecenie w terminalu systemowym i zwraca wynik.
    Args:
        command: Komenda do wykonania w powłoce systemowej.
    """
    print(f"\n[🤖 AGENT CHCE ODPALIĆ] ---> {command}")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )

    output = result.stdout if result.returncode == 0 else result.stderr
    return output if output else 'Komenda wykonana pomyślnie (brak tekstu zwrotnego)'

def open_app(target: str) -> str:
    """Otwiera aplikację systemową lub stronę WWW bez blokowania terminala."""
    print(f"\n[🚀 URUCHAMIANIE] ---> {target}")
    
    # Słownik skrótów dla trudnych aplikacji w Windowsie
    APPS_PATHS = {
        "roblox": 'Roblox Player',
        "discord": "discord",
        "spotify": "spotify",
        "code": "code"
    }
    
    # Jeśli podano skrót, podmień na pełną ścieżkę
    target_path = APPS_PATHS.get(target.lower(), target)
    
    try:
        if target.startswith("http://") or target.startswith("https://"):
            webbrowser.open(target)
            return f"Otwarto stronę: {target}"
        
        subprocess.Popen(f'cmd.exe /c start "" "{target_path}"', shell=True)
        return f"Uruchomiono aplikację/polecenie: {target_path}"
    except Exception as e:
        return f"Błąd uruchamiania {target}: {str(e)}"

def list_files(directory: str = ".") -> str:
    """Wyświetla listę wszystkich plików i folderów w podanym katalogu.
    
    Args:
        directory: Ścieżka do katalogu (domyślnie bieżący katalog '.').
    """
    print(f"\n[🤖 AGENT LISTUJE KATALOG] ---> {directory}")
    try:
        items = os.listdir(directory)
        return "\n".join(items) if items else "Katalog jest pusty."
    except Exception as e:
        return f"Błąd podczas listowania katalogu: {str(e)}"

def read_file(filename: str) -> str:
    """Odczytuje zawartość pliku z dysku i zwraca ją jako tekst.
    
    Args:
        filename: Nazwa pliku do odczytu (np. 'kalkulator.py').
    """
    print(f"\n[🤖 AGENT CHCE ODCZYTAĆ PLIK] ---> {filename}")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content if content else "Plik jest pusty."
    except Exception as e:
        return f"Błąd podczas odczytywania pliku: {str(e)}"

def write_file(filename: str, content: str) -> str:
    """Tworzy plik na dysku i zapisuje w nim zawartość content.
    Args:
        filename: Nazwa pliku np. kalkulator.py
        content: Kod do zapisania w pliku
    """
    print(f"\n[🤖 AGENT CHCE ZAPISAĆ PLIK] ---> {filename}")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Plik '{filename}' został pomyślnie utworzony i zapisany na dysku."
    except Exception as e:
        return f"Błąd podczas zapisywania pliku: {str(e)}"

available_tools = {
    'run_command': run_command,
    'open_app': open_app,
    'write_file': write_file,
    'read_file': read_file,
    'list_files': list_files
}

def main():
    model_name = 'qwen2.5:3b'
    print(f"=== STARTUP AGENT URUCHOMIONY (Model: {model_name}) ===")

    messages = [
        {
            'role': 'system',
            'content': (
                'Jesteś autonomicznym asystentem startowym w systemie Windows.\n'
                'Zasady działania:\n'
                '1. Gdy użytkownik prosi o otwarcie aplikacji (np. Discord, VS Code, Spotify) lub stron WWW (np. YouTube, GitHub), ZAWSZE używaj narzędzia open_app.\n'
                '2. Możesz wywoływać narzędzie open_app wielokrotnie w jednej odpowiedzi, aby uruchomić zestaw aplikacji jeden po drugim.\n'
                '3. Jeśli użytkownik podaje nazwę katalogu, użyj list_files (np. "." dla obecnego folderu, "../" dla folderu wyżej).\n'
                '4. Do odczytu plików używaj read_file, do zapisu write_file, a do poleceń konsolowych run_command.'
            )
        } 
    ]

    while True:
        user_input = input("\nTy: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        messages.append({'role': 'user', 'content': user_input})

        response = ollama.chat(
            model=model_name,
            messages=messages,
            tools=[run_command, open_app, write_file, read_file, list_files]
        )

        messages.append(response['message'])

        if response.get('message', {}).get('tool_calls'):
            for tool in response['message']['tool_calls']:
                function_name = tool['function']['name']
                function_args = tool['function']['arguments']

                print(f"\n[⚡ AI chce wywołać funkcja: {function_name}]")

                if function_name in available_tools:
                    tool_output = available_tools[function_name](**function_args)
                    print(f"[📤 Wynik narzędzia]: {tool_output}")

                    messages.append({
                        'role': 'tool',
                        'content': tool_output,
                        'name': function_name
                    })

            # Po wykonaniu wszystkich wywołań narzędzi prosimy model o podsumowanie
            final_response = ollama.chat(model=model_name, messages=messages)
            print(f"\nAI: {final_response['message']['content']}")
            messages.append(final_response['message'])

        else:
            content = response['message']['content']
            print(f"\nAI: {content}")


if __name__ == '__main__':
    main()