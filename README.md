django-rest-thumbnails
======================
Simple and scalable thumbnail generation via REST API

Why?
----
I couldn't find a thumbnail library suitable to large scale sites because most
libraries adopt one (or both) of the following architectures:

1. Thumbnails of arbitrary sizes are generated on user upload and,
alternatively, via management commands
2. Thumbnails of arbitrary sizes are generated during template rendering

The problems is that on high-traffic sites...

- You can't generate many thumbnails after user uploads since that blocks
workers and causes timeouts
- You can't generate many thumbnails during template rendering for the same
reasons
- You can't cope with the overhead of issuing hundreds of database/key-value
store queries to retrieve image metadata
- You can't generate thumbnails in batch when you have hundreds of gigabytes
of legacy data

This application aims to solve these issues by allowing thumbnails to be
generated on-the-fly with a REST API, or served directly via a more efficient
HTTP server when the file already exists, all under the same URL.

How does it work?
-----------------
Once configured, you can request a particular thumbnail with a URL like:

    http://thumbnailserver/path/to/file.jpg/100x100/crop/random_key.jpg

On the backend, the following things take place:

1. Reverse proxy (e.g., Nginx) try to serve the file if it exists
2. If the file doesn't exist, it sends the request upstream to Django
3. The application generates the thumbnail based on the file path and options
4. The application returns a X-Sendfile/X-Accel-Redirect instructing the proxy
to handle the output file to the client

That is, any request hits the slow backend only once, and all responses are
handled by a faster HTTP server.

How to setup the server?
----
You setup a django project to serve it with:

    from django.conf import settings
    from django.conf.urls.defaults import patterns, url, include

    urlpatterns = patterns('',
        url(r'^', include('restthumbnails.urls')),
    )

You can hook the URL onto the same project that hosts your site, but I recommend
setting up a different domain just for thumbnails.

Now, you can request a thumbnail with a URL in the format:

    http://<hostname>/<path_to_source_file>/<size>/<method>/<secret>.<extension>

That should be self-explanatory. The secret parameter is to validate that
requests come from trusted clients, so malicious users can't bog down the
server by requesting thousands of gigantic kitten images.

In this example:

    http://example.com/animals/kitten.jpg/100x100/crop/04c8f5c392a8d2b6ac86ad4e4c1dc5884a3ac317.jpg

The request will resize and crop the file at `<MEDIA_ROOT>/animals/kitten.jpg`
(using the default file storage), then return a X-Sendfile/X-Accel-Redirect
response to the same URL, which your reverse proxy should handle.

### Configuring the reverse proxy

To glue everything together, you need to configure your server to first try
serving the file, and only fallback to the Django application when it doesn't
exist.

Taking Nginx as an example, it can be accomplished with a configuration like:

    http {
        ...

        sendfile        on;

        server {
            listen       80;
            server_name  example.com;

            root    /var/www/example.com/thumbnails/;

            location ~ \.(gif|jpg|jpeg|png) {
                add_header  Cache-Control public;
                expires     30d;
                try_files   $uri @backend;
            }

            location @backend {
                internal;
                proxy_pass  http://127.0.0.1:8000; # Where Django is running
            }
        }
    }

Then selecting the Nginx backend on your project's `settings.py`:

    REST_THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.nginx.sendfile'


### Handling concurrency

To avoid dogpilling the server with simultaneous requests to the same
thumbnail, the view implements a lock (using `CACHE_BACKEND`).

While the first request is busy generating the thumbnail, subsequent requests
will temporarly return `404 Not Found`. Once the thumbnail is written to disk,
further requests don't hit the backend anymore.


What about the client?
---------------------
There's a template tag to output these URLs automatically, since you need to
provide a valid secret hash. Add `restthumbnails` to the `INSTALLED_APPS` of
your main site and use the template tag as:

    {% load thumbnail %}

    {% thumbnail model.image_field "100x100" "crop" ".jpg" as thumb %}
    <img src="{{ thumb.url }}"/>

Assuming `REST_THUMBNAILS_BASE_URL = "http://example.com/"`, this would
output:

    <img src="http://example.com/animals/kitten.jpg/100x100/crop/04c8f5c392a8d2b6ac86ad4e4c1dc5884a3ac317.jpg"/>

Because the secret hash is derived from the `SECRET_KEY` setting, make sure
this setting is in sync between your main site settings and the one running
the thumbnailing (if you opted to separate them). If the secret doesn't match,
the server will return `401 Unauthorized`.

### Size options

You can define only one dimension:

    {% thumbnail model.image_field "500x" "crop" ".jpg" as fat_kitten %}

    {% thumbnail model.image_field "x500" "crop" ".jpg" as tall_kitten %}


### Method options

`crop`
------
Crop the image, maintaining the aspect ratio when possible.

`scale`
-------
Just scale the image until it matches one or all of the dimensions.

`smart`
-------
Smart crop the image by keeping the areas with the highest entropy.


Server settings
---------------

`REST_THUMBNAILS_SOURCE_STORAGE`
-------------------------------
Default: `DEFAULT_FILE_STORAGE`, same as Django

The Django file storage class used to open the source files (the path
requested on the URL).

`REST_THUMBNAILS_STORAGE`
-------------------------
Default: `DEFAULT_FILE_STORAGE`, same as Django

The Django file storage class used to store the output thumbnail files.

`REST_THUMBNAILS_LOCK_TIMEOUT`
------------------------------
Default: `10`

The maximum amount of time workers are allowed to return `404` while a
thumbnail is being generated by another worker. This is to avoid dogpilling the server with multiple requests to the same thumbnail.

`REST_THUMBNAILS_KEY_PREFIX`
----------------------------
Default: `'restthumbnails'`

Prefix for cache key. You may change this to avoid clashes with other keys if multiple servers share the same memcached instance.

`REST_THUMBNAILS_RESPONSE_BACKEND`
----------------------------------
Default: `'restthumbnails.responses.dummy.sendfile'`

A function responsible to return an appropriate `HttpReponse` after the thumbnail is generated. The default serves the file directly using Django's built-in server and is *only* appropriate during development.


Client settings
---------------

- `REST_THUMBNAILS_BASE_URL` (Defaults to `'/'`):
The base URL for your server. It can be relative to the same server (like
`/thumbnails`) or an absolute one (`http://example.com/`)

Thanks
------
The `processors` module is adapted from [`easy-thumbnails`](http://github.com/SmileyChris/easy-thumbnails/) by Chris Beaven,
under the BSD license.
