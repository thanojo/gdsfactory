import warnings

import numpy as np

import pp
from pp.component import Component
from pp.tech import FACTORY, Factory
from pp.types import StrOrDict, StrOrDictOrNone


@pp.cell_with_validator
def delay_snake3(
    length: float = 1600.0,
    length0: float = 0.0,
    n: int = 2,
    bend180: StrOrDictOrNone = None,
    waveguide: StrOrDict = "strip",
    factory: Factory = FACTORY,
    **waveguide_settings,
) -> Component:
    r"""Snake input facing west
    Snake output facing east

    Args:
        length:
        length0: initial offset
        n: number of loops
        bend180
        waveguide
        factory
        waveguide_settings

    .. code::

                 | length0   |

                 >---------\
                            \bend180.length
                            /
       |-------------------/
       |
       |------------------->

       |   delta_length    |


    """
    if n % 2:
        warnings.warn(f"rounding {n} to {n//2 *2}", stacklevel=3)
        n = n // 2 * 2
    bend180 = bend180 or dict(
        component="bend_euler", angle=180, waveguide=waveguide, **waveguide_settings
    )
    bend180 = factory.get_component(bend180, waveguide=waveguide, **waveguide_settings)

    delta_length = (length - length0 - n * (bend180.length)) / (n + 1)
    assert (
        delta_length > 0
    ), "Snake is too short: either reduce length0, increase the total length,\
    or decrease n"

    s0 = pp.c.straight(waveguide=waveguide, length=length0, **waveguide_settings)
    sd = pp.c.straight(waveguide=waveguide, length=delta_length, **waveguide_settings)

    symbol_to_component = {
        "_": (s0, "W0", "E0"),
        "-": (sd, "W0", "E0"),
        ")": (bend180, "W1", "W0"),
        "(": (bend180, "W0", "W1"),
    }

    sequence = "_)" + n // 2 * "-(-)"
    sequence = sequence[:-1]
    c = pp.components.component_sequence(
        sequence=sequence, symbol_to_component=symbol_to_component
    )
    pp.port.auto_rename_ports(c)
    return c


def test_delay_snake3_length() -> Component:
    length = 200.0
    c = delay_snake3(
        waveguide="strip",
        n=2,
        length=length,
        bend180=dict(component="bend_circular180"),
    )
    length_measured = (
        c.aliases[")1"].parent.length * 2 + c.aliases["-1"].parent.length * 3
    )
    assert np.isclose(
        length, length_measured
    ), f"length measured = {length_measured} != {length}"
    return c


if __name__ == "__main__":
    c = test_delay_snake3_length()
    c.show()
    # c = delay_snake3(waveguide="nitride", n=2, length=200)
    # c.show()
