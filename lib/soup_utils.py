import re
import urllib
import urllib.parse


def find_tags(soup, filter_expr):
    attrs = get_filter_attrs(filter_expr)
    tags = []

    for item in attrs:
        try:
            attr = item["attr"]
            tag = item["tag"]
            select = item["select"]
            text = item["text"]
            if select != "":
                tags += soup.select(select)
            elif tag != "":
                if text != "":
                    tags = tags + soup.find_all(tag, text=text)
                else:
                    tags = tags + soup.find_all(tag, attrs=attr)

            elif len(attr) > 0:
                tags = tags + soup.find_all(attrs=attr)
        except:
            pass

    return tags


def find_tag(soup, filter_expr):
    tags = find_tags(soup, filter_expr)
    if len(tags) > 0:
        return tags[0]
    else:
        return None


def get_filter_attrs(filter_expr):
    attrs = []
    filters = filter_expr.split(";")

    for filter in filters:
        attr = {}
        tag = ""
        select = ""
        text = ""
        for xfilter in filter.split(","):
            x = xfilter.split(":")

            if len(x) == 2 and x[0].strip() == "tag":
                tag = x[1].strip()
            elif len(x) == 2 and x[0].strip() == "text":
                text = x[1].strip()
            elif len(x) == 2:
                if "recompile" in x[1]:
                    attr[x[0].strip()] = re.compile(x[1].replace("recompile-", ""))
                else:
                    attr[x[0].strip()] = x[1].strip()
            elif len(x) == 1:
                select = xfilter
        item = {'attr': attr, 'tag': tag, 'select': select, 'text': text}
        attrs.append(item)

    # print(attrs)
    return attrs


def format_url(url, reference_url):
    base_url = urllib.parse.urljoin(reference_url, '/')
    if "//" not in url:
        if url[0] != "/":
            url_elements = url.split("/")
            base_url_elements = base_url.split("/")
            base_url_elements.pop()
            new_url_elt = []
            for elt in url_elements:
                if elt == "..":
                    base_url_elements.pop()
                else:
                    new_url_elt.append(elt)

            base_url_elements += new_url_elt
            return "/".join(base_url_elements)
        else:
            url = base_url + url

    return url
