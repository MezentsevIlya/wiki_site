import datetime
from django import template
from testapp.models import Page

register = template.Library()


def gray_style(lst):
    for n, x in enumerate(lst):
        if n % 2 == 0:
            yield x, ''
        else:
            yield x, 'gray'

@register.simple_tag
def get_gray_style_tag(pages):
    lst = []
    for i in range(len(pages)):
        if i % 2 == 0:
            lst.append((pages[i], ''))
        else:
            lst.append((pages[i], 'gray'))
    return lst

@register.simple_tag
def get_modified_time_format(page):
    return page.modified.strftime("%c")
    
@register.simple_tag
def get_100_and_replace(page):
    return page.content[:100].replace("<br>", " ")
    
@register.simple_tag
def get_page_version(page):
    return page.get_version()
    
    