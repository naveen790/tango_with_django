from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category,Page 
from rango.forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime

def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    return HttpResponseRedirect('/rango/')

def index(request):
    context = RequestContext(request)
    category_list = Category.objects.order_by("-likes")[:5]
    context_dict = {'categories': category_list}
    for category in category_list:
        category.url = category.name.replace(' ', '_')

    # Return response back to the user, updating any cookies that need changed.
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    return HttpResponse("Rango ABOUT")

def category(request, category_name_url):
    context = RequestContext(request)
    
    category_name = category_name_url.replace('_',' ')
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url}
    
    try:
        category = Category.objects.get(name= category_name)
        
        page = Page.objects.filter(category=category)
        context_dict['pages'] = page
        context_dict['category'] = category
        
    except Category.DoesNotExist:
        pass
    
    return render_to_response('rango/category.html',context_dict,context)


def add_category(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            
            return index(request)
        else:
            print form.errors
            
    else:
        form = CategoryForm()
        
    return render_to_response('rango/add_category.html', {'form': form}, context)
            
from rango.forms import PageForm

def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist.
                # Go back and render the add category form as a way of saying the category does not exist.
                return render_to_response('rango/add_category.html', {}, context)

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form},
             context)
    
def register(request):
    context = RequestContext(request)
    
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            
            registered = True
            
        else:
            print user_form.errors, profile_form.errors
            
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render_to_response('rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    
    context = RequestContext(request)
    
    if request.method == 'POST':
        
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username,password=password)
        
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
            
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
        
    else:
        return render_to_response('rango/login.html',{},context)