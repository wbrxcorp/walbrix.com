#!/usr/bin/python
# -*- coding:utf-8 -*-

import os,json,urllib2,datetime
import flask,werkzeug,markdown,feedgenerator,pytz

app = flask.Flask(__name__)

timezone = pytz.timezone("Asia/Tokyo")

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return flask.send_from_directory(os.path.join(base_dir, 'static'),
                               'robots.txt', mimetype='text/plain')

def get_json_from_cms(url, throw_404=True):
    try:
        return json.load(urllib2.urlopen(app.config["CMS_BASE"] + "/" + url))
    except urllib2.HTTPError, e:
        if e.code == 404:
            if throw_404: raise werkzeug.exceptions.NotFound()
            else: return None
        #else
        raise

    except urllib2.URLError, e:
        raise werkzeug.exceptions.ServiceUnavailable(e)

@app.route('/<page_name>.html')
def page(page_name):
    return page_with_path("",page_name)

@app.route('/<path:path>/index.xml')
def rss(path):
    page_length = 100

    data = get_json_from_cms("%s/?limit=%d" % (path,page_length))
    entries = data["entries"]

    link = "%s%s/" % (flask.request.url_root,path)
    title = data["feed_title"] if "feed_title" in data else link
    description = data["feed_description"] if "feed_description" in data else link
    lang = data["lang"] if "lang" in data else "ja"

    feed = feedgenerator.Rss201rev2Feed(title=title,link=link,feed_url=flask.request.base_url,description=description,language=lang)
    for entry in entries[:50]:
        date = datetime.datetime.fromtimestamp(entry["published_at"] / 1000)
        link = "%s%s/%s.html" % (flask.request.url_root,path, entry["name"])
        feed.add_item(title=entry["title"],link=link, description=entry["description"] if "description" in entry else None,pubdate=datetime.datetime(date.year,date.month,date.day,0,0,0,0,timezone),unique_id=link)
    response = flask.make_response(feed.writeString('utf-8'))
    response.headers["Content-Type"] = "application/xml"
    return response
    

@app.route('/<path:path>/<page_name>.html')
def page_with_path(path,page_name):
    if path.startswith("templates"): return "Not found", 404
    entry = get_json_from_cms("%s/%s.json" % (path,page_name))
    if entry["format"] == "markdown":
        entry["content"] = markdown.markdown(entry["content"], extensions=['gfm'])


    page_length = entry["page_length"] if "page_length" in entry else 20
    # 同一プレフィクスのエントリ一覧も
    entry.update(get_json_from_cms("%s/?limit=%d" % (path,page_length)))

    # 同一ラベルのエントリ一覧も
    if len(entry["labels"]) > 0:
        # TODO: 複数ラベル
        entry["labeled_entries"] = get_json_from_cms("%s/?label=%s&limit=%s" % (path, entry["labels"][0],page_length))["entries"]

    return flask.render_template(entry["template"],**entry)

@app.route('/')
def index():
    return page("index")

@app.route('/<path:path>/')
def index_with_path(path):
    return page_with_path(path,"index")

@app.route('/<path:path>/<filename>')
def send_file(path,filename):
    if path.startswith("templates"): return "Not found", 404
    return flask.send_from_directory(os.path.join(app.root_path, path), filename)

@app.template_filter("datetime")
def _datetime(t):
    now = datetime.datetime.fromtimestamp(t / 1000)
    return now.strftime(u"%Y-%m-%d %H:%M")

@app.template_filter("date")
def _date(t):
    now = datetime.datetime.fromtimestamp(t / 1000)
    return u"%d年%d月%d日" % (now.year, now.month, now.day)

if __name__ == '__main__':
    app.config.from_pyfile('default_config.py')
    app.config.from_pyfile('local_config.py', silent=True)
    app.run(host='0.0.0.0',debug=True)
