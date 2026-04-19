import pytest
from unittest.mock import AsyncMock, Mock, patch

from middlewared.plugins.update_.trains import Trains, get_trains, get_next_trains_names
from middlewared.pytest.unit.middleware import Middleware


@pytest.mark.asyncio
@pytest.mark.parametrize("manifest,trains,result", [
    # Redirects current train if it was renamed
    (
        Mock(train="X-NAS-Fangtooth-RC"),
        {"trains": {"X-NAS-SCALE-Fangtooth": {}},
         "trains_redirection": {"X-NAS-Fangtooth-RC": "X-NAS-SCALE-Fangtooth"}},
        Trains.model_validate({
            "trains": {"X-NAS-SCALE-Fangtooth": {}},
            "trains_redirection": {"X-NAS-Fangtooth-RC": "X-NAS-SCALE-Fangtooth"}
        }),
    ),
    # Inserts current train as DEVELOPER profile if it does not exist
    # in the update trains file
    (
        Mock(train="X-NAS-SCALE-Goldeye-Nightlies"),
        {"trains": {"X-NAS-SCALE-Fangtooth": {}},
         "trains_redirection": {}},
        Trains.model_validate({
            "trains": {"X-NAS-SCALE-Fangtooth": {},
                       "X-NAS-SCALE-Goldeye-Nightlies": {}},
            "trains_redirection": {}
        }),
    ),
])
async def test_update_get_trains(manifest, trains, result):
    middleware = Middleware()
    middleware["network.general.will_perform_activity"] = AsyncMock()

    with patch('middlewared.plugins.update_.trains.fetch', new=AsyncMock(return_value=trains)), \
         patch('middlewared.plugins.update_.trains.get_manifest_file', return_value=manifest):
        assert await get_trains(middleware) == result


@pytest.mark.asyncio
@pytest.mark.parametrize("trains,current_train_name,result", [
    # Can be upgraded to tne next immediate train
    (
        Trains.model_validate({"trains": {"X-NAS-SCALE-Cobia": {},
                                          "X-NAS-SCALE-Dragonfish": {},
                                          "X-NAS-SCALE-ElectricEel": {},
                                          "X-NAS-SCALE-Fangtooth": {}}}),
        "X-NAS-SCALE-Dragonfish",
        ["X-NAS-SCALE-ElectricEel", "X-NAS-SCALE-Dragonfish"],
    ),
    # Already on the newest train
    (
        Trains.model_validate({"trains": {"X-NAS-SCALE-Cobia": {},
                                          "X-NAS-SCALE-Dragonfish": {},
                                          "X-NAS-SCALE-ElectricEel": {},
                                          "X-NAS-SCALE-Fangtooth": {}}}),
        "X-NAS-SCALE-Fangtooth",
        ["X-NAS-SCALE-Fangtooth"],
    ),
    # There's an unstable train between the current train and the next stable train
    (
        Trains.model_validate({"trains": {"X-NAS-SCALE-Goldeye": {},
                                          "X-NAS-26-Nightlies": {"stable": False},
                                          "X-NAS-26": {}}}),
        "X-NAS-SCALE-Goldeye",
        ["X-NAS-26", "X-NAS-26-Nightlies", "X-NAS-SCALE-Goldeye"],
    ),
    # Current train is the last stable train
    (
        Trains.model_validate({"trains": {"X-NAS-SCALE-Goldeye": {},
                                          "X-NAS-26-Nightlies": {"stable": False},
                                          "X-NAS-26-BETA": {"stable": False}}}),
        "X-NAS-SCALE-Goldeye",
        ["X-NAS-26-BETA", "X-NAS-26-Nightlies", "X-NAS-SCALE-Goldeye"],
    ),
    # There're two unstable train between the current train and the next stable train
    (
        Trains.model_validate({"trains": {"X-NAS-SCALE-Goldeye": {},
                                          "X-NAS-26-Nightlies": {"stable": False},
                                          "X-NAS-26-BETA": {"stable": False},
                                          "X-NAS-26": {}}}),
        "X-NAS-SCALE-Goldeye",
        ["X-NAS-26", "X-NAS-26-BETA", "X-NAS-26-Nightlies", "X-NAS-SCALE-Goldeye"],
    ),
    # Should stop on the first stable train
    (
        Trains.model_validate({"trains": {"X-NAS-SCALE-Goldeye": {},
                                          "X-NAS-26-Nightlies": {"stable": False},
                                          "X-NAS-26-BETA": {"stable": False},
                                          "X-NAS-26": {},
                                          "X-NAS-27": {}}}),
        "X-NAS-SCALE-Goldeye",
        ["X-NAS-26", "X-NAS-26-BETA", "X-NAS-26-Nightlies", "X-NAS-SCALE-Goldeye"],
    ),
])
async def test_update_get_next_trains_names(trains, current_train_name, result):
    context = Mock()
    context.call2 = AsyncMock(return_value=Mock(profile="DEVELOPER"))

    with patch("middlewared.plugins.update_.trains.get_current_train_name",
               AsyncMock(return_value=current_train_name)):
        assert await get_next_trains_names(context, trains) == result


@pytest.mark.asyncio
@pytest.mark.parametrize("profile,trains", [
    ("DEVELOPER", ["X-NAS-26", "X-NAS-26-BETA", "X-NAS-26-Nightlies", "X-NAS-SCALE-Goldeye"]),
    ("EARLY_ADOPTER", ["X-NAS-26", "X-NAS-26-BETA", "X-NAS-SCALE-Goldeye"]),
    ("GENERAL", ["X-NAS-26", "X-NAS-SCALE-Goldeye"]),
    ("MISSION_CRITICAL", ["X-NAS-SCALE-Goldeye"]),
])
async def test_update_get_next_trains_names_skips_trains(profile, trains):
    context = Mock()
    context.call2 = AsyncMock(return_value=Mock(profile=profile))

    with patch("middlewared.plugins.update_.trains.get_current_train_name",
               AsyncMock(return_value="X-NAS-SCALE-Goldeye")):
        assert await get_next_trains_names(context, Trains.model_validate({
            "trains": {
                "X-NAS-SCALE-Goldeye": {},
                "X-NAS-26-Nightlies": {"max_profile": "DEVELOPER", "stable": False},
                "X-NAS-26-BETA": {"max_profile": "EARLY_ADOPTER", "stable": False},
                "X-NAS-26": {"max_profile": "GENERAL"},
            }
        })) == trains
