from django.db import models

import string
import hashlib
import random
        
def make_salt():
    return "".join(random.choice(string.ascii_letters) for x in range(5))
    
def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    line = (name + pw + salt)
    h = hashlib.sha256(line.encode("utf-8")).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    return h == make_pw_hash(name, pw, salt)

class UserTest(models.Model):
    name = models.CharField(max_length = 500, blank = False)
    pw_hash = models.TextField(blank = False)
    email = models.CharField(max_length = 500, null = True)
    
    @classmethod
    def by_id(cls, uid):
        return cls.objects.filter(id = uid).first()
    
    @classmethod
    def by_name(cls, name):
        u = cls.objects.filter(name = name).first()
        return u
        
    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return UserTest(name = name,
                    pw_hash = pw_hash,
                    email = email)
    
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
            
class Page(models.Model):
    name = models.CharField(max_length = 500, blank = False)
    content = models.TextField(blank = False)
    created = models.DateTimeField(auto_now_add = True)
    modified = models.DateTimeField(auto_now = True)
    version = models.IntegerField(blank = False)
    
    #def render(self):
    #    return render_str("wikipage.html", page = self)        
    
    @classmethod
    def by_name(cls, name):
        pages = list(cls.objects.filter(name = name).order_by("-version"))
        if len(pages) > 0:            
            return pages
        return None
        
    @classmethod
    def latest_by_name(cls, name):
        pages = Page.by_name(name)
        if pages:
            p = pages[0]
            return p
        return None
    
    @classmethod
    def by_name_version(cls, name, version):
        page = Page.objects.filter(name = name).filter(version = int(version)).get()
        return page
        
    def get_version(self):
        return self.version            