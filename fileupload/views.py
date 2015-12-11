from django.views.generic import CreateView, DeleteView
from django.views.generic.base import View

import simplejson
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.conf import settings

from fileupload.models import Picture

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

class PictureCreateView(CreateView):
    model = Picture

    def form_valid(self, form):
        self.object = form.save()
        f = self.request.FILES.get('file')
        data = [{'name': f.name, 'url': settings.MEDIA_URL + "pictures/" + f.name.replace(" ", "_"),
                 'thumbnail_url': settings.MEDIA_URL + "pictures/" + f.name.replace(" ", "_"),
                 'delete_url': reverse('upload-delete', args=[self.object.id]), 'delete_type': "DELETE"}]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class MultiUploderView(View):
    model = Picture

    def post(self, request, *args, **kwargs):
        if request.FILES == None:
            raise Http404("No objects uploaded")
        file = request.FILES['file']

        url = self.save_form(request, file, *args, **kwargs)

        result = [{'name': file.name,
                   'size': file.size,
                   'url': url,
                   'thumbnail_url': url,
                   }, ]

        response_data = simplejson.dumps(result)
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)

    def save_form(self, request, file, *args, **kwargs):
        a = self.model()
        a.creator = request.user
        a.file.save(file.name, file)
        a.save()
        return a.file.url

    def get(self, request, *args, **kwargs):
        """
        required to satisfy jquery upload get request
        """
        return HttpResponse('Only POST accepted')

#    def get(self, request, *args, **kwargs):
#        """
#        required to satisfy jquery upload get request for existing images
#        """
#        try:
#            recipe = Recipe.objects.get(id=self.kwargs['recipe_id'])
#        except Recipe.DoesNotExist:
#            raise Http404("Recipe does not exist, thus can't get images")
#
#        #        import ipdb; ipdb.set_trace()
#        images = recipe.images.all()
#
#        #generating json response array
#        result = []
#
#        for image in images:
#            result.append({"name":image.description,
#                           "size":image.file.size,
#                           "url":image.file.url,
#                           "thumbnail_url":image.file.url,})
#
#        response_data = simplejson.dumps(result)
#
#        #checking for json data type
#        #big thanks to Guy Shapiro
#        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
#            mimetype = 'application/json'
#        else:
#            mimetype = 'text/plain'
#        return HttpResponse(response_data, mimetype=mimetype)


class PictureDeleteView(DeleteView):
    model = Picture

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect('/upload/new')

class JSONResponse(HttpResponse):
    """JSON response class."""

    def __init__(self, obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)
