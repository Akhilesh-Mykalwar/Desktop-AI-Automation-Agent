from reflex.scroll_reflex import handle_scroll
from reflex.youtube_click_reflex import handle_youtube_click
from reflex.double_click_reflex import handle_double_click
from reflex.universal_click_reflex import handle_universal_click
from reflex.OS_control_reflex import handle_os_controls
from reflex.type_reflex import handle_type


REFLEX_HANDLERS = [
    handle_type,
    handle_os_controls,
    handle_scroll,
    handle_youtube_click,
    handle_double_click,
    handle_universal_click,
    
]

def check_reflex(goal: str):

    goal_l = goal.lower().strip()

    for handler in REFLEX_HANDLERS:
        result = handler(goal_l)
        if result:
            return result

    return None