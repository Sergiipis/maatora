from jinja2 import Environment, Undefined, select_autoescape


class _NAFallback(Undefined):
    def __str__(self) -> str:
        return "N/A"

    def __html__(self) -> str:
        return "N/A"


def render(receipt: dict, template: str | None = None) -> str:
    if template is None:
        template = (
            "<p>Agent {{ actor_id }} performed {{ action }} "
            "at {{ timestamp }} (cost: ${{ cost_usd }}).</p>"
        )

    env = Environment(
        autoescape=select_autoescape(["html", "xml"]),
        undefined=_NAFallback,
    )
    return env.from_string(template).render(**receipt)
