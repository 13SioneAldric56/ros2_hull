#!/usr/bin/env bash
# Send a lat/lon goal with workspace environment loaded.
set -eo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

_setup_bash=""
if [ -f "${SCRIPT_DIR}/../../../../setup.bash" ]; then
    _setup_bash="${SCRIPT_DIR}/../../../../setup.bash"
elif [ -f "${SCRIPT_DIR}/../../../install/setup.bash" ]; then
    _setup_bash="${SCRIPT_DIR}/../../../install/setup.bash"
fi

if [ -z "${_setup_bash}" ]; then
    echo "Cannot find install/setup.bash. Run:" >&2
    echo "  source ~/ros2_hull/install/setup.bash" >&2
    exit 1
fi

# colcon setup.bash may reference unset vars (e.g. COLCON_TRACE); disable nounset while sourcing.
set +u
# shellcheck source=/dev/null
source "${_setup_bash}"

exec ros2 run hull_navigation send_nav_goal "$@"
