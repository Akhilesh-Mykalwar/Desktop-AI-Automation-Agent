class Skill:
    name = "base"

    def can_handle(self, intent: dict) -> bool:
        raise NotImplementedError

    def build_plan(self, intent: dict) -> list:
        """
        Return a LIST of action dicts.
        Each action must be executable by controller.
        """
        raise NotImplementedError
