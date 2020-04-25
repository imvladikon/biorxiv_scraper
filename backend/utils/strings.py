
blank_string = lambda s: not s.strip()
not_blank_string = lambda s: s.strip()

def absolute_url(host:str, url:str) ->str:
    if not url:
        return host
    url = url[1:] if url.startswith("/") else url
    return host + url if host.endswith("/") else host + "/" + url

def replace_all(string:str, *args):
    for arg in args:
        string = string.replace(arg, "")
    return string