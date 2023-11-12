'''
def generate_breadcrumbs(path):
    breadcrumbs = []
    parts = path.strip('/').split('/')
    current_url = ''

    for part in parts:
        current_url += f'/{part}'
    
    if current_url:  # Only add a breadcrumb if the URL is not empty
        breadcrumbs.append({'label': parts[-1].capitalize(), 'url': current_url})

    return breadcrumbs
'''
