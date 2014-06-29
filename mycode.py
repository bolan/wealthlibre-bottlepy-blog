# -*- coding: utf-8 -*-

from bottle import route, run, get, post, request, response, template, static_file
import os
import re
import string
import math
from xml.sax.saxutils import escape, unescape
import shelve
from datetime import datetime

# import paste

curdir = os.path.dirname(__file__)
articles = shelve.open(os.path.join(curdir, "articles_db"), writeback = True)
article_id = shelve.open(os.path.join(curdir, "article_id_db"), writeback = True)
admin = shelve.open(os.path.join(curdir, "admin_db"), writeback = True)

with open("/dev/random") as f:
    getSecretRand = f.read(32)
secretBase64 = getSecretRand.encode('base64','strict')


# WARNING: For your safty! Please change this part to your own user
# name before using!
admin['YOURNAME1'] = 'YOURPASSWORD1'
# admin['YOURNAME2'] = 'YOURPASSWORD2'
# admin['YOURNAME3'] = 'YOURPASSWORD3'
admin.sync()

entries_per_page = 38 

def smart_slice(content, length=160, suffix = ' ...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0] + suffix

if article_id == {}:
    article_id['id'] = 0
    article_id.sync()

#for i in articles.keys():
#    articles[str(i)] = {'title':articles[str(i)]['title'], 'category':'Unclassified', 'content':articles[str(i)]['content']}




@route('/')
def hello():
    return """
This is an example of a static front page. <br /><br />

Currently, this server hosts:<br>
1. <a href="/blog">Wealth & Libre Blog</a><br>
2. <a href="/the_game">Free and Open Source Video Game Project</a>, <br> 
welcome!

    """

@route('/the_game')
def the_game():
    return """
<!DOCTYPE html>
This is an example of a static sub-page. 

    """

@route('/admin')
def admin_page():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        return """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
        """
    else:
        return """
            <h2>Bo Lan's Blog Admin System</h2>
            <p>Please login before using.</p>
            <form action="/login" method="post">
                Username: <input name="username" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        """

@get('/write')
def write():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        return """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <p>This is an admin page to add a new article for website.

            <form action="/write" method="post">
                Title: 
                <br />
                <input name="title" type="text" size="60"/>
                <br />
                Category:<br />
                <input name="category" type="text" />
                <br />
                Content: 
                <br />
                <textarea name="content" cols="80" rows="23"></textarea>
                <br />
                <a href="#" onClick="MyWindow=window.open('/upload','MyWindow','toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=no,resizable=no,width=400,height=300'); return false;">Upload a file</a>
                <br />
                <p><input value="Submit article" type="submit" /></p>
            </form>
        """
    else:
        return "<p>You are not allowed to access this page."

@post('/write')
def do_write():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        article_id['id'] = article_id['id']+1
        title = request.forms.get('title')
        category = request.forms.get('category')
        content = request.forms.get('content')
        editTime = datetime.now().strftime("%a, %Y %b %d %H:%M:%S")
        urlTime = datetime.now().strftime("-%Y-%m-%d-%H-%M-%S-%f")

        urltitle = title
        urltitle = urltitle.lower()
        urltitle = urltitle.translate(string.maketrans("",""), string.punctuation)
        urltitle = string.replace(urltitle, ' ','-')
        urltitle = urltitle + urlTime

        urlcat = category
        urlcat = urlcat.lower()
        urlcat = urlcat.translate(string.maketrans("",""), string.punctuation)
        urlcat = string.replace(urlcat, ' ', '-')

        articles[str(article_id['id'])] = {'title':title, 'category':category, 'content':content, 'urltitle':urltitle, 'urlcat':urlcat}
        articles.sync()
        article_id.sync()

        return """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <p>The new article has been added, thank you.
            <p>Please click <a href="/blog">here</a> to return.
            <p>Please click <a href="/write">here</a> to add a new one.
        """
    else:
        return "<p>You are not allowed to post anything."

@route('/edit')
def edit():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        return template(
            """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <p>This is an admin page for editing articles.</p>
            <% for i in range(article_id['id'], 0, -1): %>
                <h3 style="display: inline;">{{ articles[str(i)]['title'] }}</h3> -- <a href="/edit/{{ i }}">[Edit]</a>
                <br />
                <br />
            <% end %>
            """
        , article_id = article_id
        , articles = articles
        )
    else:
        return "<p>You are not allowed to read this page.</p>"

@route('/edit/<edit_id>')
def editing(edit_id):
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        return template (
            """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <head>
            <script>
            function displaceResult() {
                alert(document.getElementById("content").defaultValue);
            }
            </script>
            </head>

            <p>You are now editing: <i>{{ articles[str(edit_id)]['title'] }}</i></p>
            <form action="/edit/{{edit_id}}" method="post">
                Title:<br />
                <input name="title" type="text" size="60" value="{{ articles[str(edit_id)]['title'] }}" /> <br />
                Category:<br />
                <input name="category" type="text" value="{{ articles[str(edit_id)]['category'] }}" /> <br />
                Content:<br />
                <textarea id="content" name="content" cols="80" rows="23">{{ articles[str(edit_id)]['content'] }}</textarea><br />
                <a href="#" onClick="MyWindow=window.open('/upload','MyWindow','toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=no,resizable=no,width=400,height=300'); return false;">Upload a file</a><br />
                <p><input value="Submit editing" type="submit" /></p>
            </form>
            """
            , edit_id = edit_id
            , articles = articles
        )
    else:
        return "<p>You are not allowed to read this page.</p>"

@post('/edit/<edit_id>')
def do_edit(edit_id):
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        title = request.forms.get('title')
        category = request.forms.get('category')
        content = request.forms.get('content')
        editTime = datetime.now().strftime("%a, %Y %b %d %H:%M:%S")
        urlTime = datetime.now().strftime("-%Y-%m-%d-%H-%M-%S-%f")

        if title != articles[str(edit_id)]['title']:
            urltitle = title
            urltitle = urltitle.lower()
            urltitle = urltitle.translate(string.maketrans("",""), string.punctuation)
            urltitle = string.replace(urltitle, ' ','-')
            urltitle = urltitle + urlTime
        else:
            urltitle = articles[str(edit_id)]['urltitle']

        urlcat = category
        urlcat = urlcat.lower()
        urlcat = urlcat.translate(string.maketrans("",""), string.punctuation)
        urlcat = string.replace(urlcat, ' ', '-')

        articles[str(edit_id)] = {'title':title, 'category':category, 'content':content, 'urltitle':urltitle, 'urlcat':urlcat}
        articles.sync()
        article_id.sync()

        return template (
            """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <p>The article has been edited, thank you.
            <p>Please click <a href="/blog/{{ articles[str(edit_id)]['urltitle'] }}">here</a> read the edited result. 
            <p>Click <a href="/edit">here</a> to edit another one.
            <p>Click <a href="/blog">here</a> to return.
            """
            , edit_id = edit_id
            , articles = articles
        )
    else:
        return "<p>You are not allowed to edit.</p>"

@route('/delete')
def delete():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        return template(
            """
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <p>This is an admin page for deleting articles.</p>
            <% for i in range(article_id['id'], 0, -1): %>
                <h3 style="display: inline;">{{ articles[str(i)]['title'] }}</h3> -- 
                <form style="display: inline;" action="/delete/{{ i }}" method="post">
                    <input value="Delete" type="submit" />
                </form> 
                <br />
                <br />
            <% end %>
            """
            , article_id = article_id
            , articles = articles
        )
    else:
        return "<p>You are not allowed to read this page.</p>"

@post('/delete/<delete_id>')
def do_delete(delete_id):
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        if int(delete_id) == article_id['id']:
            del articles[delete_id]
            article_id['id'] = article_id['id'] - 1
        else:
            del articles[delete_id]
            for i in range(int(delete_id), article_id['id']):
                articles[str(i)] = articles[str(i+1)]
            del articles[str(article_id['id'])]
            article_id['id'] = article_id['id'] - 1
        
        articles.sync()
        article_id.sync()

        return '''
            <h2>Bo Lan's Blog Admin System</h2>
            | <a href="/blog">Back to index</a> | <a href="/write">Write New Article</a> | <a href="/edit">Edit Articles</a> | <a href="/delete">Delete Articles</a> | <a href="/logout">Logout</a> |
            <p>Deleting successfully, click <a href="/blog">here</a> to index.</p>
            <p>Or, click <a href="/delete">here</a> to delete more articles</p>
        '''
    else:
        return "You are not allowed to delete."

@get('/login')
def login():
    return """
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    """

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    if username in admin and admin[username] == password:
        response.set_cookie("account", username, secret=secretBase64)
        return """
            <p>Your login information was correct.
            <script>document.write('<a href="' + document.referrer + '">Go to previous page</a>');</script>
        """
    else:
        return """
<p>Login failed, </p> <script>document.write('<a href="' + document.referrer + '">Go to previous page</a>');</script>
        """

@route('/logout')
def logout():
    response.delete_cookie("account")
    return """
        <p>You have logout.</p>
        <p>Click <a href="/blog">here</a> to index.</p>
    """

@route('/blog')
def blog():

    return template (
        """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Wealth & Libre Blog</title>    

        <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>

        <script>
        $(document).ready(function() {
            $(".hoverenlarge").hover(function() {
                $(this).stop().css({"border":"1px solid gray", "backgroundColor":"white"}).animate({
                    fontSize: "13pt"
                }, 'fast');
            }, function() {
                $(this).stop().css({"border":"0px solid gray", "backgroundColor":"whitesmoke"}).animate({
                    fontSize: "12pt"
                }, 'fast');
            });
        });
        </script>

        <style>
        html {
            background: whitesmoke;
        }
        .hoverenlarge {
            padding: 15px;
            border-radius:25px;
            border: 0px solid gray;
            background: whitesmoke;
        }
        </style>
        </head>


        <header>
        <h1>Wealth & Libre Blog</h1> 
        </header>

        <div style="padding-left:38px; width:80%; float:left;">
        <% if article_id['id'] <= entries_per_page: %>
            <% for i in range(article_id['id'], 0, -1):
                if articles[str(i)]: %>
                    <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                    <div class="hoverenlarge clickable">
                    <h3>{{ articles[str(i)]['title'] }}</h3>
                    %rmhtml = re.sub('<[^<]+?>', ' ', articles[str(i)]['content'])
                    %sliced = smart_slice(rmhtml)
                    {{ sliced }} [read more]
                    </div>
                    </a>
                    <hr />
                <% end %> 
            <% end %>
        <% else: %>
            <% for i in range(article_id['id'], article_id['id'] - entries_per_page, -1):
                if articles[str(i)]: %>
                    <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                    <div class="hoverenlarge clickable">
                    <h3>{{ articles[str(i)]['title'] }}</h3>
                    {{ !smart_slice(articles[str(i)]['content']) }} [read more]
                    </div>
                    </a>
                    <hr />
                <% end %>
            <% end %>
            <br />
            Page: <a href="/blog/page/2">[Next Page]</a>
        <% end %>
        </div>

        <div class="sidebar" style="float:left; padding-left:8px; width:15%">
        <h3>Categories</h3>
        <% cat_tmp = [] %> 
        <% for i in articles.keys(): %>
            <% if not articles[str(i)]['category'] in cat_tmp: %>
                <% cat_tmp.append(articles[str(i)]['category']) %>
                <p><a href="/blog/category/{{ articles[str(i)]['urlcat'] }}">{{ articles[str(i)]['category'] }}</a></p>
            <% end %>
        <% end %>
        </div>
        <br />
        
        <footer style = "padding-left:38px; clear:both;">
        <br />
        <font size = "2" face = "sans">
        Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation.
        </font>
        </footer>
        </html>
        """
        , article_id = article_id
        , articles = articles
        , smart_slice = smart_slice
        , entries_per_page = entries_per_page
        , re = re
    )

@route('/blog/page/<page_num>')
def pagination(page_num):
    page_num = int(page_num)
    if page_num <= 1:
        return """
            <head>
            <meta http-equiv="refresh" content="0; url=/blog" />
            </head>
        """
    if page_num > article_id['id'] / entries_per_page + 1:
        return "No more page."

    if article_id['id'] <= entries_per_page:
        return "No more page."
    else:
        return template (
            """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Wealth & Libre Blog</title>    

            <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>

            <script>
            $(document).ready(function() {
                $(".hoverenlarge").hover(function() {
                    $(this).stop().css({"border":"1px solid gray", "backgroundColor":"white"}).animate({
                        fontSize: "13pt"
                    }, 'fast');
                }, function() {
                    $(this).stop().css({"border":"0px solid gray", "backgroundColor":"whitesmoke"}).animate({
                        fontSize: "12pt"
                    }, 'fast');
                });
            });
            </script>

            <style>
            html {
                background: whitesmoke;
            }
            .hoverenlarge {
                padding: 15px;
                border-radius:25px;
                border: 0px solid gray;
                background: whitesmoke;
            }
            </style>
            </head>

            <header>
            <h1>Wealth & Libre Blog</h1> 
            </header>
            
            <div style="padding-left: 38px; float:left; width:80%">
            <% if (article_id['id'] - (entries_per_page * page_num)-1) < 0: %>
                <% for i in range(article_id['id'] - (entries_per_page * (page_num - 1)), 0, -1): %>
                    <% if articles[str(i)]: %>
                        <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                        <div class="hoverenlarge">
                        <h3>{{ articles[str(i)]['title'] }}</h3>
                        {{ !smart_slice(articles[str(i)]['content']) }} [read more]
                        </div>
                        </a>
                        <hr />
                    <% end %>
                <% end %>
            <% else: %>
                <% for i in range(article_id['id'] - (entries_per_page * (page_num - 1)), article_id['id'] - (entries_per_page * page_num), -1): %>
                    <% if articles[str(i)]: %>
                        <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                        <div class="hoverenlarge">
                        <h3>{{ articles[str(i)]['title'] }}</h3>
                        {{ !smart_slice(articles[str(i)]['content']) }} [read more]
                        </div>
                        </a>
                        <hr />
                    <% end %>
                <% end %>
            <% end %>
            <a href="/blog/page/{{ page_num - 1}}">[Previous Page]</a>, Page: {{ page_num }}, <a href="/blog/page/{{ page_num + 1}}">[Next Page]</a>
            </div>
            <br />

            <div class="sidebar" style="float:left; padding-left:8px; width:15%">
            <h3>Categories</h3>
            <% cat_tmp = [] %> 
            <% for i in articles.keys(): %>
                <% if not articles[str(i)]['category'] in cat_tmp: %>
                    <% cat_tmp.append(articles[str(i)]['category']) %>
                    <p><a href="/blog/category/{{ articles[str(i)]['urlcat'] }}">{{ articles[str(i)]['category'] }}</a></p>
                <% end %>
            <% end %>
            </div>
            <br />
        
            <br />
            <footer style = "padding-left:38px; clear:both;">
            <font size = "2" face = "sans">
            Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation.
            </font>
            </footer>
            </html>
            """
            , article_id = article_id
            , articles = articles
            , smart_slice = smart_slice
            , entries_per_page = entries_per_page
            , page_num = page_num
        )

@route('/blog/category/<cat_name>')
def cat_index(cat_name):

    cat_articles = []
    for i in range(article_id['id'], 0, -1):
        if articles[str(i)]['urlcat'] == cat_name:
            cat_realname = articles[str(i)]['category']
            cat_articles.append(i)

    cat_articles_count = 0
    for j in cat_articles:
        cat_articles_count = cat_articles_count + 1 

    if cat_articles_count <= entries_per_page:
        return template(
            """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Wealth & Libre Blog -- {{ cat_realname }}</title>    

            <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>

            <script>
            $(document).ready(function() {
                $(".hoverenlarge").hover(function() {
                    $(this).stop().css({"border":"1px solid gray", "backgroundColor":"white"}).animate({
                        fontSize: "13pt"
                    }, 'fast');
                }, function() {
                    $(this).stop().css({"border":"0px solid gray", "backgroundColor":"whitesmoke"}).animate({
                        fontSize: "12pt"
                    }, 'fast');
                });
            });
            </script>

            <style>
            html {
                background: whitesmoke;
            }
            .hoverenlarge {
                padding: 15px;
                border-radius:25px;
                border: 0px solid gray;
                background: whitesmoke;
            }
            </style>
            </head>

            <header>
            <h1>Wealth & Libre Blog -- {{ cat_realname }}</h1> 
            </header>

            <div style="padding-left: 38px; float:left; width:80%">
            <% for_count = 0 %>
            <% for i in cat_articles: %>
                <% for_count = for_count + 1 %>
                <% if for_count > entries_per_page: %>
                    <% break %>
                <% end %>
                <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                <div class="hoverenlarge">
                <h3>{{ articles[str(i)]['title'] }}</h3>
                {{ !smart_slice(articles[str(i)]['content']) }} [read more]
                </div>
                </a>
                <hr />
            <% end %>
            </div>

            <div class="sidebar" style="float:left; padding-left:8px; width:15%">
            <h3>Categories</h3>
            <% cat_tmp = [] %> 
            <% for i in articles.keys(): %>
                <% if not articles[str(i)]['category'] in cat_tmp: %>
                    <% cat_tmp.append(articles[str(i)]['category']) %>
                    <p><a href="/blog/category/{{ articles[str(i)]['urlcat'] }}">{{ articles[str(i)]['category'] }}</a></p>
                <% end %>
            <% end %>
            </div>
            <br />

            <footer style = "padding-left:38px; clear:both;">
            <br />
            <font size = "2" face = "sans">
            Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation.
            </font>
            </footer>
            </html>
            """
            , cat_articles = cat_articles
            , cat_name = cat_name
            , cat_realname = cat_realname
            , articles = articles
            , smart_slice = smart_slice
            , entries_per_page = entries_per_page
        )
    else: 
        return template (
            """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Wealth & Libre Blog -- {{ cat_realname }}</title>    

            <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>

            <script>
            $(document).ready(function() {
                $(".hoverenlarge").hover(function() {
                    $(this).stop().css({"border":"1px solid gray", "backgroundColor":"white"}).animate({
                        fontSize: "13pt"
                    }, 'fast');
                }, function() {
                    $(this).stop().css({"border":"0px solid gray", "backgroundColor":"whitesmoke"}).animate({
                        fontSize: "12pt"
                    }, 'fast');
                });
            });
            </script>

            <style>
            html {
                background: whitesmoke;
            }
            .hoverenlarge {
                padding: 15px;
                border-radius:25px;
                border: 0px solid gray;
                background: whitesmoke;
            }
            </style>
            </head>

            <header>
            <h1>Wealth & Libre Blog -- {{ cat_realname }}</h1> 
            </header>

            <div style="padding-left: 38px; float:left; width:80%">
            <% for_count = 0 %>
            <% for i in cat_articles: %>
                <% for_count = for_count + 1 %>
                <% if for_count > entries_per_page: %>
                    <% break %>
                <% end %>
                <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                <div class="hoverenlarge">
                <h3>{{ articles[str(i)]['title'] }}</h3>
                {{ !smart_slice(articles[str(i)]['content']) }} [read more]
                </div>
                </a>
                <hr />
            <% end %>
            Page: <a href="/blog/category/{{ cat_name }}/page/2">[Next Page]</a>
            <br />
            </div>

            <div class="sidebar" style="float:left; padding-left:8px; width:15%">
            <h3>Categories</h3>
            <% cat_tmp = [] %> 
            <% for i in articles.keys(): %>
                <% if not articles[str(i)]['category'] in cat_tmp: %>
                    <% cat_tmp.append(articles[str(i)]['category']) %>
                    <p><a href="/blog/category/{{ articles[str(i)]['urlcat'] }}">{{ articles[str(i)]['category'] }}</a></p>
                <% end %>
            <% end %>
            </div>
            <br />

            <footer style = "padding-left:38px; clear:both;">
            <br />
            <font size = "2" face = "sans">
            Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation.
            </font>
            </footer>
            </html>
            """
            , cat_articles = cat_articles
            , cat_name = cat_name
            , cat_realname = cat_realname
            , articles = articles
            , smart_slice = smart_slice
            , entries_per_page = entries_per_page
        )

@route('/blog/category/<cat_name>/page/<cat_page_num>')
def cat_pagination(cat_name, cat_page_num):
    cat_page_num = int(cat_page_num)
    cat_articles = []

    for i in range(article_id['id'], 0, -1):
        if articles[str(i)]['urlcat'] == cat_name:
            cat_realname = articles[str(i)]['category']
            cat_articles.append(i)

    cat_articles_count = 0
    for j in cat_articles:
        cat_articles_count = cat_articles_count + 1 

    if cat_page_num <= 1:
        return template (
            """
            <head>
            <meta http-equiv="refresh" content="0; url=/blog/category/{{ cat_name }}" />
            </head>
            """    
            , cat_name = cat_name
        )

    if cat_page_num > cat_articles_count / entries_per_page + 1:
        return "No more page."

    if cat_articles_count <= entries_per_page:
        return "No more page."
    else:
        return template (
            """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Wealth & Libre Blog -- {{ cat_realname }}</title>    

            <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>

            <script>
            $(document).ready(function() {
                $(".hoverenlarge").hover(function() {
                    $(this).stop().css({"border":"1px solid gray", "backgroundColor":"white"}).animate({
                        fontSize: "13pt"
                    }, 'fast');
                }, function() {
                    $(this).stop().css({"border":"0px solid gray", "backgroundColor":"whitesmoke"}).animate({
                        fontSize: "12pt"
                    }, 'fast');
                });
            });
            </script>

            <style>
            html {
                background: whitesmoke;
            }
            .hoverenlarge {
                padding: 15px;
                border-radius:25px;
                border: 0px solid gray;
                background: whitesmoke;
            }
            </style>
            </head>

            <header>
            <h1>Wealth & Libre Blog -- {{ cat_realname }}</h1> 
            </header>

            <div style="padding-left: 38px; float:left; width:80%">
            <% for_count = 0 %>
            <% for i in cat_articles: %>
                <% for_count = for_count + 1 %>
                <% if for_count > (entries_per_page * (cat_page_num - 1)): %>
                    <a href="/blog/{{ articles[str(i)]['urltitle'] }}" style="display:block; text-decoration:none; color:black">
                    <div class="hoverenlarge">
                    <h3>{{ articles[str(i)]['title'] }}</h3>
                    {{ !smart_slice(articles[str(i)]['content']) }} [read more]
                    </div>
                    </a>
                    <hr />
                <% end %>
                <% if for_count >= (entries_per_page * cat_page_num): %>
                    <% break %>
                <% end %>
            <% end %>
            <a href="/blog/category/{{ cat_name }}/page/{{ str(cat_page_num - 1) }}">[Previous Page]</a> Page: {{ str(cat_page_num) }} <a href="/blog/category/{{ cat_name }}/page/{{ str(cat_page_num + 1) }}">[Next Page]</a>
            <br />
            </div>

            <div class="sidebar" style="float:left; padding-left:8px; width:15%">
            <h3>Categories</h3>
            <% cat_tmp = [] %> 
            <% for i in articles.keys(): %>
                <% if not articles[str(i)]['category'] in cat_tmp: %>
                    <% cat_tmp.append(articles[str(i)]['category']) %>
                    <p><a href="/blog/category/{{ articles[str(i)]['urlcat'] }}">{{ articles[str(i)]['category'] }}</a></p>
                <% end %>
            <% end %>
            </div>
            <br />

            <footer style = "padding-left:38px; clear:both;">
            <br />
            <font size = "2" face = "sans">
            Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation.
            </font>
            </footer>
            </html>
            """
            , cat_articles = cat_articles
            , cat_name = cat_name
            , cat_realname = cat_realname
            , articles = articles
            , smart_slice = smart_slice
            , cat_page_num = cat_page_num
            , cat_articles_count = cat_articles_count
            , entries_per_page = entries_per_page
        )

@route('/blog/<urltitle>')
def read(urltitle):
    for read_id in articles.keys():
        if urltitle == articles[str(read_id)]['urltitle']:
            break
    
    html_article = string.replace(articles[str(read_id)]['content'], '\r\n', '<br />')
    return template (
        """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Wealth & Libre Blog -- {{ articles[str(read_id)]['title'] }}</title>    
        <style type="text/css">
        body {
        background-color:whitesmoke
        }

        img {
        max-width:640px
        }

        video {
        max-width:640px
        }
        </style>
        </head>

        <body>
        <header>
        <h1>Wealth & Libre Blog</h1> 
        </header>

        <div style="padding-left: 38px;">
        <h3>{{ articles[str(read_id)]['title'] }}</h3>
        {{! html_article }}
        <br />
        <br />
        <br />
        <a href="/blog">Back to Blog's index</a>
        </div>
        <br />
        <footer style="padding-left: 38px">
        <font size = "2" face = "sans">
        Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation.
        </font>
        </footer>
        </body>
        </html>
        """
        , articles = articles
        , read_id = read_id
        , html_article = html_article
    )
    

@route('/static/<filename:path>')
def static(filename):
    getCurrentPath = os.path.dirname(os.path.abspath(__file__))
    return static_file(filename, root = getCurrentPath + '/static')

@route('/upload')
def upload():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        return """
            <p>You can upload your file here.
            
            <form action="/upload" method="post" enctype="multipart/form-data">
                <br />
                Select a file: <input type="file" name="upload" />
                <br />
                <input type="submit" value="Start upload" />
            </form>
        """
    else:
        return """
        <p>You need to login before uploading</p>

        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
        """

@post('/upload')
def do_upload():
    username = request.get_cookie("account", secret=secretBase64)
    if username:
        upload = request.files.get('upload')
        name, ext = os.path.splitext(upload.filename)
        name = "webup" + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S-") + name
        upload.filename = name + ext
        getCurrentPath = os.path.dirname(os.path.abspath(__file__))
        save_path = getCurrentPath + '/static'
        upload.save(save_path)
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return template(
                """
                <p>Uploading successful, your file address:</p>
                <p><code>http://wealthlibre.info/static/{{ filename }}</code></p>
                <p>Your file is an image, so you can copy following html to your web editor:</p>
                <code>&lt;a href="http://wealthlibre.info/static/{{ filename }}"&gt;&lt;img src="http://wealthlibre.info/static/{{ filename }}" /&gt;&lt;/a&gt;</code>
                <p>or use this without link: </p>
                <code>&lt;img src="http://wealthlibre.info/static/{{ filename }}" /&gt;</code>

                """
                , filename = upload.filename
            )
        if ext in ['.ogg', '.ogv', '.webm']:
            return template(
                """
                <p>Uploading successful, your file address:</p>
                <p><code>http://wealthlibre.info/static/{{ filename }}</code></p>
                <p>Your file is an video/audio, so you can copy following html to your web editor:</p>
                <code>&lt;video src="http://wealthlibre.info/static/{{ filename }}" controls&gt;

&lt;p&gt;Your browser does not support the HTML5 video.&lt;/p&gt;&lt;/video&gt; </code>
                """
                , filename = upload.filename
            )
        else:
            return template(
                """
                <p>Uploading successful, your file address:</p>
                <code>http://wealthlibre.info/static/{{ filename }}</code>
                """,
                filename = upload.filename
            )
    else:
        return """
            <p>You are not allowed to update anything, please login firstly:</p>
            <form action="/login" method="post">
                Username: <input name="username" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        """

run(host="127.0.0.1", port=8080, debug=True, reloader=True)
#run(server='paste', host="0.0.0.0", port=80, debug=False, reloader=True)
