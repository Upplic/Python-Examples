# coding: utf-8
from django.views import generic
from django.conf import settings


class PublishedViewMixin(object):
    """ Миксин, использующуй по-умолчанию менеджер `published`
    """
    def get_queryset(self):
        return self.model.published.all()


class AjaxTemplateMixin(object):
    """ Миксин, использующуй специально определенный шаблон в случае
    ajax запроса.
    """
    template_name_ajax = None

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.template_name_ajax]
        return [self.template_name]


class ListView(PublishedViewMixin, AjaxTemplateMixin, generic.ListView):
    """ Накаченная миксинами версия дефолтного ListView
    """
    paginate_by = settings.PAGINATE_BY


class DetailView(PublishedViewMixin, generic.DetailView):
    """ Накаченная миксинами версия дефолтного DetailView
    """
