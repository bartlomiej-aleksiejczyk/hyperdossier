# infobjects/breadcrumbs.py
from django.urls import reverse, NoReverseMatch


# These will be prepended to every breadcrumb trail
BASE_CRUMBS = [
    {"label": "Home", "url_name": "home"},  # change 'home' to your real view name
    {
        "label": "Infobjects",
        "url_name": "infobjects:category_list",  # e.g. main page of this app
    },
]


# Per-view \u201ctail\u201d definitions
# You can extend this gradually.
VIEW_CRUMBS = {
    "infobjects:category_list": [
        {"label": "Categories", "url_name": None},  # current page
    ],
    "infobjects:category_edit": [
        {"label": "Categories", "url_name": "infobjects:category_list"},
        {
            # last node: EDIT <id>
            "label": lambda kwargs: f"Edit {kwargs.get('category_pk')}",
            "url_name": None,
        },
    ],
    # add note_list, note_edit, etc. here later
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

    # BASE + specific trail for this view
    config = BASE_CRUMBS + VIEW_CRUMBS.get(view_name, [])

    for item in config:
        label = item["label"]
        if callable(label):
            label = label(view_kwargs)  # e.g. lambda kwargs: f"EDIT {kwargs['category_pk']}"

        url_name = item.get("url_name")
        kwarg_keys = item.get("kwarg_keys")  # optional per-crumb

        url = _build_url(url_name, view_kwargs, kwarg_keys)

        crumbs.append({"label": label, "url": url})

    return {"breadcrumbs": crumbs}
