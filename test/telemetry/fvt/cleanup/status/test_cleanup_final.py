# Copyright 2026 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Telemetry Cleanup — Final State Verification Tests.

Verifies that no pods remain and that PVC state matches the
``Delete_volume`` flag after a full cleanup.

When ``Delete_volume=true``  (``--delete-volume true``), PVCs must be
deleted — ``test_no_pvcs_after_full_cleanup`` runs.
When ``Delete_volume=false`` (default), PVCs must be preserved —
``test_pvcs_preserved_after_cleanup`` runs instead.

Test cases:
    TC_CL_011: Verify no pods remain after full cleanup
    TC_CL_012: Verify no PVCs remain after full cleanup (Delete_volume=true)
    TC_CL_013: Verify PVCs preserved after cleanup (Delete_volume=false)
"""

import pytest

from omnia_auto import TestLogger

from library.vars.test_case_vars import TEST_CASES as TC
from library.messages.telemetry_msgs import (
    TEST_LOG_MSGS as LOG_MSGS,
    TEST_ASSERT_MSGS as ASSERT_MSGS,
)
from library.functions.cleanup_func import (
    verify_no_pods_remaining,
    verify_no_pvcs_remaining,
    verify_pvcs_preserved,
)


@pytest.mark.sanity
@pytest.mark.order(61)
def test_no_pods_after_full_cleanup(host):
    """TC_CL_011: Verify no pods remain in telemetry namespace.

    After a full cleanup (--tags cleanup), the telemetry namespace
    should contain zero pods regardless of the Delete_volume flag.
    """
    tc = TC["no_pods_after_full_cleanup"]
    tl = TestLogger(tc["title"], tc["id"])

    result = verify_no_pods_remaining(host)

    if result["success"]:
        tl.passed(LOG_MSGS["no_pods_remaining"], result["details"])
    else:
        tl.failed(
            LOG_MSGS["pods_remaining"].format(count=result["count"]),
            result["details"],
        )

    assert result["success"], ASSERT_MSGS["pods_remaining"].format(
        count=result["count"],
    )


@pytest.mark.sanity
@pytest.mark.order(62)
def test_no_pvcs_after_full_cleanup(host, delete_volume):
    """TC_CL_012: Verify no PVCs remain (Delete_volume=true only).

    After a full cleanup with ``Delete_volume=true``, the telemetry
    namespace should contain zero PersistentVolumeClaims.

    Skipped when ``Delete_volume=false`` (default) because PVCs are
    intentionally preserved in that mode.
    """
    if not delete_volume:
        pytest.skip(
            "Delete_volume=false — PVCs are preserved; "
            "skipping PVC deletion check"
        )

    tc = TC["no_pvcs_after_full_cleanup"]
    tl = TestLogger(tc["title"], tc["id"])

    result = verify_no_pvcs_remaining(host)

    if result["success"]:
        tl.passed(LOG_MSGS["no_pvcs_remaining"], result["details"])
    else:
        tl.failed(
            LOG_MSGS["pvcs_remaining"].format(count=result["count"]),
            result["details"],
        )

    assert result["success"], ASSERT_MSGS["pvcs_remaining"].format(
        count=result["count"],
    )


@pytest.mark.sanity
@pytest.mark.order(63)
def test_pvcs_preserved_after_cleanup(host, delete_volume):
    """TC_CL_013: Verify PVCs preserved (Delete_volume=false).

    After a cleanup without ``Delete_volume=true``, PVCs must still
    exist so that persistent telemetry data survives redeployment.

    Skipped when ``Delete_volume=true`` because PVCs are expected to
    be deleted in that mode.
    """
    if delete_volume:
        pytest.skip(
            "Delete_volume=true — PVCs are deleted; "
            "skipping PVC preservation check"
        )

    tc = TC["pvcs_preserved_after_cleanup"]
    tl = TestLogger(tc["title"], tc["id"])

    result = verify_pvcs_preserved(host)

    if result["success"]:
        tl.passed(
            LOG_MSGS["pvcs_preserved"],
            result["details"],
        )
    else:
        tl.failed(
            LOG_MSGS["pvcs_not_preserved"],
            result["details"],
        )

    assert result["success"], ASSERT_MSGS["pvcs_not_preserved"]
