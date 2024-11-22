import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.plan_stubs.data_session import attach_data_session_metadata_decorator
from ophyd_async.core import (
    StandardDetector,
    StandardFlyer,
)
from ophyd_async.epics.motor import Motor
from ophyd_async.fastcs.panda import (
    HDFPanda,
    StaticSeqTableTriggerLogic,
)
from ophyd_async.plan_stubs import fly_and_collect
from ophyd_async.plan_stubs._fly import (
    prepare_static_seq_table_flyer_and_detectors_with_same_trigger,
)


@attach_data_session_metadata_decorator
def plan(panda: HDFPanda, diff: StandardDetector) -> MsgGenerator:
    trigger_logic = StaticSeqTableTriggerLogic(panda.seq[1])

    flyer = StandardFlyer(
        trigger_logic,
        name="flyer",
    )

    @bpp.stage_decorator(devices=[diff, panda, flyer])
    @bpp.run_decorator()
    def inner():
        yield from prepare_static_seq_table_flyer_and_detectors_with_same_trigger(
            flyer, [diff], number_of_frames=15, exposure=0.1, shutter_time=0.05
        )
        yield from fly_and_collect(
            stream_name="primary",
            flyer=flyer,
            detectors=[diff],
        )

    yield from inner()


@attach_data_session_metadata_decorator
def plan_step_scan(detectors: set[StandardDetector], motor: Motor) -> MsgGenerator:
    @bpp.stage_decorator(devices=[*detectors, motor])
    @bpp.run_decorator()
    def inner():
        for i in range(10):
            yield from bps.mv((motor, i))
            yield from bps.trigger_and_read((*detectors, motor))

    yield from inner()
