import re

from audoma.links import AudomaLink


# consider adding status code
def register_audoma_field_link(
    viewname: str,
    view_args: tuple = None,
    view_kwargs: dict = None,
    description: str = "",
    parameters: dict = None,
    status_code: int = None,
    method: str = "get",
    link_name: str = "",
):
    view_args = view_args or ()
    view_kwargs = view_kwargs or {}
    parameters = parameters or {}

    if not link_name:
        partials = re.split(r"_|-", viewname)
        partials = [partial.capitalize() for partial in partials]
        link_name = "".join(partials)

    def decorator(func):
        link = AudomaLink(
            viewname=viewname,
            view_args=view_args,
            view_kwargs=view_kwargs,
            description=description,
            parameters=parameters,
            status_code=status_code,
            method=method,
            link_name=link_name,
        )
        _audoma_choices_links = getattr(func, "_audoma_choices_links", [])
        _audoma_choices_links.append(link)
        func._audoma_choices_links = _audoma_choices_links
        return func

    return decorator
