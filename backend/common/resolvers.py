from common.utils import to_snake_case


def multi_image_resolver(obj, info, **kwargs):
    request = info.context
    attr_name = to_snake_case(info.field_name)
    origin_attr = obj.__class__.image_map[attr_name].source
    origin = getattr(obj, origin_attr)
    default = getattr(obj, f"{attr_name}_default")
    if not origin:
        return None
    if request.user_agent.browser.family in [
        "Safari",
        "Mobile Safari",
        "Chrome Mobile iOS",
    ]:
        optimized = getattr(obj, f"{attr_name}_default")
    elif request.user_agent.browser.family in ["Internet Explorer"]:
        optimized = getattr(obj, f"{attr_name}_default")
    elif "Chrome" in request.user_agent.browser.family:
        optimized = getattr(obj, f"{attr_name}_webp")
    else:
        optimized = getattr(obj, f"{attr_name}_default")
    file = optimized or default or origin
    return file.url
