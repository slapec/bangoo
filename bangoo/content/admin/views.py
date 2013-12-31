from .forms import EditContentForm
from bangoo.content.models import Content
from bangoo.decorators import class_view_decorator
from django.contrib.auth.decorators import permission_required
from ajaxtables.views import AjaxListView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse


@class_view_decorator(permission_required('content.list_content'))
class ContentList(AjaxListView):
    model = Content
    template_names = ['content/admin/list.html', 'content/admin/list_data.html']

    def get_queryset(self):
        return self.model.objects.language('hu').all().order_by('-created')

@permission_required('content.add_content')
def edit_content(request, content_id, template_name='content/admin/edit_content.html'):
    try:
        content = Content.objects.get(pk=content_id)
    except Content.DoesNotExist:
        content = Content(is_page=True)
    form = EditContentForm(request.POST or None, instance=content, initial={'authors': [request.user]})
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('admin-content-list'))
    return render(request, template_name, {'form': form})