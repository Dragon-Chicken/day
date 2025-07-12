import requests
from bs4 import BeautifulSoup
from termcolor import colored

def search_copr(query):
    base_url = "https://copr.fedorainfracloud.org/coprs/fulltext/?projectname="
    url = base_url + query
    print(f"Fetching {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.ConnectionError:
        print("Error: Failed to connect to the server. Please check your internet connection.")
        return
    except requests.Timeout:
        print("Error: Request timed out. Please try again later.")
        return
    except requests.HTTPError as e:
        print(f"Error: HTTP error occurred - {e.response.status_code} {e.response.reason}")
        return
    except requests.RequestException as e:
        print(f"Error: Failed to fetch URL - {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    projects = [p for p in soup.find_all('a', class_='list-group-item') 
                if p.get('href', '').startswith('/coprs/') and p.find('h3')]

    print(f"Search results of {colored(query, 'green')}:")
    if not projects:
        print("No projects found.")
        return

    for project in projects:
        name = project.find('h3').text.strip()
        name_highlighted = name.replace(query, colored(query, 'green'))

        description_span = project.find('span', class_='list-group-item-text')
        description = description_span.text.strip() if description_span else "No description available."
        description_words = description.split()[:10]
        description = ' '.join(description_words) + '...'

        ul = project.find('ul', class_='list-inline')
        archs = set()
        if ul:
            small_tags = ul.find_all('small')
            for small in small_tags:
                for arch in small.text.split(','):
                    arch = arch.strip()
                    if arch:
                        archs.add(arch)
            archs_str = ', '.join(sorted(archs))
            archs_formatted = f"( {archs_str} )" if archs else "( )"
        else:
            archs_formatted = "( )"

        print("--------------------------------------------")
        print(f"   {name_highlighted} {archs_formatted} : {description}")
    print("--------------------------------------------")
