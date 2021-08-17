import gdsfactory as gf
from gdsfactory.component import Component

LENGTH = 0.5
CELL_NAME = "straight_L500n"


def test_label_fiber_single(length=LENGTH, cell_name=CELL_NAME) -> Component:
    """Test that add_fiber single adds the correct label for measurements."""
    c = gf.components.straight(length=length)

    assert len(c.labels) == 0
    cte = gf.routing.add_fiber_single(component=c, with_loopback=False)

    assert len(cte.labels) == 2
    l0 = cte.labels[0].text
    l1 = cte.labels[1].text

    assert l0 == f"opt_te_1530_({cell_name})_0_1", l0
    assert l1 == f"opt_te_1530_({cell_name})_0_2", l1

    return cte


def test_label_fiber_single_loopback(length=LENGTH, cell_name=CELL_NAME) -> Component:
    """Test that add_fiber single adds the correct label for measurements."""
    c = gf.components.straight(length=length)

    assert len(c.labels) == 0, len(c.labels)

    cte = gf.routing.add_fiber_single(component=c, with_loopback=True)
    assert len(cte.labels) == 4, len(cte.labels)

    l0 = cte.labels[0].text
    l1 = cte.labels[1].text
    l2 = cte.labels[2].text
    l3 = cte.labels[3].text

    assert l0 == f"opt_te_1530_({cell_name})_0_1", l0
    assert l1 == f"opt_te_1530_({cell_name})_0_2", l1
    assert l2 == f"opt_te_1530_(loopback_{cell_name})_0_2", l2
    assert l3 == f"opt_te_1530_(loopback_{cell_name})_1_1", l3

    return cte


if __name__ == "__main__":
    c = test_label_fiber_single()
    # c = test_label_fiber_single_loopback()
    c.show()
