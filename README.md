django-rest-thumbnails
======================
Simple and scalable thumbnail generation via REST API

Why?
----
I couldn't find a thumbnail library suitable to large scale sites because most
libraries adopt one (or both) of the following architectures:

1. Thumbnails of preset sizes are generated upon user upload and,
alternatively, via management commands
2. Thumbnails of arbitrary sizes are generated during template rendering

The problems is that on high-traffic sites...

- You can't generate many thumbnails upon user uploads since that blocks
workers and causes timeouts
- You can't generate many thumbnails during template rendering for the same
reasons
- You can't cope with the overhead of issuing hundreds of database/key-value
store queries to retrieve image metadata
- You can't generate thumbnails in batch when you have hundreds of gigabytes
of legacy data

This application aims to solve these issues by separating concerns (requesting
thumbnails vs. generating thumbnails) with a REST API. This way you can
leverage HTTP to cache and handle most of the load with a proxy (e.g. Varnish),
keeping the flexibility to generate thumbnails of any size on-the-fly.

How to setup the server?
----
You setup a django project to serve it with:

    from django.conf import settings
    from django.conf.urls.defaults import patterns, url, include

    urlpatterns = patterns('',
        url(r'^t/', include('restthumbnails.urls')),
    )

You can hook the URL on the same project that hosts your site, but I recommend
setting up a different domain just to serve the API.

Now, you can request a thumbnail with a URL in the format:

    http://<hostname>/<path_to_source_file>/<size>/<method>/?secret=XXX

That should be self-explanatory. The secret parameter is to validate that
requests come from trusted clients, so malicious users can't bog down the
server by requesting thousands of gigantic kitten images.

In this example:

    http://example.com/t/animals/kitten.jpg/100x100/crop/?secret=04c8f5c392a8d2b6ac86ad4e4c1dc5884a3ac317

The request will resize and crop the file at `<MEDIA_ROOT>/animals/kitten.jpg`
(using the default file storage) and issue `301 Moved Permanently` to the
output file on your media server.

Assuming `MEDIA_URL = "http://media.example.com"`, that would be:

    http://media.example.com/animals/kitten_100x100_crop.jpg

Because this is a `301` response, you can setup a proxy (e.g. Varnish) to cache
all responses from this domain such that only the first request hits your
"slow" backend and generates the thumbnail - all posterior requests get
redirected directly to the media server.

### Handling concurrency

To avoid dogpilling the server with simultaneous requests to the same
thumbnail, the view implements a lock (using `CACHE_BACKEND`).

While the first request is busy generating the thumbnail, subsequent requests
will just return `404 Not Found`. Once the first request finishes successfully,
the `301` response gets cached so all requests following don't hit backend
anymore. This way we can trade consistency for higher concurrency.


What about the client?
---------------------
There's a template tag to output these URLs automatically. Just add
`restthumbnails` to your `INSTALLED_APPS` and use the template tag as:

    {% load thumbnail %}

    {% thumbnail model.image_field "100x100" "crop"  as thumb %}
    <img src="{{ thumb.url }}"/>

Assuming `REST_THUMBNAILS_BASE_URL = "http://example.com/t/"` on settings, this
would output:

    <img src="http://example.com/t/animals/kitten.jpg/100x100/crop/?secret=04c8f5c392a8d2b6ac86ad4e4c1dc5884a3ac317"/>

Because the secret hash is derived from the `SECRET_KEY` setting, make sure
this setting is in sync between the server and the client, otherwise it will
return `401 Unauthorized`.

You can define only one dimension:

    {% thumbnail model.image_field "500x" "crop" as fat_kitten %}

    {% thumbnail model.image_field "x500" "crop" as tall_kitten %}

You can also choose between 3 different methods:

- `crop`: Crop the image, maintaining the aspect ratio when possible.
- `scale`: Just scale the image until it matches one or all of the dimensions.
- `smart`: Smart crop the image by keeping the areas with the highest entropy.


Server settings
---------------

`REST_THUMBNAILS_SOURCE_STORAGE`
-------------------------------
Default: `DEFAULT_FILE_STORAGE`

The Django file storage class used to open the source files (the path
requested on the URL).

`REST_THUMBNAILS_STORAGE`
-------------------------
Default: `DEFAULT_FILE_STORAGE`

The Django file storage class used to store the output thumbnail files.

`REST_THUMBNAILS_USE_SECRET_PARAM`
----------------------------------
Default: `True`

Wheter to refuse requests without a valid `REST_THUMBNAILS_SECRET_PARAM`
parameter on query string.

`REST_THUMBNAILS_SECRET_PARAM`
------------------------------
Default: `'secret'`

The query string parameter appended to the URL.

`REST_THUMBNAILS_LOCK_TIMEOUT`
------------------------------
Default: `10`

The maximum amount of time workers are allowed to return 404 while a
thumbnail is generated by another worker. This is to avoid dogpilling only. If
the thumbnail fails to be generated because the source doesn't exist, it
will issue a permanent redirect anyway and let the media server handle
posterior requests.

`REST_THUMBNAILS_RESPONSE_HEADERS`
----------------------------------
Default: `DEFAULT_RESPONSE_HEADERS = {
    'cache_control': 'public',
    'max_age': '31536000'}`

Headers sent along all responses from the thumbnail server. By default,
allow proxies to cache all responses (including 301 Permanent Redirects)
up to 1 year.

Client settings
---------------

- `REST_THUMBNAILS_BASE_URL` (Defaults to `'/'`):
The base URL for your server. It can be relative to the same server (like
`/thumbnails`) or an absolute one (`http://thumbs.example.com/`)

- `REST_THUMBNAILS_VIEW_URL` (Defaults to `'%(source)s/%(size)s/%(method)s/'`):
The view signature. You don't need to change this unless you hook the
`ThumbnailView` manually.

Thanks
------
The `processors` module is adapted from [`easy-thumbnails`](http://github.com/SmileyChris/easy-thumbnails/) by Chris Beaven,
under the BSD license.

