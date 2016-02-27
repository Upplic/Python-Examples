# coding: utf-8
from django.http import Http404
from django.conf import settings
from django.views import generic
from django.utils.functional import cached_property

from tools.views import ListView, DetailView
from article.models import Article, Educational, Tag


class ArticleList(ListView):
    """ Список статей раздела `Журнал`
    """
    model = Article
    template_name = 'article/list.html'
    template_name_ajax = 'article/list_base.html'


class ArticleListByTag(ArticleList):
    """ Список статей по тэгу.
    """
    def get(self, request, tag_pk, *args, **kwargs):
        self.tag = self.get_tag(tag_pk)
        return super(ArticleListByTag, self).get(request, *args, **kwargs)

    def get_tag(self, tag_pk):
        try:
            return Tag.objects.get(pk=tag_pk)
        except Tag.DoesNotExist:
            raise Http404

    def get_queryset(self):
        return (super(ArticleListByTag, self).get_queryset()
                .filter(tags=self.tag))

    def get_context_data(self, *args, **kwargs):
        context = super(ArticleListByTag, self).get_context_data(*args,
                                                                 **kwargs)
        context['tag'] = self.tag
        return context


class ArticleDetail(DetailView):
    model = Article
    template_name = 'article/detail.html'


class EducationalRedirectView(generic.RedirectView):
    """ Точка входа в раздел "Ликбез". В случае наличия контента - редиректит
    на первую статью.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            first = Educational.published.all()[0]
        except IndexError:
            raise Http404

        return first.get_absolute_url()


class EducationalDetail(DetailView):
    """ Отображение отдельной статьи из раздела "Ликбез".
    """
    model = Educational
    template_name = 'educational/detail.html'
