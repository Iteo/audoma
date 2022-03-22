import json

from django.conf import settings as django_settings

from audoma import settings as audoma_settings


class CustomExceptionDescCreator:
    """
    Responsible for generating common errors section in documenation.
    This section, should be added to the API description in docs.
    """

    def __init__(self):
        self.common_exceptions = audoma_settings.COMMON_API_ERRORS + getattr(
            django_settings, "COMMON_API_ERRORS", []
        )

    def get_description(self):
        desc = "###  Common API Errors \n"
        for error in self.common_exceptions:
            desc += self.__generate_exception_desc(error)
        return desc

    def __generate_exception_desc(self, error):
        exc_desc = ""
        exc_desc = f"Status Code: `{error.status_code}` \n\n"

        custom_properties_function = getattr(error, "get_custom_properties", None)
        if custom_properties_function:
            properties = custom_properties_function()
        else:
            properties = {"detail": error.detail}

        error_data = json.dumps(
            {"errors": properties}, indent=4, separators=(",", ": ")
        )

        exc_desc += f"``` \n {error_data} \n ``` \n\n"
        return exc_desc
