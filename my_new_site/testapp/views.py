from django.http import HttpResponse, HttpResponseRedirect, Http404
###from django.http import Http404
from django.template import loader

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic, View


from django.utils import timezone

from django.db.models import F

from .models import UserTest, Page

import re
import hmac
    
class TestAppClass(View):
    def get(self, request):
        return render(request, 'testapp/index.html')
        
    def post(self, request):
        choice = request.POST.get('rad')
        username = request.POST.get('username')
        if choice:
            #return HttpResponseRedirect(reverse('results'), content=choice)            
            request.session['choice'] = choice
            request.session['username'] = username
            return redirect('results')
            #return redirect(ResultsView.get(request = request, choice = choice))
        else:
            return render(request, 'testapp/index.html', {'choice': "None"})
        
class ResultsView(View):
    def get(self, request):
        #choice = args[0]
        choice = request.session['choice']
        username = request.session['username']
        params = {
            'choice': choice,
            'username': username
        }
        return render(request, 'testapp/results.html', params)
        
# User stuff

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)                  
        
class SignupView(View):
    def get(self, request):
        #username = request.session['username']
        #email = request.session['email']
        next_url = str(request.META.get('HTTP_REFERER')) 
        request.session['next_url'] = next_url
        return render(request, 'testapp/signup.html')
        
    def post(self, request):
        #next_url = str(self.request.get('next_url'))
        #if not next_url or next_url.endswith("/login") or next_url.endswith("/signup"):
        #    next_url = '/'
        next_url = str(request.session.get('next_url'))
        if not next_url or next_url.endswith("/login") or next_url.endswith("/signup"):
            next_url = '/'
        
        self.username = request.POST.get('username')
        self.password = request.POST.get('password')
        self.verify = request.POST.get('verify')
        self.email = request.POST.get('email')
        
        error_flag = False
        params = dict()
        params['username'] = self.username
        params['email'] = self.email
              
        u = UserTest.by_name(self.username)
        if not valid_username(self.username):
            params['username_error'] = "That's not valid username"
            error_flag = True
        elif u:
            params['username_error'] = "That user already exists"
            error_flag = True
        
        if not valid_password(self.password):
            params['password_error'] = "That's not valid password"
            error_flag = True
        elif self.password != self.verify:
            params['verify_error'] = "Your passwords didn't match"
            error_flag = True
                
        if self.email != "" and not valid_email(self.email):
            params['email_error'] = "That's not valid email" 
            error_flag = True                  
        
        if error_flag:            
            return render(request, 'testapp/signup.html', params)
        else:
            u = UserTest.register(self.username, self.password, self.email)
            u.save()
                
            response = HttpResponse()
            login(response, request, u)
            return redirect(next_url)
            #request.session['choice'] = choice
            #request.session['username'] = self.username
            #return redirect('welcome')
        
class WelcomeView(View):
    def get(self, request):
        username = request.session.get('username')
        if not username:
            return redirect("signup")
        params = {'username': username}
        return render(request, 'testapp/welcome.html', params)

SECRET="imsosecret".encode('utf-8')
    
def hash_str(s):
    return hmac.new(SECRET, str(s).encode('utf-8')).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val
        
def set_secure_cookie(response, name, val):
    cookie_val = make_secure_val(val)
    response.set_cookie(key=name, value=cookie_val, path="/")
            
def read_secure_cookie(request, name):
    cookie_val = request.COOKIES[name]
    return cookie_val and check_secure_val(cookie_val)
     
def login(response, request, user):
    set_secure_cookie(response, 'user_id', user.id)
    request.session['username'] = user.name
        
def logout(response, request):
    #response.set_cookie(key="user_id", value="", path="/")      
    response.delete_cookie('user_id')
    request.session.pop('username')
        
class LoginView(View):
    def get(self, request):
        next_url = str(request.META.get('HTTP_REFERER')) 
        request.session['next_url'] = next_url
        #return HttpResponse(next_url)
        return render(request, 'testapp/login.html')
        
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        next_url = str(request.session.get('next_url'))        
        #return HttpResponse(next_url)
        if not next_url or next_url.endswith('/login/') or next_url.endswith("/signup/"):
            next_url = '/'
        
        u = UserTest.login(username, password)
        if u:
            #response = redirect('welcome')
            response = redirect(next_url)
            login(response, request, u)
            #request.session['username'] = username
            return response
        else :
            params = {'login_error': 'Invalid login'}
            return render(request, "testapp/login.html", params)
        
class LogoutView(View):
    def get(self, request):
        next_url = request.META.get('HTTP_REFERER', '/')
        #response = redirect('signup')
        response = redirect(next_url)
        logout(response, request)
        return response
        #self.redirect(next_url)

# wiki pages
        
class EditPageView(View):
    def get(self, request, *args, **kwargs):
    #def get(self, request):
        #pagename = self.kwargs.get('pagename')
        #pagename = request.session.get('pagename')
        pagename = kwargs.get('pagename')
        if not request.session.get('username'):
            return redirect('login')
       
        page = Page.latest_by_name(pagename)
        if page:
            content = page.content
        else:
            content = ""
        params = {
            'content': content, 
            'pagename': pagename,
            'username': request.session.get('username')
        }
        return render(request, "testapp/editor.html", params)
        #self.render('editor.html', content=content, pagename=pagename)
        
    def post(self, request, *args, **kwargs):
        username = request.session.get('username')
        #if not request.POST.get('username'):
        if not username:
            return render(request, "testapp/login.html")
#            return error 400
            
        pagename = kwargs.get('pagename')
        content = request.POST.get('content')
        old_page = Page.latest_by_name(pagename)
      
        if not old_page:
            if not content:
                return
            else:
                page = Page(name = pagename, content = content, version=1)
                page.save()
                
        elif old_page.content != content:
            page = Page(name = pagename, content = content, version=old_page.version+1)
            page.save()
        
        #time.sleep(0.2)
        #self.redirect("%s" % pagename)
        
        return redirect("/testapp%s" % pagename)
        
class WikiPageView(View):
    def get(self, request, *args, **kwargs):
        pagename = kwargs.get('pagename')
        version = request.GET.get("v")
        if version and version.isdigit():
            version = int(version)
            page = Page.by_name_version(pagename, version)
        else:
            page = Page.latest_by_name(pagename)               
        
        if page:
            page.content = page.content.replace('\n', "<br>")
            params = {
                'page': page,
                'username': request.session.get('username')
            }
            return render(request, "testapp/wikipage.html", params)
            #self.render('wikipage.html', page=page)
        else:
            return redirect("_edit%s" % pagename)

            
class HistoryPageView(View):
    def get(self, request, *args, **kwargs):
    #def get(self, request):
        pagename = kwargs.get('pagename')
        #pagename = request.session.get("pagename")
        pages = Page.by_name(pagename)
        if pages:
            for page in pages:
                page.content = page.content.replace('\n', "<br>")
            params = {
                'pages': pages,
                'pagename': pagename,
                'username': request.session.get('username')
            }
            return render(request, "testapp/history.html", params)
            #self.render('history.html', pages=pages, pagename=pagename)
        else:
            #return redirect("%s" % pagename)
            return redirect("/testapp/_edit%s" % pagename)
        
        
