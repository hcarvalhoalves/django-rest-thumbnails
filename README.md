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

    THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.nginx.sendfile'


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

Assuming `THUMBNAILS_PROXY_BASE_URL = "http://example.com/"`, this would
output:

    <img src="http://example.com/animals/kitten.jpg/100x100/crop/04c8f5c392a8d2b6ac86ad4e4c1dc5884a3ac317.jpg"/>

Because the secret hash is derived from the `SECRET_KEY` setting, if you choose
to run the thumbnail server in a different domain / worker process, you need to
make sure this value is in sync. If the secret doesn't match, the server will
return `401 Unauthorized`.

Thumbnail tag
-------------

The thumbnail tag accepts either a `FileField` instance…

    {% thumbnail model.image_field "100x100" "crop" ".jpg" as field_kitten %}

or a path (relative to `THUMBNAILS_SOURCE_ROOT`)…

    {% thumbnail "animals/kitten.jpg" "100x100" "crop" ".jpg" as path_kitten %}

### Size options

At least one dimension is required. The app will scale and crop appropriately:

    {% thumbnail model.image_field "500x" "crop" ".jpg" as fat_kitten %}

    {% thumbnail model.image_field "x500" "crop" ".jpg" as tall_kitten %}

To maintain consistency, you may want to use predefined variables:

    {% thumbnail model.image_field avatar_size "crop" ".jpg" as kitten_avatar %}


### Method options

#### crop
Crop the image. It will maintain the aspect ratio if only one dimension is defined.

#### scale
Just scale the image until it matches at least one of the dimensions.

#### smart
Smart crop the image, by keeping the areas with the highest entropy intact.


Server settings
---------------

#### THUMBNAILS_SOURCE_STORAGE_BACKEND
*Default:* `'django.core.files.storage.FileSystemStorage'`

The Django `FileStorage` class used to open the source files images (the path
requested on the URL).

#### THUMBNAILS_SOURCE_ROOT
*Default:* `MEDIA_ROOT`

The absolute path for the directory holding your source images.

#### THUMBNAILS_STORAGE_BACKEND
*Default:* `'django.core.files.storage.FileSystemStorage'`

The Django `FileStorage` class used to store the output thumbnail files.

#### THUMBNAILS_STORAGE_ROOT
*Default:* `'%(MEDIA_ROOT)s/../thumbnails/'`

The absolute path for the directory holding the output files. By default, it's
a directory called `thumbnails` sitting *beside* your `MEDIA_ROOT`.

### THUMBNAILS_STORAGE_BASE_PATH
*Default:* `'/thumbnails/'`

Base path used for X-Sendfile/X-Accel-Redirect responses. This gets
concatenated to the file path, and should *always* be a URI relative
to the same host. Effectively, this should return the same URL that
was requested so you can use the `try_files` trick.

#### THUMBNAILS_LOCK_TIMEOUT
*Default:* `10`

The maximum amount of time workers are allowed to return `404` while another
worker is busy generating the same thumbnail. This is to avoid dogpilling the
server with multiple requests to the same thumbnail.

#### THUMBNAILS_KEY_PREFIX
*Default:* `'restthumbnails'`

Prefix for cache key. You may change this to avoid clashes with other keys if
you share the same memcached instance.

#### THUMBNAILS_RESPONSE_BACKEND
*Default:* `'restthumbnails.responses.dummy.sendfile'`

A function responsible to return an appropriate `HttpReponse` after the
thumbnail is generated. The default streams the file directly using Django's
built-in server and is *only* appropriate for development. The other options
are:

- `'restthumbnails.responses.nginx.sendfile'`

- `'restthumbnails.responses.apache.sendfile'`


Client settings
---------------

### THUMBNAILS_PROXY_BASE_URL
*Default:* `'/'`

The base URL for your thumbnail server. By default, we assume it's running on
the same host. It can be relative to the same server (like
`/thumbnails`) or an absolute one (`http://example.com/`)

Thanks
------
The `processors` module is adapted from [`easy-thumbnails`](http://github.com/SmileyChris/easy-thumbnails/) by Chris Beaven,
under the BSD license.
