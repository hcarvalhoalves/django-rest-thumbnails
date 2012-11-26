from django import http

def sendfile(request, location, **kwargs):
    response = http.HttpResponse()
    response['X-Sendfile'] = location
    del response['Content-Type'] # Let the proxy figure this out
    return response
