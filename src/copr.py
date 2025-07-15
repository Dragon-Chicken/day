import requests
from bs4 import BeautifulSoup
from termcolor import colored

def search_copr(query):
    url = f"https://copr.fedorainfracloud.org/coprs/fulltext/?projectname={query}"
    print(f"Fetching {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch COPR search: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    projects = [
        p for p in soup.find_all('a', class_='list-group-item')
        if p.get('href', '').startswith('/coprs/') and p.find('h3')
    ]

    print(f"Search results for {colored(query, 'green')}:")
    if not projects:
        print("No projects found.")
        return

    for project in projects:
        name = project.find('h3').text.strip()
        name_highlighted = name.replace(query, colored(query, 'green'))

        description = (project.find('span', class_='list-group-item-text') or {}).text.strip() or "No description available."
        description = ' '.join(description.split()[:10]) + '...'

        archs = {
            arch.strip() for small in (project.find('ul', class_='list-inline') or {}).find_all('small', recursive=False) or []
            for arch in small.text.split(',') if arch.strip()
        }
        archs_formatted = f"( {', '.join(sorted(archs))} )" if archs else "( )"

        print("--------------------------------------------")
        print(f"   {name_highlighted} {archs_formatted} : {description}")
    print("--------------------------------------------")
