from typing import Callable, List, Optional, Tuple, Union

from phidl.device_layout import Label

import gdsfactory as gf
from gdsfactory.component import Component, ComponentReference
from gdsfactory.components.grating_coupler.elliptical_trenches import grating_coupler_te
from gdsfactory.cross_section import strip
from gdsfactory.port import select_optical_ports
from gdsfactory.routing.route_fiber_array import route_fiber_array
from gdsfactory.types import CrossSectionFactory, PortName


def route_fiber_single(
    component: Component,
    fiber_spacing: float = 50.0,
    grating_coupler: Callable = grating_coupler_te,
    min_input_to_output_spacing: float = 200.0,
    optical_routing_type: int = 1,
    optical_port_labels: Optional[Tuple[PortName, ...]] = None,
    excluded_ports: Optional[Tuple[PortName, ...]] = None,
    auto_widen: bool = False,
    component_name: Optional[str] = None,
    select_ports: Callable = select_optical_ports,
    cross_section: CrossSectionFactory = strip,
    **kwargs,
) -> Tuple[List[Union[ComponentReference, Label]], List[ComponentReference]]:
    """Returns route Tuple(references, grating couplers) for single fiber input/output.

    Args:
        component: to add grating couplers
        fiber_spacing: between grating couplers
        grating_coupler:
        min_input_to_output_spacing: so opposite fibers do not touch
        optical_routing_type: 0 (basic), 1 (standard), 2 (looks at ports)
        optical_port_labels: port labels that need connection
        excluded_ports: ports excluded from routing
        auto_widen: for long routes
        cross_section:
        **kwargs: cross_section settings

    Returns:
        elements: list of routes ComponentReference
        grating_couplers: list of grating_couplers ComponentReferences

    """
    if not select_ports(component.ports):
        raise ValueError(f"No ports for {component.name}")

    component = component.copy()
    component_copy = component.copy()

    if optical_port_labels is None:
        optical_ports = select_ports(component.ports)
    else:
        optical_ports = [component.ports[lbl] for lbl in optical_port_labels]

    excluded_ports = excluded_ports or []
    optical_ports = {
        p.name: p for p in optical_ports.values() if p.name not in excluded_ports
    }
    N = len(optical_ports)

    if isinstance(grating_coupler, list):
        grating_couplers = [gf.call_if_func(g) for g in grating_coupler]
        grating_coupler = grating_couplers[0]
    else:
        grating_coupler = gf.call_if_func(grating_coupler)
        grating_couplers = [grating_coupler] * N

    gc_port2center = getattr(grating_coupler, "port2center", grating_coupler.xsize / 2)
    if component.xsize + 2 * gc_port2center < min_input_to_output_spacing:
        fanout_length = (
            gf.snap.snap_to_grid(
                min_input_to_output_spacing - component.xsize - 2 * gc_port2center, 10
            )
            / 2
        )
    else:
        fanout_length = None

    """
         _________
        |         |_E1
     W0_|         |
        |         |_E0
        |_________|

    rotate +90 deg and route West ports to South

          E1  E0
         _|___|_
        |       |
        |       |
        |       |
        |       |
        |       |
        |       |
        |_______|
            |
            W0

    """
    # route west ports to south
    component = component.rotate(90)
    south_ports = component.get_ports_dict(orientation=270)
    south_ports = select_ports(south_ports)
    component.ports = south_ports

    elements_south, gratings_south, _ = route_fiber_array(
        component=component,
        with_loopback=False,
        fiber_spacing=fiber_spacing,
        fanout_length=fanout_length,
        grating_coupler=grating_couplers[0],
        optical_routing_type=optical_routing_type,
        auto_widen=auto_widen,
        component_name=component_name,
        cross_section=cross_section,
        select_ports=select_ports,
        **kwargs,
    )

    # route the rest of the ports_south
    component = component_copy.rotate(-90)
    ports_already_routed = component.get_ports_dict(orientation=90)
    for port_already_routed in ports_already_routed.keys():
        component.ports.pop(port_already_routed)

    component.ports = select_ports(component.ports)

    elements_north, gratings_north, _ = route_fiber_array(
        component=component,
        with_loopback=False,
        fiber_spacing=fiber_spacing,
        fanout_length=fanout_length,
        grating_coupler=grating_couplers[1:],
        optical_routing_type=optical_routing_type,
        auto_widen=auto_widen,
        component_name=component_name,
        cross_section=cross_section,
        select_ports=select_ports,
        **kwargs,
    )
    for e in elements_north:
        if isinstance(e, list):
            for ei in e:
                elements_south.append(ei.rotate(180))
        else:
            elements_south.append(e.rotate(180))

    if len(gratings_north) > 0:
        for io in gratings_north[0]:
            gratings_south.append(io.rotate(180))

    return elements_south, gratings_south


if __name__ == "__main__":
    gcte = gf.components.grating_coupler_te
    gctm = gf.components.grating_coupler_tm

    c = gf.components.cross(length=500)
    c = gf.components.ring_double()
    c = gf.components.mmi2x2()
    c = gf.components.crossing()
    c = gf.components.rectangle()
    c = gf.components.ring_single()

    # elements, gc = route_fiber_single(
    #     c, grating_coupler=[gcte, gctm, gcte, gctm], auto_widen=False
    # )

    layer = (2, 0)
    c = gf.components.mmi2x2()
    c = gf.components.straight(width=2, length=500)
    gc = gf.components.grating_coupler_elliptical_te(layer=layer)
    elements, gc = route_fiber_single(
        c,
        grating_coupler=[gc, gc, gc, gc],
        auto_widen=False,
        radius=10,
        layer=layer,
    )

    cc = gf.Component("sample_route_fiber_single")
    cr = cc << c.rotate(90)

    for e in elements:
        cc.add(e)
    for e in gc:
        cc.add(e)
    cc.show()

    # layer = (31, 0)
    # c = gf.components.mmi2x2()
    # c = gf.components.straight(width=2, length=500)
    # gc = gf.components.grating_coupler_elliptical_te(layer=layer)
    # elements, gc = route_fiber_single(
    #     c,
    #     grating_coupler=[gc, gc, gc, gc],
    #     auto_widen=False,
    #     radius=10,
    #     layer=layer,
    # )

    # cc = gf.Component("sample_route_fiber_single")
    # cr = cc << c.rotate(90)

    # for e in elements:
    #     cc.add(e)
    # for e in gc:
    #     cc.add(e)
    # cc.show()
