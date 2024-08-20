import json
import urllib.parse

from apps.core.exceptions import LogicException
from apps.job_applying.enums import JobSearchPlatforms
from apps.setup.models import JobSearchFilter
from apps.user.models import User, UserJobSearchFilter


class BaseJobSearchBuilder:
    def __init__(self, user: User):
        self.user = user

    def build_search_url(self):
        raise NotImplementedError()


class LinkedinSearchBuilder(BaseJobSearchBuilder):
    base_url = "https://www.linkedin.com/jobs/search/?"

    def build_search_url(self):
        filters = self.__user_filters()

        params = {}

        for f in filters:
            if f.value or f.values:
                params[f.job_search_filter.query_param] = f.value if f.value else json.dumps(f.values)

        # add default filters with value=True
        params.update(self.__default_filters())

        return self.base_url + urllib.parse.urlencode(params)

    def __user_filters(self):
        return UserJobSearchFilter.objects.filter(
            user=self.user,
            job_search_filter__can_be_added_in_search_url=True
        )

    @staticmethod
    def __default_filters() -> dict:
        """
            Retrieve default job search filters that are marked as non-fillable.
            Returns:
                dict: A dictionary containing default filter query parameters as keys,
                      with corresponding values set to True.
        """
        return {
            f.query_param: True
            for f in JobSearchFilter.objects.filter(fillable=False, platform=JobSearchPlatforms.LINKEDIN.value)
        }


def job_search_builder_factory(platform: JobSearchPlatforms, user: User) -> BaseJobSearchBuilder:
    if platform == JobSearchPlatforms.LINKEDIN.value:
        return LinkedinSearchBuilder(user)

    raise LogicException("Unknown job search platform")