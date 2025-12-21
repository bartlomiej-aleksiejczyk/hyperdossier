from django.urls import reverse, NoReverseMatch


BASE_CRUMBS = [
    {"label": "Home", "url_name": "home"},
    {
        "label": "Infobjects",
        "url_name": "infobjects:category_list",
    },
]


VIEW_CRUMBS = {
    "infobjects:category_list": [
        {"label": "Categories", "url_name": "infobjects:category_list"},
    ],
    "infobjects:category_edit": [
        {"label": "Categories", "url_name": "infobjects:category_edit"},
        {
            "label": lambda kwargs: f"Edit {kwargs.get('category_pk')}",
            "url_name": "",
        },
    ],
    "infobjects:note_list": [
        {"label": "Notes", "url_name": "infobjects:category_list"},
    ],
}


def _build_url(url_name, view_kwargs, kwarg_keys=None):
    if not url_name:
        return None

    kwarg_keys = kwarg_keys or []
    kw = {k: view_kwargs[k] for k in kwarg_keys if k in view_kwargs}

    try:
        return reverse(url_name, kwargs=kw or None)
    except NoReverseMatch:
        try:
            return reverse(url_name)
        except NoReverseMatch:
            return None


def get_breadcrumbs_context(view_name: str, view_kwargs=None) -> dict:
    """
    view_name: e.g. 'infobjects:category_edit'
    view_kwargs: dict like {'category_pk': 1}
    """
    if view_kwargs is None:
        view_kwargs = {}

    crumbs = []

    config = BASE_CRUMBS + VIEW_CRUMBS.get(view_name, [])

    for item in config:
        label = item["label"]
        if callable(label):
            label = label(view_kwargs)

        url_name = item.get("url_name")
        kwarg_keys = item.get("kwarg_keys")

        url = _build_url(url_name, view_kwargs, kwarg_keys)

        crumbs.append({"label": label, "url": url})

    return {"breadcrumbs": crumbs}
