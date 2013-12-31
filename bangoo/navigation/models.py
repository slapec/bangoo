from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from jsonfield import JSONField
from bangoo.navigation.debug import WrongMenuFormatException
from django.conf import settings
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey
from noconflict import classmaker

class MenuManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super(MenuManager, self).get_queryset(*args, **kwargs)

    def add_menu(self, titles, urlconf, **defaults):
        default_locale = settings.LANGUAGE_CODE.split('-')[0]
        try:
            assert default_locale in titles.keys()
        except AssertionError:
            raise WrongMenuFormatException('Titles keys must contain default locale (%s)' % default_locale)
        try:
            assert urlconf in settings.INSTALLED_APPS
        except AssertionError:
            raise WrongMenuFormatException('urlconf parameter must be in INSTALLED_APPS')
        menu = Menu.objects.create(urlconf=urlconf, **defaults)
        for lang, title in titles.items():
            menu.translate(lang)
            menu.title = title
            menu.path = '/%s/' % slugify(title)
            if 'parent' in defaults.keys():
                menu.path = defaults['parent'].path + menu.path[1:]
            menu.save()
        return menu


class Menu(TranslatableModel, MPTTModel):
    """
    login_required: Is this menu public accessable
    parent: The parent menu
    urlconf: Which apps urlconf to use?
    weight: The weight of the menu item. Items in the same level are ordered by weight
    """
    __metaclass__ = classmaker()
    login_required = models.BooleanField(default=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    urlconf = models.CharField(max_length=100)
    weight = models.SmallIntegerField(default=0)
    parameters = JSONField(blank=True, null=True)
    translations = TranslatedFields(
        path = models.CharField(max_length=255),
        title = models.CharField(max_length=100),
        meta = {'unique_together': [('path', 'language_code')]},
    )
    handler = MenuManager()