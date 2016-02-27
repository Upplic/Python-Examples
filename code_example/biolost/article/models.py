# coding: utf-8
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
import sirtrevor
from sirtrevor.fields import SirTrevorField
from ordered_model.models import OrderedModel

from tools.fields import CustomImageField
from tools.models import TimeStampModel, PublishedModel, upload_to
from .blocks import ExtendedQuotes

sirtrevor.register_block(ExtendedQuotes)


class AbstractArticle(TimeStampModel, PublishedModel):
    """ Абстрактная модель для Статей и Ликбеза.
    """
    title = models.CharField(max_length=128, verbose_name=u'Заголовок')
    anons = SirTrevorField(verbose_name=u'Анонс (лид)')
    content = SirTrevorField(verbose_name=u'Тело статьи')
    image = CustomImageField(allowed=('jpeg', 'jpg', 'png'),
                             upload_to=upload_to,
                             verbose_name=u'Изображение')

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.title)


class Educational(AbstractArticle, OrderedModel):
    """ Ликбез.
    """
    class Meta(OrderedModel.Meta):
        verbose_name = u'Ликбез'
        verbose_name_plural = u'Ликбез'

    def get_absolute_url(self):
        return reverse('articles:educational_detail', args=(self.pk,))

    @cached_property
    def next_article(self):
        """ Следующая, по порядку статья ликбеза.
        """
        return self.__class__.published.filter(order__gt=self.order).first()


class Tag(models.Model):
    """ Тэги.
    """
    name = models.CharField(max_length=128, unique=True, verbose_name=u'Тэг')

    class Meta:
        verbose_name = u'Тэг'
        verbose_name_plural = u'Тэги'

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('articles:list_by_tag', args=(self.pk,))


class Article(AbstractArticle):
    """ Статьи.
    """
    tags = models.ManyToManyField(to=Tag, verbose_name=u'Тэги')

    class Meta:
        verbose_name = u'Статью'
        verbose_name_plural = u'Статьи'
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse('articles:detail', args=(self.pk,))

    @cached_property
    def next_article(self):
        """ Следующая статья.
        """
        return self.__class__.published.exclude(pk=self.pk).filter(
            created__lte=self.created).first()


class Quote(models.Model):
    """ Цитаты.
    """
    name = models.CharField(max_length=128,
                            verbose_name=u'Имя респондента')
    feature = models.CharField(max_length=256,
                               verbose_name=u'Характеристика респондента')
    anons = SirTrevorField(verbose_name=u'Анонс (лид)')
    content = SirTrevorField(verbose_name=u'Цитата')
    url = models.URLField(verbose_name=u'Видео или аудио ссылка')
    photo = CustomImageField(allowed=('jpeg', 'jpg', 'png'),
                             upload_to=upload_to,
                             verbose_name=u'Фото респондента')
    image = CustomImageField(allowed=('jpeg', 'jpg', 'png'),
                             upload_to=upload_to,
                             verbose_name=u'Изображение заглушка')

    class Meta:
        verbose_name = u'Цитату'
        verbose_name_plural = u'Цитаты'

    def __unicode__(self):
        return unicode(self.name)
