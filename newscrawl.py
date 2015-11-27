import urllib, re
from bs4 import BeautifulSoup


def get_internal_links_from_page(url, pattern):
    """WARNING: WILL ONLY GET LINKS IN THE MAIN NAMESPACE & THE
    SITE NAME CAN ONLY CONTAIN ALPHANUMERIC CHARACTERS
    Finds internal links that match the pattern specified at the given url.
    Retrieves article data from the page and puts it into a subdirectory
    The pattern is used to assemble a regex of the shape (url + pattern)"
    """

    site_url = re.match('(http://www\.\w*?\.\w*)', url).group()
    print('the site url is ' + site_url)
    if not site_url:
        print('NO MATCHES FOR SITE URL')
        site_url = url
    try:
        site = urllib.urlopen(url)
        html = site.read()
        site.close()

    except IOError:
        print('IOError at ' + url + '!')
        html = ''

    soup = BeautifulSoup(html)
    tag = soup.article
    if tag:
        destination_name = 'articles/' + re.match('http://www\.aif\.ru/\w+/\w+/(\w+)', url).group(1) + '.txt'
        print('DESTINATION:' + destination_name)
        destination = open(destination_name, 'w')
        children = tag.find_all("p")
        strings = []
        for child in children:
            strings.append(unicode(child.get_text()))

        destination.write(''.join(strings).encode("UTF-8"))
        destination.close()
        
    else: print('NO ARTICLE TAG')

    fin_pattern = '(' + site_url + pattern + ')"'
    print('the pattern is ' + fin_pattern)
    all_links = re.findall(fin_pattern, html)
    links = []

    for link in all_links:
        if link not in links and link != site_url: links.append(link)

    #print('IT IS DONE, HERE IS THE LIST:\n')
    return links

def get_internal_links_from_site(links, pattern, name='site'):
    destination = 'links_from_%s.txt' % name
    destination_text = open(destination, 'a')

    #for each page, look for all internal links there, and then add them to the list if they're not there:
    for page in links:
        new_links = get_internal_links_from_page(page, pattern)
        for link in new_links:
            if link not in links:
                links.append(link)
                print('appended link:' + link)
                destination_text.write(link + '\n')

    print('IT IS DONE, RETURNING LIST OF LINKS')
    destination_text.close()
    return links




print(get_internal_links_from_site(get_internal_links_from_page('http://www.aif.ru', '/\w*/\w*/\w*'), '/\w*/\w*/\w*', 'AiF'))
