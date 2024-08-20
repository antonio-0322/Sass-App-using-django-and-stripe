from django.urls import path
from django.conf import settings


def api_url(regex, view, name=None):
    """
    This function only adds Api version to each regex (url).
    Returns base django url function with a new generated regex.
    :param regex: str
    :param view: view object
    :param name: str name of url (optional)
    :return: django.urls.path object
    """

    regex = r'%s%s' % (settings.API_VERSION_URL, regex)
    return path(regex, view, name=name)
