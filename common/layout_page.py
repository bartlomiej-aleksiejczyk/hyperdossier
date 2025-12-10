from iommi import Page
from iommi.action import EMPTY
from iommi.admin import dispatch
from iommi.part import get_title
from iommi.style import get_style_object
from iommi._web_compat import get_template_from_string


class LayoutPage(Page):
    style=None
    @dispatch(
        render=EMPTY,
        context=EMPTY,
    )
    def render_root(*, part, context, **render):
        assert part._is_bound
        print('apud')
        if part.style:
            root_style = part.style
        else:
            root_style = get_style_object(part)
        template_name = root_style.base_template
        content_block_name = root_style.content_block

        # Render early so that all the binds are forced before we look at all_assets,
        # since they are populated as a side-effect
        content = part.__html__(**render)

        assets = part.iommi_collected_assets()

        assert template_name, f"{root_style} doesn't have a base_template defined"
        assert content_block_name, f"{root_style} doesn't have a content_block defined"

        title = get_title(part)

        from iommi import Page
        from iommi.debug import iommi_debug_panel
        from iommi.fragment import Container

        request = part.get_request()

        context = dict(
            container=Container(_name='Container').refine_done(parent=part).bind(parent=part),
            content=content,
            title=title if title not in (None, MISSING) else '',
            iommi_debug_panel=(
                iommi_debug_panel(part) if iommi_debug_panel_on() and '_iommi_disable_debug_panel' not in request.GET else ''
            ),
            iommi_language_code=getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE),
            assets=assets,
            request=request,
            **(part.context if isinstance(part, Page) else {}),
            **context,
        )

        template_string = (
            '{% extends "'
            + template_name
            + '" %} {% block '
            + content_block_name
            + ' %}{{ iommi_debug_panel }}{{ content }}{% endblock %}'
        )
        return get_template_from_string(template_string).render(context=context, request=request)