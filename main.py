import subprocess
import ollama
import os


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

import os
import subprocess
import ollama

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
    'write_file': write_file,
    'read_file': read_file,
    'list_files': list_files
}


def main():
    model_name = 'qwen2.5:3b'
    print(f"=== AGENT URUCHOMIONY (Model: {model_name}) ===")

    messages = [
        {
            'role': 'system',
    'content': (
        'Jesteś zaawansowanym asystentem z dostępem do terminala i systemu plików Windows. '
        'Zasady pracy z plikami i folderami:\n'
        '1. Jeśli użytkownik podaje nazwę katalogu, użyj narzędzia list_files, podając ścieżkę (np. "." dla bieżącego folderu, "../NazwaFolderu" dla folderu wyżej, lub pełną ścieżkę absolutną).\n'
        '2. Nigdy nie używaj read_file na katalogu – read_file służy wyłącznie do odczytu zawartości pojedynczych plików.\n'
        '3. Jeśli plik lub folder znajduje się na Pulpicie poza bieżącym projektem, użyj pełnej ścieżki lub cofnij się operatorem "../".'
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
            tools=[run_command, write_file, read_file, list_files]
        )

        if response.get('message', {}).get('tool_calls'):
            for tool in response['message']['tool_calls']:
                function_name = tool['function']['name']
                function_args = tool['function']['arguments']

                print(f"\n[⚡ AI chce wywołać funkcję: {function_name}]")

                if function_name in available_tools:
                    tool_output = available_tools[function_name](**function_args)
                    print(f"[📤 Wynik z terminala]:\n{tool_output}")

                    messages.append(response['message'])
                    messages.append({
                        'role': 'tool',
                        'content': tool_output,
                        'name': function_name
                    })

                    final_response = ollama.chat(model=model_name, messages=messages)
                    print(f"\nAI: {final_response['message']['content']}")
                    messages.append(final_response['message'])

        else:
            content = response['message']['content']
            print(f"\nAI: {content}")
            messages.append(response['message'])    


if __name__ == '__main__':
    main()